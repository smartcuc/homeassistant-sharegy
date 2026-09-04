"""
devices/tests_sensor_adapter_matrix.py

Umfassende Test-Matrix für Sensor- und SmartMeter-Adapter:
1. ShellyGen2/Gen3 RPC (NotifyStatus, em:0, emdata:0, switch:0, pm1:0, PlugS)
2. Waveshare Modbus / Eastron SDM630 / CHINT DTSU666 (Register, Phasenleistungen, kWh)
3. Tasmota SML / Hichi IR-Lesekopf (OBIS 16.7.0, 1.8.0, 2.8.0, StatusSNS)
4. Generic JSON (Home Assistant, ioBroker, Custom Frames)
5. Automatische Erkennung und Canonical Ingest Pipeline
"""

from django.test import TestCase
from django.contrib.auth import get_user_model
from django.utils import timezone
from devices.models import Home, Device, DeviceMetric, DeviceLatestMetric
from devices.adapters.sensors import (
    SensorAdapterRegistry,
    ShellySensorAdapter,
    WaveshareModbusAdapter,
    TasmotaSmlAdapter,
    GenericJsonSensorAdapter,
    CanonicalSensorReading,
    process_canonical_sensor_reading,
)

User = get_user_model()


class SensorAdapterMatrixTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="sensortest", email="sensor@example.com", password="pw")
        self.home = Home.objects.create(user=self.user, name="Sensor Home", mqtt_token="tok_sensor_1234")
        self.device = Device.objects.create(home=self.home, identifier="test_sensor_01", configured=True, active=True)

    def test_shelly_pro_3em_parsing(self):
        """Shelly Pro 3EM NotifyStatus Frame mit 3 Phasen & emdata."""
        payload = {
            "src": "shellypro3em-c82e18112233",
            "method": "NotifyStatus",
            "params": {
                "ts": 1725450000.0,
                "em:0": {
                    "id": 0,
                    "a_act_power": 1200.5,
                    "b_act_power": 450.0,
                    "c_act_power": 350.2,
                    "total_act_power": 2000.7,
                    "a_voltage": 230.1,
                    "b_voltage": 229.8,
                    "c_voltage": 231.2,
                    "a_current": 5.22,
                    "b_current": 1.96,
                    "c_current": 1.51,
                },
                "emdata:0": {
                    "id": 0,
                    "total_act": 145200.0,  # Wh -> 145.2 kWh
                }
            }
        }
        reading = SensorAdapterRegistry.detect_and_parse(payload)
        self.assertEqual(reading.device_identifier, "shellypro3em-c82e18112233")
        self.assertEqual(reading.power_w, 2000.7)
        self.assertEqual(reading.energy_import_kwh, 145.2)
        self.assertEqual(reading.voltage_l1_v, 230.1)
        self.assertEqual(reading.voltage_l2_v, 229.8)
        self.assertEqual(reading.voltage_l3_v, 231.2)
        self.assertEqual(reading.current_l1_a, 5.22)

    def test_shelly_plus_1pm_plug_and_relay(self):
        """Shelly Plus 1PM mit Relais-Status & Leistung."""
        payload = {
            "src": "shellyplus1pm-e09806a1b2c3",
            "method": "NotifyStatus",
            "params": {
                "ts": 1725450000.0,
                "switch:0": {
                    "id": 0,
                    "output": True,
                    "apower": 185.4,
                    "voltage": 232.0,
                    "current": 0.81,
                    "aenergy": {"total": 45230.0},  # Wh -> 45.23 kWh
                    "temperature": {"tC": 42.5},
                }
            }
        }
        reading = SensorAdapterRegistry.detect_and_parse(payload)
        self.assertEqual(reading.power_w, 185.4)
        self.assertEqual(reading.energy_import_kwh, 45.23)
        self.assertEqual(reading.voltage_l1_v, 232.0)
        self.assertEqual(reading.current_l1_a, 0.81)
        self.assertEqual(reading.temperature_c, 42.5)
        self.assertTrue(reading.relay_state)

    def test_waveshare_modbus_sdm630(self):
        """Waveshare Modbus Gateway mit Eastron SDM630 Registern."""
        payload = {
            "src": "waveshare_eth_gw_44",
            "params": {
                "active_power_l1": 1500.0,
                "active_power_l2": 1200.0,
                "active_power_l3": 800.0,
                "total_active_power": 3500.0,
                "import_kwh": 5120.4,
                "export_kwh": 890.1,
                "voltage_l1": 230.5,
                "voltage_l2": 231.0,
                "voltage_l3": 229.5,
                "current_l1": 6.5,
                "current_l2": 5.2,
                "current_l3": 3.5,
                "frequency": 50.01,
            }
        }
        reading = SensorAdapterRegistry.detect_and_parse(payload)
        self.assertEqual(reading.device_identifier, "waveshare_eth_gw_44")
        self.assertEqual(reading.power_w, 3500.0)
        self.assertEqual(reading.energy_import_kwh, 5120.4)
        self.assertEqual(reading.energy_export_kwh, 890.1)
        self.assertEqual(reading.frequency_hz, 50.01)

    def test_tasmota_sml_obis_meter(self):
        """Tasmota SML IR-Lesekopf mit OBIS 16.7.0, 1.8.0 und 2.8.0."""
        payload = {
            "Time": "2026-09-04T18:00:00",
            "Topic": "tasmota_stromzaehler_ir",
            "StatusSNS": {
                "SML": {
                    "16_7_0": 420.5,  # Momentanleistung W
                    "1_8_0": 12450.8, # Bezug kWh
                    "2_8_0": 3400.2,  # Einspeisung kWh
                }
            }
        }
        reading = SensorAdapterRegistry.detect_and_parse(payload)
        self.assertEqual(reading.power_w, 420.5)
        self.assertEqual(reading.energy_import_kwh, 12450.8)
        self.assertEqual(reading.energy_export_kwh, 3400.2)

    def test_generic_iobroker_payload(self):
        """ioBroker / SimpleAPI Format mit expliziter Metrik und Wert."""
        payload = {
            "src": "iobroker_smartmeter",
            "metric": "power",
            "val": 780.0,
            "unit": "W",
        }
        reading = SensorAdapterRegistry.detect_and_parse(payload)
        self.assertEqual(reading.power_w, 780.0)

    def test_canonical_sensor_ingest_persistence(self):
        """Prüft vollständige Persistierung von CanonicalSensorReading in DB & Caches."""
        reading = CanonicalSensorReading(
            device_identifier=self.device.identifier,
            power_w=1560.0,
            energy_import_kwh=320.5,
            voltage_l1_v=231.0,
            current_l1_a=6.75,
            relay_state=True,
            timestamp=timezone.now(),
        )
        metrics = process_canonical_sensor_reading(self.device, reading, source="websocket")
        self.assertEqual(metrics["power"], 1560.0)
        self.assertEqual(metrics["energy"], 320.5)

        # In DB prüfen
        p_metric = DeviceMetric.objects.filter(device=self.device, metric_key="power").first()
        self.assertIsNotNone(p_metric)
        self.assertEqual(float(p_metric.value), 1560.0)

        e_metric = DeviceMetric.objects.filter(device=self.device, metric_key="energy").first()
        self.assertIsNotNone(e_metric)
        self.assertEqual(float(e_metric.value), 320.5)

        # In Latest Metric prüfen
        p_latest = DeviceLatestMetric.objects.filter(device=self.device, metric_key="power").first()
        self.assertIsNotNone(p_latest)
        self.assertEqual(float(p_latest.value), 1560.0)
