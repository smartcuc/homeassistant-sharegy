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
        allocation_model = request.data.get("allocation_model", CommunityTariff.ALLOCATION_DYNAMIC)
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
            allocation_model=allocation_model,
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
                "allocation_model": new_tariff.allocation_model,
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
            "allocation_model": active_tariff.allocation_model,
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
                "allocation_model": t.allocation_model,
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


# ==============================================================================
# 🌐 ZENTRALES MULTI-COMMUNITY MANAGEMENT & PORTFOLIO HUB
# ==============================================================================

@api_view(["GET"])
@permission_classes([IsAuthenticated])
def community_portfolio_overview_view(request):
    """
    Zentrale Portfolio-Übersicht über alle Energiegemeinschaften:
    - Gesamt-KPIs (Autarkie, Gesamterzeugung, Gesamtverbrauch, Gesamt-Sharing, Ersparnis)
    - Liste aller verwalteten Energiegemeinschaften mit Performance-Indikatoren
    - Tarif- und Abrechnungs-Status pro Community
    """
    user = request.user
    now = timezone.now()
    today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
    month_start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)

    # 1. Berechtigte Tenants ermitteln
    if user.is_staff or user.is_superuser:
        tenants_qs = Tenant.objects.all().order_by("name")
    else:
        # User sieht Communities, in denen er Admin, UserAdmin, Auditor oder Mitglied ist
        tenant_ids = TenantMembership.objects.filter(
            user=user, is_active=True
        ).values_list("tenant_id", flat=True)
        tenants_qs = Tenant.objects.filter(id__in=tenant_ids).order_by("name")

    total_communities = tenants_qs.count()
    if total_communities == 0:
        return Response({
            "portfolio": {
                "total_communities": 0,
                "total_members": 0,
                "total_meters": 0,
                "total_produced_kwh": 0.0,
                "total_consumed_kwh": 0.0,
                "total_shared_kwh": 0.0,
                "portfolio_autarky_pct": 0.0,
                "total_savings_eur": 0.0,
            },
            "communities": [],
        })

    from billing.models import CommunityTariff, CommunityMonthlyStatement, CommunityAnnouncement
    from billing.services_sharing_settlement import get_active_community_tariff

    communities_list = []
    portfolio_prod = Decimal("0")
    portfolio_cons = Decimal("0")
    portfolio_shared = Decimal("0")
    portfolio_members = 0
    portfolio_meters = 0

    for t in tenants_qs:
        m_count = TenantMembership.objects.filter(tenant=t, is_active=True).count()
        meter_count = Meter.objects.filter(tenant=t, removed_at__isnull=True).count()
        portfolio_members += m_count
        portfolio_meters += meter_count

        # Monats-Performance berechnen
        month_slots = BalanceSlot.objects.filter(
            meter__tenant=t,
            period_start__gte=month_start,
            period_start__lte=now,
        )
        agg = month_slots.aggregate(
            prod=Sum("generation_kwh"),
            cons=Sum("consumption_kwh"),
        )
        prod = agg["prod"] or Decimal("0")
        cons = agg["cons"] or Decimal("0")
        shared = min(prod, cons)
        autarky = (shared / cons * 100) if cons > Decimal("0") else Decimal("0")
        savings = shared * Decimal("0.22")

        portfolio_prod += prod
        portfolio_cons += cons
        portfolio_shared += shared

        tariff = get_active_community_tariff(t, now.date())
        announcements_count = CommunityAnnouncement.objects.filter(tenant=t, is_active=True).count()
        statements_count = CommunityMonthlyStatement.objects.filter(tenant=t).count()

        communities_list.append({
            "id": str(t.id),
            "name": t.name,
            "slug": t.slug,
            "is_public": t.is_public,
            "primary_color": t.primary_color,
            "members_count": m_count,
            "meters_count": meter_count,
            "month_produced_kwh": round(float(prod), 1),
            "month_consumed_kwh": round(float(cons), 1),
            "month_shared_kwh": round(float(shared), 1),
            "autarky_pct": round(float(autarky), 1),
            "savings_eur": round(float(savings), 2),
            "tariff": {
                "name": tariff.name,
                "sharing_price_ct_kwh": float(tariff.sharing_price_ct_kwh),
                "producer_payout_ct_kwh": float(tariff.producer_payout_ct_kwh),
                "community_fee_ct_kwh": float(tariff.community_fee_ct_kwh),
            } if tariff else None,
            "announcements_count": announcements_count,
            "statements_count": statements_count,
        })

    portfolio_autarky = (portfolio_shared / portfolio_cons * 100) if portfolio_cons > Decimal("0") else Decimal("0")
    portfolio_savings = portfolio_shared * Decimal("0.22")

    return Response({
        "portfolio": {
            "total_communities": total_communities,
            "total_members": portfolio_members,
            "total_meters": portfolio_meters,
            "total_produced_kwh": round(float(portfolio_prod), 1),
            "total_consumed_kwh": round(float(portfolio_cons), 1),
            "total_shared_kwh": round(float(portfolio_shared), 1),
            "portfolio_autarky_pct": round(float(portfolio_autarky), 1),
            "total_savings_eur": round(float(portfolio_savings), 2),
        },
        "communities": communities_list,
        "is_platform_admin": bool(user.is_staff or user.is_superuser),
    })


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def community_drilldown_view(request, tenant_id):
    """
    Detaillierte Drill-Down-Ansicht für eine einzelne Community:
    - Mitglieder & Zähler-Zuordnungen mit individuellen kWh-Mengen
    - Leistungs- und Lastgangverlauf
    - Tarife, Abrechnungsnachweise & Mitteilungen
    - Community-Einstellungen
    """
    user = request.user
    tenant = Tenant.objects.filter(id=tenant_id).first()
    if not tenant:
        return Response({"error": "Community not found."}, status=404)

    # Permission Check
    membership = TenantMembership.objects.filter(user=user, tenant=tenant, is_active=True).first()
    is_admin = user.is_staff or user.is_superuser or (membership and membership.role in ["admin", "owner", "user_admin", "auditor"])
    if not is_admin:
        return Response({"error": "Forbidden: Insufficient permissions for community drilldown."}, status=403)

    from billing.models import CommunityTariff, CommunityMonthlyStatement, CommunityAnnouncement
    from billing.services_sharing_settlement import get_active_community_tariff

    now = timezone.now()
    month_start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)

    # 1. Mitglieder & Zähler
    memberships = TenantMembership.objects.filter(tenant=tenant).select_related("user").order_by("created_at")
    members_data = []
    for m in memberships:
        # Zähler des Mitglieds
        meters = Meter.objects.filter(tenant=tenant, owner_membership=m, removed_at__isnull=True)
        meter_list = [
            {
                "id": str(mtr.id),
                "serial_number": mtr.serial_number,
                "meter_type": mtr.meter_type,
                "integration_type": mtr.integration_type,
            }
            for mtr in meters
        ]

        # Individuelle Monatsmengen
        member_slots = BalanceSlot.objects.filter(
            meter__owner_membership=m,
            period_start__gte=month_start,
            period_start__lte=now,
        )
        agg = member_slots.aggregate(
            prod=Sum("generation_kwh"),
            cons=Sum("consumption_kwh"),
        )
        prod = float(agg["prod"] or 0.0)
        cons = float(agg["cons"] or 0.0)

        # Letztes Statement
        last_stmt = CommunityMonthlyStatement.objects.filter(membership=m).order_by("-period_start").first()

        members_data.append({
            "membership_id": str(m.id),
            "user_id": str(m.user.id),
            "email": m.user.email,
            "role": m.role,
            "is_active": m.is_active,
            "created_at": m.created_at.isoformat(),
            "meters": meter_list,
            "month_produced_kwh": round(prod, 1),
            "month_consumed_kwh": round(cons, 1),
            "last_statement": {
                "statement_number": last_stmt.statement_number,
                "net_balance_eur": float(last_stmt.net_balance_eur),
                "period_start": last_stmt.period_start.isoformat(),
            } if last_stmt else None,
        })

    # 2. Aktiver Tarif
    active_tariff = get_active_community_tariff(tenant, now.date())

    # 3. Ankündigungen
    announcements = CommunityAnnouncement.objects.filter(tenant=tenant).select_related("author").order_by("-created_at")[:10]
    announcements_data = [
        {
            "id": str(a.id),
            "title": a.title,
            "message": a.message,
            "category": a.category,
            "is_active": a.is_active,
            "author_email": a.author.email if a.author else "System",
            "created_at": a.created_at.isoformat(),
        }
        for a in announcements
    ]

    return Response({
        "community": {
            "id": str(tenant.id),
            "name": tenant.name,
            "slug": tenant.slug,
            "is_public": tenant.is_public,
            "primary_color": tenant.primary_color,
            "secondary_color": tenant.secondary_color,
            "button_color": tenant.button_color,
            "latitude": float(tenant.latitude) if tenant.latitude else None,
            "longitude": float(tenant.longitude) if tenant.longitude else None,
        },
        "members": members_data,
        "active_tariff": {
            "id": str(active_tariff.id),
            "name": active_tariff.name,
            "sharing_price_ct_kwh": float(active_tariff.sharing_price_ct_kwh),
            "producer_payout_ct_kwh": float(active_tariff.producer_payout_ct_kwh),
            "community_fee_ct_kwh": float(active_tariff.community_fee_ct_kwh),
            "grid_fee_saved_ct_kwh": float(active_tariff.grid_fee_saved_ct_kwh),
        } if active_tariff else None,
        "announcements": announcements_data,
        "is_admin": is_admin,
    })


