"""
devices/api/views_profiles.py

REST-API Endpoints für deklarative Hersteller-Cloud-Profile (Sungrow iSolarCloud, SolarEdge, Fronius).
"""

import logging
import uuid
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.response import Response
from rest_framework import status

from devices.models import Device, DeviceConfig, CloudDeviceIntegration, Home
from devices.services_profile_runner import (
    list_available_profiles,
    load_profile,
    test_cloud_credentials,
    execute_cloud_poll,
)

logger = logging.getLogger(__name__)


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def list_cloud_profiles_view(request):
    """
    Liefert alle verfügbaren Hersteller-Profile mit Metadaten und Formularfeldern.
    """
    profiles = list_available_profiles()
    return Response({
        "status": "success",
        "profiles": profiles,
        "count": len(profiles),
    })


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def list_user_cloud_integrations_view(request):
    """
    Liefert alle aktiven und konfigurierten CloudDeviceIntegration-Objekte des aktuellen Benutzers.
    """
    user = request.user
    home_id = request.query_params.get("home_id")
    qs = CloudDeviceIntegration.objects.filter(device__home__user=user).select_related("device", "device__config", "device__home")
    if home_id:
        qs = qs.filter(device__home_id=home_id)

    profiles_cache = {p["id"]: p for p in list_available_profiles()}
    items = []
    for item in qs:
        prof = profiles_cache.get(item.profile_id, {})
        cfg = getattr(item.device, "config", None)
        name = cfg.name if (cfg and cfg.name) else item.device.identifier

        masked_creds = {}
        for k, v in (item.credentials or {}).items():
            if any(secret_w in k.lower() for secret_w in ["password", "secret", "token", "key", "pass"]):
                masked_creds[k] = "••••••••" if v else ""
            else:
                masked_creds[k] = v

        items.append({
            "id": str(item.id),
            "device_id": item.device.id,
            "device_identifier": item.device.identifier,
            "device_name": name,
            "profile_id": item.profile_id,
            "profile_name": prof.get("name") or item.profile_id,
            "vendor": prof.get("vendor") or ("sungrow" if "sungrow" in item.profile_id else "other"),
            "polling_interval_seconds": item.effective_polling_interval,
            "custom_polling_interval_seconds": item.polling_interval_seconds,
            "is_active": item.is_active,
            "last_status": item.last_status,
            "last_polled_at": item.last_polled_at.isoformat() if item.last_polled_at else None,
            "last_error_message": item.last_error_message or "",
            "credentials_masked": masked_creds,
            "credentials": item.credentials or {},
        })

    return Response({
        "status": "success",
        "integrations": items,
        "count": len(items),
    })


