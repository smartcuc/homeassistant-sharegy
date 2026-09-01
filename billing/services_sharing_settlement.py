"""
billing/services_sharing_settlement.py

Berechnungs-, Allokations- und Clearing-Engine für Energy Sharing Communities (Säule 2).
Unterstützt flexible Allokationsmodelle:
1. DYNAMIC: Verbrauchsproportionale 15-Minuten-Echtzeit-Verteilung
2. STATIC: Feste Beteiligungsquoten & Miteigentumsanteile (MEA)
3. HYBRID: Vorrangige Quoten-Zuteilung + dynamischer Überlauf auf Restverbrauch

Erstellt rechtssichere Monatsabrechnungsnachweise gem. § 42b EnWG & § 42a EnWG.
"""

import calendar
from collections import defaultdict
from datetime import date, datetime, time
from decimal import Decimal
from django.utils import timezone
from django.db.models import Sum, Q, Avg

from core.models import Tenant, Meter, BalanceSlot
from accounts.models import TenantMembership
from billing.models import CommunityTariff, CommunityMemberShare, CommunityMonthlyStatement


def get_active_community_tariff(tenant: Tenant, at_date: date = None) -> CommunityTariff:
    """
    Ermittelt den aktuell gültigen Community-Tarif.
    Falls noch keiner existiert, wird ein Standardtarif (12 Ct Bezug, 10 Ct Vergütung, 2 Ct Umlage) angelegt.
    """
    if at_date is None:
        at_date = timezone.now().date()

    target_dt = timezone.make_aware(datetime.combine(at_date, time.min))

    tariff = (
        CommunityTariff.objects.filter(
            tenant=tenant,
            is_active=True,
            valid_from__lte=target_dt,
        )
        .filter(Q(valid_to__isnull=True) | Q(valid_to__gte=target_dt))
        .order_by("-valid_from")
        .first()
    )

    if not tariff:
        tariff = CommunityTariff.objects.create(
            tenant=tenant,
            name=f"Standard Sharing Tarif ({tenant.name})",
            allocation_model=CommunityTariff.ALLOCATION_DYNAMIC,
            sharing_price_ct_kwh=Decimal("12.00"),
            producer_payout_ct_kwh=Decimal("10.00"),
            community_fee_ct_kwh=Decimal("2.00"),
            grid_fee_saved_ct_kwh=Decimal("0.00"),
            valid_from=timezone.make_aware(datetime(2026, 1, 1, 0, 0)),
            is_active=True,
        )

    return tariff


def get_active_member_shares(tenant: Tenant, at_date: date = None) -> dict[str, Decimal]:
    """
    Liefert ein Dictionary {membership_id_str: share_ratio (0.0 bis 1.0)} für alle aktiven Quoten.
    """
    if at_date is None:
        at_date = timezone.now().date()
    target_dt = timezone.make_aware(datetime.combine(at_date, time.min))

    shares = CommunityMemberShare.objects.filter(
        tenant=tenant,
        is_active=True,
        valid_from__lte=target_dt,
    ).filter(Q(valid_to__isnull=True) | Q(valid_to__gte=target_dt))

    shares_map = {}
    for s in shares:
        m_id = str(s.membership_id)
        ratio = (s.share_percent / Decimal("100.0")).quantize(Decimal("0.000001"))
        shares_map[m_id] = ratio

    return shares_map


