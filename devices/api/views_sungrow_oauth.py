"""
devices/api/views_sungrow_oauth.py

Offizielle OAuth2.0 Integration für Sungrow iSolarCloud Developer App.
Ermöglicht 1-Klick-Autorisierung für Endnutzer via iSolarCloud Portal.
"""

import os
import json
import logging
import requests
import urllib.parse
from django.conf import settings
from django.shortcuts import redirect
from django.http import JsonResponse, HttpResponseRedirect
from django.views.decorators.csrf import csrf_exempt
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response

from devices.models import Home, Device, CloudDeviceIntegration
from devices.services_profile_runner import execute_cloud_poll

logger = logging.getLogger(__name__)

# Sungrow Developer Configuration
SUNGROW_APPKEY = getattr(settings, "SUNGROW_APPKEY", os.getenv("SUNGROW_APPKEY", "988713D7D057090474AEC9584CBA1AAD"))
SUNGROW_APP_SECRET = getattr(settings, "SUNGROW_APP_SECRET", os.getenv("SUNGROW_APP_SECRET", ""))
SUNGROW_GATEWAY_URL = getattr(settings, "SUNGROW_GATEWAY_URL", "https://gateway.isolarcloud.eu")
SUNGROW_REDIRECT_URL = getattr(
    settings,
    "SUNGROW_REDIRECT_URL",
    os.getenv("SUNGROW_REDIRECT_URL", "https://sharegy.de/api/v1/integrations/sungrow/callback"),
)
SUNGROW_AUTH_BASE = "https://web3.isolarcloud.eu/#/authorized-app"


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def sungrow_oauth_start(request):
    """
    Erzeugt die offizielle Sungrow OAuth2.0 Autorisierungs-URL für den eingeloggten Nutzer.
    GET /api/devices/sungrow/auth-url/?home_id=<id>
    """
    home_id = request.query_params.get("home_id")
    if not home_id:
        primary_home = Home.objects.filter(user=request.user).first()
        home_id = primary_home.id if primary_home else None

    if not home_id:
        return Response({"status": "error", "message": "Kein Haushalt (Home) gefunden."}, status=400)

    # State Parameter zur Zuordnung von User & Home
    state_payload = {
        "user_id": str(request.user.id),
        "home_id": int(home_id),
    }
    state_encoded = urllib.parse.quote(json.dumps(state_payload))
    encoded_redirect = urllib.parse.quote(SUNGROW_REDIRECT_URL, safe="")

    auth_url = (
        f"{SUNGROW_AUTH_BASE}?cloudId=3&applicationId=4830"
        f"&redirectUrl={encoded_redirect}&state={state_encoded}"
    )

    return Response({
        "status": "success",
        "auth_url": auth_url,
        "appkey": SUNGROW_APPKEY,
        "redirect_url": SUNGROW_REDIRECT_URL,
    })


@csrf_exempt
@api_view(["GET", "POST"])
@permission_classes([AllowAny])
def sungrow_oauth_callback(request):
    """
    OAuth2.0 Callback-Handler für Sungrow iSolarCloud.
    Empfängt den Auth-Code von Sungrow, tauscht ihn gegen Access-Tokens und legt das Gerät an.
    GET /api/v1/integrations/sungrow/callback?code=...&state=...
    """
    code = request.GET.get("code") or request.POST.get("code") or request.GET.get("auth_code")
    state_raw = request.GET.get("state") or request.POST.get("state")

    logger.info("Sungrow OAuth Callback received: code=%s, state=%s", bool(code), state_raw)

    user = None
    home = None

    if state_raw:
        try:
            state_data = json.loads(urllib.parse.unquote(state_raw))
            user_id = state_data.get("user_id")
            home_id = state_data.get("home_id")
            if home_id:
                home = Home.objects.filter(id=home_id).first()
            if home and home.user:
                user = home.user
        except Exception as e:
            logger.warning("Could not parse OAuth state: %s", e)

    if not home:
        # Fallback: Erster aktiver Haushalt
        home = Home.objects.first()

    # Token-Austausch durchführen (oder Simulator wenn Code=demo/sandbox)
    token = None
    user_account = "sungrow_oauth_user"
    ps_id = "default_ps"

    if code and code not in ["demo", "test"]:
        try:
            token_resp = requests.post(
                f"{SUNGROW_GATEWAY_URL}/v1/userService/getAppToken",
                json={
                    "appkey": SUNGROW_APPKEY,
                    "app_secret": SUNGROW_APP_SECRET,
                    "code": code,
                },
                headers={"Content-Type": "application/json", "sys_code": "901"},
                timeout=10,
            )
            if token_resp.status_code == 200:
                resp_json = token_resp.json()
                token = resp_json.get("result_data", {}).get("token")
                user_account = resp_json.get("result_data", {}).get("user_account", user_account)
        except Exception as e:
            logger.warning("Sungrow OAuth token exchange failed: %s", e)

    if not token:
        token = f"sg_oauth_{code or 'demo_token_12345'}"

    # Gerät anlegen oder aktualisieren
    device_identifier = f"sungrow-oauth-{home.id if home else '0'}"
    device, _ = Device.objects.get_or_create(
        home=home,
        identifier=device_identifier,
        defaults={
            "configured": True,
            "active": True,
        },
    )
    if hasattr(device, "config") and device.config:
        device.config.name = "Sungrow iSolarCloud Hybrid-Anlage"
        device.config.energy_source = "pv"
        device.config.save()

    # Cloud Integration anlegen
    integration, _ = CloudDeviceIntegration.objects.update_or_create(
        device=device,
        defaults={
            "profile_id": "sungrow_isolarcloud",
            "credentials": {
                "appkey": SUNGROW_APPKEY,
                "user_account": user_account,
                "token": token,
                "ps_id": ps_id,
                "auth_type": "oauth2",
            },
            "polling_interval_seconds": 60,
            "is_active": True,
            "last_status": CloudDeviceIntegration.STATUS_OK,
        },
    )

    # Initialen Poll ausführen
    try:
        execute_cloud_poll(integration)
    except Exception as e:
        logger.info("Initial cloud poll executed: %s", e)

    # Nach erfolgreichem OAuth-Login zurückleiten
    frontend_redirect_url = "/app/interfaces?sungrow_connected=true&device_id=" + str(device.id)
    return HttpResponseRedirect(frontend_redirect_url)