@api_view(["GET", "PUT", "DELETE"])
@permission_classes([IsAuthenticated])
def manage_user_cloud_integration_view(request, integration_id):
    """
    CRUD Endpoint für eine spezifische CloudDeviceIntegration.
    """
    user = request.user
    integration = CloudDeviceIntegration.objects.filter(
        id=integration_id,
        device__home__user=user,
    ).select_related("device", "device__config").first()

    if not integration:
        return Response(
            {"status": "error", "message": "Cloud-Integration nicht gefunden."},
            status=status.HTTP_404_NOT_FOUND,
        )

    if request.method == "GET":
        cfg = getattr(integration.device, "config", None)
        return Response({
            "status": "success",
            "integration": {
                "id": str(integration.id),
                "device_id": integration.device.id,
                "device_name": cfg.name if (cfg and cfg.name) else integration.device.identifier,
                "profile_id": integration.profile_id,
                "polling_interval_seconds": integration.effective_polling_interval,
                "custom_polling_interval_seconds": integration.polling_interval_seconds,
                "is_active": integration.is_active,
                "last_status": integration.last_status,
                "last_polled_at": integration.last_polled_at.isoformat() if integration.last_polled_at else None,
                "last_error_message": integration.last_error_message,
                "credentials": integration.credentials or {},
            }
        })

    if request.method == "PUT":
        data = request.data
        name = data.get("name")
        credentials = data.get("credentials")
        interval_raw = data.get("polling_interval") if "polling_interval" in data else data.get("polling_interval_seconds")
        is_active = data.get("is_active")

        cfg = getattr(integration.device, "config", None)
        if name and cfg:
            cfg.name = name
            cfg.save(update_fields=["name"])

        if credentials is not None and isinstance(credentials, dict):
            merged_creds = dict(integration.credentials or {})
            for k, v in credentials.items():
                if v != "••••••••" and v is not None:
                    merged_creds[k] = v
            integration.credentials = merged_creds

        if interval_raw is not None:
            integration.polling_interval_seconds = int(interval_raw) if str(interval_raw).strip() != "" else None
        if is_active is not None:
            integration.is_active = bool(is_active)

        integration.save()
        poll_res = execute_cloud_poll(integration)

        return Response({
            "status": "success",
            "message": "Cloud-Integration erfolgreich aktualisiert.",
            "integration_id": str(integration.id),
            "poll_result": poll_res,
        })

    if request.method == "DELETE":
        device = integration.device
        integration.delete()
        device.active = False
        device.configured = False
        device.save(update_fields=["active", "configured"])
        return Response({
            "status": "success",
            "message": "Cloud-Integration erfolgreich getrennt und entfernt.",
        })


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def test_cloud_connection_view(request):
    """
    Testet die eingegebenen Zugangsdaten für ein Profil live oder im Simulator.
    Payload: { profile_id: "sungrow_isolarcloud", credentials: { appkey, user_account, ... } }
    """
    profile_id = request.data.get("profile_id")
    credentials = request.data.get("credentials") or {}

    if not profile_id:
        return Response(
            {"status": "error", "message": "Parameter 'profile_id' ist erforderlich."},
            status=status.HTTP_400_BAD_REQUEST,
        )

    try:
        result = test_cloud_credentials(profile_id, credentials)
        return Response(result)
    except Exception as e:
        logger.warning("Cloud credentials test failed: %s", e)
        return Response(
            {"status": "error", "message": str(e)},
            status=status.HTTP_400_BAD_REQUEST,
        )


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def integrate_cloud_device_view(request):
    """
    Erstellt ein neues Cloud-Gerät oder verknüpft ein bestehendes Gerät mit einem Cloud-Profil.
    Payload: {
        integration_id: optional,
        home_id: ...,
        name: "Sungrow SH10RT",
        profile_id: "sungrow_isolarcloud",
        credentials: { appkey, user_account, user_password, ps_id },
        polling_interval: 60
    }
    """
    user = request.user
    integration_id = request.data.get("integration_id")
    home_id = request.data.get("home_id")
    name = request.data.get("name") or "Cloud-Wechselrichter"
    profile_id = request.data.get("profile_id")
    credentials = request.data.get("credentials") or {}
    interval_raw = request.data.get("polling_interval") if "polling_interval" in request.data else request.data.get("polling_interval_seconds")
    interval = int(interval_raw) if (interval_raw is not None and str(interval_raw).strip() != "") else None

    if not profile_id:
        return Response({"status": "error", "message": "profile_id ist erforderlich."}, status=400)

    # Wenn bestehende integration_id übergeben wurde: Aktualisieren
    if integration_id:
        integration = CloudDeviceIntegration.objects.filter(
            id=integration_id,
            device__home__user=user,
        ).select_related("device", "device__config").first()
        if integration:
            cfg = getattr(integration.device, "config", None)
            if cfg and name:
                cfg.name = name
                cfg.save(update_fields=["name"])
            merged_creds = dict(integration.credentials or {})
            for k, v in credentials.items():
                if v != "••••••••" and v is not None:
                    merged_creds[k] = v
            integration.credentials = merged_creds
            integration.profile_id = profile_id
            if interval is not None:
                integration.polling_interval_seconds = interval
            integration.is_active = True
            integration.save()
            poll_res = execute_cloud_poll(integration)
            return Response({
                "status": "success",
                "message": f"Gerät '{name}' erfolgreich aktualisiert!",
                "device_id": integration.device.id,
                "integration_id": str(integration.id),
                "poll_result": poll_res,
            })

    # Home finden oder erstes Home des Users nutzen
    home = None
    if home_id:
        home = Home.objects.filter(id=home_id, user=user).first()
    if not home:
        home = Home.objects.filter(user=user).first()

    if not home:
        return Response({"status": "error", "message": "Kein gültiges Gebäude (Home) gefunden."}, status=400)

    try:
        profile = load_profile(profile_id)
    except Exception as e:
        return Response({"status": "error", "message": f"Ungültiges Profil: {e}"}, status=400)

    # Eindeutiger Identifier, um mehrere WRs desselben Herstellers im selben Home zu ermöglichen
    base_identifier = f"cloud-{profile_id}-{home.id}"[:45]
    if Device.objects.filter(home=home, identifier=base_identifier).exists():
        identifier = f"{base_identifier}-{uuid.uuid4().hex[:6]}"[:64]
    else:
        identifier = base_identifier

    # Gerät anlegen
    device, created = Device.objects.get_or_create(
        home=home,
        identifier=identifier,
        defaults={"configured": True, "active": True},
    )

    # DeviceConfig
    config, _ = DeviceConfig.objects.get_or_create(
        device=device,
        defaults={"home": home, "name": name},
    )
    if not config.name:
        config.name = name
        config.save(update_fields=["name"])

    # CloudDeviceIntegration
    integration, int_created = CloudDeviceIntegration.objects.get_or_create(
        device=device,
        defaults={
            "profile_id": profile_id,
            "credentials": credentials,
            "polling_interval_seconds": interval,
            "is_active": True,
            "last_status": CloudDeviceIntegration.STATUS_PENDING,
        },
    )
    if not int_created:
        integration.profile_id = profile_id
        integration.credentials = credentials
        if interval is not None:
            integration.polling_interval_seconds = interval
        integration.is_active = True
        integration.save()

    # Direkt einen ersten Sync durchführen
    poll_res = execute_cloud_poll(integration)

    return Response({
        "status": "success",
        "message": f"Gerät '{name}' erfolgreich mit {profile.get('name')} verknüpft!",
        "device_id": device.id,
        "integration_id": str(integration.id),
        "poll_result": poll_res,
    })


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def poll_cloud_device_now_view(request, device_id):
    """
    Triggert eine manuelle Sofort-Abfrage der Cloud-Daten für ein Gerät.
    """
    integration = CloudDeviceIntegration.objects.filter(
        device__id=device_id,
        device__home__user=request.user,
    ).first()

    if not integration:
        return Response(
            {"status": "error", "message": "Keine Cloud-Integration für dieses Gerät gefunden."},
            status=status.HTTP_404_NOT_FOUND,
        )

    res = execute_cloud_poll(integration)
    return Response(res)


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def get_cloud_integration_status_view(request, device_id):
    """
    Liefert den aktuellen Kopplungs- und Polling-Status einer Cloud-Integration.
    """
    integration = CloudDeviceIntegration.objects.filter(
        device__id=device_id,
        device__home__user=request.user,
    ).first()

    if not integration:
        return Response(
            {"status": "error", "message": "Keine Cloud-Integration für dieses Gerät gefunden."},
            status=status.HTTP_404_NOT_FOUND,
        )

    return Response({
        "status": "success",
        "integration_id": str(integration.id),
        "profile_id": integration.profile_id,
        "is_active": integration.is_active,
        "last_status": integration.last_status,
        "last_polled_at": integration.last_polled_at.isoformat() if integration.last_polled_at else None,
        "last_error_message": integration.last_error_message,
        "polling_interval_seconds": integration.polling_interval_seconds,
    })


@api_view(["POST"])
@permission_classes([IsAdminUser])
def update_cloud_polling_interval_view(request):
    """
    Admin-Endpoint: Aktualisiert das Abfrage-Intervall (z. B. 15s) für Cloud-Integrationen (EMS-System Parameter).
    """
    profile_id = request.data.get("profile_id")
    interval = int(request.data.get("polling_interval") or request.data.get("interval") or 15)

    qs = CloudDeviceIntegration.objects.all()
    if profile_id:
        qs = qs.filter(profile_id=profile_id)

    updated_count = qs.update(polling_interval_seconds=interval)
    return Response({
        "status": "success",
        "polling_interval_seconds": interval,
        "updated_integrations": updated_count,
    })

