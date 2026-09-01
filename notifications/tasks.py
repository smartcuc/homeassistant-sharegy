"""
notifications/tasks.py

Asynchrone Celery Tasks für das Push- & Benachrichtigungssystem (Sharegy).
Entkoppelt den Push-Versand (Web-Push, FCM, APNs) vom HTTP-Request-Cycle.
"""

import logging
from datetime import timedelta
from django.utils import timezone
from celery import shared_task

from notifications.models import DeviceSubscription
from notifications.services import dispatch_alert_push, send_test_push

logger = logging.getLogger(__name__)


@shared_task(
    bind=True,
    name="notifications.dispatch_alert_push",
    max_retries=3,
    default_retry_delay=10,
    queue="realtime",  # Hohe Priorität für Alarme
)
def dispatch_alert_push_task(self, alert_event_id: str):
    """
    Asynchroner Celery Task zum Ausliefern von Push-Benachrichtigungen für ein AlertEvent.
    """
    from alerts.models import AlertEvent

    try:
        alert_event = AlertEvent.objects.select_related("home", "home__user", "device").filter(id=alert_event_id).first()
        if not alert_event:
            logger.warning("AlertEvent %s nicht gefunden für Push-Versand.", alert_event_id)
            return {"status": "not_found", "sent_count": 0}

        sent_count = dispatch_alert_push(alert_event)
        logger.info("Push-Task für Alert %s abgeschlossen: %s Nachricht(en) gesendet.", alert_event_id, sent_count)
        return {"status": "success", "alert_id": alert_event_id, "sent_count": sent_count}

    except Exception as exc:
        logger.error("Fehler im dispatch_alert_push_task für Alert %s: %s", alert_event_id, exc)
        raise self.retry(exc=exc)


@shared_task(
    name="notifications.send_test_push",
    queue="realtime",
)
def send_test_push_task(user_id: int):
    """
    Asynchroner Celery Task für den Versand eines Sofort-Test-Pushes.
    """
    from accounts.models import User

    user = User.objects.filter(id=user_id).first()
    if not user:
        return {"status": "user_not_found"}

    result = send_test_push(user)
    return result


@shared_task(
    name="notifications.cleanup_inactive_subscriptions",
    queue="background",
)
def cleanup_inactive_subscriptions_task(days_inactive: int = 90):
    """
    Regelmäßiger Housekeeping-Task:
    Deaktiviert oder löscht Push-Subscriptions, die seit mehr als X Tagen nicht mehr genutzt wurden.
    """
    cutoff = timezone.now() - timedelta(days=days_inactive)
    
    # Inaktive Subscriptions deaktivieren
    deactivated = DeviceSubscription.objects.filter(
        is_active=True,
        last_used_at__lt=cutoff,
    ).update(is_active=False)

    # Veraltete inaktive Subscriptions löschen (älter als 180 Tage inaktiv)
    hard_cutoff = timezone.now() - timedelta(days=180)
    deleted_count, _ = DeviceSubscription.objects.filter(
        is_active=False,
        last_used_at__lt=hard_cutoff,
    ).delete()

    logger.info(
        "Push-Subscription Cleanup: %s deaktiviert, %s gelöscht.",
        deactivated,
        deleted_count,
    )
    return {
        "deactivated_count": deactivated,
        "deleted_count": deleted_count,
    }