def calculate_sharing_allocation_for_slot(
    consumption_by_member: dict[str, Decimal],
    total_generation: Decimal,
    allocation_model: str,
    member_shares_map: dict[str, Decimal] = None,
) -> dict:
    """
    Berechnet die Energieverteilung (Allokation) für genau einen 15-Minuten-Slot.
    """
    member_ids = list(consumption_by_member.keys())
    if not member_ids:
        return {
            "shared_by_member": {},
            "grid_import_by_member": {},
            "grid_export_total": total_generation,
            "total_shared": Decimal("0.0"),
        }

    total_consumption = sum(consumption_by_member.values())
    if member_shares_map is None:
        member_shares_map = {}

    active_shares = {}
    configured_sum = sum(member_shares_map.get(m_id, Decimal("0.0")) for m_id in member_ids)
    
    for m_id in member_ids:
        if configured_sum > Decimal("0.0"):
            active_shares[m_id] = member_shares_map.get(m_id, Decimal("0.0"))
        else:
            active_shares[m_id] = Decimal("1.0") / Decimal(len(member_ids))

    shared_by_member = {m_id: Decimal("0.0") for m_id in member_ids}
    grid_import_by_member = {m_id: Decimal("0.0") for m_id in member_ids}

    # =========================================================================
    # MODELL 1: DYNAMISCH (Verbrauchsproportional nach Lastgang)
    # =========================================================================
    if allocation_model == CommunityTariff.ALLOCATION_DYNAMIC:
        if total_generation <= Decimal("0.0") or total_consumption <= Decimal("0.0"):
            grid_export = total_generation
            for m_id in member_ids:
                grid_import_by_member[m_id] = consumption_by_member[m_id]
            total_shared = Decimal("0.0")
        elif total_generation >= total_consumption:
            for m_id in member_ids:
                shared_by_member[m_id] = consumption_by_member[m_id]
                grid_import_by_member[m_id] = Decimal("0.0")
            grid_export = total_generation - total_consumption
            total_shared = total_consumption
        else:
            for m_id in member_ids:
                c_i = consumption_by_member[m_id]
                s_i = (total_generation * (c_i / total_consumption)).quantize(Decimal("0.000001"))
                shared_by_member[m_id] = s_i
                grid_import_by_member[m_id] = max(c_i - s_i, Decimal("0.0"))
            grid_export = Decimal("0.0")
            total_shared = total_generation

    # =========================================================================
    # MODELL 2: STATISCH (Feste Beteiligungsquote / MEA)
    # =========================================================================
    elif allocation_model == CommunityTariff.ALLOCATION_STATIC:
        total_shared = Decimal("0.0")
        unused_generation = Decimal("0.0")

        for m_id in member_ids:
            c_i = consumption_by_member[m_id]
            q_i = active_shares.get(m_id, Decimal("0.0"))
            allocated_gen = total_generation * q_i
            s_i = min(c_i, allocated_gen)
            shared_by_member[m_id] = s_i
            grid_import_by_member[m_id] = max(c_i - s_i, Decimal("0.0"))
            unused_generation += max(allocated_gen - s_i, Decimal("0.0"))
            total_shared += s_i

        unassigned_ratio = max(Decimal("1.0") - sum(active_shares.values()), Decimal("0.0"))
        grid_export = unused_generation + (total_generation * unassigned_ratio)

    # =========================================================================
    # MODELL 3: HYBRID (Stufe 1: Feste Quote, Stufe 2: Überlauf auf Restbedarf)
    # =========================================================================
    elif allocation_model == CommunityTariff.ALLOCATION_HYBRID:
        tier1_shared = {}
        tier1_surplus = Decimal("0.0")
        residual_demand = {}

        for m_id in member_ids:
            c_i = consumption_by_member[m_id]
            q_i = active_shares.get(m_id, Decimal("0.0"))
            allocated_gen = total_generation * q_i
            s1_i = min(c_i, allocated_gen)
            tier1_shared[m_id] = s1_i
            tier1_surplus += max(allocated_gen - s1_i, Decimal("0.0"))
            residual_demand[m_id] = max(c_i - s1_i, Decimal("0.0"))

        unassigned_ratio = max(Decimal("1.0") - sum(active_shares.values()), Decimal("0.0"))
        tier1_surplus += (total_generation * unassigned_ratio)
        total_res_demand = sum(residual_demand.values())

        tier2_shared = {}
        if tier1_surplus > Decimal("0.0") and total_res_demand > Decimal("0.0"):
            if tier1_surplus >= total_res_demand:
                for m_id in member_ids:
                    tier2_shared[m_id] = residual_demand[m_id]
                grid_export = tier1_surplus - total_res_demand
            else:
                for m_id in member_ids:
                    r_i = residual_demand[m_id]
                    s2_i = (tier1_surplus * (r_i / total_res_demand)).quantize(Decimal("0.000001"))
                    tier2_shared[m_id] = s2_i
                grid_export = Decimal("0.0")
        else:
            for m_id in member_ids:
                tier2_shared[m_id] = Decimal("0.0")
            grid_export = tier1_surplus

        total_shared = Decimal("0.0")
        for m_id in member_ids:
            s_i = tier1_shared[m_id] + tier2_shared[m_id]
            shared_by_member[m_id] = s_i
            grid_import_by_member[m_id] = max(consumption_by_member[m_id] - s_i, Decimal("0.0"))
            total_shared += s_i

    else:
        raise ValueError(f"Unknown allocation model: {allocation_model}")

    return {
        "shared_by_member": shared_by_member,
        "grid_import_by_member": grid_import_by_member,
        "grid_export_total": grid_export,
        "total_shared": total_shared,
    }


