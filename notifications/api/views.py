#############################
# notifications/api/views.py
#############################

import logging
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.conf import settings

from notifications.models import DeviceSubscription, NotificationPreference
from notifications.services import send_test_push

logger = logging.getLogger(__name__)


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def vapid_public_key(request):
    """
    Liefert den öffentlichen VAPID-Schlüssel für die Browser-Registrierung.
    """
    key = getattr(settings, "VAPID_PUBLIC_KEY", "")
    return Response({
        "publicKey": key,
    })


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def subscribe_device(request):
    """
    Registriert ein neues Push-Abonnement (W3C Web-Push oder FCM).
    """
    data = request.data or {}
    endpoint = data.get("endpoint", "").strip()
    keys = data.get("keys", {})
    p256dh = keys.get("p256dh", "").strip()
    auth = keys.get("auth", "").strip()
    fcm_token = data.get("fcm_token", "").strip()
    device_type = data.get("device_type", DeviceSubscription.DEVICE_WEB_PUSH)
    device_name = data.get("device_name", "")[:128]
    user_agent = request.META.get("HTTP_USER_AGENT", "")[:512]

    # Ermittle Standard-Home des Nutzers falls vorhanden
    home = getattr(request.user, "homes", None)
    default_home = home.first() if home and hasattr(home, "first") else None

    if not endpoint and not fcm_token:
        return Response(
            {"error": "Endpoint oder FCM-Token ist erforderlich."},
            status=status.HTTP_400_BAD_REQUEST,
        )

    # Prüfen, ob bereits eine Subscription mit diesem Endpoint existiert
    if endpoint:
        sub, created = DeviceSubscription.objects.update_or_create(
            endpoint=endpoint,
            defaults={
                "user": request.user,
                "home": default_home,
                "device_type": device_type,
                "p256dh_key": p256dh,
                "auth_key": auth,
                "device_name": device_name or "Web-Browser",
                "user_agent": user_agent,
                "is_active": True,
            },
        )
    else:
        sub, created = DeviceSubscription.objects.update_or_create(
            user=request.user,
            fcm_token=fcm_token,
            defaults={
                "home": default_home,
                "device_type": device_type,
                "device_name": device_name or "Mobiles Gerät",
                "user_agent": user_agent,
                "is_active": True,
            },
        )

    return Response({
        "success": True,
        "subscription_id": str(sub.id),
        "created": created,
        "device_name": sub.device_name,
    })


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def unsubscribe_device(request):
    """
    Deaktiviert ein Push-Abonnement.
    """
    data = request.data or {}
    endpoint = data.get("endpoint", "").strip()
    fcm_token = data.get("fcm_token", "").strip()

    count = 0
    if endpoint:
        count = DeviceSubscription.objects.filter(user=request.user, endpoint=endpoint).update(is_active=False)
    elif fcm_token:
        count = DeviceSubscription.objects.filter(user=request.user, fcm_token=fcm_token).update(is_active=False)

    return Response({
        "success": True,
        "deactivated_count": count,
    })


@api_view(["GET", "POST", "PUT"])
@permission_classes([IsAuthenticated])
def notification_preferences(request):
    """
    Abrufen und Aktualisieren von Push-Präferenzen & Ruhezeiten.
    """
    pref, _ = NotificationPreference.objects.get_or_create(user=request.user)

    if request.method in ["POST", "PUT"]:
        data = request.data or {}
        if "push_enabled" in data:
            pref.push_enabled = bool(data["push_enabled"])
        if "quiet_hours_enabled" in data:
            pref.quiet_hours_enabled = bool(data["quiet_hours_enabled"])
        if "quiet_hours_start" in data:
            pref.quiet_hours_start = str(data["quiet_hours_start"])
        if "quiet_hours_end" in data:
            pref.quiet_hours_end = str(data["quiet_hours_end"])
        if "allow_critical_in_quiet_hours" in data:
            pref.allow_critical_in_quiet_hours = bool(data["allow_critical_in_quiet_hours"])
        if "notify_battery" in data:
            pref.notify_battery = bool(data["notify_battery"])
        if "notify_leakage" in data:
            pref.notify_leakage = bool(data["notify_leakage"])
        if "notify_pv" in data:
            pref.notify_pv = bool(data["notify_pv"])
        if "notify_prices" in data:
            pref.notify_prices = bool(data["notify_prices"])
        if "notify_device_status" in data:
            pref.notify_device_status = bool(data["notify_device_status"])

        pref.save()

    active_devices_count = DeviceSubscription.objects.filter(user=request.user, is_active=True).count()

    return Response({
        "push_enabled": pref.push_enabled,
        "quiet_hours_enabled": pref.quiet_hours_enabled,
        "quiet_hours_start": str(pref.quiet_hours_start)[:5],
        "quiet_hours_end": str(pref.quiet_hours_end)[:5],
        "allow_critical_in_quiet_hours": pref.allow_critical_in_quiet_hours,
        "notify_battery": pref.notify_battery,
        "notify_leakage": pref.notify_leakage,
        "notify_pv": pref.notify_pv,
        "notify_prices": pref.notify_prices,
        "notify_device_status": pref.notify_device_status,
        "active_devices_count": active_devices_count,
    })


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def trigger_test_push(request):
    """
    Sendet sofort einen Test-Push an alle aktiven Geräte des Nutzers.
    """
    res = send_test_push(request.user)
    return Response(res)
