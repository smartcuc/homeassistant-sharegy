#####################
# operations/tasks.py
#####################

import logging
import redis

from celery import shared_task

from django.conf import settings
from django.utils import timezone
from datetime import timedelta
from market.models import SpotPrice
from devices.models import (
    Device,
    DeviceMetric,
    DeviceMetric1m,
    DeviceMetric5m,
    DeviceMetric15m,
    DeviceMetric1h,
)
from core.models import Meter
from forecast.models import WeatherForecast

from operations.models import HealthState


logger = logging.getLogger(__name__)


@shared_task
def run_health_checks():

    checks = [
        check_spot_prices,
        check_celery_queues,
        check_aggregation_1m,
        check_aggregation_5m,
        check_aggregation_15m,
        check_aggregation_1h,
        check_mqtt,
        check_tibber_sync,
        check_weather_sync,
        check_active_devices,
        check_device_baselines,
    ]

    for check in checks:
        try:
            check()
        except Exception:
            logger.exception(
                "health check failed: %s",
                check.__name__,
            )

    # 🚨 Automatische Ticket-Erstellung bei Abweichungen / Erholungen
    try:
        check_and_create_incident_tickets()
    except Exception:
        logger.exception("Fehler bei automatischer Incident-Triage")


def check_device_baselines():
    """
    Überwacht zyklisch die Baseline aller konfigurierten Geräte (Standby-Anstieg, Dauerlauf).
    """
    from devices.services_profiling import evaluate_all_device_baselines
    res = evaluate_all_device_baselines()
    HealthState.objects.update_or_create(
        key="device_baselines",
        defaults={
            "status": "error" if res["anomalies"] > 0 else "ok",
            "value": f"{res['evaluated']} Geräte überwacht, {res['anomalies']} Anomalien",
            "details": res,
        },
    )




def check_spot_prices():

    latest = SpotPrice.objects.order_by("-timestamp").first()

    if not latest:

        HealthState.objects.update_or_create(
            key="spot_prices",
            defaults={
                "status": "error",
                "value": "no spot prices available",
                "details": {},
            },
        )

        return

    timestamp = latest.timestamp

    if timezone.is_naive(timestamp):
        timestamp = timezone.make_aware(timestamp)

    age = timezone.now() - timestamp

    if age.total_seconds() > 21600:

        status = "error"

    elif age.total_seconds() > 10800:

        status = "warn"

    else:

        status = "ok"

    HealthState.objects.update_or_create(
        key="spot_prices",
        defaults={
            "status": status,
            "value": (f"latest spot price: " f"{timestamp.isoformat()}"),
            "details": {
                "age_seconds": int(age.total_seconds()),
                "timestamp": timestamp.isoformat(),
            },
        },
    )


def check_celery_queues():

    redis_url = settings.CELERY_BROKER_URL

    client = redis.from_url(redis_url)

    queues = [
        "fiscal",
        "realtime",
        "analytics",
        "background",
        "celery",
    ]

    valid_keys = [f"celery_queue_{q}" for q in queues]
    # 🧹 Veraltete Queue-Keys aus früheren Versionen automatisch bereinigen
    HealthState.objects.filter(key__startswith="celery_queue_").exclude(key__in=valid_keys).delete()

    for queue in queues:

        queue_length = client.llen(queue)

        if queue_length >= 10000:

            status = "error"

        elif queue_length >= 1000:

            status = "warn"

        else:

            status = "ok"

        HealthState.objects.update_or_create(
            key=f"celery_queue_{queue}",
            defaults={
                "status": status,
                "value": str(queue_length),
                "details": {
                    "queue": queue,
                    "length": queue_length,
                },
            },
        )


def update_aggregation_health(
    key,
    model,
    warn_seconds=None,
    error_seconds=None,
    max_age_seconds=None,
):
    latest = model.objects.order_by("-bucket").first()

    if not latest:
        HealthState.objects.update_or_create(
            key=key,
            defaults={
                "status": "error",
                "value": "no data",
                "details": {},
            },
        )
        return

    age = timezone.now() - latest.bucket
    age_sec = int(age.total_seconds())

    if error_seconds is not None and warn_seconds is not None:
        if age_sec > error_seconds:
            status = "error"
        elif age_sec > warn_seconds:
            status = "warn"
        else:
            status = "ok"
    else:
        max_age = max_age_seconds or 10800
        if age_sec > max_age:
            status = "error"
        elif age_sec > (max_age / 2):
            status = "warn"
        else:
            status = "ok"

    HealthState.objects.update_or_create(
        key=key,
        defaults={
            "status": status,
            "value": latest.bucket.isoformat(),
            "details": {
                "age_seconds": age_sec,
            },
        },
    )


