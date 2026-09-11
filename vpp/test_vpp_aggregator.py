from decimal import Decimal
from datetime import date
from django.test import TestCase
from django.contrib.auth import get_user_model
from django.utils import timezone
from rest_framework.test import APIClient

from devices.models import Home, Device, DeviceRole, DeviceConfig, DeviceLatestMetric
from energy.models import SteuVEDeviceConfig
from vpp.models import VPPFlexibilityPool, VPPDispatchOrder, VPPDispatchTelemetry
from vpp.services_vpp import (
    calculate_fleet_flexibility,
    generate_redispatch_schedule_15min,
    trigger_vpp_dispatch,
)

User = get_user_model()


class VPPAggregatorTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="vpp_admin", email="vpp@sharegy.cloud", password="password123", is_staff=True
        )
        self.home = Home.objects.create(user=self.user, name="VPP Asset Home", postal_code="10115")

        # Rollen & Geräte anlegen
        self.role_battery, _ = DeviceRole.objects.get_or_create(key="battery", defaults={"label": "Batterie"})
        self.role_producer, _ = DeviceRole.objects.get_or_create(key="producer", defaults={"label": "PV-Anlage"})

        self.dev_bat = Device.objects.create(home=self.home, identifier="BAT-001", active=True, configured=True)
        DeviceConfig.objects.create(device=self.dev_bat, home=self.home, role=self.role_battery, name="Heimspeicher 10kWh")

        # Metrik für Batterie (SoC 80%, 10 kWh, 5 kW)
        now = timezone.now()
        DeviceLatestMetric.objects.create(device=self.dev_bat, metric_key="soc", value=80.0, unit="%", timestamp=now)
        DeviceLatestMetric.objects.create(device=self.dev_bat, metric_key="capacity_kwh", value=10.0, unit="kWh", timestamp=now)
        DeviceLatestMetric.objects.create(device=self.dev_bat, metric_key="max_power_kw", value=5.0, unit="kW", timestamp=now)

        self.dev_pv = Device.objects.create(home=self.home, identifier="PV-001", active=True, configured=True)
        DeviceConfig.objects.create(device=self.dev_pv, home=self.home, role=self.role_producer, name="PV 10kWp")

        # § 14a EnWG SteuVE Wallbox
        self.role_consumer, _ = DeviceRole.objects.get_or_create(key="consumer", defaults={"label": "Verbraucher"})
        self.dev_wb = Device.objects.create(home=self.home, identifier="WB-001", active=True, configured=True)
        DeviceConfig.objects.create(device=self.dev_wb, home=self.home, role=self.role_consumer, name="Wallbox 11kW")

        self.steuve = SteuVEDeviceConfig.objects.create(
            device=self.dev_wb,
            steuve_type="wallbox",
            rated_power_kw=Decimal("11.00"),
            minimum_power_kw=Decimal("1.40"),
            is_dimmable=True,
        )

        self.pool = VPPFlexibilityPool.objects.create(
            name="50Hertz SRL-Pool Test",
            tso_operator="50hertz",
            market_product="afrr_positive",
            grid_region="Berlin-Brandenburg",
            postal_code_prefix="10*",
        )

        self.client = APIClient()
        self.client.force_authenticate(user=self.user)

    def test_calculate_fleet_flexibility(self):
        fleet = calculate_fleet_flexibility()
        self.assertGreater(fleet["summary"]["total_available_positive_flex_kw"], 0.0)
        self.assertGreater(fleet["summary"]["total_available_negative_flex_kw"], 0.0)
        self.assertEqual(fleet["battery_fleet"]["assets_count"], 1)
        self.assertEqual(fleet["battery_fleet"]["average_soc_pct"], 80.0)
        self.assertEqual(fleet["steuve_and_loads"]["assets_count"], 1)
        self.assertEqual(fleet["pv_curtailment"]["assets_count"], 1)

    def test_generate_redispatch_schedule_15min(self):
        schedule = generate_redispatch_schedule_15min(target_date=date(2026, 9, 15), tso_operator="50hertz")
        self.assertEqual(schedule["slots_count"], 96)
        self.assertEqual(schedule["resolution"], "PT15M")
        self.assertEqual(len(schedule["schedule"]), 96)
        self.assertIn("planned_net_power_kw", schedule["schedule"][0])
        self.assertIn("p_max_kw", schedule["schedule"][0])
        self.assertIn("p_min_kw", schedule["schedule"][0])

    def test_trigger_vpp_dispatch(self):
        order = trigger_vpp_dispatch(
            target_power_kw=Decimal("50.00"),
            duration_minutes=15,
            dispatch_type="positive_flex",
            requested_by="50Hertz Leitsystem",
            pool=self.pool,
        )

        self.assertEqual(order.status, "active")
        self.assertEqual(order.target_power_kw, Decimal("50.00"))
        self.assertGreater(order.telemetry_points.count(), 0)
        self.assertGreater(order.remuneration_eur, Decimal("0.00"))

    def test_vpp_rest_api_endpoints(self):
        # 1. Summary
        resp = self.client.get("/api/vpp/summary/")
        self.assertEqual(resp.status_code, 200)
        self.assertIn("summary", resp.json())

        # 2. Flexibility
        resp = self.client.get("/api/vpp/flexibility/")
        self.assertEqual(resp.status_code, 200)
        self.assertIn("available_positive_power_kw", resp.json())

        # 3. Redispatch Schedule
        resp = self.client.get("/api/vpp/redispatch-schedule/?tso=50hertz")
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.json()["slots_count"], 96)

        # 4. Pools
        resp = self.client.get("/api/vpp/pools/")
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.json()["count"], 1)

        # 5. Dispatch Order POST
        resp = self.client.post("/api/vpp/dispatch/", {
            "target_power_kw": 25.0,
            "duration_minutes": 15,
            "dispatch_type": "positive_flex",
            "requested_by": "TenneT Automated Balancing",
            "pool_id": str(self.pool.id),
        }, format="json")
        self.assertEqual(resp.status_code, 201)
        order_id = resp.json()["id"]

        # 6. Dispatch Detail GET
        resp_detail = self.client.get(f"/api/vpp/dispatch/{order_id}/")
        self.assertEqual(resp_detail.status_code, 200)
        self.assertEqual(resp_detail.json()["status"], "active")
        self.assertIn("telemetry", resp_detail.json())

        # 7. Cancel POST
        resp_cancel = self.client.post(f"/api/vpp/dispatch/{order_id}/cancel/")
        self.assertEqual(resp_cancel.status_code, 200)
        self.assertEqual(resp_cancel.json()["status"], "cancelled")
