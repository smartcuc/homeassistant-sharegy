##################
# billing/tasks.py
##################

from datetime import datetime, timedelta
from celery import shared_task
from django.utils import timezone

from billing.services_balance import compute_balance_range, recalculate_meter_slot
from billing.services_allocation import allocate_user_balance_range


@shared_task
def compute_balance_last_24h():
    now = timezone.now()
    start = now - timedelta(hours=24)
    compute_balance_range(start, now)
    return {"status": "ok", "from": str(start), "to": str(now)}


@shared_task
def allocate_user_balance_last_24h():
    now = timezone.now()
    start = now - timedelta(hours=24)
    return allocate_user_balance_range(start, now)


@shared_task
def recalculate_late_slot(meter_id: str, slot_start_iso: str):
    """
    Event-basierte Sofort-Nachberechnung:
    Wird bei eintreffenden Nachzüglern (Late Arrivals) sofort ausgeführt.
    """
    dt = datetime.fromisoformat(slot_start_iso.replace("Z", "+00:00"))
    if timezone.is_naive(dt):
        dt = timezone.make_aware(dt)
    return recalculate_meter_slot(meter_id, dt)


@shared_task
def reconcile_balance_last_30d():
    """
    Wöchentlicher / monatlicher Fiskal-Abgleich:
    Berechnet alle Slots der letzten 30 Tage neu, um selbst extreme
    Gateway-Offline-Zeiten oder manuelle Zählerkorrekturen 100% konsistent zu halten.
    """
    now = timezone.now()
    start = now - timedelta(days=30)
    compute_balance_range(start, now)
    alloc_res = allocate_user_balance_range(start, now)
    return {"status": "ok", "from": str(start), "to": str(now), "allocation_slots": len(alloc_res.get("results", []))}

