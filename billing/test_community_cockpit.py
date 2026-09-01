##########################################
# billing/test_community_cockpit.py
##########################################

from decimal import Decimal
from datetime import timedelta
from django.test import TestCase
from django.utils import timezone
from rest_framework.test import APIClient

from accounts.models import User, TenantMembership
from core.models import Tenant, Meter, BalanceSlot
from forecast.models import SolarForecast


class CommunityCockpitTests(TestCase):
    def setUp(self):
        self.client = APIClient()

        # 1. Tenants erstellen
        self.tenant_a = Tenant.objects.create(name="Bonn-Share Solar", slug="bonn-share")
        self.tenant_b = Tenant.objects.create(name="Köln-West Solar", slug="koeln-west")

        # 2. User & Memberships
        self.user_a = User.objects.create_user(
            email="member_bonn@example.com", username="member_bonn", password="password123"
        )
        self.user_b = User.objects.create_user(
            email="member_koeln@example.com", username="member_koeln", password="password123"
        )

        self.membership_a = TenantMembership.objects.create(
            user=self.user_a, tenant=self.tenant_a, role="member", is_active=True
        )
        self.membership_b = TenantMembership.objects.create(
            user=self.user_b, tenant=self.tenant_b, role="member", is_active=True
        )

        # 3. Zähler anlegen
        self.meter_prod = Meter.objects.create(
            tenant=self.tenant_a,
            serial_number="METER-PROD-01",
            owner_membership=self.membership_a,
        )
        self.meter_cons = Meter.objects.create(
            tenant=self.tenant_a,
            serial_number="METER-CONS-01",
            owner_membership=self.membership_a,
        )

        # 4. 15-Minuten-Slots für Heute simulieren
        now = timezone.now()
        slot_1 = now - timedelta(minutes=15)
        slot_1 = slot_1.replace(minute=(slot_1.minute // 15) * 15, second=0, microsecond=0)

        # Producer erzeugt 10 kWh
        BalanceSlot.objects.create(
            meter=self.meter_prod,
            tenant=self.tenant_a,
            period_start=slot_1,
            consumption_kwh=Decimal("0.0"),
            generation_kwh=Decimal("10.0"),
            self_consumption_kwh=Decimal("0.0"),
            grid_import_kwh=Decimal("0.0"),
            grid_export_kwh=Decimal("10.0"),
        )

        # Consumer verbraucht 6 kWh
        BalanceSlot.objects.create(
            meter=self.meter_cons,
            tenant=self.tenant_a,
            period_start=slot_1,
            consumption_kwh=Decimal("6.0"),
            generation_kwh=Decimal("0.0"),
            self_consumption_kwh=Decimal("0.0"),
            grid_import_kwh=Decimal("6.0"),
            grid_export_kwh=Decimal("0.0"),
        )

        # 5. 48h-Prognose anlegen
        from devices.models import Home
        from producer.models import GeneratorSystem, GeneratorString, Orientation

        orient, _ = Orientation.objects.get_or_create(key="s", defaults={"name": "Süd", "azimuth_deg": 180})
        home = Home.objects.create(user=self.user_a, name="Bonn Solar Home")
        gen_sys = GeneratorSystem.objects.create(home=home, name="PV Roof System")
        gen_str = GeneratorString.objects.create(
            generator=gen_sys,
            name="String 1",
            peak_power_kwp=Decimal("5.0"),
            orientation=orient,
        )

        SolarForecast.objects.create(
            generator_string=gen_str,
            timestamp=now + timedelta(hours=2),
            forecast_kwh=Decimal("4.5"),
            source="hybrid",
        )

    def test_community_cockpit_authenticated(self):
        """Prüft korrekte Aggregation von Erzeugung, Verbrauch, Sharing und Prognosen."""
        self.client.force_authenticate(user=self.user_a)
        response = self.client.get(
            "/api/billing/community/cockpit/",
            HTTP_X_TENANT_ID=str(self.tenant_a.id),
        )
        self.assertEqual(response.status_code, 200)
        data = response.data

        # Community-Header
        self.assertEqual(data["community"]["name"], "Bonn-Share Solar")
        self.assertEqual(data["community"]["meters_count"], 2)

        # Kennzahlen: 10 kWh erzeugt, 6 kWh verbraucht -> 6 kWh geteilt (100% Autarkie)
        today = data["today"]
        self.assertEqual(today["produced_kwh"], 10.0)
        self.assertEqual(today["consumed_kwh"], 6.0)
        self.assertEqual(today["shared_kwh"], 6.0)
        self.assertEqual(today["grid_export_kwh"], 4.0)
        self.assertEqual(today["autarky_pct"], 100.0)
        self.assertGreater(today["savings_eur"], 0)

        # 48h Prognose
        self.assertGreaterEqual(len(data["forecast_48h"]["hours"]), 1)
        self.assertEqual(data["forecast_48h"]["hours"][0]["power_kw"], 4.5)

    def test_community_cockpit_isolation(self):
        """Mitglied von Köln darf Bonn-Cockpit nicht abrufen."""
        self.client.force_authenticate(user=self.user_b)
        response = self.client.get(
            "/api/billing/community/cockpit/",
            HTTP_X_TENANT_ID=str(self.tenant_a.id),
        )
        self.assertEqual(response.status_code, 403)
