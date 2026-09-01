"""
billing/test_mscons_and_dynamic_tariffs.py

Unit-Tests für:
1. Dynamische & Börsenpreis-indexierte Sharing-Tarife (EPEX Spot, Floor, Cap, Aufschlag).
2. BNetzA-konforme MSCONS / EDIFACT Lastgang-Generierung (Export).
3. MSCONS EDIFACT Ingest & Parsing (Import).
"""

from decimal import Decimal
from datetime import date, datetime, time
from django.test import TestCase
from django.utils import timezone
from django.contrib.auth import get_user_model

from core.models import Tenant, Meter, AggregatedReading
from accounts.models import TenantMembership
from billing.models import CommunityTariff, CommunityMonthlyStatement
from billing.services_sharing_settlement import (
    get_effective_tariff_prices_for_slot,
    calculate_monthly_community_statements,
)
from billing.services_mscons import (
    generate_community_mscons_export,
    parse_mscons_payload,
    import_mscons_to_database,
)

User = get_user_model()


class DynamicTariffAndMsconsTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="settlement_test@sharegy.cloud",
            email="settlement_test@sharegy.cloud",
            password="securePassword123!",
        )
        self.tenant = Tenant.objects.create(
            name="Quartier Sonnenfeld",
            slug="quartier-sonnenfeld",
        )
        self.membership = TenantMembership.objects.create(
            tenant=self.tenant,
            user=self.user,
            role="member",
            is_active=True,
        )
        self.meter = Meter.objects.create(
            tenant=self.tenant,
            serial_number="1EMH0012345678",
            meter_type="electricity",
            owner_membership=self.membership,
        )

    def test_spot_indexed_tariff_price_calculation(self):
        """Testet die dynamische Preisberechnung mit Börsenpreis, Aufschlag, Cap & Floor."""
        tariff = CommunityTariff.objects.create(
            tenant=self.tenant,
            name="Dynamischer Börsentarif",
            pricing_model=CommunityTariff.PRICING_MODEL_SPOT_INDEXED,
            sharing_price_ct_kwh=Decimal("12.00"),
            spot_markup_ct_kwh=Decimal("3.50"),
            spot_floor_price_ct_kwh=Decimal("5.00"),
            spot_cap_price_ct_kwh=Decimal("30.00"),
            feed_in_spot_share_pct=Decimal("80.00"),
            grid_fee_saved_ct_kwh=Decimal("1.00"),
            community_fee_ct_kwh=Decimal("2.00"),
            is_active=True,
        )

        now_dt = timezone.now()

        # Fall A: Normaler Börsenpreis = 10.00 Ct/kWh
        # Bezug = 10.00 + 3.50 - 1.00 = 12.50 Ct/kWh
        # Einspeisung = 10.00 * 0.80 = 8.00 Ct/kWh
        p_in, p_out, p_fee = get_effective_tariff_prices_for_slot(
            tariff, now_dt, spot_price_ct_kwh=Decimal("10.00")
        )
        self.assertEqual(p_in, Decimal("12.50"))
        self.assertEqual(p_out, Decimal("8.00"))
        self.assertEqual(p_fee, Decimal("2.00"))

        # Fall B: Negativer / sehr niedriger Börsenpreis = -2.00 Ct/kWh
        # Ungebremst: -2.00 + 3.50 - 1.00 = 0.50 Ct/kWh -> greift Floor von 5.00 Ct/kWh!
        p_in_floor, p_out_floor, _ = get_effective_tariff_prices_for_slot(
            tariff, now_dt, spot_price_ct_kwh=Decimal("-2.00")
        )
        self.assertEqual(p_in_floor, Decimal("5.00"))
        self.assertEqual(p_out_floor, Decimal("0.00"))

        # Fall C: Extrem hoher Börsenpreis = 50.00 Ct/kWh
        # Ungebremst: 50.00 + 3.50 - 1.00 = 52.50 Ct/kWh -> greift Cap von 30.00 Ct/kWh!
        p_in_cap, p_out_cap, _ = get_effective_tariff_prices_for_slot(
            tariff, now_dt, spot_price_ct_kwh=Decimal("50.00")
        )
        self.assertEqual(p_in_cap, Decimal("30.00"))
        self.assertEqual(p_out_cap, Decimal("40.00"))

    def test_time_of_use_tariff_calculation(self):
        """Testet den Tag-/Nachttarif (HT / NT)."""
        tariff = CommunityTariff.objects.create(
            tenant=self.tenant,
            name="Zeittarif HT/NT",
            pricing_model=CommunityTariff.PRICING_MODEL_TIME_OF_USE,
            sharing_price_ct_kwh=Decimal("20.00"),
            producer_payout_ct_kwh=Decimal("10.00"),
            is_active=True,
        )

        day_dt = datetime(2026, 9, 1, 14, 0)
        night_dt = datetime(2026, 9, 1, 3, 0)

        # Tag (HT): Voller Preis
        p_in_ht, p_out_ht, _ = get_effective_tariff_prices_for_slot(tariff, day_dt)
        self.assertEqual(p_in_ht, Decimal("20.00"))
        self.assertEqual(p_out_ht, Decimal("10.00"))

        # Nacht (NT): 20% Rabatt (16.00 Ct), 10% Abschlag (9.00 Ct)
        p_in_nt, p_out_nt, _ = get_effective_tariff_prices_for_slot(tariff, night_dt)
        self.assertEqual(p_in_nt, Decimal("16.00"))
        self.assertEqual(p_out_nt, Decimal("9.00"))

    def test_mscons_generation_and_export(self):
        """Testet die Erzeugung eines validen EDIFACT MSCONS Datenstroms."""
        # 15-Minuten-Messwerte anlegen
        dt1 = timezone.make_aware(datetime(2026, 8, 1, 12, 0))
        dt2 = timezone.make_aware(datetime(2026, 8, 1, 12, 15))

        AggregatedReading.objects.create(
            tenant=self.tenant,
            meter=self.meter,
            obis_code="1.8.0",
            period_start=dt1,
            period_end=dt2,
            value=Decimal("1.250"),
            unit="kWh",
        )
        AggregatedReading.objects.create(
            tenant=self.tenant,
            meter=self.meter,
            obis_code="2.8.0",
            period_start=dt1,
            period_end=dt2,
            value=Decimal("4.500"),
            unit="kWh",
        )

        mscons_edi = generate_community_mscons_export(
            tenant=self.tenant,
            period_start=date(2026, 8, 1),
            period_end=date(2026, 8, 1),
            sender_mp_id="9901234567890",
            receiver_mp_id="9909876543210",
        )

        # Prüfe EDIFACT Segmente
        self.assertIn("UNA:+.? '", mscons_edi)
        self.assertIn("UNB+UNOC:3+9901234567890:500+9909876543210:500+", mscons_edi)
        self.assertIn("UNH+1+MSCONS:D:04B:UN:EAN008'", mscons_edi)
        self.assertIn(f"LOC+172+{self.meter.serial_number}'", mscons_edi)
        self.assertIn("PIA+5+1-1?:1.8.0:SRX'", mscons_edi)
        self.assertIn("QTY+220:1.250:KWH'", mscons_edi)
        self.assertIn("PIA+5+1-1?:2.8.0:SRX'", mscons_edi)
        self.assertIn("QTY+220:4.500:KWH'", mscons_edi)
        self.assertIn("UNT+", mscons_edi)
        self.assertIn("UNZ+1+", mscons_edi)

    def test_mscons_import_and_parsing(self):
        """Testet das Parsen und den Datenbankimport einer MSCONS-Datei."""
        edi_sample = (
            "UNA:+.? '"
            "UNB+UNOC:3+9909876543210:500+9901234567890:500+260801:1400+MSG001++MSCONS'"
            "UNH+1+MSCONS:D:04B:UN:EAN008'"
            "BGM+E03+DOC123+9'"
            "NAD+MS+9909876543210::293'"
            "LOC+172+1EMH0012345678'"
            "PIA+5+1-1?:1.8.0:SRX'"
            "QTY+220:2.750:KWH'"
            "DTM+163:202608011400:203'"
            "UNT+9+1'"
            "UNZ+1+MSG001'"
        )

        parsed = parse_mscons_payload(edi_sample)
        self.assertEqual(len(parsed), 1)
        self.assertEqual(parsed[0]["malo_id"], "1EMH0012345678")
        self.assertEqual(parsed[0]["obis_code"], "1.8.0")
        self.assertEqual(parsed[0]["value"], Decimal("2.750"))

        # Datenbank-Import
        res = import_mscons_to_database(self.tenant, edi_sample)
        self.assertTrue(res["success"])
        self.assertEqual(res["imported_count"], 1)

        reading = AggregatedReading.objects.get(
            meter=self.meter,
            obis_code="1.8.0",
            period_start=timezone.make_aware(datetime(2026, 8, 1, 14, 0)),
        )
        self.assertEqual(reading.value, Decimal("2.750"))
