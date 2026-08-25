from datetime import timedelta
from django.test import TestCase
from django.contrib.auth import get_user_model
from django.utils import timezone
from django.core.cache import cache

from devices.models import (
    Home,
    Device,
    DeviceConfig,
    DeviceRole,
    MetricDefinition,
    DeviceMetric,
    DeviceLatestMetric,
    DeviceMetric1m,
    DeviceMetric5m,
    DeviceMetric15m,
    DeviceMetric1h,
)
from devices.services.aggregation import floor_bucket, aggregate_1m, aggregate_5m
from devices.services.metrics import get_latest_values

User = get_user_model()


class DeviceAggregationTest(TestCase):
    def setUp(self):
        cache.clear()
        self.user = User.objects.create_user(
            username="devicetestuser",
            email="devices@example.com",
            password="testpassword123",
        )
        self.home = Home.objects.create(
            user=self.user,
            name="Test Home",
        )
        self.metric_def = MetricDefinition.objects.create(
            key="power",
            name="Active Power",
            unit="W",
        )
        self.role_consumer = DeviceRole.objects.create(
            key="consumer",
            label="Consumer",
        )
        self.device = Device.objects.create(
            home=self.home,
            identifier="test_meter_1",
            configured=True,
        )
        self.config = DeviceConfig.objects.create(
            device=self.device,
            home=self.home,
            role=self.role_consumer,
            metric_definition=self.metric_def,
        )

    def test_floor_bucket(self):
        dt = timezone.now().replace(minute=17, second=42, microsecond=0)
        floored = floor_bucket(dt, 300)  # 5 minute bucket
        self.assertEqual(floored.minute, 15)
        self.assertEqual(floored.second, 0)

    def test_get_latest_values_from_cache_and_db(self):
        # Set cache
        cache.set(f"device:{self.device.id}:latest_power", 350.5, timeout=60)
        values = get_latest_values([self.device.id])
        self.assertEqual(values.get(self.device.id), 350.5)

        # Clear cache and test DeviceLatestMetric DB fallback
        cache.clear()
        DeviceLatestMetric.objects.update_or_create(
            device=self.device,
            metric_key="power",
            defaults={"value": 420.0, "timestamp": timezone.now()},
        )
        values_from_db = get_latest_values([self.device.id])
        self.assertEqual(values_from_db.get(self.device.id), 420.0)

    def test_aggregate_1m(self):
        now = timezone.now()
        current_bucket = floor_bucket(now, 60)
        target = current_bucket - timedelta(minutes=1)

        # Create raw metrics in target minute
        DeviceMetric.objects.create(
            device=self.device,
            metric_key="power",
            value=100.0,
            unit="W",
            timestamp=target + timedelta(seconds=10),
        )
        DeviceMetric.objects.create(
            device=self.device,
            metric_key="power",
            value=200.0,
            unit="W",
            timestamp=target + timedelta(seconds=30),
        )

        aggregate_1m(now)

        agg = DeviceMetric1m.objects.filter(
            device=self.device,
            bucket=target,
        ).first()

        self.assertIsNotNone(agg)
        self.assertEqual(agg.count, 2)
        self.assertEqual(agg.avg, 150.0)
        self.assertEqual(agg.min, 100.0)
        self.assertEqual(agg.max, 200.0)

    def test_multi_metric_endpoints(self):
        # 1. Mehrere Metriken für ein Gerät anlegen
        now = timezone.now()
        DeviceLatestMetric.objects.create(
            device=self.device,
            metric_key="power",
            value=1250.0,
            unit="W",
            timestamp=now,
        )
        DeviceLatestMetric.objects.create(
            device=self.device,
            metric_key="voltage_l1",
            value=231.5,
            unit="V",
            timestamp=now,
        )
        DeviceLatestMetric.objects.create(
            device=self.device,
            metric_key="battery_soc",
            value=85.0,
            unit="%",
            timestamp=now,
        )

        # 2. Endpoint /api/devices/<id>/metrics/ testen
        response = self.client.get(f"/api/devices/{self.device.id}/metrics/")
        self.assertEqual(response.status_code, 200)
        metrics = response.json().get("metrics", [])
        self.assertEqual(len(metrics), 3)
        keys = [m["key"] for m in metrics]
        self.assertIn("power", keys)
        self.assertIn("voltage_l1", keys)
        self.assertIn("battery_soc", keys)

        # 3. Timeseries mit metric-Filter testen
        bucket_time = floor_bucket(now, 900) - timedelta(minutes=15)
        DeviceMetric15m.objects.create(
            device=self.device,
            metric_key="voltage_l1",
            bucket=bucket_time,
            avg=230.8,
            min=230.0,
            max=231.5,
            count=15,
        )

        ts_response = self.client.get(f"/api/devices/{self.device.id}/timeseries/?range=24h&metric=voltage_l1")
        self.assertEqual(ts_response.status_code, 200)
        ts_data = ts_response.json()
        self.assertEqual(ts_data.get("metric"), "voltage_l1")
        self.assertEqual(ts_data.get("unit"), "V")
        self.assertTrue(len(ts_data.get("points", [])) >= 1)
        self.assertEqual(ts_data["points"][0]["v"], 230.8)

    def test_device_configured_as_battery_auto_creates_storage_system(self):
        from producer.models import StorageSystem
        role_bat = DeviceRole.objects.create(key="battery", label="Hausspeicher")

        new_bat_dev = Device.objects.create(
            home=self.home,
            identifier="test_victron_multiplus_01",
        )

        self.client.force_login(self.user)
        resp = self.client.patch(
            f"/api/devices/{new_bat_dev.id}/",
            data={
                "name": "Victron MultiPlus Speicher",
                "role_id": role_bat.id,
            },
            content_type="application/json",
        )
        self.assertEqual(resp.status_code, 200)

        # Prüfe ob StorageSystem automatisch unter Erzeuger- & Speicheranlagen existiert
        storage = StorageSystem.objects.filter(home=self.home, primary_device=new_bat_dev).first()
        self.assertIsNotNone(storage, "StorageSystem muss automatisch bei Rolle 'battery' angelegt werden")
        self.assertEqual(storage.name, "Victron MultiPlus Speicher")
        self.assertEqual(storage.capacity_kwh, 10.0)
        self.assertTrue(storage.is_auto_detected)

    def test_device_setup_modal_patch_config_endpoint(self):
        # Testet den exakten Aufruf aus DeviceSetupModal.jsx:
        # PATCH /api/devices/{id}/config/ mit display_name und optionalen leeren Strings
        self.client.force_login(self.user)
        resp = self.client.patch(
            f"/api/devices/{self.device.id}/config/",
            data={
                "display_name": "Hauptzähler Wohnzimmer",
                "role_id": self.role_consumer.id,
                "metric_definition_id": self.metric_def.id,
                "generator_type_id": "",
                "energy_signal_type_id": "",
                "floor_id": "",
                "room_id": "",
                "home_id": str(self.home.id),
            },
            content_type="application/json",
        )
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertEqual(data["status"], "ok")
        self.assertEqual(data["device"]["display_name"], "Hauptzähler Wohnzimmer")
        self.assertEqual(data["device"]["config"]["role"]["id"], self.role_consumer.id)