def get_effective_tariff_prices_for_slot(
    tariff: CommunityTariff,
    slot_dt: datetime,
    spot_price_ct_kwh: Decimal = None,
) -> tuple[Decimal, Decimal, Decimal]:
    """
    Ermittelt die effektiven Arbeitspreise (Ct/kWh) für genau einen Zeitschlitz:
    Rückgabe: (effective_sharing_price_ct, effective_producer_payout_ct, community_fee_ct)
    """
    community_fee_ct = tariff.community_fee_ct_kwh or Decimal("0.00")

    # 1. Statischer Festpreis
    if tariff.pricing_model == CommunityTariff.PRICING_MODEL_STATIC:
        sharing_price = tariff.sharing_price_ct_kwh
        producer_payout = tariff.producer_payout_ct_kwh

    # 2. Börsenpreis-indexierter dynamischer Tarif (EPEX Spot)
    elif tariff.pricing_model == CommunityTariff.PRICING_MODEL_SPOT_INDEXED:
        spot_ct = spot_price_ct_kwh if spot_price_ct_kwh is not None else Decimal("10.00")
        
        # Basis = Spotpreis + Aufschlag - Netzentgelt-Rabatt
        sharing_price = spot_ct + (tariff.spot_markup_ct_kwh or Decimal("3.50")) - (tariff.grid_fee_saved_ct_kwh or Decimal("0.00"))
        
        # Floor (Mindestpreis) anwenden
        if tariff.spot_floor_price_ct_kwh is not None:
            sharing_price = max(sharing_price, tariff.spot_floor_price_ct_kwh)
            
        # Cap (Preisbremse / Obergrenze) anwenden
        if tariff.spot_cap_price_ct_kwh is not None:
            sharing_price = min(sharing_price, tariff.spot_cap_price_ct_kwh)

        # Einspeisevergütung: prozentualer Anteil des Börsenpreises
        share_factor = (tariff.feed_in_spot_share_pct or Decimal("80.00")) / Decimal("100.0")
        producer_payout = max(Decimal("0.00"), spot_ct * share_factor)

    # 3. Zeittarif (HT / NT)
    elif tariff.pricing_model == CommunityTariff.PRICING_MODEL_TIME_OF_USE:
        # HT = 06:00 bis 22:00 Uhr, NT = 22:00 bis 06:00 Uhr
        hour = slot_dt.hour
        is_ht = 6 <= hour < 22
        if is_ht:
            sharing_price = tariff.sharing_price_ct_kwh
            producer_payout = tariff.producer_payout_ct_kwh
        else:
            # NT: 20% Rabatt auf Bezug, 10% Abschlag auf Einspeisung
            sharing_price = (tariff.sharing_price_ct_kwh * Decimal("0.80")).quantize(Decimal("0.01"))
            producer_payout = (tariff.producer_payout_ct_kwh * Decimal("0.90")).quantize(Decimal("0.01"))
    else:
        sharing_price = tariff.sharing_price_ct_kwh
        producer_payout = tariff.producer_payout_ct_kwh

    return sharing_price, producer_payout, community_fee_ct


