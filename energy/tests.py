from decimal import Decimal
from django.test import TestCase
from django.contrib.auth import get_user_model
from django.utils import timezone

from energy.flow_engine import calculate_energy_flow
from energy.services.sankey import build_live_sankey
from energy.ems.services import build_device_signals
from energy.models import EMSSignalType, EMSSignalSource
from devices.models import Home, Device, DeviceConfig, DeviceRole, MetricDefinition

User = get_user_model()


class EnergyFlowEngineTest(TestCase):
    def test_calculate_energy_flow_basic(self):
        signals = {
            "pv": {"production": 5000},
            "battery": {"charge": 1000, "discharge": 0},
            "grid": {"import": 500, "export": 0},
            "load": {"consumption": 4500},
        }
        flow = calculate_energy_flow(signals)

        self.assertIn("pv_to_load", flow)
        self.assertIn("pv_to_battery", flow)
        self.assertIn("pv_to_grid", flow)
        self.assertIn("battery_to_load", flow)
        self.assertIn("grid_to_load", flow)

    def test_calculate_energy_flow_empty(self):
        flow = calculate_energy_flow({})
        self.assertEqual(flow["pv_to_load"], 0)
        self.assertEqual(flow["pv_to_battery"], 0)
        self.assertEqual(flow["pv_to_grid"], 0)
        self.assertEqual(flow["battery_to_load"], 0)
        self.assertEqual(flow["grid_to_load"], 0)


class EMSSignalServiceTest(TestCase):
    def setUp(self):
        from django.core.cache import cache
        cache.clear()

        self.user = User.objects.create_user(
            username="testenergyuser",
            email="energy@example.com",
            password="testpassword123",
        )
        self.home = Home.objects.create(
            user=self.user,
            name="Test Home",
        )
        self.signal_pv = EMSSignalType.objects.create(key="pv", label="PV")
        self.signal_grid = EMSSignalType.objects.create(key="grid", label="Grid")

        self.pv_device = Device.objects.create(
            home=self.home,
            identifier="pv_inverter_1",
            configured=True,
        )
        self.grid_device = Device.objects.create(
            home=self.home,
            identifier="grid_meter_1",
            configured=True,
        )

        EMSSignalSource.objects.create(
            home=self.home,
            device=self.pv_device,
            signal_type=self.signal_pv,
        )
        EMSSignalSource.objects.create(
            home=self.home,
            device=self.grid_device,
            signal_type=self.signal_grid,
        )

    def test_build_device_signals_empty_cache(self):
        signals = build_device_signals(self.user)
        self.assertIn("pv", signals)
        self.assertIn("grid", signals)
        self.assertIn("battery", signals)
        self.assertIn("load", signals)
        self.assertEqual(signals["pv"]["production"], 0)
        self.assertEqual(signals["grid"]["import"], 0)
        self.assertEqual(signals["grid"]["export"], 0)


class EnergyBalanceAPITest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="testbalanceuser",
            email="balance@example.com",
            password="testpassword123",
        )
        self.client.force_login(self.user)

    def test_energy_balance_empty_user(self):
        response = self.client.get("/api/energy/balance/?period=today")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn("kpis", data)
        self.assertIn("submeters", data)
        self.assertIn("charts", data)

    def test_energy_balance_seed_and_calculate(self):
        seed_resp = self.client.post("/api/energy/seed-demo/")
        self.assertEqual(seed_resp.status_code, 200)
        self.assertEqual(seed_resp.json()["status"], "ok")

        for p in ["today", "7d", "30d", "year"]:
            resp = self.client.get(f"/api/energy/balance/?period={p}")
            self.assertEqual(resp.status_code, 200)
            data = resp.json()
            self.assertIn("kpis", data)
            self.assertGreaterEqual(data["kpis"]["pv_generation_kwh"], 0)
            self.assertGreater(len(data["submeters"]), 0)
            for sm in data["submeters"]:
                self.assertTrue(bool(sm["name"]))

        # Check 7d specifically has positive PV and consumption
        resp_7d = self.client.get("/api/energy/balance/?period=7d").json()
        self.assertGreater(resp_7d["kpis"]["pv_generation_kwh"], 0)
        self.assertGreater(resp_7d["kpis"]["house_consumption_kwh"], 0)

    def test_energy_optimizer_api(self):
        # Seed demo user
        self.client.post("/api/energy/seed-demo/")

        response = self.client.get("/api/energy/optimizer/?horizon=24")
        self.assertEqual(response.status_code, 200)
        data = response.json()

        self.assertIn("timeline", data)
        self.assertIn("windows", data)
        self.assertIn("1h", data["windows"])
        self.assertIn("2h", data["windows"])
        self.assertIn("4h", data["windows"])

        # Check 1h, 2h, 4h windows structure
        for dur in ["1h", "2h", "4h"]:
            win_info = data["windows"][dur]
            self.assertIn("best_overall", win_info)
            self.assertIn("savings_eur", win_info)
            best = win_info["best_overall"]
            self.assertIn("start_label", best)
            self.assertIn("end_label", best)
            self.assertIn("avg_cost_ct", best)

    def test_battery_soc_forecast_api(self):
        self.client.post("/api/energy/seed-demo/")

        response = self.client.get("/api/energy/battery-forecast/?horizon=24")
        self.assertEqual(response.status_code, 200)
        data = response.json()

        self.assertIn("parameters", data)
        self.assertIn("kpis", data)
        self.assertIn("timeline", data)
        self.assertEqual(len(data["timeline"]), 24)

        kpis = data["kpis"]
        self.assertIn("start_soc_pct", kpis)
        self.assertIn("end_soc_pct", kpis)
        self.assertIn("total_charged_kwh", kpis)
        self.assertIn("total_discharged_kwh", kpis)
        self.assertIn("night_autarky_pct", kpis)

        slot0 = data["timeline"][0]
        self.assertIn("soc_pct", slot0)
        self.assertIn("stored_kwh", slot0)
        self.assertIn("bat_flow_kw", slot0)
        self.assertIn("status", slot0)
