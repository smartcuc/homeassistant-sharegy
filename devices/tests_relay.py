"""Tests for Bidirectional Relay Actuation and Switching."""

from django.test import TestCase
from django.contrib.auth import get_user_model
from django.core.cache import cache
from rest_framework.test import APIClient

from devices.models import Home, Device, DeviceConfig, DeviceRole

User = get_user_model()


class DeviceRelaySwitchingTests(TestCase):
    def setUp(self):
        cache.clear()
        self.user = User.objects.create_user(
            username="tester@example.com",
            email="tester@example.com",
            password="securePassword123!",
        )
        self.other_user = User.objects.create_user(
            username="stranger@example.com",
            email="stranger@example.com",
            password="otherPassword123!",
        )
        self.home = Home.objects.create(
            user=self.user,
            name="Test House",
            timezone="Europe/Berlin",
            mqtt_token="ABCDEF123456",
        )
        self.other_home = Home.objects.create(
            user=self.other_user,
            name="Other House",
            timezone="UTC",
            mqtt_token="987654FEDCBA",
        )

        self.role_consumer = DeviceRole.objects.create(key="consumer", label="Verbraucher")

        self.device = Device.objects.create(
            home=self.home,
            identifier="shelly1pmg3-b08184ef1274",
            configured=True,
            active=True,
        )
        DeviceConfig.objects.create(
            home=self.home,
            device=self.device,
            name="Wärmepumpe Relais",
            role=self.role_consumer,
        )

        self.client = APIClient()
        self.client.force_authenticate(user=self.user)

    def test_relay_switching_on_off_toggle(self):
        # 1. Turn ON
        res_on = self.client.post(
            f"/api/devices/{self.device.id}/switch/",
            {"state": "on", "channel": 0},
            format="json",
        )
        self.assertEqual(res_on.status_code, 200)
        self.assertEqual(res_on.data["relay_state"], True)
        self.assertEqual(res_on.data["command"], "on")
        self.assertTrue(cache.get(f"device_relay_state_{self.device.id}"))

        # 2. Toggle (should turn OFF)
        res_toggle = self.client.post(
            f"/api/devices/{self.device.id}/switch/",
            {"state": "toggle"},
            format="json",
        )
        self.assertEqual(res_toggle.status_code, 200)
        self.assertEqual(res_toggle.data["relay_state"], False)
        self.assertEqual(res_toggle.data["command"], "off")
        self.assertFalse(cache.get(f"device_relay_state_{self.device.id}"))

        # 3. Turn OFF explicitly
        res_off = self.client.post(
            f"/api/devices/{self.device.id}/switch/",
            {"state": "off"},
            format="json",
        )
        self.assertEqual(res_off.status_code, 200)
        self.assertEqual(res_off.data["relay_state"], False)

    def test_forbidden_for_other_user(self):
        other_client = APIClient()
        other_client.force_authenticate(user=self.other_user)

        res = other_client.post(
            f"/api/devices/{self.device.id}/switch/",
            {"state": "on"},
            format="json",
        )
        self.assertEqual(res.status_code, 403)

    def test_device_serializer_includes_switch_fields(self):
        cache.set(f"device_relay_state_{self.device.id}", True)
        res = self.client.get("/api/devices/")
        self.assertEqual(res.status_code, 200)
        dev_data = next((d for d in res.data if d["id"] == self.device.id), None)
        self.assertIsNotNone(dev_data)
        self.assertTrue(dev_data.get("is_switchable"))
        self.assertTrue(dev_data.get("relay_state"))
