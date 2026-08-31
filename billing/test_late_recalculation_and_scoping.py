####################################################
# billing/test_late_recalculation_and_scoping.py
####################################################

from decimal import Decimal
from datetime import timedelta
from django.test import TestCase
from django.utils import timezone
from rest_framework.test import APIClient

from accounts.models import User, TenantMembership
from core.models import Tenant, Meter, IntervalReading, AggregatedReading, BalanceSlot
from billing.models import UserMeterAssignment, UserBalanceSlot
from core.services_validation import validate_obis_reading
from billing.services_balance import recalculate_meter_slot
from billing.tasks import recalculate_late_slot, reconcile_balance_last_30d


class LateRecalculationAndTenantScopingTests(TestCase):
    def setUp(self):
        self.client = APIClient()

        # 1. Tenants erstellen
        self.tenant_a = Tenant.objects.create(name="Community A", slug="community-a")
        self.tenant_b = Tenant.objects.create(name="Community B", slug="community-b")

        # 2. User & Memberships
        self.admin_user = User.objects.create_user(
            email="admin_a@example.com", username="admin_a", password="password123"
        )
        self.member_user = User.objects.create_user(
            email="member_a@example.com", username="member_a", password="password123"
        )
        self.other_user = User.objects.create_user(
            email="admin_b@example.com", username="admin_b", password="password123"
        )

        self.membership_admin_a = TenantMembership.objects.create(
            user=self.admin_user, tenant=self.tenant_a, role="admin", is_active=True
        )
        self.membership_member_a = TenantMembership.objects.create(
            user=self.member_user, tenant=self.tenant_a, role="member", is_active=True
        )
        self.membership_admin_b = TenantMembership.objects.create(
            user=self.other_user, tenant=self.tenant_b, role="admin", is_active=True
        )

        # 3. Zähler für Tenant A und Tenant B anlegen
        self.meter_a1 = Meter.objects.create(
            tenant=self.tenant_a,
            serial_number="METER-A1-COMMUNITY",
            owner_membership=self.membership_admin_a,
        )
        self.meter_a2 = Meter.objects.create(
            tenant=self.tenant_a,
            serial_number="METER-A2-MEMBER",
            owner_membership=self.membership_member_a,
        )
        self.meter_b1 = Meter.objects.create(
            tenant=self.tenant_b,
            serial_number="METER-B1-OTHER",
            owner_membership=self.membership_admin_b,
        )

        # User-Meter Zuweisung
        UserMeterAssignment.objects.create(
            user=self.member_user,
            meter=self.meter_a2,
            valid_from=timezone.now() - timedelta(days=60),
            is_active=True,
        )

    def test_obis_reading_validation(self):
        """Prüft Plausibilitätsregeln für OBIS 1.8.0 / 2.8.0."""
        # Gültiger Wert
        res_ok = validate_obis_reading("1.8.0", Decimal("3.450"), "kWh")
        self.assertTrue(res_ok["is_valid"])

        # Negativer Wert (ungültig)
        res_neg = validate_obis_reading("1.8.0", Decimal("-1.200"), "kWh")
        self.assertFalse(res_neg["is_valid"])
        self.assertIn("negative_energy", res_neg["flags"])

        # Extremspitze (> 250 kWh / 15m)
        res_spike = validate_obis_reading("2.8.0", Decimal("350.000"), "kWh")
        self.assertTrue(res_spike["is_valid"])
        self.assertIn("high_spike", res_spike["flags"])

    def test_tenant_admin_meter_scoping(self):
        """Tenant-Admin A sieht alle Zähler von Community A, aber keine von Community B."""
        self.client.force_authenticate(user=self.admin_user)
        response = self.client.get(
            "/api/meters/",
            HTTP_X_TENANT_ID=str(self.tenant_a.id),
        )
        self.assertEqual(response.status_code, 200)
        data = response.data if isinstance(response.data, list) else response.data.get("results", [])
        serials = [m["serial_number"] for m in data]
        self.assertIn("METER-A1-COMMUNITY", serials)
        self.assertIn("METER-A2-MEMBER", serials)
        self.assertNotIn("METER-B1-OTHER", serials)

    def test_tenant_member_meter_scoping(self):
        """Reguläres Mitglied A sieht nur seinen eigenen Zähler in Community A."""
        self.client.force_authenticate(user=self.member_user)
        response = self.client.get(
            "/api/meters/",
            HTTP_X_TENANT_ID=str(self.tenant_a.id),
        )
        self.assertEqual(response.status_code, 200)
        data = response.data if isinstance(response.data, list) else response.data.get("results", [])
        serials = [m["serial_number"] for m in data]
        self.assertNotIn("METER-A1-COMMUNITY", serials)
        self.assertIn("METER-A2-MEMBER", serials)
        self.assertNotIn("METER-B1-OTHER", serials)

    def test_cross_tenant_isolation(self):
        """Tenant-Admin B darf Zähler von Community A nicht über API abrufen."""
        self.client.force_authenticate(user=self.other_user)
        response = self.client.get(
            f"/api/meters/{self.meter_a1.id}/",
            HTTP_X_TENANT_ID=str(self.tenant_b.id),
        )
        self.assertEqual(response.status_code, 404)

    def test_late_slot_recalculation(self):
        """Prüft, dass verspätet eintreffende 15m-Zählerwerte die Bilanzen sauber nachberechnen."""
        slot_time = timezone.now() - timedelta(days=3)  # 3 Tage in der Vergangenheit (> 24h)
        slot_time = slot_time.replace(minute=(slot_time.minute // 15) * 15, second=0, microsecond=0)

        # 1. IntervalReading für Verbrauch (1.8.0) und Erzeugung (2.8.0) anlegen
        IntervalReading.objects.create(
            meter=self.meter_a2,
            tenant=self.tenant_a,
            obis_code="1.8.0",
            ts_start=slot_time,
            ts_end=slot_time + timedelta(minutes=15),
            value=Decimal("5.000"),
            is_late=True,
        )
        IntervalReading.objects.create(
            meter=self.meter_a2,
            tenant=self.tenant_a,
            obis_code="2.8.0",
            ts_start=slot_time,
            ts_end=slot_time + timedelta(minutes=15),
            value=Decimal("2.000"),
            is_late=True,
        )

        # 2. Late Recalculation ausführen
        result = recalculate_late_slot(str(self.meter_a2.id), slot_time.isoformat())
        self.assertEqual(result["status"], "ok")

        # 3. BalanceSlot prüfen
        slot = BalanceSlot.objects.filter(meter=self.meter_a2, period_start=slot_time).first()
        self.assertIsNotNone(slot)
        self.assertEqual(slot.consumption_kwh, Decimal("5.000"))
        self.assertEqual(slot.generation_kwh, Decimal("2.000"))
        self.assertEqual(slot.self_consumption_kwh, Decimal("2.000"))
        self.assertEqual(slot.grid_import_kwh, Decimal("3.000"))
        self.assertEqual(slot.grid_export_kwh, Decimal("0.000"))

        # 4. UserBalanceSlot prüfen
        user_slot = UserBalanceSlot.objects.filter(
            user=self.member_user, meter=self.meter_a2, period_start=slot_time
        ).first()
        self.assertIsNotNone(user_slot)
        self.assertEqual(user_slot.consumption_kwh, Decimal("5.000"))
        self.assertEqual(user_slot.grid_import_kwh, Decimal("3.000"))

    def test_reconcile_balance_last_30d_task(self):
        """Prüft die fehlerfreie Ausführung des 30-Tage Reconcile-Tasks."""
        res = reconcile_balance_last_30d()
        self.assertEqual(res["status"], "ok")


