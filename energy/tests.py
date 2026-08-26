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

    def test_battery_soc_forecast_with_custom_storage_system(self):
        from producer.models import StorageSystem
        from devices.models import DeviceLatestMetric

        home = Home.objects.create(user=self.user, name="Custom Storage Home")
        bat_dev = Device.objects.create(home=home, identifier="custom_byd_hvs", active=True)
        DeviceLatestMetric.objects.create(
            device=bat_dev,
            metric_key="soc",
            value=82.5,
            timestamp=timezone.now(),
        )

        StorageSystem.objects.create(
            home=home,
            name="BYD Premium Speicher",
            capacity_kwh=15.0,
            max_charge_power_kw=7.5,
            max_discharge_power_kw=7.5,
            min_soc_reserve_pct=12.0,
            soc_device=bat_dev,
            soc_metric_key="soc",
            primary_device=bat_dev,
            active=True,
        )

        response = self.client.get("/api/energy/battery-forecast/?horizon=24")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertTrue(data.get("has_battery"))
        params = data.get("parameters", {})
        self.assertEqual(params.get("battery_name"), "BYD Premium Speicher")
        self.assertEqual(params.get("capacity_kwh"), 15.0)
        self.assertEqual(params.get("current_soc_pct"), 82.5)
        self.assertEqual(params.get("min_soc_reserve_pct"), 12.0)


class SubmeterTrendsTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="trendtestuser",
            email="trends@example.com",
            password="testpassword123",
        )
        self.home = Home.objects.create(user=self.user, name="Trend Test Home")

    def test_submeter_trends_api_and_service(self):
        from energy.services.submeter_trends import get_submeter_trends

        # 1. Service Test
        data_30d = get_submeter_trends(self.user, period="30d")
        self.assertIn("meters", data_30d)
        self.assertIn("timeseries", data_30d)
        self.assertGreaterEqual(len(data_30d["meters"]), 2)
        self.assertIn("selected_meter", data_30d)
        self.assertIn("selected_timeseries", data_30d)

        # 2. API Endpoint Test
        self.client.force_login(self.user)
        response = self.client.get("/api/energy/submeters/trends/?period=7d")
        self.assertEqual(response.status_code, 200)
        json_data = response.json()
        self.assertEqual(json_data.get("period"), "7d")
        self.assertIsInstance(json_data.get("meters"), list)
        self.assertIsInstance(json_data.get("timeseries"), list)
        self.assertGreater(len(json_data.get("timeseries")), 0)


class GrafanaAndHomeAssistantPluginTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="pluginuser",
            email="plugin@example.com",
            password="testpassword123",
        )
        self.home = Home.objects.create(
            user=self.user,
            name="Plugin Test Home",
        )
        self.token = self.home.mqtt_token

    def test_grafana_endpoints_with_auth(self):
        # 1. Test unauthenticated request fails
        res_unauth = self.client.get("/api/grafana/")
        self.assertIn(res_unauth.status_code, [401, 403])

        # 2. Test Bearer Token Auth on Root
        res_root = self.client.get(
            "/api/grafana/",
            HTTP_AUTHORIZATION=f"Bearer {self.token}",
        )
        self.assertEqual(res_root.status_code, 200)
        self.assertEqual(res_root.json().get("status"), "success")

        # 3. Test X-API-Key Auth on Search
        res_search = self.client.post(
            "/api/grafana/search",
            HTTP_X_API_KEY=self.token,
        )
        self.assertEqual(res_search.status_code, 200)
        self.assertIn("pv_power_w", res_search.json())
        self.assertIn("load_power_w", res_search.json())
        self.assertIn("battery_soc_pct", res_search.json())

        # 4. Test Query Endpoint
        res_query = self.client.post(
            "/api/grafana/query",
            data={
                "range": {"from": "2026-08-25T00:00:00Z", "to": "2026-08-25T23:59:59Z"},
                "targets": [{"target": "pv_power_w"}, {"target": "load_power_w"}],
            },
            content_type="application/json",
            HTTP_AUTHORIZATION=f"Bearer {self.token}",
        )
        self.assertEqual(res_query.status_code, 200)
        datapoints_list = res_query.json()
        self.assertEqual(len(datapoints_list), 2)
        self.assertEqual(datapoints_list[0]["target"], "pv_power_w")
        self.assertGreater(len(datapoints_list[0]["datapoints"]), 0)

    def test_home_assistant_telemetry_push(self):
        # Test pushing local HA device telemetry to Sharegy
        payload = {
            "devices": [
                {
                    "identifier": "shelly_3em_ha",
                    "name": "Shelly 3EM HA",
                    "power_w": 2840.5,
                    "energy_kwh": 1500.2,
                    "role": "grid",
                },
                {
                    "identifier": "heatpump_ha",
                    "name": "Wärmepumpe HA",
                    "power_w": 1800.0,
                    "energy_kwh": 320.0,
                    "role": "consumer",
                },
            ]
        }

        res_push = self.client.post(
            "/api/devices/telemetry/push/",
            data=payload,
            content_type="application/json",
            HTTP_X_API_KEY=self.token,
        )
        self.assertEqual(res_push.status_code, 200)
        data = res_push.json()
        self.assertEqual(data.get("status"), "success")
        self.assertEqual(data.get("saved_metrics"), 2)
        self.assertIn("shelly_3em_ha", data.get("devices_updated"))

    def test_custom_date_range_and_multi_format_exports(self):
        self.client.force_login(self.user)

        # 1. Custom Date Range Balance
        res_custom = self.client.get(
            "/api/energy/balance/?period=custom&start_date=2026-05-01&end_date=2026-08-15"
        )
        self.assertEqual(res_custom.status_code, 200)
        data = res_custom.json()
        self.assertEqual(data.get("period"), "custom")
        self.assertIn("kpis", data)
        self.assertIn("01.05.2026", data.get("period_label", ""))

        # 2. JSON Export
        res_json = self.client.get(
            "/api/energy/export/balance/?period=custom&start_date=2026-05-01&end_date=2026-08-15&format=json"
        )
        self.assertEqual(res_json.status_code, 200)
        self.assertEqual(res_json["Content-Type"], "application/json; charset=utf-8")

        # 3. CSV Export
        res_csv = self.client.get(
            "/api/energy/export/balance/?period=30d&format=csv"
        )
        self.assertEqual(res_csv.status_code, 200)
        self.assertIn("text/csv", res_csv["Content-Type"])

        # 4. XLSX Export
        res_xlsx = self.client.get(
            "/api/energy/export/balance/?period=today&format=xlsx"
        )
        self.assertEqual(res_xlsx.status_code, 200)
        self.assertIn("spreadsheetml.sheet", res_xlsx["Content-Type"])

        # 5. PDF Export
        res_pdf = self.client.get(
            "/api/energy/export/balance/?period=today&format=pdf"
        )
        self.assertEqual(res_pdf.status_code, 200)
        self.assertEqual(res_pdf["Content-Type"], "application/pdf")

    def test_battery_arbitrage_view(self):
        self.client.force_login(self.user)
        res = self.client.get(
            "/api/energy/battery-arbitrage/"
        )
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertIn("has_battery", data)
        self.assertIn("capacity_kwh", data)
        self.assertIn("roundtrip_efficiency_pct", data)
        self.assertIn("daily_profit_eur", data)
        self.assertIn("timeline", data)
        self.assertGreater(len(data["timeline"]), 0)



