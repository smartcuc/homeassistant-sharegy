from django.test import TestCase
from django.contrib.auth import get_user_model
from django.utils import timezone
from datetime import datetime, timedelta
from devices.models import Home, Device, DeviceLatestMetric
from devices.services_discovergy import DiscovergyClient, sync_discovergy_meter_for_user

User = get_user_model()


class DiscovergyConnectorTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="disco_test_user", email="disco@sharegy.local", password="pw")
        self.home = Home.objects.create(user=self.user, name="Discovergy Test Home")

    def test_discovergy_client_test_connection(self):
        client = DiscovergyClient(email="demo@discovergy.com", password="dummy")
        res = client.test_connection()
        self.assertEqual(res["status"], "success")
        self.assertTrue(res["connected"])
        self.assertGreaterEqual(res["meters_count"], 1)

    def test_discovergy_client_get_last_reading(self):
        client = DiscovergyClient(email="demo@discovergy.com", password="dummy")
        reading = client.get_last_reading("DISCO-METER-01")
        self.assertIn("values", reading)
        self.assertIn("power", reading["values"])
        self.assertIn("energy", reading["values"])

    def test_discovergy_client_get_15m_readings(self):
        client = DiscovergyClient(email="demo@discovergy.com", password="dummy")
        now = timezone.now()
        readings = client.get_15m_readings("DISCO-METER-01", now - timedelta(hours=1), now)
        self.assertIsInstance(readings, list)
        self.assertGreaterEqual(len(readings), 4)

    def test_sync_discovergy_meter_for_user(self):
        res = sync_discovergy_meter_for_user(
            user=self.user,
            email="demo@discovergy.com",
            password="dummy",
            meter_id="DISCO-METER-01",
            home_id=self.home.id,
        )
        self.assertEqual(res["status"], "success")
        self.assertEqual(res["meter_id"], "DISCO-METER-01")

        # Verify Device & Metric
        device = Device.objects.get(id=res["device_id"])
        self.assertEqual(device.identifier, "discovergy_DISCO-METER-01")
        self.assertTrue(device.active)

        power_metric = DeviceLatestMetric.objects.get(device=device, metric_key="power")
        self.assertGreater(power_metric.value, 0)