@api_view(["GET", "POST"])
@permission_classes([IsAuthenticated])
def community_announcements_view(request, tenant_id):
    """
    Rundschreiben & Mitteilungen für eine Community abrufen und neu erstellen.
    """
    user = request.user
    tenant = Tenant.objects.filter(id=tenant_id).first()
    if not tenant:
        return Response({"error": "Community not found."}, status=404)

    from billing.models import CommunityAnnouncement

    if request.method == "GET":
        announcements = CommunityAnnouncement.objects.filter(tenant=tenant, is_active=True).select_related("author").order_by("-created_at")
        return Response({
            "announcements": [
                {
                    "id": str(a.id),
                    "title": a.title,
                    "message": a.message,
                    "category": a.category,
                    "author_email": a.author.email if a.author else "System",
                    "created_at": a.created_at.isoformat(),
                }
                for a in announcements
            ]
        })

    # POST: Nur Admins
    membership = TenantMembership.objects.filter(user=user, tenant=tenant, is_active=True).first()
    if not user.is_staff and (not membership or membership.role not in ["admin", "owner", "user_admin"]):
        return Response({"error": "Forbidden: Only community admins can post announcements."}, status=403)

    title = request.data.get("title")
    message = request.data.get("message")
    category = request.data.get("category", "info")

    if not title or not message:
        return Response({"error": "Title and message are required."}, status=400)

    announcement = CommunityAnnouncement.objects.create(
        tenant=tenant,
        author=user,
        title=title,
        message=message,
        category=category,
        is_active=True,
    )

    return Response({
        "message": "Announcement created successfully.",
        "id": str(announcement.id),
    }, status=201)


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def community_settings_update_view(request, tenant_id):
    """
    Einstellungen & Stammdaten einer Energiegemeinschaft aktualisieren.
    """
    user = request.user
    tenant = Tenant.objects.filter(id=tenant_id).first()
    if not tenant:
        return Response({"error": "Community not found."}, status=404)

    membership = TenantMembership.objects.filter(user=user, tenant=tenant, is_active=True).first()
    if not user.is_staff and (not membership or membership.role not in ["admin", "owner"]):
        return Response({"error": "Forbidden: Only community admins can update settings."}, status=403)

    name = request.data.get("name")
    if name:
        tenant.name = name.strip()

    if "is_public" in request.data:
        tenant.is_public = bool(request.data["is_public"])

    if "primary_color" in request.data:
        tenant.primary_color = request.data["primary_color"]

    if "latitude" in request.data:
        tenant.latitude = request.data["latitude"]

    if "longitude" in request.data:
        tenant.longitude = request.data["longitude"]

    tenant.save()

    return Response({
        "message": "Community settings updated successfully.",
        "community": {
            "id": str(tenant.id),
            "name": tenant.name,
            "slug": tenant.slug,
            "is_public": tenant.is_public,
            "primary_color": tenant.primary_color,
        }
    })


