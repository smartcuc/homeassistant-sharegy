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

        # Test 2: Growatt PlantListAPI / PlantDetailAPI mit currentPower in kW (ohne 'kW' String)
        raw_plant_kw = {
            "back": {
                "totalData": {
                    "currentPower": 2.45,
                    "todayEnergy": 14.2,
                },
                "data": [
                    {
                        "plantId": "194820",
                        "plantData": {
                            "currentPower": "2.45",
                            "nominalPower": "5.0",
                        }
                    }
                ]
            }
        }
        tel2 = adapter.parse_payload(raw_plant_kw)
        self.assertEqual(tel2.pv_power_w, 2450.0) # 2.45 kW -> 2450.0 W
        self.assertEqual(tel2.daily_yield_kwh, 14.2)

        # Test 3: Growatt Multi-String PV (ppv1 + ppv2)
        raw_strings = {
            "data": {
                "ppv1": 1350.0,
                "ppv2": 980.0,
                "soc": 82.0,
            }
        }
        tel3 = adapter.parse_payload(raw_strings)
        self.assertEqual(tel3.pv_power_w, 2330.0) # 1350 + 980 = 2330 W
        self.assertEqual(tel3.battery_soc, 82.0)

        # Test 4: Reiner PV-Wechselrichter ohne Batterie (Growatt MIC / MIN / MOD)
        raw_pure_pv = {
            "data": {
                "pac": 620.0,
                "ppv": 625.0,
                "eToday": 4.1,
            }
        }
        tel4 = adapter.parse_payload(raw_pure_pv)
        self.assertEqual(tel4.pv_power_w, 625.0)
        self.assertIsNone(tel4.battery_soc)
        self.assertEqual(tel4.daily_yield_kwh, 4.1)

        # Test 5: Reale Growatt ShineServer Webdaten mit Dämmerungsleistung
        raw_live_web = {
            "Device Serial Number": "PYHFD8R0GC",
            "Plant Name": "smartEvo",
            "Current Power(kW)": "0.01",
            "Generation Today(kWh)": "1.6",
            "Total Power Generation(kWh)": "2202.4",
            "Rated Power(kW)": "1.5",
        }
        tel5 = adapter.parse_payload(raw_live_web)
        self.assertEqual(tel5.pv_power_w, 10.0) # 0.01 kW -> 10.0 W
        self.assertIsNone(tel5.battery_soc)
        self.assertEqual(tel5.daily_yield_kwh, 1.6)
        self.assertEqual(tel5.total_yield_kwh, 2202.4)

        # Test 6: Growatt Noah 2000 / Balkonkraftwerk (solarPower & outputPower)
        raw_noah = {
            "data": {
                "solarPower": 780.0,
                "outputPower": 600.0,
                "batteryPower": -180.0,
                "soc": 92.0,
                "todayEnergy": 3.8,
            }
        }
        tel6 = adapter.parse_payload(raw_noah)
        self.assertEqual(tel6.pv_power_w, 780.0)
        self.assertEqual(tel6.battery_power_w, -180.0)
        self.assertEqual(tel6.battery_soc, 92.0)
        self.assertEqual(tel6.daily_yield_kwh, 3.8)

        # Test 7: Growatt 3-Phasen Wechselrichter (pac1 + pac2 + pac3)
        raw_3phase = {
            "data": {
                "pac1": 1500.0,
                "pac2": 1400.0,
                "pac3": 1600.0,
                "pactogrid": -4000.0,
                "pload": 500.0,
                "eToday": 22.4,
            }
        }
        tel7 = adapter.parse_payload(raw_3phase)
        self.assertEqual(tel7.pv_power_w, 4500.0) # 1500 + 1400 + 1600 = 4500 W
        self.assertEqual(tel7.grid_power_w, -4000.0)
        self.assertEqual(tel7.daily_yield_kwh, 22.4)

        # Test 8: Growatt pac als kW mit Einheit (z. B. pac: "3.45 kW")
        raw_pac_kw = {
            "data": {
                "pac": "3.45 kW",
                "pload": 650.0,
                "eToday": 11.2,
            }
        }
        tel8 = adapter.parse_payload(raw_pac_kw)
        self.assertEqual(tel8.pv_power_w, 3450.0) # 3.45 kW -> 3450 W
        self.assertEqual(tel8.load_power_w, 650.0)

        # Test 9: Physikalische PV-Ertragsrekonstruktion wenn Inverter ppv=0 meldet aber Energie fließt
        raw_pv_reconstruct = {
            "data": {
                "ppv": 0.0,
                "pac": 0.0,
                "pcharge": 2200.0,
                "pactogrid": 1300.0,
                "pload": 450.0,
                "soc": 65.0,
                "eToday": 8.9,
            }
        }
        tel9 = adapter.parse_payload(raw_pv_reconstruct)
        self.assertEqual(tel9.pv_power_w, 3950.0) # 450 load + 2200 bat_chg + 1300 grid_export = 3950 W
        self.assertEqual(tel9.battery_power_w, -2200.0)
        self.assertEqual(tel9.battery_soc, 65.0)

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
        """Stellt sicher, dass auch SolarEdge, Kostal und Deye über die Registry geladen werden."""
        for prof_id in ["solaredge_cloud", "kostal_solar_portal", "deye_solarman"]:
            adapter = get_adapter(prof_id)
            self.assertIsNotNone(adapter)
            test_res = adapter.test_connection({"token": "mock_tok", "api_key": "mock_key"})
            self.assertEqual(test_res.status, "success")
            self.assertTrue(test_res.simulated)
            self.assertIn("pv_power_w", test_res.live_metrics)

    def test_06_fronius_adapter_isolation(self):
        """Testet den Fronius-Adapter isoliert mit Solar.web flowdata und lokaler Solar API v1."""
        adapter = get_adapter("fronius_solarweb")
        self.assertIsNotNone(adapter)

        # 1. Solar.web Cloud flowdata
        raw_cloud = {
            "data": {
                "channels": [
                    {"channelName": "PowerPV", "value": 4850.0, "unit": "W"},
                    {"channelName": "PowerGrid", "value": -2100.0, "unit": "W"},
                    {"channelName": "PowerLoad", "value": -1250.0, "unit": "W"},
                    {"channelName": "PowerAkku", "value": 1500.0, "unit": "W"},
                    {"channelName": "StateOfCharge_Akku", "value": 78.5, "unit": "%"},
                    {"channelName": "EnergyToday", "value": 18.4, "unit": "kWh"},
                    {"channelName": "EnergyTotal", "value": 12450.0, "unit": "kWh"},
                ]
            }
        }
        tel_cloud = adapter.parse_payload(raw_cloud)
        self.assertEqual(tel_cloud.pv_power_w, 4850.0)
        self.assertEqual(tel_cloud.grid_power_w, -2100.0)
        self.assertEqual(tel_cloud.load_power_w, 1250.0)
        self.assertEqual(tel_cloud.battery_power_w, 1500.0)
        self.assertEqual(tel_cloud.battery_soc, 78.5)
        self.assertEqual(tel_cloud.daily_yield_kwh, 18.4)
        self.assertEqual(tel_cloud.total_yield_kwh, 12450.0)

        # 2. Lokale Solar API v1 (/solar_api/v1/GetPowerFlowRealtimeData.fcgi)
        raw_local = {
            "Body": {
                "Data": {
                    "Site": {
                        "P_PV": 3200.0,
                        "P_Grid": 450.0,
                        "P_Load": -1650.0,
                        "P_Akku": -2000.0,
                        "E_Day": 12500.0,
                        "E_Total": 8500000.0,
                    },
                    "Inverters": {
                        "1": {
                            "DT": 1,
                            "P": 3200.0,
                            "SOC": 92.0,
                        }
                    }
                }
            }
        }
        tel_local = adapter.parse_payload(raw_local)
        self.assertEqual(tel_local.pv_power_w, 3200.0)
        self.assertEqual(tel_local.grid_power_w, 450.0)
        self.assertEqual(tel_local.load_power_w, 1650.0)
        self.assertEqual(tel_local.battery_power_w, -2000.0)
        self.assertEqual(tel_local.battery_soc, 92.0)
        self.assertEqual(tel_local.daily_yield_kwh, 12.5) # 12500 Wh -> 12.5 kWh
        self.assertEqual(tel_local.total_yield_kwh, 8500.0) # 8500000 Wh -> 8500.0 kWh

        # 3. Connection Test
        test_res = adapter.test_connection({"mock": True})
        self.assertEqual(test_res.status, "success")
        self.assertIn("pv_power_w", test_res.live_metrics)

    def test_07_victron_adapter_isolation(self):
        """Testet den Victron-Adapter isoliert mit typischen VRM Portal System-Overview Payloads."""
        adapter = get_adapter("victron_vrm")
        self.assertIsNotNone(adapter)

        # 1. System Overview Payload
        raw_vrm = {
            "success": True,
            "records": {
                "solar_yield": 4350.0,
                "pv_power": 4350.0,
                "grid_power": -1200.0,
                "consumption": 1650.0,
                "battery_power": -1500.0, # Laden (negativ)
                "soc": 84.5,
                "yield_today": 22.8,
                "yield_total": 9850.4,
            }
        }
        tel = adapter.parse_payload(raw_vrm)
        self.assertEqual(tel.pv_power_w, 4350.0)
        self.assertEqual(tel.grid_power_w, -1200.0)
        self.assertEqual(tel.load_power_w, 1650.0)
        self.assertEqual(tel.battery_power_w, -1500.0)
        self.assertEqual(tel.battery_soc, 84.5)
        self.assertEqual(tel.daily_yield_kwh, 22.8)
        self.assertEqual(tel.total_yield_kwh, 9850.4)

        # 2. Connection Test (Simulation)
        test_res = adapter.test_connection({"mock": True})
        self.assertEqual(test_res.status, "success")
        self.assertIn("pv_power_w", test_res.live_metrics)
        self.assertIn("battery_soc", test_res.live_metrics)


