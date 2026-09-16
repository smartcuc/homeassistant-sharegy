"""
vpp/services_clearing.py

VPP Market Clearing & Settlement Engine:
- Allokiert Dispatch-Abrufe auf eingeschriebene Kunden-Assets (Heimspeicher, § 14a SteuVE).
- Berechnet den 80/20 Revenue Split (80% an Kunden, 20% Sharegy Plattform-Marge).
- Erstellt periodische Clearing Statements für Kunden und verbucht Erlöse.
- Liefert aggregierte Earnings- und Performance-Kennzahlen für das Kunden-Cockpit.
"""

from decimal import Decimal
from datetime import date, datetime, timedelta
from typing import Optional, Dict, Any, List
import random

from django.db import transaction
from django.db.models import Sum, Count, Q
from django.utils import timezone

from devices.models import Device, DeviceLatestMetric
from vpp.models import (
    VPPFlexibilityPool,
    VPPDispatchOrder,
    VPPAssetEnrollment,
    VPPAssetDispatch,
    VPPClearingStatement,
)


DEFAULT_CUSTOMER_SHARE_PCT = Decimal("80.00")
DEFAULT_SHAREGY_FEE_PCT = Decimal("20.00")


def enroll_device_in_vpp(
    user,
    device_id: int,
    pool_id: Optional[str] = None,
    min_soc_reserve_pct: Decimal = Decimal("20.00"),
    auto_spot_arbitrage: bool = True,
    auto_afrr_frequency: bool = True,
) -> VPPAssetEnrollment:
    """
    Schreibt ein Gerät (Heimspeicher, Wallbox, § 14a WP) in das VPP ein.
    Validiert Eigentümerschaft und setzt Standard-Grenzwerte.
    """
    device = Device.objects.get(id=device_id)
    # Validierung: Gehört das Gerät zum Nutzer bzw. seinem Haushalt?
    if hasattr(device, "home") and device.home and hasattr(device.home, "user"):
        if device.home.user_id != user.id and not user.is_staff:
            raise PermissionError("Gerät gehört nicht zum angemeldeten Benutzer.")
    elif hasattr(device, "user") and device.user:
        if device.user_id != user.id and not user.is_staff:
            raise PermissionError("Gerät gehört nicht zum angemeldeten Benutzer.")

    pool = None
    if pool_id:
        pool = VPPFlexibilityPool.objects.filter(id=pool_id).first()
    if not pool:
        # Standard-Pool suchen oder ersten aktiven Pool zuweisen
        pool = VPPFlexibilityPool.objects.filter(is_active=True).first()

    enrollment, _ = VPPAssetEnrollment.objects.update_or_create(
        user=user,
        device=device,
        defaults={
            "pool": pool,
            "status": "active",
            "min_soc_reserve_pct": max(Decimal("10.00"), min(Decimal("60.00"), min_soc_reserve_pct)),
            "payout_share_pct": DEFAULT_CUSTOMER_SHARE_PCT,
            "auto_spot_arbitrage": auto_spot_arbitrage,
            "auto_afrr_frequency": auto_afrr_frequency,
        },
    )
    return enrollment


def set_enrollment_status(user, enrollment_id: str, new_status: str) -> VPPAssetEnrollment:
    """
    Pausiert, aktiviert oder beendet die VPP-Teilnahme eines Geräts.
    """
    qs = VPPAssetEnrollment.objects.filter(id=enrollment_id)
    if not user.is_staff:
        qs = qs.filter(user=user)
    enrollment = qs.first()
    if not enrollment:
        raise ValueError("Einschreibung nicht gefunden.")

    if new_status in ["active", "paused", "opted_out"]:
        enrollment.status = new_status
        enrollment.save(update_fields=["status", "updated_at"])
    return enrollment


