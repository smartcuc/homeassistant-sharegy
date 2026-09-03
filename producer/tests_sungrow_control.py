from django.test import TestCase
from django.contrib.auth import get_user_model
from django.utils import timezone
from devices.models import Home, Device, CloudDeviceIntegration
from producer.models import StorageSystem
from producer.services_sungrow_control import send_sungrow_cloud_control_command
from producer.services_dispatch import dispatch_inverter_write_command

User = get_user_model()


class SungrowCloudControlTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="sungrow_ctrl_user", email="sg@sharegy.local", password="pw")
        self.home = Home.objects.create(user=self.user, name="Sungrow Solar Home")
        self.device = Device.objects.create(
            home=self.home,
            identifier="sg_sh10rt_ctrl_01",
            configured=True,
            active=True,
        )
        self.storage = StorageSystem.objects.create(
            home=self.home,
            primary_device=self.device,
            name="Sungrow SBR224 Storage",
            capacity_kwh=22.4,
            ems_control_enabled=True,
            control_mode="price_optimized",
            target_charge_power_kw=5.0,
            price_threshold_ct=15.0,
        )
        self.integration = CloudDeviceIntegration.objects.create(
            device=self.device,
            profile_id="sungrow_isolarcloud",
            credentials={
                "appkey": "988713D7D057090474AEC9584CBA1AAD",
                "token": "sg_oauth_demo_123",
                "ps_id": "123456",
            },
            is_active=True,
        )

    def test_forced_charge_command(self):
        """Testet das Absenden eines Forced-Charge Steuerbefehls via Sungrow OpenAPI Service."""
        res = send_sungrow_cloud_control_command(self.storage, action="forced_charge", power_kw=6.5, target_soc=90.0)
        self.assertEqual(res["status"], "success")
        self.assertEqual(res["action"], "forced_charge")
        self.assertEqual(res["mode_code"], 1)
        self.assertEqual(res["power_kw"], 6.5)
        self.assertEqual(res["power_w"], 6500)
        self.assertTrue(res.get("simulated"))

    def test_self_consumption_command(self):
        """Testet das Zurücksetzen auf PV-Autarkie (self_consumption)."""
        res = send_sungrow_cloud_control_command(self.storage, action="self_consumption", power_kw=0.0)
        self.assertEqual(res["status"], "success")
        self.assertEqual(res["action"], "self_consumption")
        self.assertEqual(res["mode_code"], 0)

    def test_dispatch_inverter_write_command_integration(self):
        """Testet die Integration in den zentralen dispatch_inverter_write_command."""
        res = dispatch_inverter_write_command(self.storage, action="forced_charge", power_kw=5.0)
        self.assertEqual(res["status"], "dispatched")
        self.assertIn("sungrow_result", res)
        self.assertEqual(res["sungrow_result"]["mode_code"], 1)
