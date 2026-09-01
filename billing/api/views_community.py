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


@api_view(["GET", "POST"])
@permission_classes([IsAuthenticated])
def community_tariffs_view(request):
    """
    GET: Ruft alle Tarife der Community ab und kennzeichnet den aktiven Tarif.
    POST: Erstellt einen neuen Sharing-Tarif (nur für Community-Admins).
    """
    user = request.user
    tenant_id = request.headers.get("X-Tenant-ID") or request.GET.get("tenant_id") or request.data.get("tenant_id")

    if tenant_id:
        membership = TenantMembership.objects.filter(user=user, tenant_id=tenant_id, is_active=True).first()
        if not membership and not user.is_staff:
            return Response({"error": "Forbidden: No active membership in requested community."}, status=403)
        tenant = Tenant.objects.filter(id=tenant_id).first()
    else:
        membership = TenantMembership.objects.filter(user=user, is_active=True).first()
        tenant = membership.tenant if membership else None

    if not tenant:
        return Response({"error": "No active community found for user."}, status=404)

    from billing.models import CommunityTariff
    from billing.services_sharing_settlement import get_active_community_tariff

    if request.method == "POST":
        if not user.is_staff and (not membership or membership.role not in ["admin", "owner"]):
            return Response({"error": "Forbidden: Only community admins can configure tariffs."}, status=403)

        name = request.data.get("name", "Sharing Tarif")
        sharing_price = Decimal(str(request.data.get("sharing_price_ct_kwh", "12.00")))
        producer_payout = Decimal(str(request.data.get("producer_payout_ct_kwh", "10.00")))
        community_fee = Decimal(str(request.data.get("community_fee_ct_kwh", "2.00")))
        grid_fee_saved = Decimal(str(request.data.get("grid_fee_saved_ct_kwh", "0.00")))

        # Vorherige Tarife deaktivieren, falls gewünscht
        if request.data.get("set_active", True):
            CommunityTariff.objects.filter(tenant=tenant).update(is_active=False)

        new_tariff = CommunityTariff.objects.create(
            tenant=tenant,
            name=name,
            sharing_price_ct_kwh=sharing_price,
            producer_payout_ct_kwh=producer_payout,
            community_fee_ct_kwh=community_fee,
            grid_fee_saved_ct_kwh=grid_fee_saved,
            valid_from=timezone.now(),
            is_active=True,
        )

        return Response({
            "message": "Tariff created successfully",
            "tariff": {
                "id": str(new_tariff.id),
                "name": new_tariff.name,
                "sharing_price_ct_kwh": float(new_tariff.sharing_price_ct_kwh),
                "producer_payout_ct_kwh": float(new_tariff.producer_payout_ct_kwh),
                "community_fee_ct_kwh": float(new_tariff.community_fee_ct_kwh),
                "grid_fee_saved_ct_kwh": float(new_tariff.grid_fee_saved_ct_kwh),
                "valid_from": new_tariff.valid_from.isoformat(),
                "is_active": new_tariff.is_active,
            }
        }, status=201)

    active_tariff = get_active_community_tariff(tenant)
    all_tariffs = CommunityTariff.objects.filter(tenant=tenant).order_by("-valid_from")

    return Response({
        "active_tariff": {
            "id": str(active_tariff.id),
            "name": active_tariff.name,
            "sharing_price_ct_kwh": float(active_tariff.sharing_price_ct_kwh),
            "producer_payout_ct_kwh": float(active_tariff.producer_payout_ct_kwh),
            "community_fee_ct_kwh": float(active_tariff.community_fee_ct_kwh),
            "grid_fee_saved_ct_kwh": float(active_tariff.grid_fee_saved_ct_kwh),
            "valid_from": active_tariff.valid_from.isoformat(),
            "is_active": active_tariff.is_active,
        },
        "tariffs": [
            {
                "id": str(t.id),
                "name": t.name,
                "sharing_price_ct_kwh": float(t.sharing_price_ct_kwh),
                "producer_payout_ct_kwh": float(t.producer_payout_ct_kwh),
                "community_fee_ct_kwh": float(t.community_fee_ct_kwh),
                "grid_fee_saved_ct_kwh": float(t.grid_fee_saved_ct_kwh),
                "valid_from": t.valid_from.isoformat(),
                "is_active": t.is_active,
            }
            for t in all_tariffs
        ]
    })


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def community_statements_view(request):
    """
    Ruft die monatlichen Abrechnungsnachweise ab.
    Mitglieder sehen ihre eigenen Abrechnungen.
    Admins/Auditoren sehen alle Abrechnungen der Community.
    """
    user = request.user
    tenant_id = request.headers.get("X-Tenant-ID") or request.GET.get("tenant_id")

    if tenant_id:
        membership = TenantMembership.objects.filter(user=user, tenant_id=tenant_id, is_active=True).first()
        if not membership and not user.is_staff:
            return Response({"error": "Forbidden: No active membership in requested community."}, status=403)
        tenant = Tenant.objects.filter(id=tenant_id).first()
    else:
        membership = TenantMembership.objects.filter(user=user, is_active=True).first()
        tenant = membership.tenant if membership else None

    if not tenant:
        return Response({"error": "No active community found for user."}, status=404)

    from billing.models import CommunityMonthlyStatement

    is_admin_or_auditor = user.is_staff or (membership and membership.role in ["admin", "owner", "auditor"])

    qs = CommunityMonthlyStatement.objects.filter(tenant=tenant)
    if not is_admin_or_auditor:
        qs = qs.filter(user=user)

    statements = qs.select_related("user", "tariff").order_by("-period_start", "-created_at")

    results = []
    for s in statements:
        results.append({
            "id": str(s.id),
            "statement_number": s.statement_number,
            "period_start": s.period_start.isoformat(),
            "period_end": s.period_end.isoformat(),
            "user_email": s.user.email,
            "produced_total_kwh": float(s.produced_total_kwh),
            "consumed_total_kwh": float(s.consumed_total_kwh),
            "shared_imported_kwh": float(s.shared_imported_kwh),
            "shared_exported_kwh": float(s.shared_exported_kwh),
            "grid_residual_import_kwh": float(s.grid_residual_import_kwh),
            "grid_residual_export_kwh": float(s.grid_residual_export_kwh),
            "charge_shared_import_eur": float(s.charge_shared_import_eur),
            "credit_shared_export_eur": float(s.credit_shared_export_eur),
            "community_fee_eur": float(s.community_fee_eur),
            "net_balance_eur": float(s.net_balance_eur),
            "is_payout": float(s.net_balance_eur) > 0,
            "status": s.status,
            "finalized_at": s.finalized_at.isoformat() if s.finalized_at else None,
        })

    return Response({
        "statements": results,
        "is_admin": is_admin_or_auditor,
    })


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def generate_community_statements_view(request):
    """
    Generiert oder aktualisiert die Monatsabrechnungen für einen angegebenen Monat.
    Nur für Community-Admins und Staff zugelassen.
    """
    user = request.user
    tenant_id = request.headers.get("X-Tenant-ID") or request.data.get("tenant_id")

    if tenant_id:
        membership = TenantMembership.objects.filter(user=user, tenant_id=tenant_id, is_active=True).first()
        if not membership and not user.is_staff:
            return Response({"error": "Forbidden: No active membership in requested community."}, status=403)
        tenant = Tenant.objects.filter(id=tenant_id).first()
    else:
        membership = TenantMembership.objects.filter(user=user, is_active=True).first()
        tenant = membership.tenant if membership else None

    if not tenant:
        return Response({"error": "No active community found for user."}, status=404)

    if not user.is_staff and (not membership or membership.role not in ["admin", "owner"]):
        return Response({"error": "Forbidden: Only community admins can trigger monthly settlements."}, status=403)

    now = timezone.now()
    year = int(request.data.get("year", now.year))
    month = int(request.data.get("month", now.month))

    from billing.services_sharing_settlement import calculate_monthly_community_statements

    statements = calculate_monthly_community_statements(tenant, year, month)

    return Response({
        "message": f"Successfully generated {len(statements)} statements for {month:02d}/{year}",
        "count": len(statements),
    })