def allocate_and_clear_dispatch(order: VPPDispatchOrder) -> List[VPPAssetDispatch]:
    """
    Verteilt die abgerufene Soll-Leistung (kW) eines VPPDispatchOrders auf die
    aktiv eingeschriebenen Geräte und berechnet den 80/20 Erlös-Split.
    """
    # 1. Aktive Einschreibungen laden
    enrollments_qs = VPPAssetEnrollment.objects.filter(
        status="active",
        device__active=True,
    ).select_related("device", "user", "pool")

    if order.pool_id:
        enrollments_qs = enrollments_qs.filter(Q(pool_id=order.pool_id) | Q(pool__isnull=True))

    enrollments = list(enrollments_qs)
    if not enrollments:
        return []

    # 2. Metriken und aktuelle SoCs batch-laden
    device_ids = [e.device_id for e in enrollments]
    metrics = DeviceLatestMetric.objects.filter(device_id__in=device_ids)
    metrics_map: Dict[int, Dict[str, float]] = {}
    for m in metrics:
        if m.device_id not in metrics_map:
            metrics_map[m.device_id] = {}
        try:
            metrics_map[m.device_id][m.metric_key] = float(m.value)
        except (ValueError, TypeError):
            continue

    total_target_kw = order.target_power_kw
    duration_hours = Decimal(str(order.duration_minutes / 60.0))
    total_gross_eur = order.remuneration_eur or Decimal("0.00")

    # Falls remuneration noch 0 ist, Standard 0.35 €/kWh annehmen
    if total_gross_eur == Decimal("0.00"):
        total_gross_eur = (total_target_kw * duration_hours * Decimal("0.35")).quantize(Decimal("0.01"))
        order.remuneration_eur = total_gross_eur
        order.save(update_fields=["remuneration_eur"])

    dispatches: List[VPPAssetDispatch] = []
    total_shares = len(enrollments)
    per_device_kw = (total_target_kw / Decimal(str(total_shares))).quantize(Decimal("0.01"))

    with transaction.atomic():
        for e in enrollments:
            dev_metrics = metrics_map.get(e.device_id, {})
            current_soc = Decimal(str(dev_metrics.get("soc", 65.0)))

            # Prüfen, ob SoC die Mindestreserve einhält (für positive Entladung)
            if order.dispatch_type == "positive_flex" and current_soc <= e.min_soc_reserve_pct:
                continue

            # Leistungsanteil
            alloc_kw = per_device_kw
            delivered_kw = (alloc_kw * Decimal("0.98")).quantize(Decimal("0.01"))
            energy_kwh = (delivered_kw * duration_hours).quantize(Decimal("0.001"))

            # Anteiliger Brutto-Erlös
            device_gross_eur = (total_gross_eur / Decimal(str(total_shares))).quantize(Decimal("0.01"))
            customer_share = (e.payout_share_pct / Decimal("100.00"))
            customer_payout = (device_gross_eur * customer_share).quantize(Decimal("0.01"))
            sharegy_fee = (device_gross_eur - customer_payout).quantize(Decimal("0.01"))

            # SoC Simulation
            soc_delta = (energy_kwh / Decimal("10.0")) * Decimal("100.0")  # ca. 10 kWh Speicher
            if order.dispatch_type == "positive_flex":
                soc_after = max(Decimal("5.0"), current_soc - soc_delta).quantize(Decimal("0.01"))
            else:
                soc_after = min(Decimal("100.0"), current_soc + soc_delta).quantize(Decimal("0.01"))

            asset_dispatch = VPPAssetDispatch.objects.create(
                dispatch_order=order,
                enrollment=e,
                device=e.device,
                allocated_power_kw=alloc_kw,
                delivered_power_kw=delivered_kw,
                energy_kwh=energy_kwh,
                gross_revenue_eur=device_gross_eur,
                customer_payout_eur=customer_payout,
                sharegy_fee_eur=sharegy_fee,
                soc_before_pct=current_soc.quantize(Decimal("0.01")),
                soc_after_pct=soc_after,
                is_cleared=False,
            )
            dispatches.append(asset_dispatch)

            # Einschreibungs-Statistiken aktualisieren
            e.total_earned_eur = (e.total_earned_eur + customer_payout).quantize(Decimal("0.01"))
            e.total_dispatches_count += 1
            e.save(update_fields=["total_earned_eur", "total_dispatches_count", "updated_at"])

        order.activated_devices_count = len(dispatches)
        order.save(update_fields=["activated_devices_count"])

    return dispatches


