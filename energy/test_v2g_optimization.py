###########################################
# energy/test_v2g_optimization.py
# Unit- & Integrationstests für V2G / V2H Optimierungsalgorithmen (ISO 15118-20)
###########################################

import datetime
from decimal import Decimal
from django.test import TestCase
from django.contrib.auth import get_user_model
from django.utils import timezone
from rest_framework.test import APIClient
from rest_framework import status

from devices.models import Home
from devices.models_ocpp import ChargingStation, ChargingSession
from energy.services.services_v2g import V2GDispatchEngine

User = get_user_model()


class V2GOptimizationAlgorithmTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="v2g_driver",
            email="v2g@sharegy.de",
            password="securepassword123"
        )
        self.home = Home.objects.create(
            user=self.user,
            name="V2G Test Home"
        )
        self.station = ChargingStation.objects.create(
            home=self.home,
            charge_point_id="WB-V2G-TEST-01",
            name="Bidirectional Wallbox Pro",
            phases=3,
            max_current_a=16.0,
            voltage_v=230.0,
            supports_bidirectional=True,
            v2g_mode="v2h_home",
            v2g_min_soc_pct=40,
            v2g_max_discharge_power_kw=11.0,
            ev_battery_capacity_kwh=77.0,
            ev_soc_pct=75.0,
            departure_time=datetime.time(7, 30),
            target_departure_soc_pct=80,
            peak_shaving_threshold_w=4200.0,
            battery_care_mode=True,
            max_c_rate=0.5,
            is_online=True
        )
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)

    def test_smart_departure_schedule_charging_must_start(self):
        """Wenn Abfahrt in 1 Stunde ist und Akku von 50% auf 80% geladen werden muss -> muss sofort laden."""
        self.station.ev_soc_pct = 50.0
        self.station.departure_time = datetime.time(8, 0)
        self.station.target_departure_soc_pct = 80
        self.station.save()

        # Simuliere aktuelle Zeit: 07:00 (1h vor Abfahrt)
        test_now = timezone.make_aware(datetime.datetime(2026, 9, 10, 7, 0, 0))

        schedule = V2GDispatchEngine.calculate_departure_schedule(self.station, current_time=test_now)
        self.assertTrue(schedule["has_departure_schedule"])
        self.assertTrue(schedule["charging_must_start"])
        self.assertGreater(schedule["time_needed_hours"], 1.5)

        # Dispatch-Aufruf muss "charging" zurückgeben
        dispatch = V2GDispatchEngine.calculate_v2x_dispatch(self.station, None, 80.0, current_time=test_now)
        self.assertEqual(dispatch["mode"], "charging")
        self.assertGreater(dispatch["target_power_w"], 0.0)
        self.assertEqual(dispatch["target_current_a"], 16.0)
        self.assertIn("Smart Departure", dispatch["reason"])

    def test_smart_departure_schedule_sufficient_soc(self):
        """Wenn aktueller SoC >= Ziel-SoC -> kein Vorab-Laden erzwungen."""
        self.station.ev_soc_pct = 85.0
        self.station.target_departure_soc_pct = 80
        self.station.departure_time = datetime.time(8, 0)
        self.station.save()

        test_now = timezone.make_aware(datetime.datetime(2026, 9, 10, 7, 30, 0))
        schedule = V2GDispatchEngine.calculate_departure_schedule(self.station, current_time=test_now)
        self.assertFalse(schedule["charging_must_start"])
        self.assertEqual(schedule["time_needed_hours"], 0.0)

    def test_peak_shaving_mode_triggers_discharge(self):
        """Peak Shaving: Wenn Hauslast 6,5 kW und Schwelle 4,2 kW -> Entladung von ca. 2,3 kW."""
        self.station.v2g_mode = "peak_shaving"
        self.station.ev_soc_pct = 70.0
        self.station.peak_shaving_threshold_w = 4200.0
        self.station.save()

        class MockHomeMetric:
            pv_power_w = 0.0
            house_power_w = 6500.0
            battery_soc_pct = 10.0
            battery_power_w = 0.0

        dispatch = V2GDispatchEngine.calculate_v2x_dispatch(self.station, MockHomeMetric(), 80.0)
        self.assertEqual(dispatch["mode"], "discharging")
        self.assertAlmostEqual(dispatch["target_power_w"], -2300.0, delta=50.0)
        self.assertIn("Peak Shaving", dispatch["reason"])

    def test_peak_shaving_mode_idle_when_below_threshold(self):
        """Peak Shaving: Wenn Hauslast 3,0 kW unter 4,2 kW Schwelle -> Idle."""
        self.station.v2g_mode = "peak_shaving"
        self.station.ev_soc_pct = 70.0
        self.station.peak_shaving_threshold_w = 4200.0
        self.station.save()

        class MockHomeMetric:
            pv_power_w = 0.0
            house_power_w = 3000.0
            battery_soc_pct = 10.0
            battery_power_w = 0.0

        dispatch = V2GDispatchEngine.calculate_v2x_dispatch(self.station, MockHomeMetric(), 80.0)
        self.assertEqual(dispatch["mode"], "idle")
        self.assertEqual(dispatch["target_power_w"], 0.0)

    def test_battery_care_c_rate_limit(self):
        """Battery Care: C-Rate von 0.3C bei 50 kWh Akku limitiert Entladung auf 15 kW."""
        self.station.ev_battery_capacity_kwh = 50.0
        self.station.max_c_rate = 0.3
        self.station.v2g_max_discharge_power_kw = 22.0
        self.station.battery_care_mode = True
        self.station.save()

        safe_power = V2GDispatchEngine.apply_battery_care_limits(
            self.station,
            requested_discharge_w=22000.0,
            current_soc=80.0,
            effective_min_soc=40.0
        )
        self.assertEqual(safe_power, 15000.0)

    def test_v2g_grid_arbitrage_with_degradation_margin(self):
        """V2G Börsenstrom-Arbitrage speist bei Preisen über 33.5 ct/kWh ein."""
        self.station.v2g_mode = "v2g_grid"
        self.station.ev_soc_pct = 80.0
        self.station.save()

        # Fall 1: Preis 40 ct/kWh (400 EUR/MWh) -> Volle Netzeinspeisung
        dispatch_high = V2GDispatchEngine.calculate_v2x_dispatch(self.station, None, 400.0)
        self.assertEqual(dispatch_high["mode"], "discharging")
        self.assertEqual(dispatch_high["target_power_w"], -11000.0)

        # Fall 2: Preis 25 ct/kWh (250 EUR/MWh) -> Idle
        dispatch_low = V2GDispatchEngine.calculate_v2x_dispatch(self.station, None, 250.0)
        self.assertEqual(dispatch_low["mode"], "idle")

    def test_v2x_auto_mode_priority_cascade(self):
        """V2X Auto: Priorisiert Peak Shaving vor Börsenarbitrage vor V2H."""
        self.station.v2g_mode = "v2x_auto"
        self.station.ev_soc_pct = 75.0
        self.station.peak_shaving_threshold_w = 4000.0
        self.station.save()

        # 1. Extreme Lastspitze (7 kW) -> Peak Shaving Prio 1
        class PeakMetric:
            pv_power_w = 0.0
            house_power_w = 7000.0
            battery_soc_pct = 10.0
            battery_power_w = 0.0

        dispatch = V2GDispatchEngine.calculate_v2x_dispatch(self.station, PeakMetric(), 100.0)
        self.assertEqual(dispatch["mode"], "discharging")
        self.assertAlmostEqual(dispatch["target_power_w"], -3000.0, delta=50.0)
        self.assertIn("Lastspitzenkappung", dispatch["reason"])

        # 2. Hoher Börsenpreis (360 EUR/MWh = 36 ct) ohne Lastspitze -> Netzeinspeisung Prio 2
        class LowLoadMetric:
            pv_power_w = 0.0
            house_power_w = 1000.0
            battery_soc_pct = 10.0
            battery_power_w = 0.0

        dispatch_spot = V2GDispatchEngine.calculate_v2x_dispatch(self.station, LowLoadMetric(), 360.0)
        self.assertEqual(dispatch_spot["mode"], "discharging")
        self.assertEqual(dispatch_spot["target_power_w"], -11000.0)

        # 3. Normaler Preis, Hausbedarf 2.5 kW -> V2H Hauspuffer Prio 3
        dispatch_v2h = V2GDispatchEngine.calculate_v2x_dispatch(self.station, LowLoadMetric(), 100.0)
        self.assertEqual(dispatch_v2h["mode"], "discharging")
        self.assertEqual(dispatch_v2h["target_power_w"], -1000.0)

    def test_api_patch_and_v2g_mode_configuration(self):
        """REST-API Test: Aktualisierung von Abfahrtszeit, Peak Shaving und V2G-Parametern."""
        url = f"/api/energy/wallboxes/{self.station.id}/"
        payload = {
            "v2g_mode": "peak_shaving",
            "departure_time": "06:45",
            "target_departure_soc_pct": 85,
            "peak_shaving_threshold_w": 3800.0,
            "battery_care_mode": True,
            "max_c_rate": 0.4
        }
        res = self.client.patch(url, payload, format="json")
        self.assertEqual(res.status_code, status.HTTP_200_OK)

        self.station.refresh_from_db()
        self.assertEqual(self.station.v2g_mode, "peak_shaving")
        self.assertEqual(self.station.departure_time, datetime.time(6, 45))
        self.assertEqual(self.station.target_departure_soc_pct, 85)
        self.assertEqual(self.station.peak_shaving_threshold_w, 3800.0)
        self.assertTrue(self.station.battery_care_mode)
        self.assertEqual(self.station.max_c_rate, 0.4)

        # GET Request Prüfung
        list_res = self.client.get("/api/energy/wallboxes/")
        self.assertEqual(list_res.status_code, status.HTTP_200_OK)
        wb_data = [w for w in list_res.data["wallboxes"] if w["id"] == str(self.station.id)][0]
        self.assertEqual(wb_data["departure_time"], "06:45")
        self.assertEqual(wb_data["target_departure_soc_pct"], 85)
        self.assertEqual(wb_data["peak_shaving_threshold_w"], 3800.0)
