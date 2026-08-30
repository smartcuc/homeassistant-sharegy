####################################
# devices/tests_battery_direction.py
####################################

from django.test import TestCase
from django.utils import timezone
from django.contrib.auth import get_user_model
from django.core.cache import cache

from devices.models import Home, Device, DeviceConfig, DeviceRole, MetricDefinition, DeviceLatestMetric
from devices.services.metrics import resolve_battery_direction, normalize_battery_metrics, get_latest_values
from devices.services.ingest import ingest_metric_payload
from energy.ems.services import build_device_signals
from energy.services.balance import get_energy_balance

User = get_user_model()


class BatteryDirectionHandlingTest(TestCase):
    """
    Testet die herstellerunabhängige Vorzeichen- & Richtungsauflösung für Batteriespeicher (z. B. Sungrow, Modbus, MQTT).
    """

    def setUp(self):
        cache.clear()
        self.user = User.objects.create_user(username="sungrow_user", email="sungrow@sharegy.local", password="password123")
        self.home = Home.objects.create(user=self.user, name="Sungrow Home")

        self.role_batt, _ = DeviceRole.objects.get_or_create(key="battery", defaults={"label": "Batteriespeicher"})
        self.role_pv, _ = DeviceRole.objects.get_or_create(key="producer", defaults={"label": "Photovoltaik"})

        self.mdef_power, _ = MetricDefinition.objects.get_or_create(key="power", defaults={"name": "Wirkleistung", "unit": "W"})

        self.bat_device = Device.objects.create(
            home=self.home,
            identifier="sungrow_battery_01",
            configured=True,
            active=True,
        )
        self.bat_config = DeviceConfig.objects.create(
            device=self.bat_device,
            home=self.home,
            role=self.role_batt,
            metric_definition=self.mdef_power,
        )

        self.pv_device = Device.objects.create(
            home=self.home,
            identifier="sungrow_inverter_01",
            configured=True,
            active=True,
        )
        self.pv_config = DeviceConfig.objects.create(
            device=self.pv_device,
            home=self.home,
            role=self.role_pv,
            metric_definition=self.mdef_power,
        )

    def test_resolve_battery_direction(self):
        # Sungrow Modbus: 1 = Charge, 2 = Discharge, 0 = Standby
        self.assertEqual(resolve_battery_direction(1), -1)
        self.assertEqual(resolve_battery_direction(2), 1)
        self.assertEqual(resolve_battery_direction(0), 0)

        # String-Werte
        self.assertEqual(resolve_battery_direction("charging"), -1)
        self.assertEqual(resolve_battery_direction("charge"), -1)
        self.assertEqual(resolve_battery_direction("laden"), -1)
        self.assertEqual(resolve_battery_direction("discharging"), 1)
        self.assertEqual(resolve_battery_direction("discharge"), 1)
        self.assertEqual(resolve_battery_direction("entladen"), 1)
        self.assertEqual(resolve_battery_direction("idle"), 0)

    def test_sungrow_charging_ingestion(self):
        # Sungrow sendet positive 2500W mit running_state: 1 (Laden)
        payload = {
            "battery_power": 2500,
            "running_state": 1,
        }
        res = ingest_metric_payload(self.bat_device, payload, source="modbus_sungrow")
        
        # In Redis / Latest Metric muss -2500 W stehen
        latest_vals = get_latest_values([self.bat_device.id])
        self.assertEqual(latest_vals[self.bat_device.id], -2500.0)

        # In EMS Live Signalen muss charge=2500W und discharge=0W stehen
        signals = build_device_signals(self.user)
        self.assertEqual(signals["battery"]["charge"], 2500.0)
        self.assertEqual(signals["battery"]["discharge"], 0.0)

    def test_sungrow_discharging_ingestion(self):
        # Sungrow sendet positive 1800W mit running_state: 2 (Entladen)
        payload = {
            "battery_power": 1800,
            "running_state": 2,
        }
        res = ingest_metric_payload(self.bat_device, payload, source="modbus_sungrow")

        latest_vals = get_latest_values([self.bat_device.id])
        self.assertEqual(latest_vals[self.bat_device.id], 1800.0)

        signals = build_device_signals(self.user)
        self.assertEqual(signals["battery"]["charge"], 0.0)
        self.assertEqual(signals["battery"]["discharge"], 1800.0)

    def test_separate_charging_and_discharging_power(self):
        # Home Assistant / MQTT Format
        payload = {
            "battery_charging_power": 3200,
            "battery_discharging_power": 0,
        }
        res = ingest_metric_payload(self.bat_device, payload, source="homeassistant")

        latest_vals = get_latest_values([self.bat_device.id])
        self.assertEqual(latest_vals[self.bat_device.id], -3200.0)

        signals = build_device_signals(self.user)
        self.assertEqual(signals["battery"]["charge"], 3200.0)
        self.assertEqual(signals["battery"]["discharge"], 0.0)

    def test_battery_current_signed_charging(self):
        # Sungrow: battery_power positiv (2800W), aber battery_current negativ (-8.5A)
        payload = {
            "battery_power": 2800,
            "battery_current": -8.5,
        }
        res = ingest_metric_payload(self.bat_device, payload, source="modbus_sungrow")

        latest_vals = get_latest_values([self.bat_device.id])
        self.assertEqual(latest_vals[self.bat_device.id], -2800.0)

        signals = build_device_signals(self.user)
        self.assertEqual(signals["battery"]["charge"], 2800.0)
        self.assertEqual(signals["battery"]["discharge"], 0.0)

    def test_battery_current_signed_discharging(self):
        # Sungrow: battery_power positiv (1750W), battery_current positiv (5.2A)
        payload = {
            "battery_power": 1750,
            "battery_current": 5.2,
        }
        res = ingest_metric_payload(self.bat_device, payload, source="modbus_sungrow")

        latest_vals = get_latest_values([self.bat_device.id])
        self.assertEqual(latest_vals[self.bat_device.id], 1750.0)

        signals = build_device_signals(self.user)
        self.assertEqual(signals["battery"]["charge"], 0.0)
        self.assertEqual(signals["battery"]["discharge"], 1750.0)

    def test_battery_voltage_and_current_calculation(self):
        # Falls Wechselrichter gar keine battery_power sendet, sondern nur U (400V) und I (-7.5A)
        payload = {
            "battery_voltage": 400.0,
            "battery_current": -7.5,
        }
        res = ingest_metric_payload(self.bat_device, payload, source="modbus_sungrow")

        latest_vals = get_latest_values([self.bat_device.id])
        self.assertEqual(latest_vals[self.bat_device.id], -3000.0)

        signals = build_device_signals(self.user)
        self.assertEqual(signals["battery"]["charge"], 3000.0)
        self.assertEqual(signals["battery"]["discharge"], 0.0)

