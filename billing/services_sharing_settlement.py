"""
billing/services_sharing_settlement.py

Berechnungs- und Clearing-Engine für Energy Sharing Communities (Säule 2).
Erstellt monatliche Abrechnungsnachweise für Erzeuger, Verbraucher und Prosumer.
"""

import calendar
from datetime import date, datetime, time
from decimal import Decimal
from django.utils import timezone
from django.db.models import Sum, Q

from core.models import Tenant, Meter, BalanceSlot
from accounts.models import TenantMembership
from billing.models import CommunityTariff, CommunityMonthlyStatement


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
            sharing_price_ct_kwh=Decimal("12.00"),
            producer_payout_ct_kwh=Decimal("10.00"),
            community_fee_ct_kwh=Decimal("2.00"),
            grid_fee_saved_ct_kwh=Decimal("0.00"),
            valid_from=timezone.make_aware(datetime(2026, 1, 1, 0, 0)),
            is_active=True,
        )

    return tariff


def calculate_monthly_community_statements(tenant: Tenant, year: int, month: int) -> list[CommunityMonthlyStatement]:
    """
    Erstellt oder aktualisiert monatliche Abrechnungsnachweise für alle Mitglieder einer Community.
    """
    _, last_day = calendar.monthrange(year, month)
    period_start = date(year, month, 1)
    period_end = date(year, month, last_day)

    period_start_dt = timezone.make_aware(datetime.combine(period_start, time.min))
    period_end_dt = timezone.make_aware(datetime.combine(period_end, time.max))

    tariff = get_active_community_tariff(tenant, at_date=period_start)
    memberships = TenantMembership.objects.filter(tenant=tenant).select_related("user")

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
        # Bezug aus Community = Gesamter Verbrauch - Reststrom vom Netz - Eigenverbrauch vor Ort
        shared_imported_kwh = max(consumed_kwh - grid_import_kwh - self_consumed_kwh, Decimal("0.0"))
        # Abgabe an Community = Gesamte Erzeugung - Netzeinspeisung - Eigenverbrauch vor Ort
        shared_exported_kwh = max(produced_kwh - grid_export_kwh - self_consumed_kwh, Decimal("0.0"))

        # Falls keine getrennte Slot-Nettung vorliegt, min(produced, consumed) als Fallback
        if shared_imported_kwh == Decimal("0.0") and shared_exported_kwh == Decimal("0.0") and (produced_kwh > 0 or consumed_kwh > 0):
            if produced_kwh > consumed_kwh:
                shared_exported_kwh = produced_kwh - consumed_kwh
            else:
                shared_imported_kwh = consumed_kwh - produced_kwh

        # Finanzielle Beträge berechnen
        # 1. Kosten für bezogenen Community-Strom: kWh * Ct / 100
        charge_import_eur = (shared_imported_kwh * (tariff.sharing_price_ct_kwh / Decimal("100.0"))).quantize(Decimal("0.01"))

        # 2. Gutschrift für eingespeisten Community-Strom: kWh * Ct / 100
        credit_export_eur = (shared_exported_kwh * (tariff.producer_payout_ct_kwh / Decimal("100.0"))).quantize(Decimal("0.01"))

        # 3. Community-Umlage: bezogene kWh * Umlage-Ct / 100
        community_fee_eur = (shared_imported_kwh * (tariff.community_fee_ct_kwh / Decimal("100.0"))).quantize(Decimal("0.01"))

        # 4. Netto-Saldo: Gutschrift - Bezugskosten - Umlage
        net_balance_eur = (credit_export_eur - charge_import_eur - community_fee_eur).quantize(Decimal("0.01"))

        # Eindeutige Abrechnungsnummer generieren
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
