"""
devices/tests_self_test.py

Unit- und Integrationstests für den 1-Klick Hardware-Selbsttest.
"""

from django.test import TestCase
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient

from devices.models import Home, Device, DeviceConfig, MetricDefinition, DeviceLatestMetric
from devices.services_self_test import run_device_self_test

User = get_user_model()


class DeviceSelfTestTestCase(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            email="selftest@sharegy.de",
            username="selftest_user",
            password="testpassword123",
        )
        self.home = Home.objects.create(
            user=self.user,
            name="Test Solar Home",
            city="Berlin",
            postal_code="10115",
        )
        self.device = Device.objects.create(
            home=self.home,
            identifier="sungrow_inverter_01",
            configured=True,
        )
        self.config = DeviceConfig.objects.create(
            device=self.device,
            home=self.home,
            name="Sungrow Hybrid SH10RT",
        )
        from django.utils import timezone
        self.latest_metric = DeviceLatestMetric.objects.create(
            device=self.device,
            metric_key="power_w",
            value=4850.5,
            unit="W",
            timestamp=timezone.now(),
        )
        self.client = APIClient()

    def test_01_service_self_test_with_device(self):
        """Testet den Selbsttest-Service direkt mit einem echten Gerät."""
        res = run_device_self_test(device=self.device)
        self.assertEqual(res["status"], "success")
        self.assertEqual(res["device_id"], self.device.id)
        self.assertIn("Sungrow Hybrid SH10RT", res["device_name"])
        self.assertGreaterEqual(res["health_score"], 90)
        self.assertEqual(len(res["steps"]), 3)

        # Schritt 1: Connectivity
        self.assertEqual(res["steps"][0]["step"], "connectivity")
        self.assertIn("latency_ms", res["steps"][0])

        # Schritt 2: Telemetry
        self.assertEqual(res["steps"][1]["step"], "telemetry")
        self.assertEqual(res["steps"][1]["live_metrics"]["power_w"], 4850.5)

        # Schritt 3: Control Loop
        self.assertEqual(res["steps"][2]["step"], "control_loop")
        self.assertTrue(res["steps"][2]["dispatch_ready"])

    def test_02_service_self_test_simulation(self):
        """Testet den Simulator-Modus ohne persistiertes Gerät."""
        res = run_device_self_test(device=None, mock_profile_id="huawei_fusionsolar")
        self.assertEqual(res["status"], "success")
        self.assertIsNone(res["device_id"])
        self.assertGreaterEqual(res["health_score"], 90)
        self.assertEqual(len(res["steps"]), 3)

    def test_03_api_self_test_endpoint(self):
        """Testet den REST-Endpoint /api/devices/<id>/self-test/."""
        resp = self.client.post(f"/api/devices/{self.device.id}/self-test/")
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.data["status"], "success")
        self.assertEqual(resp.data["device_id"], self.device.id)
        self.assertIn("steps", resp.data)

    def test_04_api_self_test_simulate_endpoint(self):
        """Testet den REST-Endpoint /api/devices/self-test/simulate/."""
        resp = self.client.post("/api/devices/self-test/simulate/", {"profile_id": "deye_solarman"}, format="json")
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.data["status"], "success")
        self.assertGreaterEqual(resp.data["health_score"], 90)
