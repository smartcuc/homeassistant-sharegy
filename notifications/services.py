##########################
# notifications/services.py
##########################

import json
import logging
from typing import Dict, Any, Optional
from datetime import datetime, time
from django.conf import settings
from django.utils import timezone
from pywebpush import webpush, WebPushException

from notifications.models import DeviceSubscription, NotificationPreference

logger = logging.getLogger(__name__)


def is_in_quiet_hours(pref: NotificationPreference) -> bool:
    """
    Prüft, ob der aktuelle Zeitpunkt innerhalb der konfigurierten Ruhezeit liegt.
    """
    if not pref or not pref.quiet_hours_enabled:
        return False

    now_time = timezone.localtime().time()
    start = pref.quiet_hours_start
    end = pref.quiet_hours_end

    if start <= end:
        # z. B. 13:00 bis 15:00
        return start <= now_time <= end
    else:
        # Über Mitternacht hinweg, z. B. 22:00 bis 07:00
        return now_time >= start or now_time <= end


def send_web_push(subscription: DeviceSubscription, payload: Dict[str, Any]) -> bool:
    """
    Sendet eine Web-Push Benachrichtigung über die W3C VAPID Schnittstelle.
    """
    if not subscription.endpoint or not subscription.p256dh_key or not subscription.auth_key:
        logger.warning("Subscription %s fehlt endpoint/keys.", subscription.id)
        return False

    subscription_info = {
        "endpoint": subscription.endpoint,
        "keys": {
            "p256dh": subscription.p256dh_key,
            "auth": subscription.auth_key,
        },
    }

    vapid_private_key = getattr(settings, "VAPID_PRIVATE_KEY", None)
    vapid_claims = {
        "sub": getattr(settings, "VAPID_ADMIN_EMAIL", "mailto:support@sharegy.cloud"),
    }

    try:
        response = webpush(
            subscription_info=subscription_info,
            data=json.dumps(payload),
            vapid_private_key=vapid_private_key,
            vapid_claims=vapid_claims,
            ttl=86400,  # 24 Stunden Vorhaltezeit beim Push-Server
        )
        subscription.last_used_at = timezone.now()
        subscription.save(update_fields=["last_used_at"])
        logger.info("Web-Push erfolgreich gesendet an %s (Status: %s)", subscription.device_name or subscription.id, response.status_code if hasattr(response, "status_code") else 200)
        return True
    except WebPushException as ex:
        status_code = ex.response.status_code if ex.response is not None else 0
        logger.warning("WebPush Fehler für Subscription %s: %s (Status: %s)", subscription.id, str(ex), status_code)
        # 404 Not Found oder 410 Gone -> Gerät/Browser hat Push abbestellt -> Subscription deaktivieren
        if status_code in (404, 410):
            subscription.is_active = False
            subscription.save(update_fields=["is_active"])
            logger.info("Abgelaufene Subscription %s deaktiviert.", subscription.id)
        return False
    except Exception as ex:
        logger.error("Unerwarteter Fehler beim Web-Push Versand an %s: %s", subscription.id, str(ex))
        return False


def dispatch_alert_push(alert_event) -> int:
    """
    Verteilt eine AlertEvent-Benachrichtigung an alle aktiven Push-Abonnements des Home-Besitzers / Nutzers.
    Berücksichtigt Quiet Hours und Kategorie-Filter.
    Gibt die Anzahl der erfolgreich zugestellten Pushes zurück.
    """
    home = alert_event.home
    if not home:
        return 0

    user = home.user
    if not user:
        return 0

    pref, _ = NotificationPreference.objects.get_or_create(user=user)

    if not pref.push_enabled:
        logger.debug("Push für User %s ist global deaktiviert.", user.email)
        return 0

    # 1. Kategorie-Filter prüfen
    alert_type = alert_event.alert_type
    if alert_type in ("battery_empty", "battery_charging_stopped") and not pref.notify_battery:
        return 0
    if alert_type in ("night_leakage", "high_consumption") and not pref.notify_leakage:
        return 0
    if alert_type in ("no_pv", "pv_anomaly") and not pref.notify_pv:
        return 0
    if alert_type in ("negative_price", "price_peak") and not pref.notify_prices:
        return 0
    if alert_type in ("device_offline",) and not pref.notify_device_status:
        return 0

    # 2. Ruhezeit prüfen
    if is_in_quiet_hours(pref):
        is_critical = alert_event.severity == "critical"
        if not (is_critical and pref.allow_critical_in_quiet_hours):
            logger.info("Push für Alert %s unterdrückt wegen aktiver Ruhezeit für User %s.", alert_event.id, user.email)
            return 0

    # 3. Payload schnüren
    icon_map = {
        "critical": "🚨",
        "warning": "⚠️",
        "info": "💡",
    }
    badge_icon = icon_map.get(alert_event.severity, "⚡")

    payload = {
        "title": f"{badge_icon} {alert_event.title}",
        "body": alert_event.message,
        "icon": "/logo192.png",
        "badge": "/favicon.ico",
        "tag": f"sharegy-alert-{alert_event.id}",
        "data": {
            "url": "/app/alerts",
            "alert_id": str(alert_event.id),
            "alert_type": alert_event.alert_type,
            "severity": alert_event.severity,
            "created_at": alert_event.created_at.isoformat() if alert_event.created_at else timezone.now().isoformat(),
        },
    }

    # 4. An alle aktiven Subscriptions ausliefern
    subscriptions = DeviceSubscription.objects.filter(user=user, is_active=True)
    success_count = 0

    for sub in subscriptions:
        if sub.device_type == DeviceSubscription.DEVICE_WEB_PUSH:
            if send_web_push(sub, payload):
                success_count += 1
        # Platzhalter für native FCM/APNs Dispatcher
        elif sub.fcm_token:
            logger.debug("FCM Native Push Dispatch an %s", sub.device_name)

    return success_count


def send_test_push(user) -> Dict[str, Any]:
    """
    Versendet eine Sofort-Testnachricht an alle aktiven Geräte des Nutzers.
    """
    subscriptions = DeviceSubscription.objects.filter(user=user, is_active=True)
    if not subscriptions.exists():
        return {
            "success": False,
            "count": 0,
            "message": "Keine aktiven Push-Geräte für dieses Konto registriert. Bitte aktiviere Push zuerst im Browser.",
        }

    payload = {
        "title": "⚡ Sharegy Live-Test",
        "body": "Perfekt! Dein Smartphone & Browser empfangen Push-Alarme in Echtzeit.",
        "icon": "/logo192.png",
        "badge": "/favicon.ico",
        "tag": "sharegy-test-push",
        "data": {
            "url": "/app/alerts",
            "type": "test",
        },
    }

    sent = 0
    for sub in subscriptions:
        if sub.device_type == DeviceSubscription.DEVICE_WEB_PUSH:
            if send_web_push(sub, payload):
                sent += 1

    return {
        "success": sent > 0,
        "count": sent,
        "total_devices": subscriptions.count(),
        "message": f"Test-Push erfolgreich an {sent} von {subscriptions.count()} Gerät(en) gesendet.",
    }
