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

    # UserSettings anlegen
    UserSettings.objects.get_or_create(
        user=admin_user,
        defaults={"language": "de", "timezone": "Europe/Berlin", "onboarding_step": "done"},
    )
    UserSettings.objects.get_or_create(
        user=member_user,
        defaults={"language": "de", "timezone": "Europe/Berlin", "onboarding_step": "done"},
    )

    # 2. DEMO COMMUNITIES (TENANTS) ERSTELLEN
    tenant_sonnenfeld, _ = Tenant.objects.update_or_create(
        slug="quartier-sonnenfeld",
        defaults={
            "name": "Quartier Sonnenfeld (Energy Sharing Community)",
            "primary_color": "#10b981",
            "is_public": True,
        },
    )

    tenant_amselweg, _ = Tenant.objects.update_or_create(
        slug="bioenergie-dorf-amselweg",
        defaults={
            "name": "Bioenergie-Dorf Amselweg & Solarpark",
            "primary_color": "#6366f1",
            "is_public": True,
        },
    )

    # 3. MITGLIEDSCHAFTEN (MEMBERSHIPS)
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

    # 4. TARIFE ANLEGEN
    tariff_sonnenfeld, _ = CommunityTariff.objects.update_or_create(
        tenant=tenant_sonnenfeld,
        defaults={
            "name": "Sonnenfeld Börsentarif Dynamisch (§ 42b EnWG)",
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

    # 6. ZÄHLER ANLEGEN
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

    # 7. BALANCE SLOTS (15-MINUTEN HISTORIE FÜR ECHTZEIT-CHARTS & MONATSABRECHNUNG)
    now = timezone.now()
    now_slot = now.replace(minute=(now.minute // 15) * 15, second=0, microsecond=0)

    # Wenn noch keine BalanceSlots existieren, generiere die letzten 7 Tage + Heute
    if BalanceSlot.objects.filter(tenant=tenant_sonnenfeld).count() < 50:
        slots_to_create = []
        readings_to_create = []

        start_dt = now_slot - timedelta(days=7)
        cur_dt = start_dt

        while cur_dt <= now_slot:
            cur_end = cur_dt + timedelta(minutes=15)
            hour = cur_dt.hour

            # PV Profil (Sonne zwischen 06:00 und 20:00 Uhr)
            pv_kwh = Decimal("0.0")
            if 6 <= hour <= 19:
                peak = Decimal("7.5")  # 30 kWp Anlage / 4 = max 7.5 kWh pro 15m Slot
                factor = Decimal(max(0, 1 - abs(hour - 13) / 7.0))
                pv_kwh = (peak * factor).quantize(Decimal("0.001"))

            # User Verbrauch (0.2 bis 0.8 kWh pro 15m)
            user_con_kwh = Decimal("0.25") if (hour < 6 or hour > 22) else Decimal("0.65")

            # PV Erzeugungs-Slot
            slots_to_create.append(BalanceSlot(
                tenant=tenant_sonnenfeld,
                meter=pv_central_meter,
                period_start=cur_dt,
                generation_kwh=pv_kwh,
                consumption_kwh=Decimal("0.0"),
                self_consumption_kwh=Decimal("0.0"),
                grid_import_kwh=Decimal("0.0"),
                grid_export_kwh=pv_kwh,
            ))

            # User Verbrauchs-Slot
            user_shared = min(user_con_kwh, pv_kwh * Decimal("0.40"))
            user_grid = max(Decimal("0.0"), user_con_kwh - user_shared)
            slots_to_create.append(BalanceSlot(
                tenant=tenant_sonnenfeld,
                meter=user_meter,
                period_start=cur_dt,
                generation_kwh=Decimal("0.0"),
                consumption_kwh=user_con_kwh,
                self_consumption_kwh=Decimal("0.0"),
                grid_import_kwh=user_grid,
                grid_export_kwh=Decimal("0.0"),
            ))

            # 15m OBIS Messwerte für MSCONS Export (1.8.0 Bezug, 2.8.0 Einspeisung)
            readings_to_create.append(AggregatedReading(
                tenant=tenant_sonnenfeld,
                meter=user_meter,
                obis_code="1.8.0",
                period_start=cur_dt,
                value=user_con_kwh,
                unit="kWh",
            ))
            if pv_kwh > 0:
                readings_to_create.append(AggregatedReading(
                    tenant=tenant_sonnenfeld,
                    meter=pv_central_meter,
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

    statement_num = f"SHR-SONN-{prev_month_start.year}{prev_month_start.month:02d}-JULIA"
    CommunityMonthlyStatement.objects.update_or_create(
        statement_number=statement_num,
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

    return {
        "admin_user": admin_user,
        "member_user": member_user,
        "tenant_sonnenfeld": tenant_sonnenfeld,
        "tenant_amselweg": tenant_amselweg,
    }
