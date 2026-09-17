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

    # Standard Demo User (demo@sharegy.de) mit Zugriff auf alle 3 Gemeinschaften
    demo_user = User.objects.filter(email="demo@sharegy.de").first() or User.objects.filter(username="demo@sharegy.de").first()
    if not demo_user:
        demo_user = User.objects.create(
            email="demo@sharegy.de",
            username="demo@sharegy.de",
            first_name="Demo",
            last_name="User",
            is_active=True,
        )
        demo_user.set_password("DemoSharegy2026!")
        demo_user.save()

    TenantMembership.objects.update_or_create(
        tenant=tenant_sonnenfeld,
        user=demo_user,
        defaults={"role": "member", "is_active": True},
    )
    TenantMembership.objects.update_or_create(
        tenant=tenant_mieterstrom,
        user=demo_user,
        defaults={"role": "member", "is_active": True},
    )
    TenantMembership.objects.update_or_create(
        tenant=tenant_ggv,
        user=demo_user,
        defaults={"role": "member", "is_active": True},
    )

    # 4. TARIFE ANLEGEN (Defensiv gegen bestehende Duplikate)
    tariff_sonnenfeld = CommunityTariff.objects.filter(tenant=tenant_sonnenfeld).first()
    if not tariff_sonnenfeld:
        tariff_sonnenfeld = CommunityTariff(tenant=tenant_sonnenfeld)
    tariff_sonnenfeld.name = "Sonnenfeld Börsentarif Dynamisch (Energy Sharing)"
    tariff_sonnenfeld.pricing_model = CommunityTariff.PRICING_MODEL_SPOT_INDEXED
    tariff_sonnenfeld.allocation_model = CommunityTariff.ALLOCATION_HYBRID
    tariff_sonnenfeld.sharing_price_ct_kwh = Decimal("12.50")
    tariff_sonnenfeld.producer_payout_ct_kwh = Decimal("10.00")
    tariff_sonnenfeld.community_fee_ct_kwh = Decimal("2.00")
    tariff_sonnenfeld.grid_fee_saved_ct_kwh = Decimal("1.50")
    tariff_sonnenfeld.spot_markup_ct_kwh = Decimal("3.20")
    tariff_sonnenfeld.spot_floor_price_ct_kwh = Decimal("5.00")
    tariff_sonnenfeld.spot_cap_price_ct_kwh = Decimal("30.00")
    tariff_sonnenfeld.feed_in_spot_share_pct = Decimal("85.00")
    tariff_sonnenfeld.is_active = True
    tariff_sonnenfeld.save()

    tariff_amselweg = CommunityTariff.objects.filter(tenant=tenant_amselweg).first()
    if not tariff_amselweg:
        tariff_amselweg = CommunityTariff(tenant=tenant_amselweg)
    tariff_amselweg.name = "Amselweg Quartierstarif Fix"
    tariff_amselweg.pricing_model = CommunityTariff.PRICING_MODEL_STATIC
    tariff_amselweg.allocation_model = CommunityTariff.ALLOCATION_DYNAMIC
    tariff_amselweg.sharing_price_ct_kwh = Decimal("14.00")
    tariff_amselweg.producer_payout_ct_kwh = Decimal("11.00")
    tariff_amselweg.community_fee_ct_kwh = Decimal("1.50")
    tariff_amselweg.grid_fee_saved_ct_kwh = Decimal("1.20")
    tariff_amselweg.is_active = True
    tariff_amselweg.save()

    tariff_mieterstrom = CommunityTariff.objects.filter(tenant=tenant_mieterstrom).first()
    if not tariff_mieterstrom:
        tariff_mieterstrom = CommunityTariff(tenant=tenant_mieterstrom)
    tariff_mieterstrom.name = "Mieterstrom Vollversorgung (§ 42a EnWG)"
    tariff_mieterstrom.pricing_model = CommunityTariff.PRICING_MODEL_STATIC
    tariff_mieterstrom.allocation_model = CommunityTariff.ALLOCATION_DYNAMIC
    tariff_mieterstrom.sharing_price_ct_kwh = Decimal("21.50")
    tariff_mieterstrom.producer_payout_ct_kwh = Decimal("16.00")
    tariff_mieterstrom.community_fee_ct_kwh = Decimal("0.00")
    tariff_mieterstrom.grid_fee_saved_ct_kwh = Decimal("2.80")
    tariff_mieterstrom.is_active = True
    tariff_mieterstrom.save()

    tariff_ggv = CommunityTariff.objects.filter(tenant=tenant_ggv).first()
    if not tariff_ggv:
        tariff_ggv = CommunityTariff(tenant=tenant_ggv)
    tariff_ggv.name = "GGV Solare Vor-Ort-Aufteilung (§ 42b EnWG)"
    tariff_ggv.pricing_model = CommunityTariff.PRICING_MODEL_STATIC
    tariff_ggv.allocation_model = CommunityTariff.ALLOCATION_HYBRID
    tariff_ggv.sharing_price_ct_kwh = Decimal("11.00")
    tariff_ggv.producer_payout_ct_kwh = Decimal("10.00")
    tariff_ggv.community_fee_ct_kwh = Decimal("1.00")
    tariff_ggv.grid_fee_saved_ct_kwh = Decimal("0.00")
    tariff_ggv.is_active = True
    tariff_ggv.save()

    # 5. MEA-BETEILIGUNGSQUOTEN ANLEGEN
    # 5. MEA-BETEILIGUNGSQUOTEN ANLEGEN
    for (t, m, u, pct) in [
        (tenant_sonnenfeld, member_membership, member_user, Decimal("40.00")),
        (tenant_sonnenfeld, neighbor_membership, neighbor_user, Decimal("35.00")),
        (tenant_sonnenfeld, admin_membership, admin_user, Decimal("25.00")),
        (tenant_ggv, ggv_user_membership, ggv_user, Decimal("12.50")),
    ]:
        share = CommunityMemberShare.objects.filter(tenant=t, membership=m).first()
        if not share:
            share = CommunityMemberShare(tenant=t, membership=m)
        share.user = u
        share.share_percent = pct
        share.valid_from = timezone.make_aware(datetime(2026, 1, 1, 0, 0))
        share.is_active = True
        share.save()

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
        if BalanceSlot.objects.filter(tenant=cur_tenant, period_start__gte=now_slot - timedelta(days=2)).count() < 20:
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
    announcements_data = [
        (
            tenant_sonnenfeld,
            "☀️ Frühlings-Solarprognose: Höchstwerte im Quartier Sonnenfeld erwartet!",
            admin_user,
            "Liebe Mitglieder, dank der optimalen Wetterlage und den dynamischen Börsenstromtarifen konnten wir die Autarkiequote im Quartier auf über 68% steigern. Die Monatsnachweise stehen im Portal als PDF bereit.",
            CommunityAnnouncement.CATEGORY_TARIFF,
        ),
        (
            tenant_mieterstrom,
            "⚡ Mieterstrom-Transparenzbericht: 65% Solarstrom-Deckung im Quartier Spreeblick",
            mieterstrom_admin,
            "Die Abrechnung für den Vormonat ist abgeschlossen. Durch die PV-Dachanlage konnten die Stromkosten um 28% unter dem örtlichen Grundversorgertarif gehalten werden.",
            CommunityAnnouncement.CATEGORY_INFO,
        ),
        (
            tenant_ggv,
            "⚖️ GGV-Aufteilungsschlüssel (§ 42b EnWG) für die WEG Parkstraße hinterlegt",
            ggv_admin,
            "Die viertelstündliche Aufteilung des PV-Solarstroms erfolgt statisch nach Miteigentumsanteilen (MEA). Der Reststrom wird separat über den eigenen Stromliefervertrag bezogen.",
            CommunityAnnouncement.CATEGORY_INFO,
        ),
        (
            tenant_sonnenfeld,
            "BNetzA § 42b EnWG Meldung erfolgreich an VNB übermittelt",
            admin_user,
            "Die 15-Minuten-Lastgangdaten für den abgelaufenen Abrechnungsmonat wurden über die MSCONS EDIFACT-Schnittstelle fehlerfrei an den Verteilnetzbetreiber übertragen.",
            CommunityAnnouncement.CATEGORY_INFO,
        ),
    ]
    for (t, title, author, msg, cat) in announcements_data:
        ann = CommunityAnnouncement.objects.filter(tenant=t, title=title).first()
        if not ann:
            ann = CommunityAnnouncement(tenant=t, title=title)
        ann.author = author
        ann.message = msg
        ann.category = cat
        ann.is_active = True
        ann.save()

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