def calculate_monthly_community_statements(
    tenant: Tenant, year: int, month: int, force_model: str = None
) -> list[CommunityMonthlyStatement]:
    """
    Erstellt oder aktualisiert monatliche Abrechnungsnachweise für alle Mitglieder einer Community.
    Unterstützt alle Allokationsmodelle sowie statische, börsenpreis-indexierte und Zeittarife.
    """
    _, last_day = calendar.monthrange(year, month)
    period_start = date(year, month, 1)
    period_end = date(year, month, last_day)

    period_start_dt = timezone.make_aware(datetime.combine(period_start, time.min))
    period_end_dt = timezone.make_aware(datetime.combine(period_end, time.max))

    tariff = get_active_community_tariff(tenant, at_date=period_start)
    allocation_model = force_model or tariff.allocation_model or CommunityTariff.ALLOCATION_DYNAMIC
    member_shares = get_active_member_shares(tenant, at_date=period_start)

    memberships = list(TenantMembership.objects.filter(tenant=tenant).select_related("user"))
    if not memberships:
        return []

    # Durchschnittlichen Spotpreis für den Monat als Referenz ermitteln
    from market.models import SpotPrice
    avg_spot_record = SpotPrice.objects.filter(
        timestamp__gte=period_start_dt,
        timestamp__lte=period_end_dt,
    ).aggregate(avg_price=Avg("price_eur_per_kwh"))
    
    avg_spot_eur = avg_spot_record.get("avg_price")
    avg_spot_ct = (Decimal(str(avg_spot_eur)) * Decimal("100.0")) if avg_spot_eur is not None else Decimal("10.00")

    effective_sharing_price_ct, effective_payout_ct, effective_fee_ct = get_effective_tariff_prices_for_slot(
        tariff, period_start_dt, spot_price_ct_kwh=avg_spot_ct
    )

    created_statements = []

    for membership in memberships:
        user = membership.user
        if not user:
            continue

        # Zähler des Nutzers in diesem Tenant ermitteln
        user_meters = Meter.objects.filter(
            tenant=tenant,
            removed_at__isnull=True,
        ).filter(
            Q(owner_membership=membership)
            | Q(owner_user=user)
            | Q(billing_assignments__user=user, billing_assignments__is_active=True)
        ).distinct()

        # BalanceSlots aggregieren
        slots_agg = BalanceSlot.objects.filter(
            tenant=tenant,
            meter__in=user_meters,
            period_start__gte=period_start_dt,
            period_start__lte=period_end_dt,
        ).aggregate(
            total_gen=Sum("generation_kwh"),
            total_con=Sum("consumption_kwh"),
            total_self=Sum("self_consumption_kwh"),
            total_grid_in=Sum("grid_import_kwh"),
            total_grid_out=Sum("grid_export_kwh"),
        )

        produced_kwh = slots_agg["total_gen"] or Decimal("0.0")
        consumed_kwh = slots_agg["total_con"] or Decimal("0.0")
        self_consumed_kwh = slots_agg["total_self"] or Decimal("0.0")
        grid_import_kwh = slots_agg["total_grid_in"] or Decimal("0.0")
        grid_export_kwh = slots_agg["total_grid_out"] or Decimal("0.0")

        # Geteilte Mengen (Sharing) berechnen:
        shared_imported_kwh = max(consumed_kwh - grid_import_kwh - self_consumed_kwh, Decimal("0.0"))
        shared_exported_kwh = max(produced_kwh - grid_export_kwh - self_consumed_kwh, Decimal("0.0"))

        # Falls keine getrennte Slot-Nettung vorliegt, min(produced, consumed) als Fallback
        if shared_imported_kwh == Decimal("0.0") and shared_exported_kwh == Decimal("0.0") and (produced_kwh > 0 or consumed_kwh > 0):
            if produced_kwh > consumed_kwh:
                shared_exported_kwh = produced_kwh - consumed_kwh
            else:
                shared_imported_kwh = consumed_kwh - produced_kwh

        # Falls Gemeinschafts-Quoten vorliegen und kein direkter Erzeugungszähler existiert:
        m_id = str(membership.id)
        if produced_kwh == Decimal("0.0") and m_id in member_shares:
            # Virtuelle Erzeugungsquote an zentralen Gemeinschaftsanlagen
            community_gen_agg = BalanceSlot.objects.filter(
                tenant=tenant,
                period_start__gte=period_start_dt,
                period_start__lte=period_end_dt,
            ).exclude(meter__in=user_meters).aggregate(total=Sum("generation_kwh"))["total"] or Decimal("0.0")
            
            if community_gen_agg > Decimal("0.0"):
                q_i = member_shares[m_id]
                allocated_community_pv = community_gen_agg * q_i
                if allocation_model == CommunityTariff.ALLOCATION_STATIC:
                    shared_imported_kwh = min(consumed_kwh, allocated_community_pv)
                elif allocation_model == CommunityTariff.ALLOCATION_HYBRID:
                    shared_imported_kwh = min(consumed_kwh, allocated_community_pv)

        # Finanzielle Beträge basierend auf den dynamisch ermittelten Tarifpreisen berechnen
        charge_import_eur = (shared_imported_kwh * (effective_sharing_price_ct / Decimal("100.0"))).quantize(Decimal("0.01"))
        credit_export_eur = (shared_exported_kwh * (effective_payout_ct / Decimal("100.0"))).quantize(Decimal("0.01"))
        community_fee_eur = (shared_imported_kwh * (effective_fee_ct / Decimal("100.0"))).quantize(Decimal("0.01"))
        net_balance_eur = (credit_export_eur - charge_import_eur - community_fee_eur).quantize(Decimal("0.01"))

        t_prefix = str(tenant.id)[:4].upper()
        m_prefix = str(membership.id)[:6].upper()
        statement_number = f"SHR-{t_prefix}-{year}{month:02d}-{m_prefix}"

        statement, _ = CommunityMonthlyStatement.objects.update_or_create(
            membership=membership,
            period_start=period_start,
            period_end=period_end,
            defaults={
                "statement_number": statement_number,
                "tenant": tenant,
                "user": user,
                "tariff": tariff,
                "produced_total_kwh": produced_kwh,
                "consumed_total_kwh": consumed_kwh,
                "shared_imported_kwh": shared_imported_kwh,
                "shared_exported_kwh": shared_exported_kwh,
                "grid_residual_import_kwh": grid_import_kwh,
                "grid_residual_export_kwh": grid_export_kwh,
                "charge_shared_import_eur": charge_import_eur,
                "credit_shared_export_eur": credit_export_eur,
                "community_fee_eur": community_fee_eur,
                "net_balance_eur": net_balance_eur,
                "status": CommunityMonthlyStatement.STATUS_FINALIZED,
                "finalized_at": timezone.now(),
            },
        )
        created_statements.append(statement)

    return created_statements


