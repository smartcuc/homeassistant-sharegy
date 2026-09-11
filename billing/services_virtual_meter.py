"""
billing/services_virtual_meter.py

Virtueller Summenzähler für Mehrfamilienhäuser (MFH), Quartiere und Nachbarschaften (Energy Sharing).
Aggregiert Erzeugungs- und Verbrauchszähler im 15-Minuten-Takt am virtuellen Netzanschlusspunkt (NAP)
und berechnet Eigenverbrauch, Restnetzbezug, Überschusseinspeisung sowie Autarkiegrade.
"""

from datetime import date, datetime, time, timedelta
from decimal import Decimal
from django.utils import timezone
from django.db.models import Sum, Q

from core.models import Tenant, Meter, BalanceSlot
from accounts.models import TenantMembership
from billing.models import CommunityTariff, CommunityMemberShare
from billing.services_sharing_settlement import (
    get_active_community_tariff,
    get_active_member_shares,
    calculate_sharing_allocation_for_slot,
)


def calculate_virtual_master_meter_timeline(
    tenant: Tenant,
    start_date: date,
    end_date: date,
    allocation_model: str = None,
) -> dict:
    """
    Berechnet die 15-Minuten-Zeitreihe des virtuellen Summenzählers für eine Liegenschaft / Community.
    
    Rückgabe:
    - timeline: Liste aller 15-Minuten-Intervalle mit Summen und Allokation
    - totals: Aggregierte Gesamtkennzahlen für den gewählten Zeitraum (kWh & %)
    - members: Liste der beteiligten Mitglieder/Parteien
    """
    start_dt = timezone.make_aware(datetime.combine(start_date, time.min))
    end_dt = timezone.make_aware(datetime.combine(end_date, time.max))

    tariff = get_active_community_tariff(tenant, at_date=start_date)
    model = allocation_model or tariff.allocation_model or CommunityTariff.ALLOCATION_DYNAMIC
    member_shares = get_active_member_shares(tenant, at_date=start_date)

    memberships = list(
        TenantMembership.objects.filter(tenant=tenant)
        .select_related("user")
        .order_by("user__last_name", "user__first_name")
    )
    members_info = [
        {
            "membership_id": str(m.id),
            "user_id": str(m.user_id),
            "name": f"{m.user.first_name} {m.user.last_name}".strip() or m.user.username or m.user.email,
            "email": m.user.email,
            "role": m.role,
            "share_percent": float(member_shares.get(str(m.id), Decimal("0.0")) * 100),
        }
        for m in memberships
    ]

    slots = (
        BalanceSlot.objects.filter(
            tenant=tenant,
            period_start__gte=start_dt,
            period_start__lte=end_dt,
        )
        .order_by("period_start")
    )

    timeline = []
    total_generation_kwh = Decimal("0.0")
    total_consumption_kwh = Decimal("0.0")
    total_shared_kwh = Decimal("0.0")
    total_grid_import_kwh = Decimal("0.0")
    total_grid_export_kwh = Decimal("0.0")

    member_totals = {
        str(m.id): {
            "consumption_kwh": Decimal("0.0"),
            "shared_kwh": Decimal("0.0"),
            "grid_import_kwh": Decimal("0.0"),
        }
        for m in memberships
    }

    for slot in slots:
        slot_gen = slot.generation_kwh or Decimal("0.0")
        slot_cons = slot.consumption_kwh or Decimal("0.0")

        c_by_member = {}
        if members_info:
            n_members = len(members_info)
            for m in memberships:
                m_id = str(m.id)
                q_i = member_shares.get(m_id, Decimal(1) / Decimal(n_members))
                c_by_member[m_id] = (slot_cons * q_i).quantize(Decimal("0.0001"))
        else:
            c_by_member = {}

        alloc = calculate_sharing_allocation_for_slot(
            consumption_by_member=c_by_member,
            total_generation=slot_gen,
            allocation_model=model,
            member_shares_map=member_shares,
        )

        shared_slot = alloc["total_shared"]
        grid_exp_slot = alloc["grid_export_total"]
        grid_imp_slot = sum(alloc["grid_import_by_member"].values(), Decimal("0.0"))

        total_generation_kwh += slot_gen
        total_consumption_kwh += slot_cons
        total_shared_kwh += shared_slot
        total_grid_import_kwh += grid_imp_slot
        total_grid_export_kwh += grid_exp_slot

        for m_id, s_val in alloc["shared_by_member"].items():
            if m_id in member_totals:
                member_totals[m_id]["consumption_kwh"] += c_by_member.get(m_id, Decimal("0.0"))
                member_totals[m_id]["shared_kwh"] += s_val
                member_totals[m_id]["grid_import_kwh"] += alloc["grid_import_by_member"].get(m_id, Decimal("0.0"))

        timeline.append({
            "timestamp": slot.period_start.isoformat(),
            "generation_kwh": float(slot_gen),
            "consumption_kwh": float(slot_cons),
            "shared_solar_kwh": float(shared_slot),
            "grid_import_kwh": float(grid_imp_slot),
            "grid_export_kwh": float(grid_exp_slot),
            "self_consumption_rate_pct": float((shared_slot / slot_gen * 100).quantize(Decimal("0.1"))) if slot_gen > 0 else 0.0,
            "self_sufficiency_rate_pct": float((shared_slot / slot_cons * 100).quantize(Decimal("0.1"))) if slot_cons > 0 else 0.0,
        })

    autarky_pct = (
        float((total_shared_kwh / total_consumption_kwh * 100).quantize(Decimal("0.1")))
        if total_consumption_kwh > 0
        else 0.0
    )
    self_consumption_pct = (
        float((total_shared_kwh / total_generation_kwh * 100).quantize(Decimal("0.1")))
        if total_generation_kwh > 0
        else 0.0
    )

    return {
        "tenant": {
            "id": str(tenant.id),
            "name": tenant.name,
            "slug": getattr(tenant, "slug", ""),
        },
        "period": {
            "start": start_date.isoformat(),
            "end": end_date.isoformat(),
            "slots_count": len(timeline),
        },
        "tariff": {
            "name": tariff.name,
            "allocation_model": model,
            "sharing_price_ct_kwh": float(tariff.sharing_price_ct_kwh),
            "producer_payout_ct_kwh": float(tariff.producer_payout_ct_kwh),
        },
        "totals": {
            "total_generation_kwh": float(total_generation_kwh),
            "total_consumption_kwh": float(total_consumption_kwh),
            "total_shared_kwh": float(total_shared_kwh),
            "total_grid_import_kwh": float(total_grid_import_kwh),
            "total_grid_export_kwh": float(total_grid_export_kwh),
            "self_sufficiency_rate_pct": autarky_pct,
            "self_consumption_rate_pct": self_consumption_pct,
        },
        "members": [
            {
                **m_info,
                "totals": {
                    "consumption_kwh": float(member_totals[m_info["membership_id"]]["consumption_kwh"]),
                    "shared_kwh": float(member_totals[m_info["membership_id"]]["shared_kwh"]),
                    "grid_import_kwh": float(member_totals[m_info["membership_id"]]["grid_import_kwh"]),
                },
            }
            for m_info in members_info
        ],
        "timeline": timeline,
    }
