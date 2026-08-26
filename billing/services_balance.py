#############################
# billing/services_balance.py
#############################

from decimal import Decimal
from datetime import timedelta

from django.db.models import Sum, Q
from django.utils import timezone

from core.models import AggregatedReading, Meter, BalanceSlot

from core.utils.slots import floor_to_slot, slot_minutes


def _sum_kwh(qs):
    v = qs.aggregate(total=Sum("value"))["total"]
    return v if v is not None else Decimal("0")


def compute_balance_for_meter_slot(meter, slot_start):
    """
    Berechnet Balance für genau EINEN Meter und Slot.
    """

    base = AggregatedReading.objects.filter(
        meter=meter,
        period_start=slot_start,
    )
    
    # fallback
    if not base.exists():
        return None

    consumption = _sum_kwh(base.filter(obis_code__startswith="1.8"))
    generation = _sum_kwh(base.filter(obis_code__startswith="2.8"))

    self_consumption = min(consumption, generation)
    grid_import = max(consumption - generation, Decimal("0"))
    grid_export = max(generation - consumption, Decimal("0"))

    # ✅ Tenant sauber über Meter ableiten
    tenant = meter.tenant

    obj, _ = BalanceSlot.objects.update_or_create(
        meter=meter,
        tenant=tenant,
        period_start=slot_start,
        defaults={
            "consumption_kwh": consumption,
            "generation_kwh": generation,
            "self_consumption_kwh": self_consumption,
            "grid_import_kwh": grid_import,
            "grid_export_kwh": grid_export,
        },
    )

    return obj


def floor_to_billing_slot(dt):
    return floor_to_slot(dt, slot_minutes())


def compute_balance_range(start, end):
    """
    Berechnet Balance für ALLE Meter über Zeitraum in einem einzigen Datenbank-Query (Task 2.2).
    Reduziert 24.000+ Einzelschleifen-Queries auf 1 Aggregationsabfrage + 1 bulk_create.
    """

    start = floor_to_billing_slot(start)
    end = floor_to_billing_slot(end)

    rows = (
        AggregatedReading.objects.filter(period_start__gte=start, period_start__lt=end)
        .values("meter_id", "meter__tenant_id", "period_start")
        .annotate(
            consumption=Sum("value", filter=Q(obis_code__startswith="1.8")),
            generation=Sum("value", filter=Q(obis_code__startswith="2.8")),
        )
    )

    slots_to_upsert = []
    for r in rows:
        c = r["consumption"] or Decimal("0")
        g = r["generation"] or Decimal("0")
        slots_to_upsert.append(
            BalanceSlot(
                meter_id=r["meter_id"],
                tenant_id=r["meter__tenant_id"],
                period_start=r["period_start"],
                consumption_kwh=c,
                generation_kwh=g,
                self_consumption_kwh=min(c, g),
                grid_import_kwh=max(c - g, Decimal("0")),
                grid_export_kwh=max(g - c, Decimal("0")),
            )
        )

    if slots_to_upsert:
        BalanceSlot.objects.bulk_create(
            slots_to_upsert,
            update_conflicts=True,
            update_fields=[
                "consumption_kwh",
                "generation_kwh",
                "self_consumption_kwh",
                "grid_import_kwh",
                "grid_export_kwh",
                "tenant_id",
            ],
            unique_fields=["meter", "period_start"],
        )