def get_allocation_comparison_preview(tenant: Tenant, year: int, month: int) -> dict:
    """
    Simuliert und vergleicht die 3 Allokationsmodelle (Dynamisch, Statisch, Hybrid)
    für einen angegebenen Abrechnungsmonat nebeneinander.
    """
    models = [
        ("dynamic", "Dynamisch nach Verbrauch"),
        ("static", "Statische Beteiligungsquoten (MEA)"),
        ("hybrid", "Hybrid (Vorrang-Quote + Überlauf)"),
    ]

    tariff = get_active_community_tariff(tenant)
    shares = get_active_member_shares(tenant)

    results = {}
    for model_key, model_label in models:
        statements = calculate_monthly_community_statements(tenant, year, month, force_model=model_key)
        total_shared = sum(float(s.shared_imported_kwh) for s in statements)
        total_savings = total_shared * 0.22
        
        member_results = [
            {
                "membership_id": str(s.membership_id),
                "user_email": s.user.email,
                "share_percent": float(shares.get(str(s.membership_id), 0.0) * 100),
                "consumed_kwh": float(s.consumed_total_kwh),
                "shared_kwh": float(s.shared_imported_kwh),
                "grid_import_kwh": float(s.grid_residual_import_kwh),
                "net_balance_eur": float(s.net_balance_eur),
                "autarky_pct": round((float(s.shared_imported_kwh) / float(s.consumed_total_kwh) * 100), 1) if float(s.consumed_total_kwh) > 0 else 0.0,
            }
            for s in statements
        ]

        results[model_key] = {
            "key": model_key,
            "label": model_label,
            "total_shared_kwh": round(total_shared, 2),
            "total_savings_eur": round(total_savings, 2),
            "members": member_results,
        }

    return {
        "tenant_id": str(tenant.id),
        "tenant_name": tenant.name,
        "active_model": tariff.allocation_model,
        "year": year,
        "month": month,
        "comparison": results,
    }