# ==============================================================================
# 📥 DOWNLOAD & EXPORTE: PDF, EXCEL, CSV, XML
# ==============================================================================

@api_view(["GET"])
@permission_classes([IsAuthenticated])
def statement_pdf_download_view(request, statement_id):
    """
    Generiert das druckfähige PDF für einen Monatsabrechnungsnachweis.
    """
    user = request.user
    from billing.models import CommunityMonthlyStatement
    from billing.services_sharing_exports import generate_statement_pdf

    statement = CommunityMonthlyStatement.objects.filter(id=statement_id).select_related("tenant", "user", "tariff").first()
    if not statement:
        return Response({"error": "Statement not found."}, status=404)

    # Permission Check
    membership = TenantMembership.objects.filter(user=user, tenant=statement.tenant, is_active=True).first()
    is_admin = user.is_staff or user.is_superuser or (membership and membership.role in ["admin", "owner", "auditor"])
    if statement.user != user and not is_admin:
        return Response({"error": "Forbidden: You cannot access this statement."}, status=403)

    return generate_statement_pdf(statement)


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def statements_export_view(request):
    """
    Exportiert Abrechnungsdaten als CSV, XLSX oder XML für ERP- und Buchhaltungszwecke.
    Query-Parameter:
    - format: 'csv' | 'xlsx' | 'xml' (Default: 'xlsx')
    - tenant_id: UUID der Energiegemeinschaft (Optional für Superadmin)
    - year: int (Optional)
    - month: int (Optional)
    """
    user = request.user
    tenant_id = (
        request.headers.get("X-Tenant-ID")
        or request.query_params.get("tenant_id")
        or request.GET.get("tenant_id")
    )
    export_format = (
        request.query_params.get("export_format")
        or request.query_params.get("format_type")
        or request.query_params.get("type")
        or request.query_params.get("format")
        or "xlsx"
    ).lower()
    year = request.query_params.get("year") or request.GET.get("year")
    month = request.query_params.get("month") or request.GET.get("month")


    tenant = None
    if tenant_id:
        membership = TenantMembership.objects.filter(user=user, tenant_id=tenant_id, is_active=True).first()
        if not membership and not user.is_staff and not user.is_superuser:
            return Response({"error": "Forbidden: No active membership in requested community."}, status=403)
        tenant = Tenant.objects.filter(id=tenant_id).first()
    else:
        membership = TenantMembership.objects.filter(user=user, is_active=True).first()
        tenant = membership.tenant if membership else None


    if not tenant and not (user.is_staff or user.is_superuser):
        return Response({"error": "No community specified."}, status=400)

    from billing.models import CommunityMonthlyStatement
    from billing.services_sharing_exports import (
        export_statements_csv,
        export_statements_xlsx,
        export_statements_xml,
    )

    qs = CommunityMonthlyStatement.objects.all().select_related("user", "tenant", "tariff")
    if tenant:
        qs = qs.filter(tenant=tenant)
    
    is_admin = user.is_staff or user.is_superuser or (membership and membership.role in ["admin", "owner", "auditor"])
    if not is_admin:
        qs = qs.filter(user=user)

    if year:
        qs = qs.filter(period_start__year=int(year))
    if month:
        qs = qs.filter(period_start__month=int(month))

    tenant_name = tenant.name if tenant else "Alle_Gemeinschaften"

    if export_format == "csv":
        return export_statements_csv(qs, tenant_name=tenant_name)
    elif export_format == "xml":
        return export_statements_xml(qs, tenant_name=tenant_name)
    else:
        return export_statements_xlsx(qs, tenant_name=tenant_name)


