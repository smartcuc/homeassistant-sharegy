from django.test import TestCase
from energy.flow_engine import calculate_energy_flow

class BatteryBalanceFlowTest(TestCase):
    def test_grid_charging_without_pv(self):
        # 2500 W Netzbezug: 2000 W in Speicher geladen, 500 W Hausverbrauch
        signals = {
            "pv": {"production": 0.0},
            "battery": {"charge": 2000.0, "discharge": 0.0},
            "grid": {"import": 2500.0, "export": 0.0},
            "load": {"consumption": 0.0},
        }
        flow = calculate_energy_flow(signals)
        self.assertEqual(flow["total_consumption"], 500.0)
        self.assertEqual(flow["grid_to_battery"], 2000.0)
        self.assertEqual(flow["grid_to_load"], 500.0)
        self.assertEqual(flow["pv_to_grid"], 0.0)
        self.assertEqual(flow["pv_to_battery"], 0.0)

    def test_pv_charging_without_grid_export(self):
        # 3000 W PV: 2500 W in Speicher geladen, 500 W Hausverbrauch, 0 W Einspeisung
        signals = {
            "pv": {"production": 3000.0},
            "battery": {"charge": 2500.0, "discharge": 0.0},
            "grid": {"import": 0.0, "export": 0.0},
            "load": {"consumption": 500.0},
        }
        flow = calculate_energy_flow(signals)
        self.assertEqual(flow["total_consumption"], 500.0)
        self.assertEqual(flow["pv_to_battery"], 2500.0)
        self.assertEqual(flow["pv_to_load"], 500.0)
        self.assertEqual(flow["pv_to_grid"], 0.0)
        self.assertEqual(flow["grid_to_battery"], 0.0)

    def test_pv_charging_with_surplus_grid_export(self):
        # 5000 W PV: 2000 W in Speicher, 1000 W Haus, 2000 W Einspeisung
        signals = {
            "pv": {"production": 5000.0},
            "battery": {"charge": 2000.0, "discharge": 0.0},
            "grid": {"import": 0.0, "export": 2000.0},
            "load": {"consumption": 1000.0},
        }
        flow = calculate_energy_flow(signals)
        self.assertEqual(flow["total_consumption"], 1000.0)
        self.assertEqual(flow["pv_to_battery"], 2000.0)
        self.assertEqual(flow["pv_to_load"], 1000.0)
        self.assertEqual(flow["pv_to_grid"], 2000.0)
