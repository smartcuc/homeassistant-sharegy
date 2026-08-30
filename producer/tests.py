#####################
# producer/tests.py
#####################

from django.test import TestCase
from django.contrib.auth import get_user_model
from devices.models import Home, Device, DeviceConfig, DeviceRole, DeviceLatestMetric
from producer.models import StorageSystem, GeneratorSystem, GeneratorType

User = get_user_model()


class StorageSystemTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="storageuser",
            email="storage@example.com",
            password="testpassword123",
        )
        self.home = Home.objects.create(user=self.user, name="Storage Test Home")
        self.client.force_login(self.user)

        # Geräte anlegen
        self.inverter = Device.objects.create(
            home=self.home,
            identifier="sungrow-hybrid-01",
            active=True,
        )
        DeviceConfig.objects.create(
            device=self.inverter,
            home=self.home,
            name="Sungrow SH10RT Inverter",
        )

        self.bms_sensor = Device.objects.create(
            home=self.home,
            identifier="ha-byd-bms-soc",
            active=True,
        )
        DeviceConfig.objects.create(
            device=self.bms_sensor,
            home=self.home,
            name="Home Assistant BYD Battery SoC",
        )

        from django.utils import timezone

        # Metriken erzeugen
        DeviceLatestMetric.objects.create(
            device=self.bms_sensor,
            metric_key="soc",
            value=78.5,
            timestamp=timezone.now(),
        )
        DeviceLatestMetric.objects.create(
            device=self.inverter,
            metric_key="power",
            value=-1850.0,  # Entladen
            timestamp=timezone.now(),
        )

    def test_storage_system_create_and_live_values(self):
        storage = StorageSystem.objects.create(
            home=self.home,
            name="Keller Speicher (BYD)",
            capacity_kwh=12.8,
            max_charge_power_kw=6.0,
            max_discharge_power_kw=6.0,
            min_soc_reserve_pct=10.0,
            soc_device=self.bms_sensor,
            soc_metric_key="soc",
            power_device=self.inverter,
            power_metric_key="power",
        )

        self.assertEqual(storage.get_live_soc(), 78.5)
        self.assertEqual(storage.get_live_power(), -1850.0)

    def test_storage_list_and_create_api(self):
        # 1. Create API
        create_resp = self.client.post(
            "/api/producer/storage/create/",
            data={
                "name": "Hauptspeicher",
                "capacity_kwh": 10.0,
                "max_charge_power_kw": 5.0,
                "max_discharge_power_kw": 5.0,
                "min_soc_reserve_pct": 15.0,
                "soc_device_id": str(self.bms_sensor.id),
                "soc_metric_key": "soc",
                "power_device_id": str(self.inverter.id),
                "power_metric_key": "power",
            },
            content_type="application/json",
        )
        self.assertEqual(create_resp.status_code, 201)
        created_data = create_resp.json()
        self.assertEqual(created_data["name"], "Hauptspeicher")
        self.assertEqual(created_data["live_soc_pct"], 78.5)
        self.assertEqual(created_data["live_power_w"], -1850.0)
        self.assertEqual(created_data["status"], "charging")

        # 2. List API
        list_resp = self.client.get("/api/producer/storage/")
        self.assertEqual(list_resp.status_code, 200)
        list_data = list_resp.json()
        self.assertEqual(len(list_data), 1)

    def test_storage_detect_api(self):
        response = self.client.get("/api/producer/storage/detect/")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn("candidates", data)
        self.assertIn("devices", data)
        self.assertGreaterEqual(len(data["devices"]), 2)
