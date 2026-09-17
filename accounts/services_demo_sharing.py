"""
accounts/services_demo_sharing.py

Automatisches Seeding von repräsentativen, produktionsreifen Demo-Daten für:
1. Energy Sharing Community Admin (Multi-Community Hub, Tarife, MEA-Quoten, Abrechnungen, BNetzA MSCONS)
2. Energy Sharing Community User / Member (Cockpit, 15m-Netto-Sharing, Ersparnisse, Monatsabrechnungs-PDFs)
"""

import uuid
import logging
from decimal import Decimal
from datetime import datetime, date, timedelta, time
from django.utils import timezone
from django.contrib.auth import get_user_model
from django.db import transaction

from core.models import Tenant, Meter, BalanceSlot, AggregatedReading
from accounts.models import TenantMembership, UserSettings
from billing.models import (
    CommunityTariff,
    CommunityMemberShare,
    CommunityMonthlyStatement,
    CommunityAnnouncement,
)

User = get_user_model()
logger = logging.getLogger(__name__)


@transaction.atomic
def seed_sharing_demo_environment():
    """
    Erstellt oder aktualisiert realistische Test- und Demo-Daten für Sharing-Admins und Sharing-User.
    Defensiv implementiert gegen Unique-Constraints und bestehende Test-Daten.
    """
    # 1. USERS ERSTELLEN ODER HOLEN
    # --- Energy Sharing Personas ---
    admin_user = User.objects.filter(email="sharing-admin@sharegy.de").first() or User.objects.filter(username="sharing-admin@sharegy.de").first()
    if not admin_user:
        admin_user = User.objects.create(
            email="sharing-admin@sharegy.de",
            username="sharing-admin@sharegy.de",
            first_name="Alexander",
            last_name="Quartiermanager",
            is_staff=True,
            is_active=True,
        )
    admin_user.set_password("DemoSharingAdmin2026!")
    admin_user.is_staff = True
    admin_user.save()

    member_user = User.objects.filter(email="sharing-user@sharegy.de").first() or User.objects.filter(username="sharing-user@sharegy.de").first()
    if not member_user:
        member_user = User.objects.create(
            email="sharing-user@sharegy.de",
            username="sharing-user@sharegy.de",
            first_name="Julia",
            last_name="Sonnenschein",
            is_active=True,
        )
    member_user.set_password("DemoSharingUser2026!")
    member_user.save()

    neighbor_user = User.objects.filter(email="nachbar.mueller@sharegy.de").first() or User.objects.filter(username="nachbar.mueller@sharegy.de").first()
    if not neighbor_user:
        neighbor_user = User.objects.create(
            email="nachbar.mueller@sharegy.de",
            username="nachbar.mueller@sharegy.de",
            first_name="Markus",
            last_name="Müller",
            is_active=True,
        )
        neighbor_user.set_password("DemoSharingNeighbor2026!")
        neighbor_user.save()

    # --- Mieterstrom Personas (§ 42a EnWG) ---
    mieterstrom_admin = User.objects.filter(email="mieterstrom-admin@sharegy.de").first() or User.objects.filter(username="mieterstrom-admin@sharegy.de").first()
    if not mieterstrom_admin:
        mieterstrom_admin = User.objects.create(
            email="mieterstrom-admin@sharegy.de",
            username="mieterstrom-admin@sharegy.de",
            first_name="Maximilian",
            last_name="Contractor",
            is_staff=True,
            is_active=True,
        )
    mieterstrom_admin.set_password("DemoMieterstromAdmin2026!")
    mieterstrom_admin.is_staff = True
    mieterstrom_admin.save()

    mieterstrom_user = User.objects.filter(email="mieterstrom-user@sharegy.de").first() or User.objects.filter(username="mieterstrom-user@sharegy.de").first()
    if not mieterstrom_user:
        mieterstrom_user = User.objects.create(
            email="mieterstrom-user@sharegy.de",
            username="mieterstrom-user@sharegy.de",
            first_name="Tim",
            last_name="Mieter",
            is_active=True,
        )
    mieterstrom_user.set_password("DemoMieterstromUser2026!")
    mieterstrom_user.save()

    # --- GGV Personas (§ 42b EnWG) ---
    ggv_admin = User.objects.filter(email="ggv-admin@sharegy.de").first() or User.objects.filter(username="ggv-admin@sharegy.de").first()
    if not ggv_admin:
        ggv_admin = User.objects.create(
            email="ggv-admin@sharegy.de",
            username="ggv-admin@sharegy.de",
            first_name="Susanne",
            last_name="WEG-Verwaltung",
            is_staff=True,
            is_active=True,
        )
    ggv_admin.set_password("DemoGGVAdmin2026!")
    ggv_admin.is_staff = True
    ggv_admin.save()

    ggv_user = User.objects.filter(email="ggv-user@sharegy.de").first() or User.objects.filter(username="ggv-user@sharegy.de").first()
    if not ggv_user:
        ggv_user = User.objects.create(
            email="ggv-user@sharegy.de",
            username="ggv-user@sharegy.de",
            first_name="Sabine",
            last_name="Eigentümerin",
            is_active=True,
        )
    ggv_user.set_password("DemoGGVUser2026!")
    ggv_user.save()

    # UserSettings anlegen
    for u in [admin_user, member_user, neighbor_user, mieterstrom_admin, mieterstrom_user, ggv_admin, ggv_user]:
        UserSettings.objects.get_or_create(
            user=u,
            defaults={"language": "de", "timezone": "Europe/Berlin", "onboarding_step": "done"},
        )

    # 2. DEMO COMMUNITIES / TENANTS ERSTELLEN
    # Energy Sharing (eG)
    tenant_sonnenfeld, _ = Tenant.objects.update_or_create(
        slug="quartier-sonnenfeld",
        defaults={
            "name": "Quartier Sonnenfeld (Bürgerenergie eG)",
            "model_type": Tenant.MODEL_TYPE_ENERGY_SHARING,
            "legal_form": Tenant.LEGAL_FORM_COOPERATIVE,
            "primary_color": "#10b981",
            "is_public": True,
        },
    )

    tenant_amselweg, _ = Tenant.objects.update_or_create(
        slug="bioenergie-dorf-amselweg",
        defaults={
            "name": "Bioenergie-Dorf Amselweg & Solarpark",
            "model_type": Tenant.MODEL_TYPE_ENERGY_SHARING,
            "legal_form": Tenant.LEGAL_FORM_COOPERATIVE,
            "primary_color": "#6366f1",
            "is_public": True,
        },
    )

    # Mieterstrom (§ 42a EnWG)
    tenant_mieterstrom, _ = Tenant.objects.update_or_create(
        slug="quartier-spreeblick",
        defaults={
            "name": "Wohnquartier Spreeblick (Mieterstrom)",
            "model_type": Tenant.MODEL_TYPE_MIETERSTROM,
            "legal_form": Tenant.LEGAL_FORM_LANDLORD,
            "primary_color": "#059669",
            "is_public": True,
        },
    )

    # GGV (§ 42b EnWG)
    tenant_ggv, _ = Tenant.objects.update_or_create(
        slug="weg-parkstrasse",
        defaults={
            "name": "WEG Parkstraße 12-14 (Gebäudeversorgung)",
            "model_type": Tenant.MODEL_TYPE_GGV,
            "legal_form": Tenant.LEGAL_FORM_WEG,
            "primary_color": "#d97706",
            "is_public": True,
        },
    )

    # 3. MITGLIEDSCHAFTEN (MEMBERSHIPS)
    # Sharing
    admin_membership, _ = TenantMembership.objects.update_or_create(
        tenant=tenant_sonnenfeld,
        user=admin_user,
        defaults={"role": "admin", "is_active": True},
    )
    TenantMembership.objects.update_or_create(
        tenant=tenant_amselweg,
        user=admin_user,
        defaults={"role": "admin", "is_active": True},
    )
    member_membership, _ = TenantMembership.objects.update_or_create(
        tenant=tenant_sonnenfeld,
        user=member_user,
        defaults={"role": "member", "is_active": True},
    )
    neighbor_membership, _ = TenantMembership.objects.update_or_create(
        tenant=tenant_sonnenfeld,
        user=neighbor_user,
        defaults={"role": "member", "is_active": True},
    )

    # Mieterstrom
    mieterstrom_admin_membership, _ = TenantMembership.objects.update_or_create(
        tenant=tenant_mieterstrom,
        user=mieterstrom_admin,
        defaults={"role": "admin", "is_active": True},
    )
    mieterstrom_user_membership, _ = TenantMembership.objects.update_or_create(
        tenant=tenant_mieterstrom,
        user=mieterstrom_user,
        defaults={"role": "member", "is_active": True},
    )

    # GGV
    ggv_admin_membership, _ = TenantMembership.objects.update_or_create(
        tenant=tenant_ggv,
        user=ggv_admin,
        defaults={"role": "admin", "is_active": True},
    )
    ggv_user_membership, _ = TenantMembership.objects.update_or_create(
        tenant=tenant_ggv,
        user=ggv_user,
        defaults={"role": "member", "is_active": True},
    )

    # 4. TARIFE ANLEGEN
    tariff_sonnenfeld, _ = CommunityTariff.objects.update_or_create(
        tenant=tenant_sonnenfeld,
        defaults={
            "name": "Sonnenfeld Börsentarif Dynamisch (Energy Sharing)",
            "pricing_model": CommunityTariff.PRICING_MODEL_SPOT_INDEXED,
            "allocation_model": CommunityTariff.ALLOCATION_HYBRID,
            "sharing_price_ct_kwh": Decimal("12.50"),
            "producer_payout_ct_kwh": Decimal("10.00"),
            "community_fee_ct_kwh": Decimal("2.00"),
            "grid_fee_saved_ct_kwh": Decimal("1.50"),
            "spot_markup_ct_kwh": Decimal("3.20"),
            "spot_floor_price_ct_kwh": Decimal("5.00"),
            "spot_cap_price_ct_kwh": Decimal("30.00"),
            "feed_in_spot_share_pct": Decimal("85.00"),
            "is_active": True,
        },
    )

    CommunityTariff.objects.update_or_create(
        tenant=tenant_amselweg,
        defaults={
            "name": "Amselweg Quartierstarif Fix",
            "pricing_model": CommunityTariff.PRICING_MODEL_STATIC,
            "allocation_model": CommunityTariff.ALLOCATION_DYNAMIC,
            "sharing_price_ct_kwh": Decimal("14.00"),
            "producer_payout_ct_kwh": Decimal("11.00"),
            "community_fee_ct_kwh": Decimal("1.50"),
            "grid_fee_saved_ct_kwh": Decimal("1.20"),
            "is_active": True,
        },
    )

    tariff_mieterstrom, _ = CommunityTariff.objects.update_or_create(
        tenant=tenant_mieterstrom,
        defaults={
            "name": "Mieterstrom Vollversorgung (§ 42a EnWG)",
            "pricing_model": CommunityTariff.PRICING_MODEL_STATIC,
            "allocation_model": CommunityTariff.ALLOCATION_DYNAMIC,
            "sharing_price_ct_kwh": Decimal("21.50"),
            "producer_payout_ct_kwh": Decimal("16.00"),
            "community_fee_ct_kwh": Decimal("0.00"),
            "grid_fee_saved_ct_kwh": Decimal("2.80"),
            "is_active": True,
        },
    )

    tariff_ggv, _ = CommunityTariff.objects.update_or_create(
        tenant=tenant_ggv,
        defaults={
            "name": "GGV Solare Vor-Ort-Aufteilung (§ 42b EnWG)",
            "pricing_model": CommunityTariff.PRICING_MODEL_STATIC,
            "allocation_model": CommunityTariff.ALLOCATION_HYBRID,
            "sharing_price_ct_kwh": Decimal("11.00"),
            "producer_payout_ct_kwh": Decimal("10.00"),
            "community_fee_ct_kwh": Decimal("1.00"),
            "grid_fee_saved_ct_kwh": Decimal("0.00"),
            "is_active": True,
        },
    )

    # 5. MEA-BETEILIGUNGSQUOTEN ANLEGEN
    CommunityMemberShare.objects.update_or_create(
        tenant=tenant_sonnenfeld,
        membership=member_membership,
        defaults={
            "user": member_user,
            "share_percent": Decimal("40.00"),
            "valid_from": timezone.make_aware(datetime(2026, 1, 1, 0, 0)),
            "is_active": True,
        },
    )

    CommunityMemberShare.objects.update_or_create(
        tenant=tenant_sonnenfeld,
        membership=neighbor_membership,
        defaults={
            "user": neighbor_user,
            "share_percent": Decimal("35.00"),
            "valid_from": timezone.make_aware(datetime(2026, 1, 1, 0, 0)),
            "is_active": True,
        },
    )

    CommunityMemberShare.objects.update_or_create(
        tenant=tenant_sonnenfeld,
        membership=admin_membership,
        defaults={
            "user": admin_user,
            "share_percent": Decimal("25.00"),
            "valid_from": timezone.make_aware(datetime(2026, 1, 1, 0, 0)),
            "is_active": True,
        },
    )

    # GGV MEA Anteile (125/1000 = 12.5% für Sabine)
    CommunityMemberShare.objects.update_or_create(
        tenant=tenant_ggv,
        membership=ggv_user_membership,
        defaults={
            "user": ggv_user,
            "share_percent": Decimal("12.50"),
            "valid_from": timezone.make_aware(datetime(2026, 1, 1, 0, 0)),
            "is_active": True,
        },
    )

    # 6. ZÄHLER ANLEGEN
    # Sharing
    pv_central_meter, _ = Meter.objects.update_or_create(
        serial_number="1EMH-PV-SONNENFELD-01",
        defaults={
            "tenant": tenant_sonnenfeld,
            "meter_type": "pv",
            "owner_membership": admin_membership,
        },
    )

    user_meter, _ = Meter.objects.update_or_create(
        serial_number="1EMH-USER-JULIA-02",
        defaults={
            "tenant": tenant_sonnenfeld,
            "meter_type": "electricity",
            "owner_membership": member_membership,
        },
    )

    neighbor_meter, _ = Meter.objects.update_or_create(
        serial_number="1EMH-USER-MUELLER-03",
        defaults={
            "tenant": tenant_sonnenfeld,
            "meter_type": "electricity",
            "owner_membership": neighbor_membership,
        },
    )

    # Mieterstrom Zähler
    pv_mieterstrom_meter, _ = Meter.objects.update_or_create(
        serial_number="1EMH-PV-SPREEBLICK-01",
        defaults={
            "tenant": tenant_mieterstrom,
            "meter_type": "pv",
            "owner_membership": mieterstrom_admin_membership,
        },
    )

    user_mieterstrom_meter, _ = Meter.objects.update_or_create(
        serial_number="1EMH-USER-TIM-02",
        defaults={
            "tenant": tenant_mieterstrom,
            "meter_type": "electricity",
            "owner_membership": mieterstrom_user_membership,
        },
    )

    # GGV Zähler
    pv_ggv_meter, _ = Meter.objects.update_or_create(
        serial_number="1EMH-PV-PARKSTRASSE-01",
        defaults={
            "tenant": tenant_ggv,
            "meter_type": "pv",
            "owner_membership": ggv_admin_membership,
        },
    )

    user_ggv_meter, _ = Meter.objects.update_or_create(
        serial_number="1EMH-USER-SABINE-02",
        defaults={
            "tenant": tenant_ggv,
            "meter_type": "electricity",
            "owner_membership": ggv_user_membership,
        },
    )

    # 7. BALANCE SLOTS (15-MINUTEN HISTORIE FÜR ECHTZEIT-CHARTS & MONATSABRECHNUNG)
    now = timezone.now()
    now_slot = now.replace(minute=(now.minute // 15) * 15, second=0, microsecond=0)

    for (cur_tenant, cur_pv_meter, cur_user_meter, user_share_ratio) in [
        (tenant_sonnenfeld, pv_central_meter, user_meter, Decimal("0.40")),
        (tenant_mieterstrom, pv_mieterstrom_meter, user_mieterstrom_meter, Decimal("0.50")),
        (tenant_ggv, pv_ggv_meter, user_ggv_meter, Decimal("0.125")),
    ]:
        if BalanceSlot.objects.filter(tenant=cur_tenant).count() < 50:
            slots_to_create = []
            readings_to_create = []

            start_dt = now_slot - timedelta(days=7)
            cur_dt = start_dt

            while cur_dt <= now_slot:
                cur_end = cur_dt + timedelta(minutes=15)
                hour = cur_dt.hour

                pv_kwh = Decimal("0.0")
                if 6 <= hour <= 19:
                    peak = Decimal("8.0")
                    factor = Decimal(max(0, 1 - abs(hour - 13) / 7.0))
                    pv_kwh = (peak * factor).quantize(Decimal("0.001"))

                user_con_kwh = Decimal("0.25") if (hour < 6 or hour > 22) else Decimal("0.65")

                slots_to_create.append(BalanceSlot(
                    tenant=cur_tenant,
                    meter=cur_pv_meter,
                    period_start=cur_dt,
                    generation_kwh=pv_kwh,
                    consumption_kwh=Decimal("0.0"),
                    self_consumption_kwh=Decimal("0.0"),
                    grid_import_kwh=Decimal("0.0"),
                    grid_export_kwh=pv_kwh,
                ))

                user_shared = min(user_con_kwh, pv_kwh * user_share_ratio)
                user_grid = max(Decimal("0.0"), user_con_kwh - user_shared)
                slots_to_create.append(BalanceSlot(
                    tenant=cur_tenant,
                    meter=cur_user_meter,
                    period_start=cur_dt,
                    generation_kwh=Decimal("0.0"),
                    consumption_kwh=user_con_kwh,
                    self_consumption_kwh=Decimal("0.0"),
                    grid_import_kwh=user_grid,
                    grid_export_kwh=Decimal("0.0"),
                ))

                readings_to_create.append(AggregatedReading(
                    tenant=cur_tenant,
                    meter=cur_user_meter,
                    obis_code="1.8.0",
                    period_start=cur_dt,
                    value=user_con_kwh,
                    unit="kWh",
                ))
                if pv_kwh > 0:
                    readings_to_create.append(AggregatedReading(
                        tenant=cur_tenant,
                        meter=cur_pv_meter,
                        obis_code="2.8.0",
                        period_start=cur_dt,
                        value=pv_kwh,
                        unit="kWh",
                    ))

                cur_dt = cur_end

            BalanceSlot.objects.bulk_create(slots_to_create, ignore_conflicts=True)
            AggregatedReading.objects.bulk_create(readings_to_create, ignore_conflicts=True)

    # 8. MONATLICHE ABRECHNUNGSNACHWEISE (STATEMENTS)
    current_month_start = date(now.year, now.month, 1)
    prev_month_end = current_month_start - timedelta(days=1)
    prev_month_start = date(prev_month_end.year, prev_month_end.month, 1)

    # Sharing Statement
    statement_num_sharing = f"SHR-SONN-{prev_month_start.year}{prev_month_start.month:02d}-JULIA"
    CommunityMonthlyStatement.objects.update_or_create(
        statement_number=statement_num_sharing,
        defaults={
            "membership": member_membership,
            "period_start": prev_month_start,
            "period_end": prev_month_end,
            "tenant": tenant_sonnenfeld,
            "user": member_user,
            "tariff": tariff_sonnenfeld,
            "produced_total_kwh": Decimal("0.00"),
            "consumed_total_kwh": Decimal("380.50"),
            "shared_imported_kwh": Decimal("245.80"),
            "shared_exported_kwh": Decimal("0.00"),
            "grid_residual_import_kwh": Decimal("134.70"),
            "grid_residual_export_kwh": Decimal("0.00"),
            "charge_shared_import_eur": Decimal("30.73"),
            "credit_shared_export_eur": Decimal("0.00"),
            "community_fee_eur": Decimal("4.92"),
            "net_balance_eur": Decimal("-35.65"),
            "status": CommunityMonthlyStatement.STATUS_FINALIZED,
            "finalized_at": timezone.now(),
        },
    )

    # Mieterstrom Statement (§ 42a EnWG Vollversorgung)
    statement_num_mieterstrom = f"MTR-SPREE-{prev_month_start.year}{prev_month_start.month:02d}-TIM"
    CommunityMonthlyStatement.objects.update_or_create(
        statement_number=statement_num_mieterstrom,
        defaults={
            "membership": mieterstrom_user_membership,
            "period_start": prev_month_start,
            "period_end": prev_month_end,
            "tenant": tenant_mieterstrom,
            "user": mieterstrom_user,
            "tariff": tariff_mieterstrom,
            "produced_total_kwh": Decimal("0.00"),
            "consumed_total_kwh": Decimal("320.00"),
            "shared_imported_kwh": Decimal("210.00"), # Solarer Mieterstromanteil
            "shared_exported_kwh": Decimal("0.00"),
            "grid_residual_import_kwh": Decimal("110.00"), # Reststrom
            "grid_residual_export_kwh": Decimal("0.00"),
            "charge_shared_import_eur": Decimal("45.15"),
            "credit_shared_export_eur": Decimal("0.00"),
            "community_fee_eur": Decimal("0.00"),
            "net_balance_eur": Decimal("-78.25"),
            "status": CommunityMonthlyStatement.STATUS_FINALIZED,
            "finalized_at": timezone.now(),
        },
    )

    # GGV Statement (§ 42b EnWG Aufteilung)
    statement_num_ggv = f"GGV-PARK-{prev_month_start.year}{prev_month_start.month:02d}-SABINE"
    CommunityMonthlyStatement.objects.update_or_create(
        statement_number=statement_num_ggv,
        defaults={
            "membership": ggv_user_membership,
            "period_start": prev_month_start,
            "period_end": prev_month_end,
            "tenant": tenant_ggv,
            "user": ggv_user,
            "tariff": tariff_ggv,
            "produced_total_kwh": Decimal("0.00"),
            "consumed_total_kwh": Decimal("275.00"),
            "shared_imported_kwh": Decimal("165.00"), # Solarer Vor-Ort-Anteil
            "shared_exported_kwh": Decimal("0.00"),
            "grid_residual_import_kwh": Decimal("110.00"), # Externer EVU
            "grid_residual_export_kwh": Decimal("0.00"),
            "charge_shared_import_eur": Decimal("18.15"),
            "credit_shared_export_eur": Decimal("0.00"),
            "community_fee_eur": Decimal("1.65"),
            "net_balance_eur": Decimal("-19.80"),
            "status": CommunityMonthlyStatement.STATUS_FINALIZED,
            "finalized_at": timezone.now(),
        },
    )

    # 9. COMMUNITY ANNOUNCEMENTS (RUNDSCHREIBEN)
    CommunityAnnouncement.objects.update_or_create(
        tenant=tenant_sonnenfeld,
        title="☀️ Frühlings-Solarprognose: Höchstwerte im Quartier Sonnenfeld erwartet!",
        defaults={
            "author": admin_user,
            "message": "Liebe Mitglieder, dank der optimalen Wetterlage und den dynamischen Börsenstromtarifen konnten wir die Autarkiequote im Quartier auf über 68% steigern. Die Monatsnachweise stehen im Portal als PDF bereit.",
            "category": CommunityAnnouncement.CATEGORY_TARIFF,
            "is_active": True,
        },
    )

    CommunityAnnouncement.objects.update_or_create(
        tenant=tenant_mieterstrom,
        title="⚡ Mieterstrom-Transparenzbericht: 65% Solarstrom-Deckung im Quartier Spreeblick",
        defaults={
            "author": mieterstrom_admin,
            "message": "Die Abrechnung für den Vormonat ist abgeschlossen. Durch die PV-Dachanlage konnten die Stromkosten um 28% unter dem örtlichen Grundversorgertarif gehalten werden.",
            "category": CommunityAnnouncement.CATEGORY_INFO,
            "is_active": True,
        },
    )

    CommunityAnnouncement.objects.update_or_create(
        tenant=tenant_ggv,
        title="⚖️ GGV-Aufteilungsschlüssel (§ 42b EnWG) für die WEG Parkstraße hinterlegt",
        defaults={
            "author": ggv_admin,
            "message": "Die viertelstündliche Aufteilung des PV-Solarstroms erfolgt statisch nach Miteigentumsanteilen (MEA). Der Reststrom wird separat über den eigenen Stromliefervertrag bezogen.",
            "category": CommunityAnnouncement.CATEGORY_INFO,
            "is_active": True,
        },
    )

    CommunityAnnouncement.objects.update_or_create(
        tenant=tenant_sonnenfeld,
        title="BNetzA § 42b EnWG Meldung erfolgreich an VNB übermittelt",
        defaults={
            "author": admin_user,
            "message": "Die 15-Minuten-Lastgangdaten für den abgelaufenen Abrechnungsmonat wurden über die MSCONS EDIFACT-Schnittstelle fehlerfrei an den Verteilnetzbetreiber übertragen.",
            "category": CommunityAnnouncement.CATEGORY_INFO,
            "is_active": True,
        },
    )

    # 10. VIRTUAL POWER PLANT (VPP) DEMO POOLS & DISPATCH ORDERS
    try:
        from vpp.models import VPPFlexibilityPool, VPPDispatchOrder

        vpp_pool_50hertz, _ = VPPFlexibilityPool.objects.update_or_create(
            name="50Hertz Heimspeicher- & Flexibilitäts-Pool Sonnenfeld",
            defaults={
                "tso_operator": "50hertz",
                "market_product": "afrr_positive",
                "grid_region": "Regelzone 50Hertz (Nord-Ost)",
                "postal_code_prefix": "10,12,13,14",
                "min_activation_power_kw": Decimal("5.00"),
                "max_activation_power_kw": Decimal("250.00"),
                "is_active": True,
            }
        )

        VPPFlexibilityPool.objects.update_or_create(
            name="TenneT Redispatch 2.0 Pool Amselweg",
            defaults={
                "tso_operator": "tennet",
                "market_product": "redispatch_2_0",
                "grid_region": "Regelzone TenneT",
                "postal_code_prefix": "20,21,22,23",
                "min_activation_power_kw": Decimal("10.00"),
                "max_activation_power_kw": Decimal("500.00"),
                "is_active": True,
            }
        )

        # Letzte Dispatch Orders für Demo-Historie
        VPPDispatchOrder.objects.update_or_create(
            requested_by="50Hertz Automated Leitsystem (Demo)",
            target_power_kw=Decimal("45.00"),
            defaults={
                "pool": vpp_pool_50hertz,
                "dispatch_type": "positive_flex",
                "duration_minutes": 15,
                "status": "completed",
                "start_time": timezone.now() - timedelta(hours=2),
                "end_time": timezone.now() - timedelta(hours=1, minutes=45),
                "delivered_power_kw": Decimal("44.80"),
                "energy_delivered_kwh": Decimal("11.200"),
                "remuneration_eur": Decimal("18.50"),
            }
        )
    except Exception as e:
        logger.warning("VPP demo seeding skipped: %s", e)

    # 11. DEMO HOUSEHOLDS FÜR ADMIN & USER (OHNE EXTERNE SYSTEMVERBINDUNG)
    try:
        from demo.services.data_generator import setup_demo_household, generate_demo_telemetry
        if not member_user.homes.exists() or member_user.homes.first().devices.count() == 0:
            setup_demo_household(member_user)
        if not admin_user.homes.exists() or admin_user.homes.first().devices.count() == 0:
            setup_demo_household(admin_user)
        generate_demo_telemetry()
    except Exception as e:
        logger.warning("Demo household generation warning: %s", e)

    # 12. FRISCHE BENUTZER-INSTANZEN AUS DB HOLEN (GARANTIERT SAUBERE DB-SYNC FÜR LOGIN)
    admin_user.refresh_from_db()
    member_user.refresh_from_db()
    mieterstrom_admin.refresh_from_db()
    mieterstrom_user.refresh_from_db()
    ggv_admin.refresh_from_db()
    ggv_user.refresh_from_db()

    return {
        "admin_user": admin_user,
        "member_user": member_user,
        "mieterstrom_admin": mieterstrom_admin,
        "mieterstrom_user": mieterstrom_user,
        "ggv_admin": ggv_admin,
        "ggv_user": ggv_user,
        "tenant_sonnenfeld": tenant_sonnenfeld,
        "tenant_amselweg": tenant_amselweg,
        "tenant_mieterstrom": tenant_mieterstrom,
        "tenant_ggv": tenant_ggv,
    }
