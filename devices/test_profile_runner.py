"""
devices/test_profile_runner.py

Unit-Tests für die deklarative YAML-Profile-Engine (Sungrow iSolarCloud, SolarEdge, Fronius).
"""

from django.test import TestCase
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient

from devices.models import Home, Device, DeviceConfig, DeviceMetric, CloudDeviceIntegration
from devices.services_profile_runner import (
    load_profile,
    list_available_profiles,
    extract_jsonpath,
    test_cloud_credentials,
    execute_cloud_poll,
)
from devices.tasks import poll_cloud_integrations_task

User = get_user_model()


class ProfileRunnerTestCase(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="sungrow_tester",
            email="sungrow@sharegy.de",
            password="StrongTestPassword123!",
        )
        self.home = Home.objects.create(
            user=self.user,
            name="Test Villa",
            city="Berlin",
        )
        self.device = Device.objects.create(
            home=self.home,
            identifier="test-sungrow-sh10rt",
            configured=True,
            active=True,
        )
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)

    def test_01_load_sungrow_profile(self):
        """Testet das Laden und Parsen des Sungrow iSolarCloud YAML-Profils."""
        profile = load_profile("sungrow_isolarcloud")
        self.assertEqual(profile["id"], "sungrow_isolarcloud")
        self.assertEqual(profile["vendor"], "Sungrow")
        self.assertEqual(profile["protocol"], "http_cloud")
        self.assertIn("metrics_mapping", profile)
        self.assertIn("pv_power_w", profile["metrics_mapping"])
        self.assertEqual(profile["metrics_mapping"]["pv_power_w"]["scale"], 1000.0)

    def test_02_list_available_profiles(self):
        """Testet das Scannen aller verfügbaren YAML-Profile im Ordner."""
        profiles = list_available_profiles()
        profile_ids = [p["id"] for p in profiles]
        self.assertIn("sungrow_isolarcloud", profile_ids)
        self.assertIn("solaredge_cloud", profile_ids)
        self.assertIn("fronius_solarweb", profile_ids)
        self.assertIn("kostal_solar_portal", profile_ids)
        self.assertIn("growatt_server", profile_ids)

        sungrow = next(p for p in profiles if p["id"] == "sungrow_isolarcloud")
        field_keys = [f["key"] for f in sungrow["fields"]]
        self.assertIn("appkey", field_keys)
        self.assertIn("user_account", field_keys)
        self.assertIn("ps_id", field_keys)

        kostal = next(p for p in profiles if p["id"] == "kostal_solar_portal")
        self.assertEqual(kostal["vendor"], "Kostal")
        self.assertIn("api_key", [f["key"] for f in kostal["fields"]])

        growatt = next(p for p in profiles if p["id"] == "growatt_server")
        self.assertEqual(growatt["vendor"], "Growatt")
        self.assertIn("token", [f["key"] for f in growatt["fields"]])
        self.assertIn("de", growatt.get("help", {}))



    def test_03_jsonpath_extractor(self):
        """Testet den JSONPath-Evaluator auf verschachtelten Daten."""
        sample_data = {
            "result_code": "1",
            "result_data": {
                "curr_power": 5.42,
                "grid_power": -2.10,
                "battery_soc": 85.0,
            }
        }
        val1 = extract_jsonpath(sample_data, "$.result_data.curr_power")
        self.assertEqual(val1, 5.42)

        val2 = extract_jsonpath(sample_data, "$.result_data.battery_soc")
        self.assertEqual(val2, 85.0)

        val_fallback = extract_jsonpath(sample_data, "$.result_data.non_existent", fallback=0.0)
        self.assertEqual(val_fallback, 0.0)

    def test_04_test_sungrow_credentials_simulation(self):
        """Testet die Prüfung von Sungrow-Zugangsdaten im Sandbox/Simulator-Modus."""
        creds = {
            "appkey": "demo",
            "user_account": "tester@sharegy.de",
            "user_password": "testpassword",
            "ps_id": "12345",
        }
        res = test_cloud_credentials("sungrow_isolarcloud", creds)
        self.assertEqual(res["status"], "success")
        self.assertTrue(res["simulated"])
        self.assertIn("live_metrics", res)
        self.assertIn("pv_power_w", res["live_metrics"])
        self.assertIn("battery_soc", res["live_metrics"])
        self.assertGreaterEqual(res["live_metrics"]["pv_power_w"], 0.0)

    def test_05_execute_cloud_poll_saves_metrics(self):
        """Testet die Ausführung eines Pollings und das Anlegen von DeviceMetrics."""
        integration = CloudDeviceIntegration.objects.create(
            device=self.device,
            profile_id="sungrow_isolarcloud",
            credentials={"appkey": "demo", "user_account": "sungrow@sharegy.de", "ps_id": "9988"},
            is_active=True,
        )
        res = execute_cloud_poll(integration)
        self.assertEqual(res["status"], "success")

        # DB prüfen
        integration.refresh_from_db()
        self.assertEqual(integration.last_status, CloudDeviceIntegration.STATUS_OK)
        self.assertIsNotNone(integration.last_polled_at)

        # DeviceMetric Einträge vorhanden
        metrics = DeviceMetric.objects.filter(device=self.device)
        self.assertTrue(metrics.exists())

    def test_06_celery_polling_task(self):
        """Testet den Celery Hintergrund-Task für Cloud-Integrationen."""
        CloudDeviceIntegration.objects.create(
            device=self.device,
            profile_id="sungrow_isolarcloud",
            credentials={"appkey": "demo", "user_account": "demo@sharegy.de", "ps_id": "1122"},
            is_active=True,
        )
        task_res = poll_cloud_integrations_task()
        self.assertGreaterEqual(task_res["polled"], 1)
        self.assertEqual(task_res["errors"], 0)

    def test_07_rest_api_cloud_profiles(self):
        """Testet die REST-APIs für Profile-Listing, Test und Integration."""
        # 1. GET /api/devices/cloud-profiles/
        resp = self.client.get("/api/devices/cloud-profiles/")
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.data["status"], "success")
        self.assertGreaterEqual(resp.data["count"], 1)

        # 2. POST /api/devices/cloud-profiles/test/
        resp_test = self.client.post("/api/devices/cloud-profiles/test/", {
            "profile_id": "sungrow_isolarcloud",
            "credentials": {
                "appkey": "demo",
                "user_account": "tester@sharegy.de",
                "ps_id": "12345",
            }
        }, format="json")
        self.assertEqual(resp_test.status_code, 200)
        self.assertEqual(resp_test.data["status"], "success")

        # 3. POST /api/devices/cloud-profiles/integrate/
        resp_int = self.client.post("/api/devices/cloud-profiles/integrate/", {
            "home_id": self.home.id,
            "name": "Mein Sungrow Hybrid SH10RT",
            "profile_id": "sungrow_isolarcloud",
            "credentials": {
                "appkey": "demo",
                "user_account": "tester@sharegy.de",
                "ps_id": "12345",
            },
            "polling_interval": 60,
        }, format="json")
        self.assertEqual(resp_int.status_code, 200)
        self.assertEqual(resp_int.data["status"], "success")
        self.assertIn("device_id", resp_int.data)

    def test_08_load_and_simulate_kostal_profile(self):
        """Testet das Laden und die Testverbindung für Kostal Solar Portal."""
        profile = load_profile("kostal_solar_portal")
        self.assertEqual(profile["id"], "kostal_solar_portal")
        self.assertEqual(profile["vendor"], "Kostal")
        self.assertIn("metrics_mapping", profile)

        # Test-Credentials Simulation
        creds = {"api_key": "ksp_secret_123", "plant_id": "990011"}
        res = test_cloud_credentials("kostal_solar_portal", creds)
        self.assertEqual(res["status"], "success")
        self.assertTrue(res["simulated"])
        self.assertIn("live_metrics", res)
        self.assertIn("pv_power_w", res["live_metrics"])
        self.assertIn("battery_soc", res["live_metrics"])

    def test_09_load_and_simulate_growatt_profile(self):
        """Testet das Laden und die Testverbindung für Growatt ShineServer."""
        profile = load_profile("growatt_server")
        self.assertEqual(profile["id"], "growatt_server")
        self.assertEqual(profile["vendor"], "Growatt")
        self.assertIn("metrics_mapping", profile)

        # Test-Credentials Simulation
        creds = {"token": "growatt_openapi_secret_token", "plant_id": "194820"}
        res = test_cloud_credentials("growatt_server", creds)
        self.assertEqual(res["status"], "success")
        self.assertTrue(res["simulated"])
        self.assertIn("live_metrics", res)
        self.assertIn("pv_power_w", res["live_metrics"])
        self.assertIn("daily_generation_kwh", res["live_metrics"])


