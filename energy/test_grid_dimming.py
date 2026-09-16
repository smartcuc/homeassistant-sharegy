"""
energy/test_grid_dimming.py

Unit-Tests für § 14a EnWG Steuerbox- & Dimm-Engine nach dem BNetzA-Summenleistungsmodell.
"""

from decimal import Decimal
from django.test import TestCase
from django.utils import timezone
from rest_framework.test import APIClient

from accounts.models import User
from core.models import Tenant
from devices.models import Home, Device, DeviceRole, DeviceLatestMetric
from energy.models import GridDimmingSignal, SteuVEDeviceConfig
from energy.services_dimming import (
    trigger_grid_dimming,
    clear_grid_dimming,
    evaluate_home_power_budget,
    get_active_dimming_signal,
)


class GridDimmingEngineTestCase(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(username="grid@sharegy.de", email="grid@sharegy.de", password="pw")
        self.tenant = Tenant.objects.create(name="Smart Grid Test Quartier", slug="smart-grid-test")
        self.home = Home.objects.create(name="Musterhaus EnWG", user=self.user)

        # Rollen
        self.role_wb = DeviceRole.objects.create(key="wallbox", label="Wallbox")
        self.role_hp = DeviceRole.objects.create(key="heat_pump", label="Wärmepumpe")
        self.role_pv = DeviceRole.objects.create(key="pv_inverter", label="PV Wechselrichter")

        # 1. SteuVE Wallbox (11 kW Nennleistung, Prio 3 = nachrangig dimmbar)
        self.dev_wb = Device.objects.create(home=self.home, identifier="easee-wb-01", active=True)
        from devices.models import DeviceConfig
        DeviceConfig.objects.create(device=self.dev_wb, home=self.home, name="Easee Wallbox Garage", role=self.role_wb)
        self.steuve_wb = SteuVEDeviceConfig.objects.create(
            device=self.dev_wb,
            steuve_type="wallbox",
            rated_power_kw=Decimal("11.00"),
            minimum_power_kw=Decimal("1.40"),
            priority=3,
        )

        # 2. SteuVE Wärmepumpe (6 kW Nennleistung, Prio 1 = höchste Priorität)
        self.dev_hp = Device.objects.create(home=self.home, identifier="viessmann-hp-01", active=True)
        DeviceConfig.objects.create(device=self.dev_hp, home=self.home, name="Viessmann Wärmepumpe", role=self.role_hp)
        self.steuve_hp = SteuVEDeviceConfig.objects.create(
            device=self.dev_hp,
            steuve_type="heat_pump",
            rated_power_kw=Decimal("6.00"),
            minimum_power_kw=Decimal("2.00"),
            priority=1,
        )

        # 3. PV Anlage
        self.dev_pv = Device.objects.create(home=self.home, identifier="fronius-pv-01", active=True)
        DeviceConfig.objects.create(device=self.dev_pv, home=self.home, name="Fronius PV Inverter", role=self.role_pv)
        DeviceLatestMetric.objects.create(
            device=self.dev_pv,
            metric_key="power_w",
            value=5000.0,
            timestamp=timezone.now()
        )

    def test_sum_power_budget_calculation(self):
        """Prüft die Budgetberechnung: P_allow = 4,2 kW (Netz) + 5,0 kW (PV) = 9,2 kW."""
        signal = trigger_grid_dimming(
            home=self.home,
            source="vnb_api",
            target_max_kw=Decimal("4.20"),
            duration_minutes=120,
        )

        budget = evaluate_home_power_budget(self.home)
        self.assertTrue(budget["is_dimmed"])
        self.assertEqual(budget["max_grid_kw"], 4.2)
        self.assertEqual(budget["current_pv_gen_kw"], 5.0)
        # 4,2 kW + 5,0 kW PV = 9,2 kW Gesamtlaufleistung
        self.assertEqual(budget["allowed_steuve_budget_kw"], 9.2)

        # SteuVE-Drosselungen prüfen
        self.steuve_hp.refresh_from_db()
        self.steuve_wb.refresh_from_db()

        # Wärmepumpe (Prio 1, 6 kW) bekommt volles Kontingent (6 kW <= 9,2 kW) -> NICHT gedimmt
        self.assertFalse(self.steuve_hp.is_currently_dimmed)
        self.assertEqual(self.steuve_hp.current_power_limit_kw, Decimal("6.00"))

        # Wallbox (Prio 3, 11 kW) bekommt das Restbudget (9,2 - 6,0 = 3,2 kW) -> GEDIMMT auf 3,2 kW
        self.assertTrue(self.steuve_wb.is_currently_dimmed)
        self.assertEqual(self.steuve_wb.current_power_limit_kw, Decimal("3.20"))

    def test_clear_grid_dimming(self):
        """Prüft das Aufheben eines Dimmsignals und Wiederherstellen des Normalbetriebs."""
        trigger_grid_dimming(home=self.home, source="manual_test")
        self.assertIsNotNone(get_active_dimming_signal(home=self.home))

        clear_res = clear_grid_dimming(self.home)
        self.assertEqual(clear_res["status"], "cleared")
        self.assertIsNone(get_active_dimming_signal(home=self.home))

        self.steuve_wb.refresh_from_db()
        self.assertFalse(self.steuve_wb.is_currently_dimmed)
        self.assertIsNone(self.steuve_wb.current_power_limit_kw)

    def test_inbound_webhook_and_status_api(self):
        """Prüft Inbound-Webhook und Status-API."""
        # 1. Inbound Webhook vom VNB
        res_webhook = self.client.post("/api/energy/grid/dimming/signal/", {
            "home_id": str(self.home.id),
            "source": "vnb_api",
            "target_max_grid_kw": "4.20",
            "duration_minutes": 60,
        }, format="json")

        self.assertEqual(res_webhook.status_code, 201)
        self.assertTrue(res_webhook.data["is_active"])

        # 2. Status API abrufen
        self.client.force_authenticate(user=self.user)
        res_status = self.client.get(f"/api/energy/grid/dimming/status/?home_id={self.home.id}")
        self.assertEqual(res_status.status_code, 200)
        self.assertTrue(res_status.data["budget"]["is_dimmed"])
        self.assertEqual(len(res_status.data["steuve_devices"]), 2)

        # 3. Clear Webhook
        res_clear = self.client.post("/api/energy/grid/dimming/signal/", {
            "home_id": str(self.home.id),
            "action": "clear",
        }, format="json")
        self.assertEqual(res_clear.status_code, 200)
        self.assertEqual(res_clear.data["status"], "cleared")

    def test_audit_logging_lifecycle(self):
        """Prüft die lückenlose Erstellung von Revisions-Audit-Logs für VNB-Nachweise."""
        from energy.models import EnWG14aDimmingAuditLog

        # 1. Dimming auslösen
        signal = trigger_grid_dimming(
            home=self.home,
            source="vnb_api",
            target_max_kw=Decimal("4.20"),
            duration_minutes=60,
        )

        # Audit Logs prüfen: DIMMING_TRIGGERED + SteuVE Einträge
        triggered_log = EnWG14aDimmingAuditLog.objects.filter(home=self.home, action="DIMMING_TRIGGERED").first()
        self.assertIsNotNone(triggered_log)
        self.assertEqual(triggered_log.signal, signal)
        self.assertEqual(triggered_log.commanded_power_limit_kw, Decimal("4.20"))
        self.assertTrue(triggered_log.compliance_verified)

        dimmed_wb_log = EnWG14aDimmingAuditLog.objects.filter(home=self.home, device=self.dev_wb, action="DEVICE_DIMMED").first()
        self.assertIsNotNone(dimmed_wb_log)
        self.assertEqual(dimmed_wb_log.commanded_power_limit_kw, Decimal("3.20"))
        self.assertTrue(dimmed_wb_log.response_time_ms > 0)

        # 2. Dimming aufheben
        clear_grid_dimming(self.home)

        cleared_log = EnWG14aDimmingAuditLog.objects.filter(home=self.home, action="LIMIT_CLEARED").first()
        self.assertIsNotNone(cleared_log)

        restored_wb_log = EnWG14aDimmingAuditLog.objects.filter(home=self.home, device=self.dev_wb, action="DEVICE_RESTORED").first()
        self.assertIsNotNone(restored_wb_log)
        self.assertEqual(restored_wb_log.commanded_power_limit_kw, Decimal("11.00"))

    def test_cls_smgw_api_lifecycle(self):
        """Prüft den BNetzA CLS-Kanal (/api/energy/cls/*) mit VNB-Quittierung und Statusabfrage."""
        self.client.force_authenticate(user=self.user)

        # 1. CLS Dimm-Befehl Ingest (BSI TR-03109-1 konform)
        res_signal = self.client.post("/api/energy/cls/signal/", {
            "home_id": str(self.home.id),
            "target_max_grid_kw": "4.20",
            "duration_minutes": 90,
            "sender": "Netzleitstelle VNB Rheinland CLS-Proxy",
            "signal_reason": "§ 14a EnWG Engpass-Drosselung",
        }, format="json")

        self.assertEqual(res_signal.status_code, 200)
        self.assertEqual(res_signal.data["status"], "acknowledged")
        self.assertEqual(res_signal.data["protocol"], "BSI-TR-03109-1 / FNN-Steuerbox CLS")
        self.assertEqual(res_signal.data["target_max_grid_kw"], 4.2)
        self.assertEqual(res_signal.data["steuve_affected_count"], 2)

        # 2. CLS Status abrufen
        res_status = self.client.get(f"/api/energy/cls/status/?home_id={self.home.id}")
        self.assertEqual(res_status.status_code, 200)
        self.assertTrue(res_status.data["is_dimmed"])
        self.assertEqual(len(res_status.data["steuve_devices"]), 2)
        self.assertTrue(len(res_status.data["recent_audit_log"]) > 0)

        # 3. CLS Drosselung aufheben (Clear)
        res_clear = self.client.post("/api/energy/cls/clear/", {
            "home_id": str(self.home.id),
            "notes": "Netzengpass behoben.",
        }, format="json")

        self.assertEqual(res_clear.status_code, 200)
        self.assertEqual(res_clear.data["status"], "cleared")

        # 4. Status nach Clear prüfen
        res_status_after = self.client.get(f"/api/energy/cls/status/?home_id={self.home.id}")
        self.assertFalse(res_status_after.data["is_dimmed"])