def execute_periodic_clearing_run(
    period_start: Optional[date] = None,
    period_end: Optional[date] = None,
) -> List[VPPClearingStatement]:
    """
    Führt den monatlichen oder periodischen Clearing-Lauf durch:
    Fasst alle offenen VPPAssetDispatch-Einträge zusammen, erstellt Statements
    und markiert die Posten als abgerechnet ('credited').
    """
    if period_end is None:
        period_end = timezone.now().date()
    if period_start is None:
        period_start = period_end.replace(day=1)

    # Alle noch nicht abgerechneten Asset-Dispatches abfragen
    unbilled_dispatches = VPPAssetDispatch.objects.filter(
        is_cleared=False,
        created_at__date__gte=period_start,
        created_at__date__lte=period_end,
    ).select_related("enrollment__user")

    user_map: Dict[int, List[VPPAssetDispatch]] = {}
    for d in unbilled_dispatches:
        u_id = d.enrollment.user_id
        if u_id not in user_map:
            user_map[u_id] = []
        user_map[u_id].append(d)

    created_statements: List[VPPClearingStatement] = []

    with transaction.atomic():
        for user_id, d_list in user_map.items():
            user_obj = d_list[0].enrollment.user
            total_events = len(d_list)
            total_energy = sum(d.energy_kwh for d in d_list)
            gross_rev = sum(d.gross_revenue_eur for d in d_list)
            customer_payout = sum(d.customer_payout_eur for d in d_list)
            sharegy_fee = sum(d.sharegy_fee_eur for d in d_list)

            ref_code = f"VPP-CLR-{period_end.strftime('%Y%m')}-{str(user_id)[:6]}"

            statement, created = VPPClearingStatement.objects.update_or_create(
                user=user_obj,
                period_start=period_start,
                period_end=period_end,
                defaults={
                    "dispatches_count": total_events,
                    "total_energy_kwh": total_energy,
                    "gross_revenue_eur": gross_rev,
                    "customer_payout_eur": customer_payout,
                    "sharegy_fee_eur": sharegy_fee,
                    "status": "credited",
                    "payment_reference": ref_code,
                    "credited_at": timezone.now(),
                },
            )

            # Dispatches auf is_cleared=True setzen
            for d in d_list:
                d.is_cleared = True
                d.save(update_fields=["is_cleared"])

            created_statements.append(statement)

    return created_statements


def get_user_flexibility_summary(user) -> Dict[str, Any]:
    """
    Liefert die aggregierten Flexibilitäts- und Erlösdaten für das Endkunden-Dashboard.
    """
    enrollments = VPPAssetEnrollment.objects.filter(user=user).select_related("device", "pool")
    
    total_earned = sum(e.total_earned_eur for e in enrollments)
    total_dispatches = sum(e.total_dispatches_count for e in enrollments)
    active_count = sum(1 for e in enrollments if e.status == "active")
    
    # Letzte Dispatches
    recent_dispatches = VPPAssetDispatch.objects.filter(
        enrollment__user=user
    ).select_related("device", "dispatch_order").order_by("-created_at")[:10]

    # Letzte Clearing Statements
    statements = VPPClearingStatement.objects.filter(
        user=user
    ).order_by("-period_end")[:6]

    # Hochrechnung jährlicher Verdienst
    estimated_annual_eur = round(float(total_earned) * 12.0 / max(1, len(statements) or 1), 2)
    if estimated_annual_eur == 0 and active_count > 0:
        estimated_annual_eur = round(active_count * 185.0, 2)  # Benchmark ca. 185 € / Speicher / Jahr

    return {
        "is_participating": active_count > 0,
        "enrolled_devices_count": len(enrollments),
        "active_devices_count": active_count,
        "total_earned_eur": float(total_earned),
        "estimated_annual_eur": estimated_annual_eur,
        "total_dispatches_count": total_dispatches,
        "co2_saved_kg": round(float(total_dispatches) * 4.2, 1),
        "enrollments": [
            {
                "id": str(e.id),
                "device_id": e.device_id,
                "device_name": e.device.name,
                "pool_name": e.pool.name if e.pool else "Standard Regelenergie Pool",
                "status": e.status,
                "min_soc_reserve_pct": float(e.min_soc_reserve_pct),
                "payout_share_pct": float(e.payout_share_pct),
                "total_earned_eur": float(e.total_earned_eur),
                "auto_spot_arbitrage": e.auto_spot_arbitrage,
                "auto_afrr_frequency": e.auto_afrr_frequency,
                "joined_at": e.joined_at.isoformat(),
            }
            for e in enrollments
        ],
        "recent_dispatches": [
            {
                "id": str(d.id),
                "device_name": d.device.name,
                "dispatch_type": d.dispatch_order.get_dispatch_type_display(),
                "delivered_power_kw": float(d.delivered_power_kw),
                "energy_kwh": float(d.energy_kwh),
                "customer_payout_eur": float(d.customer_payout_eur),
                "soc_before_pct": float(d.soc_before_pct),
                "soc_after_pct": float(d.soc_after_pct),
                "timestamp": d.created_at.isoformat(),
                "is_cleared": d.is_cleared,
            }
            for d in recent_dispatches
        ],
        "statements": [
            {
                "id": str(s.id),
                "period": f"{s.period_start.strftime('%d.%m.%Y')} - {s.period_end.strftime('%d.%m.%Y')}",
                "dispatches_count": s.dispatches_count,
                "total_energy_kwh": float(s.total_energy_kwh),
                "customer_payout_eur": float(s.customer_payout_eur),
                "status": s.get_status_display(),
                "payment_reference": s.payment_reference,
            }
            for s in statements
        ],
    }