def check_aggregation_1m():
    update_aggregation_health(
        key="aggregation_1m",
        model=DeviceMetric1m,
        warn_seconds=300,    # 5 min
        error_seconds=600,   # 10 min
    )


def check_aggregation_5m():
    update_aggregation_health(
        key="aggregation_5m",
        model=DeviceMetric5m,
        warn_seconds=1200,   # 20 min
        error_seconds=2400,  # 40 min
    )


def check_aggregation_15m():
    update_aggregation_health(
        key="aggregation_15m",
        model=DeviceMetric15m,
        warn_seconds=4500,   # 75 min
        error_seconds=7200,  # 120 min
    )


def check_aggregation_1h():
    update_aggregation_health(
        key="aggregation_1h",
        model=DeviceMetric1h,
        warn_seconds=10800,  # 3 Stunden (Normal bis zu 2.5h)
        error_seconds=18000, # 5 Stunden
    )


def check_mqtt():

    latest = (
        Device.objects.exclude(last_seen__isnull=True).order_by("-last_seen").first()
    )

    if not latest:

        HealthState.objects.update_or_create(
            key="mqtt",
            defaults={
                "status": "error",
                "value": "no device seen",
                "details": {},
            },
        )

        return

    last_seen = latest.last_seen

    age = timezone.now() - latest.last_seen

    if age.total_seconds() > 900:

        status = "error"

    elif age.total_seconds() > 300:

        status = "warn"

    else:

        status = "ok"

    HealthState.objects.update_or_create(
        key="mqtt",
        defaults={
            "status": status,
            "value": latest.last_seen.isoformat(),
            "details": {
                "device_id": latest.id,
                "last_seen": last_seen.isoformat(),
                "age_seconds": int(age.total_seconds()),
            },
        },
    )


