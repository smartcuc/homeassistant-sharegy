from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from django.utils import timezone
from datetime import timedelta

from devices.models import Home, Device, DeviceMetric, DeviceBaselineProfile
from devices.services_profiling import (
    get_or_create_device_profile,
    learn_device_baseline,
    evaluate_device_baseline,
    APPLIANCE_PRESETS,
)
from alerts.models import AlertEvent

User = get_user_model()


class DeviceBaselineProfilingTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="profiling_user",
            email="profiling@sharegy.de",
            password="Password123!",
        )
        self.home = Home.objects.create(user=self.user, name="Musterhaus")
        self.device = Device.objects.create(
            home=self.home,
            identifier="bwwp_shelly_01",
            configured=True,
            active=True,
        )

        self.client = Client()
        self.client.force_login(self.user)

    def test_preset_initialization(self):
        profile = get_or_create_device_profile(self.device, appliance_type="bwwp")
        self.assertEqual(profile.appliance_type, "bwwp")
        self.assertEqual(profile.standby_power_w, 30.0)
        self.assertEqual(profile.standby_max_w, 45.0)
        self.assertEqual(profile.operating_power_min_w, 350.0)
        self.assertEqual(profile.operating_power_max_w, 750.0)

    def test_healthy_standby_evaluation(self):
        profile = get_or_create_device_profile(self.device, appliance_type="bwwp")
        # Simuliere normale 28W Standby
        DeviceMetric.objects.create(
            device=self.device,
            metric_key="power",
            value=28.5,
            timestamp=timezone.now(),
        )

        res = evaluate_device_baseline(self.device)
        self.assertEqual(res["status"], DeviceBaselineProfile.HEALTH_HEALTHY)
        profile.refresh_from_db()
        self.assertEqual(profile.current_health_status, DeviceBaselineProfile.HEALTH_HEALTHY)
        self.assertEqual(AlertEvent.objects.filter(device=self.device, status=AlertEvent.STATUS_ACTIVE).count(), 0)

    def test_standby_increase_anomaly_detection(self):
        """
        Testet genau den User-Fall: Standby-Verbrauch steigt von 30W auf 52W (über Grenzwert 45W).
        Erwartung: Anomalie erkannt und AlertEvent generiert!
        """
        profile = get_or_create_device_profile(self.device, appliance_type="bwwp")
        # Simuliere erhöhten Standby (52.0 W statt 30W)
        now = timezone.now()
        for i in range(5):
            DeviceMetric.objects.create(
                device=self.device,
                metric_key="power",
                value=52.0,
                timestamp=now - timedelta(minutes=i * 2),
            )

        res = evaluate_device_baseline(self.device)
        self.assertEqual(res["status"], DeviceBaselineProfile.HEALTH_ANOMALY)
        self.assertIn("52.0 W", res["reason"])
        self.assertIn("30.0 W", res["reason"])

        profile.refresh_from_db()
        self.assertEqual(profile.current_health_status, DeviceBaselineProfile.HEALTH_ANOMALY)

        # Überprüfe, dass AlertEvent in der Alarmzentrale erzeugt wurde
        alert = AlertEvent.objects.filter(device=self.device, status=AlertEvent.STATUS_ACTIVE).first()
        self.assertIsNotNone(alert)
        self.assertEqual(alert.severity, AlertEvent.SEVERITY_WARNING)
        self.assertIn("Geräteanomalie (Standby-Erhöhung)", alert.title)
        self.assertIn("52.0 W", alert.message)

    def test_api_device_profile_get_and_patch(self):
        # 1. GET Profile
        res_get = self.client.get(f"/api/devices/{self.device.id}/profile/")
        self.assertEqual(res_get.status_code, 200)
        data = res_get.json()
        self.assertIn("standby_power_w", data)
        self.assertIn("presets", data)

        # 2. PATCH Profile to bwwp preset
        res_patch = self.client.patch(
            f"/api/devices/{self.device.id}/profile/",
            data={"appliance_type": "bwwp", "apply_preset": True, "standby_power_w": 32.0},
            content_type="application/json",
        )
        self.assertEqual(res_patch.status_code, 200)
        self.assertEqual(res_patch.json()["appliance_type"], "bwwp")
        self.assertEqual(res_patch.json()["standby_power_w"], 32.0)
