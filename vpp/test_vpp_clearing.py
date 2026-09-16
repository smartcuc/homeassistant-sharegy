"""
vpp/test_vpp_clearing.py

Umfassende Test-Suite für VPP Flexibility Enrollment, Automated Market Clearing,
80/20 Revenue Splits, Periodic Clearing Runs und Webhook-Dispatching.
"""

from decimal import Decimal
from datetime import date, timedelta
from django.test import TestCase
from django.contrib.auth import get_user_model
from django.utils import timezone

from devices.models import Home, Device, DeviceRole, DeviceConfig, DeviceLatestMetric
from energy.models import SteuVEDeviceConfig
from vpp.models import (
    VPPFlexibilityPool,
    VPPDispatchOrder,
    VPPAssetEnrollment,
    VPPAssetDispatch,
    VPPClearingStatement,
)
from vpp.services_clearing import (
    enroll_device_in_vpp,
    set_enrollment_status,
    allocate_and_clear_dispatch,
    execute_periodic_clearing_run,
    get_user_flexibility_summary,
)
from vpp.services_vpp import trigger_vpp_dispatch

User = get_user_model()


class VPPClearingAndSettlementTests(TestCase):
    def setUp(self):
        # 1. Test User anlegen
        self.user = User.objects.create_user(
            username="prosumer_clearing",
            email="clearing@sharegy.cloud",
            password="securepassword123",
        )
        self.staff_user = User.objects.create_user(
            username="vpp_staff",
            email="staff@sharegy.cloud",
            password="securepassword123",
            is_staff=True,
        )

        self.home = Home.objects.create(user=self.user, name="Clearing Prosumer Home", postal_code="10115")

        # 2. Rolle & Device anlegen
        self.battery_role, _ = DeviceRole.objects.get_or_create(key="battery", defaults={"label": "Batterie"})
        
        self.battery_device = Device.objects.create(
            home=self.home,
            identifier="BAT-CLEAR-001",
            active=True,
            configured=True,
        )
        self.device_config = DeviceConfig.objects.create(
            device=self.battery_device,
            home=self.home,
            role=self.battery_role,
            name="Alpha ESS Smile-Hi10",
        )

        # 3. Metriken setzen (10 kWh Kapazität, 80% SoC)
        now = timezone.now()
        DeviceLatestMetric.objects.create(device=self.battery_device, metric_key="soc", value=80.0, timestamp=now)
        DeviceLatestMetric.objects.create(device=self.battery_device, metric_key="capacity_kwh", value=10.0, timestamp=now)
        DeviceLatestMetric.objects.create(device=self.battery_device, metric_key="max_power_kw", value=5.0, timestamp=now)

        # 4. VPP Pool
        self.pool = VPPFlexibilityPool.objects.create(
            name="50Hertz Heimspeicher Pool",
            tso_operator="50hertz",
            market_product="afrr_positive",
            min_activation_power_kw=Decimal("1.0"),
            max_activation_power_kw=Decimal("100.0"),
            is_active=True,
        )

    def test_enroll_device_in_vpp(self):
        """Prüft die Registrierung eines Geräts im VPP und Validierung der Parameter."""
        enrollment = enroll_device_in_vpp(
            user=self.user,
            device_id=self.battery_device.id,
            pool_id=str(self.pool.id),
            min_soc_reserve_pct=Decimal("25.00"),
        )
        self.assertEqual(enrollment.status, "active")
        self.assertEqual(enrollment.min_soc_reserve_pct, Decimal("25.00"))
        self.assertEqual(enrollment.payout_share_pct, Decimal("80.00"))
        self.assertEqual(enrollment.pool, self.pool)

    def test_allocate_and_clear_dispatch_revenue_split(self):
        """Prüft die Zuweisung von Erlösen mit 80/20 Split beim VPP-Dispatch."""
        enrollment = enroll_device_in_vpp(
            user=self.user,
            device_id=self.battery_device.id,
            pool_id=str(self.pool.id),
            min_soc_reserve_pct=Decimal("20.00"),
        )

        # Dispatch auslösen (50 kW für 15 Minuten)
        order = trigger_vpp_dispatch(
            target_power_kw=Decimal("50.0"),
            duration_minutes=15,
            dispatch_type="positive_flex",
            pool=self.pool,
        )

        # Überprüfen, ob VPPAssetDispatch erstellt wurde
        asset_dispatches = VPPAssetDispatch.objects.filter(dispatch_order=order)
        self.assertEqual(asset_dispatches.count(), 1)
        
        ad = asset_dispatches.first()
        self.assertEqual(ad.enrollment, enrollment)
        self.assertGreater(ad.gross_revenue_eur, Decimal("0.00"))
        self.assertGreater(ad.customer_payout_eur, Decimal("0.00"))
        self.assertGreater(ad.sharegy_fee_eur, Decimal("0.00"))

        # 80/20 Split verifizieren
        expected_customer = (ad.gross_revenue_eur * Decimal("0.80")).quantize(Decimal("0.01"))
        self.assertEqual(ad.customer_payout_eur, expected_customer)
        self.assertEqual(ad.gross_revenue_eur, ad.customer_payout_eur + ad.sharegy_fee_eur)

    def test_execute_periodic_clearing_run(self):
        """Prüft die Generierung von monatlichen VPPClearingStatements."""
        enrollment = enroll_device_in_vpp(
            user=self.user,
            device_id=self.battery_device.id,
            pool_id=str(self.pool.id),
        )

        # 2 Dispatches ausführen
        trigger_vpp_dispatch(target_power_kw=Decimal("20.0"), duration_minutes=15, pool=self.pool)
        trigger_vpp_dispatch(target_power_kw=Decimal("30.0"), duration_minutes=15, pool=self.pool)

        # Clearing Run starten
        statements = execute_periodic_clearing_run()
        self.assertEqual(len(statements), 1)

        stmt = statements[0]
        self.assertEqual(stmt.user, self.user)
        self.assertEqual(stmt.dispatches_count, 2)
        self.assertEqual(stmt.status, "credited")
        self.assertGreater(stmt.customer_payout_eur, Decimal("0.00"))

        # Alle Dispatches müssen jetzt is_cleared=True sein
        uncleared = VPPAssetDispatch.objects.filter(is_cleared=False)
        self.assertEqual(uncleared.count(), 0)

    def test_user_earnings_summary(self):
        """Prüft die zusammenfassenden Kennzahlen für das Frontend-Cockpit."""
        enroll_device_in_vpp(
            user=self.user,
            device_id=self.battery_device.id,
            pool_id=str(self.pool.id),
        )
        trigger_vpp_dispatch(target_power_kw=Decimal("25.0"), duration_minutes=15, pool=self.pool)
        execute_periodic_clearing_run()

        summary = get_user_flexibility_summary(self.user)
        self.assertTrue(summary["is_participating"])
        self.assertEqual(summary["active_devices_count"], 1)
        self.assertGreater(summary["total_earned_eur"], 0.0)
        self.assertEqual(len(summary["statements"]), 1)
        self.assertEqual(len(summary["recent_dispatches"]), 1)

    def test_rest_api_enrollments_and_earnings(self):
        """Prüft die REST-Endpunkte für Einschreibung, Dashboard und Aggregator Webhook."""
        self.client.force_login(self.user)

        # 1. Asset einschreiben
        resp = self.client.post("/api/vpp/enrollments/", {
            "device_id": self.battery_device.id,
            "min_soc_reserve_pct": "30.0",
        }, content_type="application/json")
        self.assertEqual(resp.status_code, 201)
        enrollment_id = resp.json()["enrollment_id"]

        # 2. Status abfragen
        resp_get = self.client.get("/api/vpp/enrollments/")
        self.assertEqual(resp_get.status_code, 200)
        self.assertTrue(resp_get.json()["is_participating"])

        # 3. Reserve SoC per PATCH ändern
        resp_patch = self.client.patch(f"/api/vpp/enrollments/{enrollment_id}/", {
            "min_soc_reserve_pct": "35.0",
        }, content_type="application/json")
        self.assertEqual(resp_patch.status_code, 200)
        self.assertEqual(resp_patch.json()["min_soc_reserve_pct"], 35.0)

        # 4. Earnings API
        resp_earnings = self.client.get("/api/vpp/earnings/")
        self.assertEqual(resp_earnings.status_code, 200)
        self.assertEqual(resp_earnings.json()["enrolled_devices_count"], 1)

        # 5. Aggregator Webhook (mit Token)
        self.client.logout()
        resp_webhook = self.client.post(
            "/api/vpp/aggregator/webhook/",
            {"target_power_kw": 40.0, "duration_minutes": 15},
            content_type="application/json",
            HTTP_X_VPP_API_KEY="sharegy-vpp-secure-key-2026",
        )
        self.assertEqual(resp_webhook.status_code, 202)
        self.assertEqual(resp_webhook.json()["status"], "accepted")