# ==============================================================================
# ⚖️ BETEILIGUNGSQUOTEN & ALLOKATIONS-VORSCHAU / SIMULATION
# ==============================================================================

@api_view(["GET", "POST"])
@permission_classes([IsAuthenticated])
def community_member_shares_view(request):
    """
    GET: Ruft alle Beteiligungsquoten der Mitglieder einer Community ab.
    POST: Erstellt oder aktualisiert eine Beteiligungsquote für ein Mitglied (Admin).
    """
    user = request.user
    tenant_id = request.headers.get("X-Tenant-ID") or request.GET.get("tenant_id") or request.data.get("tenant_id")

    if tenant_id:
        membership = TenantMembership.objects.filter(user=user, tenant_id=tenant_id, is_active=True).first()
        if not membership and not user.is_staff and not user.is_superuser:
            return Response({"error": "Forbidden: No active membership in requested community."}, status=403)
        tenant = Tenant.objects.filter(id=tenant_id).first()
    else:
        membership = TenantMembership.objects.filter(user=user, is_active=True).first()
        tenant = membership.tenant if membership else None

    if not tenant:
        return Response({"error": "No active community found for user."}, status=404)

    from billing.models import CommunityMemberShare

    if request.method == "POST":
        is_admin = user.is_staff or user.is_superuser or (membership and membership.role in ["admin", "owner"])
        if not is_admin:
            return Response({"error": "Forbidden: Only community admins can configure member shares."}, status=403)

        target_membership_id = request.data.get("membership_id")
        target_membership = TenantMembership.objects.filter(id=target_membership_id, tenant=tenant).first()
        if not target_membership:
            return Response({"error": "Target membership not found in this community."}, status=404)

        share_percent = Decimal(str(request.data.get("share_percent", "0.0000")))
        mea_numerator = request.data.get("mea_numerator")
        mea_denominator = int(request.data.get("mea_denominator", 1000))
        assigned_kwp = request.data.get("assigned_kwp")

        if mea_numerator is not None and int(mea_numerator) > 0 and (not share_percent or share_percent == Decimal("0.0")):
            share_percent = (Decimal(int(mea_numerator)) / Decimal(mea_denominator)) * Decimal("100.0")

        share, _ = CommunityMemberShare.objects.update_or_create(
            tenant=tenant,
            membership=target_membership,
            user=target_membership.user,
            defaults={
                "share_percent": share_percent,
                "mea_numerator": int(mea_numerator) if mea_numerator is not None else None,
                "mea_denominator": mea_denominator,
                "assigned_kwp": Decimal(str(assigned_kwp)) if assigned_kwp is not None else None,
                "is_active": request.data.get("is_active", True),
            },
        )

        return Response({
            "message": "Member share updated successfully.",
            "share": {
                "id": str(share.id),
                "membership_id": str(share.membership_id),
                "user_email": share.user.email,
                "share_percent": float(share.share_percent),
                "mea_numerator": share.mea_numerator,
                "mea_denominator": share.mea_denominator,
                "assigned_kwp": float(share.assigned_kwp) if share.assigned_kwp else None,
                "is_active": share.is_active,
            }
        }, status=201)

    # GET
    all_memberships = TenantMembership.objects.filter(tenant=tenant, is_active=True).select_related("user")
    active_shares = {
        str(s.membership_id): s for s in CommunityMemberShare.objects.filter(tenant=tenant, is_active=True)
    }

    shares_list = []
    total_percent = Decimal("0.0")

    for m in all_memberships:
        if not m.user:
            continue
        m_id = str(m.id)
        share_obj = active_shares.get(m_id)
        if share_obj:
            pct = share_obj.share_percent
            total_percent += pct
            shares_list.append({
                "membership_id": m_id,
                "user_id": str(m.user.id),
                "user_email": m.user.email,
                "role": m.role,
                "has_custom_share": True,
                "share_percent": float(pct),
                "mea_numerator": share_obj.mea_numerator,
                "mea_denominator": share_obj.mea_denominator,
                "assigned_kwp": float(share_obj.assigned_kwp) if share_obj.assigned_kwp else None,
                "is_active": share_obj.is_active,
            })
        else:
            shares_list.append({
                "membership_id": m_id,
                "user_id": str(m.user.id),
                "user_email": m.user.email,
                "role": m.role,
                "has_custom_share": False,
                "share_percent": 0.0,
                "mea_numerator": None,
                "mea_denominator": 1000,
                "assigned_kwp": None,
                "is_active": True,
            })

    is_balanced_100 = Decimal("99.9") <= total_percent <= Decimal("100.1")

    return Response({
        "community_id": str(tenant.id),
        "community_name": tenant.name,
        "total_allocated_percent": round(float(total_percent), 4),
        "total_configured_share_percent": round(float(total_percent), 4),
        "is_balanced_100": is_balanced_100,
        "shares": shares_list,
    })


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def community_member_shares_bulk_view(request):
    """
    Speichert Beteiligungsquoten im Bulk (z. B. für alle WEG-Mitglieder auf einmal)
    und unterstützt optionale Normierung auf 100,00%.
    """
    user = request.user
    tenant_id = request.headers.get("X-Tenant-ID") or request.data.get("tenant_id")

    if tenant_id:
        membership = TenantMembership.objects.filter(user=user, tenant_id=tenant_id, is_active=True).first()
        if not membership and not user.is_staff and not user.is_superuser:
            return Response({"error": "Forbidden: No active membership in requested community."}, status=403)
        tenant = Tenant.objects.filter(id=tenant_id).first()
    else:
        membership = TenantMembership.objects.filter(user=user, is_active=True).first()
        tenant = membership.tenant if membership else None

    if not tenant:
        return Response({"error": "No active community found for user."}, status=404)

    is_admin = user.is_staff or user.is_superuser or (membership and membership.role in ["admin", "owner"])
    if not is_admin:
        return Response({"error": "Forbidden: Only community admins can configure member shares."}, status=403)

    shares_data = request.data.get("shares", [])
    if not isinstance(shares_data, list):
        return Response({"error": "Payload 'shares' must be a list."}, status=400)

    normalize_to_100 = bool(request.data.get("normalize_to_100", False))
    from billing.models import CommunityMemberShare

    # Falls Normierung gewünscht: Gesamtsumme ermitteln
    raw_sum = Decimal("0.0")
    for item in shares_data:
        raw_sum += Decimal(str(item.get("share_percent", 0)))

    saved_count = 0
    for item in shares_data:
        m_id = item.get("membership_id")
        target_membership = TenantMembership.objects.filter(id=m_id, tenant=tenant).first()
        if not target_membership:
            continue

        raw_pct = Decimal(str(item.get("share_percent", 0)))
        if normalize_to_100 and raw_sum > Decimal("0.0"):
            pct = (raw_pct / raw_sum) * Decimal("100.0")
        else:
            pct = raw_pct

        mea_num = item.get("mea_numerator")
        mea_den = int(item.get("mea_denominator", 1000))
        kwp = item.get("assigned_kwp")

        CommunityMemberShare.objects.update_or_create(
            tenant=tenant,
            membership=target_membership,
            user=target_membership.user,
            defaults={
                "share_percent": round(pct, 4),
                "mea_numerator": int(mea_num) if mea_num is not None else None,
                "mea_denominator": mea_den,
                "assigned_kwp": Decimal(str(kwp)) if kwp is not None else None,
                "is_active": bool(item.get("is_active", True)),
            },
        )
        saved_count += 1

    return Response({
        "message": f"Successfully updated {saved_count} member shares.",
        "normalized": normalize_to_100,
    })


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def community_allocation_preview_view(request):
    """
    Simuliert und vergleicht für einen Abrechnungsmonat die 3 Allokationsmodelle:
    1. Dynamisch nach Lastgang
    2. Statische Beteiligungsquoten (MEA)
    3. Hybride Vorrangquote mit Überlauf
    """
    user = request.user
    tenant_id = request.headers.get("X-Tenant-ID") or request.GET.get("tenant_id")

    if tenant_id:
        membership = TenantMembership.objects.filter(user=user, tenant_id=tenant_id, is_active=True).first()
        if not membership and not user.is_staff and not user.is_superuser:
            return Response({"error": "Forbidden: No active membership in requested community."}, status=403)
        tenant = Tenant.objects.filter(id=tenant_id).first()
    else:
        membership = TenantMembership.objects.filter(user=user, is_active=True).first()
        tenant = membership.tenant if membership else None

    if not tenant:
        return Response({"error": "No active community found for user."}, status=404)

    now = timezone.now()
    year = int(request.GET.get("year", now.year))
    month = int(request.GET.get("month", now.month))

    from billing.services_sharing_settlement import get_allocation_comparison_preview

    preview_data = get_allocation_comparison_preview(tenant, year, month)
    return Response(preview_data)


