###################################
# billing/api/views_community.py
###################################

from decimal import Decimal
from datetime import timedelta
from django.utils import timezone
from django.db.models import Sum, Q, Count
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from accounts.models import TenantMembership
from core.models import Tenant, Meter, BalanceSlot
from forecast.models import SolarForecast


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def community_cockpit_view(request):
    """
    Liefert die aggregierten Energy-Sharing-Kennzahlen für eine Community (Tenant):
    - Produziert (OBIS 2.8.0)
    - Verbraucht (OBIS 1.8.0)
    - Geteilt / Sharing-Deckung (kWh & Autarkie %)
    - Zugekaufter Reststrom (Netzbezug)
    - Überschuss-Einspeisung ins Netz
    - Finanzieller Mehrwert / Ersparnis (€)
    - 15-Minuten-Zeitreihe für Diagramme (Heute / 7 Tage)
    - 48h-KI-Prognose für Solarertrag & Ladefenster
    - Zähler- & Teilnehmer-Statistiken
    """
    user = request.user
    tenant_id = request.headers.get("X-Tenant-ID") or request.GET.get("tenant_id")

    # 1. Tenant ermitteln & Mitgliedschaft prüfen
    if tenant_id:
        membership = TenantMembership.objects.filter(
            user=user, tenant_id=tenant_id, is_active=True
        ).first()
        if not membership and not user.is_staff:
            return Response({"error": "Forbidden: No active membership in requested community."}, status=403)
        tenant = Tenant.objects.filter(id=tenant_id).first()
    else:
        membership = TenantMembership.objects.filter(user=user, is_active=True).first()
        tenant = membership.tenant if membership else None

    if not tenant:
        return Response({"error": "No active community found for user."}, status=404)

    now = timezone.now()
    today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
    month_start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    seven_days_ago = now - timedelta(days=7)

    # 2. Zähler der Community ermitteln
    meters = Meter.objects.filter(tenant=tenant, removed_at__isnull=True)
    total_meters = meters.count()

    # 3. Aggregationen für Heute & Monat aus BalanceSlot
    today_slots = BalanceSlot.objects.filter(
        meter__tenant=tenant,
        period_start__gte=today_start,
        period_start__lte=now,
    )
    month_slots = BalanceSlot.objects.filter(
        meter__tenant=tenant,
        period_start__gte=month_start,
        period_start__lte=now,
    )

    def _calc_totals(qs):
        agg = qs.aggregate(
            prod=Sum("generation_kwh"),
            cons=Sum("consumption_kwh"),
            self_cons=Sum("self_consumption_kwh"),
            grid_in=Sum("grid_import_kwh"),
            grid_out=Sum("grid_export_kwh"),
        )
        prod = agg["prod"] or Decimal("0")
        cons = agg["cons"] or Decimal("0")
        # Bei Community-Ebene: Geteilter Strom ist das Minimum aus gesamter Erzeugung und gesamtem Verbrauch
        shared = min(prod, cons)
        grid_in = max(cons - prod, Decimal("0"))
        grid_out = max(prod - cons, Decimal("0"))
        autarky = (shared / cons * 100) if cons > Decimal("0") else Decimal("0")
        
        # Standard-Preisdelta: Netzstrom ca. 34 Ct - Sharingstrom ca. 12 Ct = 22 Ct Ersparnis / kWh
        savings_eur = shared * Decimal("0.22")

        return {
            "produced_kwh": round(float(prod), 2),
            "consumed_kwh": round(float(cons), 2),
            "shared_kwh": round(float(shared), 2),
            "grid_import_kwh": round(float(grid_in), 2),
            "grid_export_kwh": round(float(grid_out), 2),
            "autarky_pct": round(float(autarky), 1),
            "savings_eur": round(float(savings_eur), 2),
        }

    today_stats = _calc_totals(today_slots)
    month_stats = _calc_totals(month_slots)

    # 4. 15-Minuten-Zeitreihe der letzten 24 Stunden (für Diagramme)
    last_24h_start = now - timedelta(hours=24)
    time_series_slots = (
        BalanceSlot.objects.filter(
            meter__tenant=tenant,
            period_start__gte=last_24h_start,
            period_start__lte=now,
        )
        .values("period_start")
        .annotate(
            produced=Sum("generation_kwh"),
            consumed=Sum("consumption_kwh"),
        )
        .order_by("period_start")
    )

    timeseries = []
    for s in time_series_slots:
        p = float(s["produced"] or 0)
        c = float(s["consumed"] or 0)
        sh = min(p, c)
        timeseries.append({
            "timestamp": s["period_start"].isoformat(),
            "produced_kwh": round(p, 3),
            "consumed_kwh": round(c, 3),
            "shared_kwh": round(sh, 3),
            "grid_import_kwh": round(max(c - p, 0), 3),
            "grid_export_kwh": round(max(p - c, 0), 3),
        })

    # 5. 48-Stunden KI-Prognose (SolarForecast)
    forecast_48h = (
        SolarForecast.objects.filter(
            generator_string__generator__home__user__memberships__tenant=tenant,
            timestamp__gte=now,
            timestamp__lte=now + timedelta(hours=48),
        )
        .values("timestamp")
        .annotate(total_kwh=Sum("forecast_kwh"))
        .order_by("timestamp")[:48]
    )

    forecast_items = []
    total_forecast_kwh = Decimal("0")
    for f in forecast_48h:
        kwh = Decimal(str(f.get("total_kwh") or 0))
        # Da 1 Stunde: Leistung kW entspricht grob kWh/h
        kw = kwh
        total_forecast_kwh += kwh
        forecast_items.append({
            "timestamp": f["timestamp"].isoformat(),
            "power_kw": round(float(kw), 2),
            "energy_kwh": round(float(kwh), 2),
            "is_peak_window": float(kw) > 1.5,
        })

    # 6. Teilnehmer & Zähler-Übersicht
    members_count = TenantMembership.objects.filter(tenant=tenant, is_active=True).count()

    return Response({
        "community": {
            "id": str(tenant.id),
            "name": tenant.name,
            "slug": tenant.slug,
            "members_count": members_count,
            "meters_count": total_meters,
        },
        "today": today_stats,
        "month": month_stats,
        "timeseries_24h": timeseries,
        "forecast_48h": {
            "total_predicted_kwh": round(float(total_forecast_kwh), 2),
            "hours": forecast_items,
        },
    })
