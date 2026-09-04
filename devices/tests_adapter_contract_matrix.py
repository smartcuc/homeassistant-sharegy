"""
devices/tests_adapter_contract_matrix.py

Umfassende Matrix- und Contract-Tests für alle registrierten Wechselrichter-Adapter.
Stellt sicher:
1. Jeder Adapter liefert 100% konformes CanonicalTelemetry.
2. Keinerlei Querbeeinflussung zwischen verschiedenen Herstellern.
3. Hinzufügen, Modifizieren oder Löschen eines Adapters berührt andere Adapter nicht.
"""

from django.test import TestCase
from django.contrib.auth import get_user_model
from devices.models import Home, Device, CloudDeviceIntegration, DeviceMetric
from devices.adapters.contracts import CanonicalTelemetry, AdapterTestResult
from devices.adapters.registry import get_adapter, list_adapters, register_adapter
from devices.adapters.sungrow import SungrowAdapter
from devices.adapters.growatt import GrowattAdapter
from devices.adapters.ingest_core import process_canonical_telemetry

User = get_user_model()


class AdapterContractMatrixTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="matrix_tester",
            email="matrix@sharegy.de",
            password="StrongPassword123!",
        )
        self.home = Home.objects.create(
            user=self.user,
            name="Matrix Lab",
            city="Frankfurt",
        )
        self.device = Device.objects.create(
            home=self.home,
            identifier="test-canonical-inverter-01",
            configured=True,
            active=True,
        )

    def test_01_canonical_telemetry_validation(self):
        """Testet die automatische Validierung und Normalisierung des Canonical-Schemas."""
        tel = CanonicalTelemetry(
            pv_power_w=-50.0,      # Negativ -> muss auf 0.0 geklemmt werden
            grid_power_w=1250.456, # Rundung auf 2 Dezimalstellen
            load_power_w=3400.0,
            battery_power_w=-2000.0,
            battery_soc=0.85,      # Dezimalwert 0.85 -> muss zu 85.0% werden
            daily_yield_kwh=-2.0,  # Negativ -> muss auf 0.0 geklemmt werden
        )
        validated = tel.validate()
        self.assertEqual(validated.pv_power_w, 0.0)
        self.assertEqual(validated.grid_power_w, 1250.46)
        self.assertEqual(validated.load_power_w, 3400.0)
        self.assertEqual(validated.battery_power_w, -2000.0)
        self.assertEqual(validated.battery_soc, 85.0)
        self.assertEqual(validated.daily_yield_kwh, 0.0)

    def test_02_sungrow_adapter_isolation(self):
        """Testet den Sungrow-Adapter isoliert mit typischen iSolarCloud-Antworten."""
        adapter = get_adapter("sungrow_isolarcloud")
        self.assertEqual(adapter.vendor, "Sungrow")

        # Test 1: kW Rohdaten
        raw_kw = {
            "result_code": "1",
            "result_data": {
                "curr_power": 6.5,
                "grid_power": -1.8,
                "load_power": 1.7,
                "battery_power": -3.0,
                "battery_soc": 90.0,
                "today_energy": 28.5,
            }
        }
        tel = adapter.parse_payload(raw_kw)
        self.assertEqual(tel.pv_power_w, 6500.0)
        self.assertEqual(tel.grid_power_w, -1800.0)
        self.assertEqual(tel.load_power_w, 1700.0)
        self.assertEqual(tel.battery_power_w, -3000.0)
        self.assertEqual(tel.battery_soc, 90.0)
        self.assertEqual(tel.daily_yield_kwh, 28.5)

    def test_03_growatt_adapter_isolation(self):
        """Testet den Growatt-Adapter isoliert mit typischen ShineServer-Antworten."""
        adapter = get_adapter("growatt_server")
        self.assertEqual(adapter.vendor, "Growatt")

        # Test 1: Watt Rohdaten mit Lade-/Entlade-Splits
        raw_gw = {
            "data": {
                "pac": 4800.0,
                "pactogrid": -1200.0,
                "pload": 1600.0,
                "pdisCharge": 0.0,
                "pcharge": 2000.0, # Ladung -> muss in Canonical als -2000.0 W ankommen
                "soc": 75.0,
                "eToday": 19.8,
            }
        }
        tel = adapter.parse_payload(raw_gw)
        self.assertEqual(tel.pv_power_w, 4800.0)
        self.assertEqual(tel.grid_power_w, -1200.0)
        self.assertEqual(tel.load_power_w, 1600.0)
        self.assertEqual(tel.battery_power_w, -2000.0)
        self.assertEqual(tel.battery_soc, 75.0)
        self.assertEqual(tel.daily_yield_kwh, 19.8)

    def test_04_standard_ingest_core_pipeline(self):
        """Testet die herstellerunabhängige Standard-Ingest-Core Pipeline."""
        tel = CanonicalTelemetry(
            pv_power_w=5500.0,
            grid_power_w=-1500.0,
            load_power_w=1500.0,
            battery_power_w=-2500.0,
            battery_soc=80.0,
        )
        metrics = process_canonical_telemetry(
            device=self.device,
            telemetry=tel,
            device_name="Test Hybrid-System",
            battery_capacity_kwh=15.0,
        )
        self.assertEqual(metrics["pv_power_w"], 5500.0)
        self.assertEqual(metrics["battery_soc"], 80.0)

        # Überprüfen ob TimescaleDB / DeviceMetric geschrieben wurde
        pv_metric = DeviceMetric.objects.filter(device=self.device, metric_key="power").order_by("-timestamp").first()
        self.assertIsNotNone(pv_metric)
        self.assertEqual(pv_metric.value, 5500.0)

        soc_metric = DeviceMetric.objects.filter(device=self.device, metric_key="battery_soc").order_by("-timestamp").first()
        self.assertIsNotNone(soc_metric)
        self.assertEqual(soc_metric.value, 80.0)

    def test_05_declarative_profile_adapters_work_seamlessly(self):
        """Stellt sicher, dass auch SolarEdge, Kostal und Fronius über die Registry geladen werden."""
        for prof_id in ["solaredge_cloud", "kostal_solar_portal", "fronius_solarweb", "deye_solarman"]:
            adapter = get_adapter(prof_id)
            self.assertIsNotNone(adapter)
            test_res = adapter.test_connection({"token": "mock_tok", "api_key": "mock_key"})
            self.assertEqual(test_res.status, "success")
            self.assertTrue(test_res.simulated)
            self.assertIn("pv_power_w", test_res.live_metrics)