def check_tibber_sync():
    """Prüft den Zeitpunkt der letzten erfolgreichen Tibber-Synchronisation."""
    tibber_meter = (
        Meter.objects.filter(integration_type="tibber")
        .exclude(last_tibber_sync__isnull=True)
        .order_by("-last_tibber_sync")
        .first()
    )

    if not tibber_meter or not tibber_meter.last_tibber_sync:
        HealthState.objects.update_or_create(
            key="tibber_sync",
            defaults={
                "status": "warn",
                "value": "Keine aktiven Tibber-Zähler synchronisiert",
                "details": {"meters_count": Meter.objects.filter(integration_type="tibber").count()},
            },
        )
        return

    age = timezone.now() - tibber_meter.last_tibber_sync
    # Tibber sync sollte mindestens einmal alle 2-4 Stunden erfolgen
    if age.total_seconds() > 14400:  # > 4h
        status = "error"
    elif age.total_seconds() > 7200:  # > 2h
        status = "warn"
    else:
        status = "ok"

    HealthState.objects.update_or_create(
        key="tibber_sync",
        defaults={
            "status": status,
            "value": f"Zuletzt vor {int(age.total_seconds() // 60)} Min. ({tibber_meter.last_tibber_sync.strftime('%H:%M %d.%m.')})",
            "details": {
                "meter_id": str(tibber_meter.id),
                "last_sync": tibber_meter.last_tibber_sync.isoformat(),
                "age_minutes": int(age.total_seconds() // 60),
            },
        },
    )


def check_weather_sync():
    """Prüft die Aktualität der Wetter- und PV-Prognosedaten."""
    latest_forecast = WeatherForecast.objects.order_by("-ts").first()

    if not latest_forecast:
        HealthState.objects.update_or_create(
            key="weather_sync",
            defaults={
                "status": "error",
                "value": "Keine Wetterdaten vorhanden",
                "details": {},
            },
        )
        return

    # Prüfen, ob wir Daten für die Zukunft (mindestens die nächsten 12h) haben
    horizon = latest_forecast.ts - timezone.now()
    if horizon.total_seconds() < 21600:  # weniger als 6h Zukunft
        status = "error"
    elif horizon.total_seconds() < 43200:  # weniger als 12h Zukunft
        status = "warn"
    else:
        status = "ok"

    HealthState.objects.update_or_create(
        key="weather_sync",
        defaults={
            "status": status,
            "value": f"Prognose bis {latest_forecast.ts.strftime('%d.%m. %H:%M')} (Horizont: {int(horizon.total_seconds() // 3600)}h)",
            "details": {
                "latest_horizon": latest_forecast.ts.isoformat(),
                "horizon_hours": int(horizon.total_seconds() // 3600),
            },
        },
    )


def check_active_devices():
    """Ermittelt die Anzahl aktiver vs. inaktiver realer EMS-Geräte (Demo-Accounts ausgenommen)."""
    demo_emails = ["demo@sharegy.de", "demo@sharegy.local", "dev@example.com"]
    demo_usernames = ["demo", "dev_tibber"]

    real_devices = Device.objects.filter(
        active=True,
        pending_delete=False,
    ).exclude(
        home__user__email__in=demo_emails
    ).exclude(
        home__user__username__in=demo_usernames
    )

    total_configured = real_devices.filter(configured=True).count()
    active_cutoff = timezone.now() - timedelta(minutes=15)
    active_count = real_devices.filter(configured=True, last_seen__gte=active_cutoff).count()

    if total_configured == 0:
        status = "ok"
        val = f"1 Reales Gerät registriert (warten auf Ingest)" if real_devices.count() > 0 else "Keine konfigurierten Geräte vorhanden"
    elif active_count == 0:
        status = "warn"
        val = f"0 von {total_configured} Geräten online (letzte 15 Min.)"
    elif active_count < total_configured:
        status = "warn"
        val = f"{active_count} von {total_configured} Geräten online ({int(active_count / total_configured * 100)}%)"
    else:
        status = "ok"
        val = f"Alle {active_count} Geräte online"

    HealthState.objects.update_or_create(
        key="active_devices",
        defaults={
            "status": status,
            "value": val,
            "details": {
                "active_devices": active_count,
                "total_configured": total_configured,
                "offline_devices": max(0, total_configured - active_count),
            },
        },
    )


def check_and_create_incident_tickets():
    """
    Automatische Triage & Incident-Erstellung:
    Prüft alle HealthState-Einträge. Wenn ein Subsystem auf 'error' steht,
    wird automatisch ein Support-Ticket mit Prio 'urgent' oder 'high' erstellt
    (sofern für diesen Vorfall noch kein offenes Ticket existiert).
    Bei Erholung ('ok') wird das Ticket automatisch aktualisiert bzw. gelöst.
    """
    from support_desk.models import Ticket, TicketMessage
    from support_desk.services.ticket_engine import create_ticket

    states = HealthState.objects.all()
    for state in states:
        marker = f"[Auto-Incident: {state.key}]"
        open_ticket = Ticket.objects.filter(
            subject__contains=marker,
            status__in=[Ticket.STATUS_OPEN, Ticket.STATUS_IN_PROGRESS, Ticket.STATUS_WAITING_INTERNAL],
        ).first()

        if state.status == "error":
            if not open_ticket:
                # 🚨 Neues automatisches Incident-Ticket erstellen
                subject = f"[System-Incident 🚨] {marker} Störung bei {state.key}"
                desc = (
                    f"### 🚨 Automatische System-Störung erkannt\n\n"
                    f"**Komponente:** `{state.key}`\n"
                    f"**Status:** `{state.status.upper()}`\n"
                    f"**Meldung:** {state.value}\n"
                    f"**Zeitpunkt:** {timezone.now().strftime('%d.%m.%Y %H:%M:%S UTC')}\n\n"
                    f"#### Diagnosedaten:\n```json\n"
                    f"{state.details}\n```\n\n"
                    f"*Dieses Ticket wurde automatisch durch den Sharegy Health Watchdog generiert.*"
                )
                try:
                    ticket = create_ticket(
                        project_key="sharegy",
                        subject=subject,
                        category="infrastructure",
                        priority=Ticket.PRIORITY_URGENT,
                        initial_message=desc,
                        contact_name="Sharegy System Watchdog",
                        contact_email="system-alerts@sharegy.de",
                        context_payload={"auto_incident": True, "health_key": state.key, "details": state.details},
                    )
                    logger.warning("🚨 Automatisches Incident-Ticket #%s für %s erstellt", ticket.ticket_number, state.key)
                except Exception as e:
                    logger.exception("Fehler beim Erstellen des Incident-Tickets für %s: %s", state.key, str(e))
        elif state.status == "ok" and open_ticket:
            # ✅ Automatische Entwarnung / Resolution
            resolution_msg = (
                f"### ✅ Automatische Entwarnung\n\n"
                f"Die Komponente `{state.key}` hat sich normalisiert.\n"
                f"**Aktueller Wert:** {state.value}\n"
                f"**Zeitpunkt:** {timezone.now().strftime('%d.%m.%Y %H:%M:%S UTC')}"
            )
            TicketMessage.objects.create(
                ticket=open_ticket,
                external_sender_name="Sharegy System Watchdog",
                external_sender_email="system-alerts@sharegy.de",
                body=resolution_msg,
                is_internal_note=True,
            )
            open_ticket.status = Ticket.STATUS_RESOLVED
            open_ticket.save(update_fields=["status", "updated_at"])
            logger.info("✅ Incident-Ticket #%s für %s automatisch gelöst", open_ticket.ticket_number, state.key)