# =========================================================================
# 5. MSCONS / EDIFACT EXPORT & IMPORT (MARKTKOMMUNIKATION)
# =========================================================================

@api_view(["GET"])
@permission_classes([IsAuthenticated])
def community_mscons_export_view(request):
    """
    Exportiert 15-Minuten Lastgänge der Community im BNetzA-konformen EDIFACT MSCONS Format.
    """
    from django.http import HttpResponse
    from datetime import date
    import calendar
    from billing.services_mscons import generate_community_mscons_export

    user = request.user
    tenant_id = request.headers.get("X-Tenant-ID") or request.GET.get("tenant_id")

    if tenant_id:
        membership = TenantMembership.objects.filter(user=user, tenant_id=tenant_id, is_active=True).first()
        if not membership and not user.is_staff and not user.is_superuser:
            return Response({"error": "Forbidden"}, status=403)
        tenant = Tenant.objects.filter(id=tenant_id).first()
    else:
        membership = TenantMembership.objects.filter(user=user, is_active=True).first()
        tenant = membership.tenant if membership else None

    if not tenant:
        return Response({"error": "No community found"}, status=404)

    now = timezone.now()
    year = int(request.GET.get("year", now.year))
    month = int(request.GET.get("month", now.month))
    _, last_day = calendar.monthrange(year, month)

    period_start = date(year, month, 1)
    period_end = date(year, month, last_day)

    obis_param = request.GET.get("obis", "1.8.0,2.8.0")
    obis_codes = [c.strip() for c in obis_param.split(",") if c.strip()]

    sender_id = request.GET.get("sender_id", "9901234567890")
    receiver_id = request.GET.get("receiver_id", "9909876543210")

    mscons_text = generate_community_mscons_export(
        tenant=tenant,
        period_start=period_start,
        period_end=period_end,
        obis_codes=obis_codes,
        sender_mp_id=sender_id,
        receiver_mp_id=receiver_id,
    )

    t_slug = tenant.name.lower().replace(" ", "_")[:12]
    filename = f"mscons_{t_slug}_{year}_{month:02d}.edi"

    response = HttpResponse(mscons_text, content_type="text/plain; charset=iso-8859-1")
    response["Content-Disposition"] = f'attachment; filename="{filename}"'
    return response


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def community_mscons_import_view(request):
    """
    Importiert eine empfangene MSCONS-Datei (EDIFACT) von VNB oder wMSB und schreibt Messwerte in die Datenbank.
    """
    from billing.services_mscons import import_mscons_to_database

    user = request.user
    tenant_id = request.headers.get("X-Tenant-ID") or request.data.get("tenant_id") or request.GET.get("tenant_id")

    if tenant_id:
        membership = TenantMembership.objects.filter(user=user, tenant_id=tenant_id, is_active=True).first()
        if not membership and not user.is_staff and not user.is_superuser:
            return Response({"error": "Forbidden"}, status=403)
        tenant = Tenant.objects.filter(id=tenant_id).first()
    else:
        membership = TenantMembership.objects.filter(user=user, is_active=True).first()
        tenant = membership.tenant if membership else None

    if not tenant:
        return Response({"error": "No community found"}, status=404)

    edi_content = None
    if "file" in request.FILES:
        uploaded = request.FILES["file"]
        edi_content = uploaded.read().decode("iso-8859-1", errors="replace")
    elif "edi_content" in request.data:
        edi_content = request.data["edi_content"]

    if not edi_content:
        return Response({"error": "No file or edi_content provided"}, status=400)

    result = import_mscons_to_database(tenant, edi_content)
    return Response(result)


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def community_obis_ingest_view(request):
    """
    Importiert 15-Minuten-OBIS-Readings im JSON-Format (z. B. von wMSB Webhooks oder Smart Meter Gateways).
    """
    from billing.services_mscons import import_obis_json_readings

    user = request.user
    tenant_id = request.headers.get("X-Tenant-ID") or request.data.get("tenant_id") or request.GET.get("tenant_id")

    if tenant_id:
        membership = TenantMembership.objects.filter(user=user, tenant_id=tenant_id, is_active=True).first()
        if not membership and not user.is_staff and not user.is_superuser:
            return Response({"error": "Forbidden"}, status=403)
        tenant = Tenant.objects.filter(id=tenant_id).first()
    else:
        membership = TenantMembership.objects.filter(user=user, is_active=True).first()
        tenant = membership.tenant if membership else None

    if not tenant:
        return Response({"error": "No community found"}, status=404)

    readings = request.data.get("readings")
    if readings is None and isinstance(request.data, list):
        readings = request.data

    if not readings:
        return Response({"error": "No readings array provided"}, status=400)

    result = import_obis_json_readings(tenant, readings)
    return Response(result)


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def community_msb_meters_view(request):
    """
    Liefert alle Zähler und Smart Meter der Community inklusive Zählpunkt (MaLo-ID),
    zugeordnetem Mitglied, Rolle und letztem Ingestion-Zeitstempel.
    """
    user = request.user
    tenant_id = request.headers.get("X-Tenant-ID") or request.GET.get("tenant_id")

    if tenant_id:
        membership = TenantMembership.objects.filter(user=user, tenant_id=tenant_id, is_active=True).first()
        if not membership and not user.is_staff and not user.is_superuser:
            return Response({"error": "Forbidden"}, status=403)
        tenant = Tenant.objects.filter(id=tenant_id).first()
    else:
        membership = TenantMembership.objects.filter(user=user, is_active=True).first()
        tenant = membership.tenant if membership else None

    if not tenant:
        return Response({"error": "No community found"}, status=404)

    meters = Meter.objects.filter(tenant=tenant, removed_at__isnull=True).select_related("owner_membership__user").order_by("serial_number")
    
    meter_list = []
    for m in meters:
        latest_reading = AggregatedReading.objects.filter(meter=m).order_by("-period_start").first()
        total_readings = AggregatedReading.objects.filter(meter=m).count()

        member_name = (
            f"{m.owner_membership.user.first_name} {m.owner_membership.user.last_name}".strip()
            or m.owner_membership.user.email
            if m.owner_membership and m.owner_membership.user
            else "Community Allgemein"
        )
        role = m.owner_membership.role if m.owner_membership else "member"

        meter_list.append({
            "id": str(m.id),
            "serial_number": m.serial_number,
            "meter_type": m.meter_type,
            "member_name": member_name,
            "member_role": role,
            "total_15m_readings": total_readings,
            "last_reading_time": latest_reading.period_start.isoformat() if latest_reading else None,
            "last_reading_val": float(latest_reading.value) if latest_reading else None,
            "last_reading_obis": latest_reading.obis_code if latest_reading else None,
            "status": "active" if total_readings > 0 else "waiting_data",
        })

    return Response({
        "tenant_id": str(tenant.id),
        "tenant_name": tenant.name,
        "meters_count": len(meter_list),
        "meters": meter_list,
    })





