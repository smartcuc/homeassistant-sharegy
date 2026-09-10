from django.test import TestCase
from django.contrib.auth import get_user_model
from devices.models import Home, Device
from devices.services.interface_tracker import (
    classify_interface,
    track_interface_telemetry,
    get_home_interface_statuses,
    get_aggregated_interface_stats,
)

User = get_user_model()


class InterfaceTrackerTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="tracker_test@sharegy.de", email="tracker_test@sharegy.de")
        self.home = Home.objects.create(user=self.user, name="Tracker Home")

    def test_classify_interface(self):
        self.assertEqual(classify_interface("homeassistant"), "homeassistant")
        self.assertEqual(classify_interface("homeassistant_feedback"), "homeassistant")
        self.assertEqual(classify_interface(None, {"source": "homeassistant"}), "homeassistant")
        self.assertEqual(classify_interface("iobroker"), "iobroker")
        self.assertEqual(classify_interface(None, {"source": "iobroker.sharegy"}), "iobroker")
        self.assertEqual(classify_interface("shelly_1pm"), "shelly_wss")
        self.assertEqual(classify_interface(None, {"method": "NotifyStatus"}), "shelly_wss")
        self.assertEqual(classify_interface("isolarcloud"), "cloud_inverter")
        self.assertEqual(classify_interface("mqtt_direct"), "mqtt_direct")

    def test_track_and_get_home_status(self):
        track_interface_telemetry(self.home.id, "homeassistant", {"val": 1200})
        track_interface_telemetry(self.home.id, "iobroker", {"val": 350})

        statuses = get_home_interface_statuses(self.home)
        self.assertIn("homeassistant", statuses)
        self.assertIn("iobroker", statuses)
        self.assertTrue(statuses["homeassistant"]["configured"])
        self.assertTrue(statuses["homeassistant"]["online"])
        self.assertTrue(statuses["iobroker"]["configured"])
        self.assertTrue(statuses["iobroker"]["online"])

    def test_aggregated_stats(self):
        track_interface_telemetry(self.home.id, "homeassistant", {"val": 1200})
        stats = get_aggregated_interface_stats()
        self.assertGreaterEqual(stats["total_homes"], 1)
        self.assertIn("interfaces", stats)
        ha_stat = next((i for i in stats["interfaces"] if i["key"] == "homeassistant"), None)
        self.assertIsNotNone(ha_stat)
        self.assertGreaterEqual(ha_stat["total_configured"], 1)
