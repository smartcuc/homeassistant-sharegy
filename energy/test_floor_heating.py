"""
energy/test_floor_heating.py

Automatisierte Unit- und Integrationstests für:
1. Fußbodenheizungs- & Estrich-Vorladungs-Engine (Thermal Battery Dispatch).
2. Physikalische Estrich-Speicherberechnung (Masse, Kapazität, thermischer SoC).
3. PV-Überschuss & Börsenstrompreis-Vorladungs-Logik.
4. Überhitzungs- & Komfortschutz-Regeln.
5. REST API Endpunkte für Status, Konfiguration und 1-Klick Vorladeboost.
"""

from decimal import Decimal
from datetime import timedelta
from django.test import TestCase
from django.utils import timezone
from django.core.cache import cache
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient

from devices.models import Home, Device, DeviceRole, DeviceConfig
from energy.models import FloorHeatingConfig
from energy.services.floor_heating_manager import (
    evaluate_floor_heating,
    find_or_create_floor_heating_config,
    calculate_thermal_storage_metrics,
    calculate_predictive_flow_temperature,
    generate_24h_predictive_heating_schedule,
    trigger_floor_heating_boost,
    actuate_floor_heating_relay,
)
from energy.services.dispatch_hub import get_all_load_consumers, execute_hub_device_action

User = get_user_model()


class FloorHeatingTests(TestCase):
    def setUp(self):
        cache.clear()
        self.user = User.objects.create_user(
            username="heating_tester@sharegy.cloud",
            email="heating_tester@sharegy.cloud",
            password="securePassword123!",
        )
        self.home = Home.objects.create(
            name="Smart Home Sonnenhang",
            user=self.user,
        )
        self.role_heating = DeviceRole.objects.create(
            key="floor_heating",
            label="Fußbodenheizungs-Pumpe",
        )
        self.dev_heating = Device.objects.create(
            home=self.home,
            identifier="shelly_floor_heating",
            active=True,
        )
        DeviceConfig.objects.create(
            device=self.dev_heating,
            home=self.home,
            name="Fußbodenheizung EG & OG",
            role=self.role_heating,
        )

        self.role_sensor = DeviceRole.objects.create(
            key="climate_sensor",
            label="Raumtemperatursensor",
        )
        self.dev_sensor = Device.objects.create(
            home=self.home,
            identifier="shelly_temp_wohnzimmer",
            active=True,
        )
        DeviceConfig.objects.create(
            device=self.dev_sensor,
            home=self.home,
            name="Raumsensor Wohnzimmer",
            role=self.role_sensor,
        )

        self.config = FloorHeatingConfig.objects.create(
            home=self.home,
            device=self.dev_heating,
            temp_sensor_device=self.dev_sensor,
            active=True,
            control_mode="autopilot",
            target_room_temp_c=Decimal("21.0"),
            boost_delta_k=Decimal("1.0"),
            max_floor_temp_c=Decimal("24.5"),
            min_pv_surplus_w=Decimal("1000.0"),
            max_spot_price_ct_kwh=Decimal("16.00"),
            estrich_area_sqm=Decimal("120.0"),
            min_run_minutes=30,
            min_rest_minutes=15,
        )

        self.client = APIClient()
        self.client.force_authenticate(user=self.user)

    def tearDown(self):
        cache.clear()

    def test_thermal_storage_metrics_calculation(self):
        """Testet die physikalischen Speicherkennzahlen des Estrichs."""
        # Bei 120 m² Fläche -> Masse = 120 * 0.07 * 2000 = 16.800 kg
        # Speicherkapazität = 16800 * 1.0 / 3600 = ~4.67 kWh/K
        metrics_mid = calculate_thermal_storage_metrics(self.config, current_temp=21.0)
        self.assertEqual(metrics_mid["estrich_mass_kg"], 16800.0)
        self.assertEqual(metrics_mid["thermal_capacity_kwh_k"], 4.67)
        # Bei 21.0°C (Mitte zwischen 20.5 und 22.0) -> SoC = 33.3%
        self.assertAlmostEqual(metrics_mid["thermal_soc_pct"], 33.3, places=1)

        # Voll geladen bei 22.0°C -> SoC = 100%
        metrics_full = calculate_thermal_storage_metrics(self.config, current_temp=22.0)
        self.assertEqual(metrics_full["thermal_soc_pct"], 100.0)

    def test_solar_preheating_trigger(self):
        """Bei starkem Solarüberschuss (z. B. 2500 W >= 1000 W) wird die thermische Vorladung aktiv."""
        cache.set(f"device:{self.dev_sensor.id}:temp_room", 21.2)
        cache.set(f"home_{self.home.id}_pv_surplus_w", 2500.0)
        cache.set(f"device_relay_state_{self.dev_heating.id}", False)
        self.config.last_switched_at = timezone.now() - timedelta(hours=1)
        self.config.save()

        res = evaluate_floor_heating(self.home, config=self.config, force=False)

        self.assertTrue(res["relay_state"])
        self.assertTrue(res["is_preheating_active"])
        self.assertIn("Thermische Estrich-Vorladung aktiv", res["decision_reason"])
        self.assertTrue(cache.get(f"device_relay_state_{self.dev_heating.id}"))

    def test_spot_price_preheating_trigger(self):
        """Bei günstigem Börsenstrompreis (z. B. 12.0 ct <= 16.0 ct) und Price-Saver Modus wird Vorladung aktiv."""
        self.config.control_mode = "price_saver"
        self.config.last_switched_at = timezone.now() - timedelta(hours=1)
        self.config.save()

        cache.set(f"device:{self.dev_sensor.id}:temp_room", 21.3)
        cache.set(f"home_{self.home.id}_pv_surplus_w", 0.0)
        cache.set("latest_spot_price_ct_kwh", 12.0)

        res = evaluate_floor_heating(self.home, config=self.config, force=True)
        self.assertTrue(res["relay_state"])
        self.assertTrue(res["is_preheating_active"])

    def test_overheating_protection(self):
        """Überhitzungsschutz: Bei T >= 24.5°C wird die Heizung sofort zwingend abgeschaltet."""
        cache.set(f"device:{self.dev_sensor.id}:temp_room", 24.8)
        cache.set(f"home_{self.home.id}_pv_surplus_w", 5000.0)  # Selbst bei extremem PV-Überschuss!
        cache.set(f"device_relay_state_{self.dev_heating.id}", True)

        res = evaluate_floor_heating(self.home, config=self.config, force=False)

        self.assertFalse(res["relay_state"])
        self.assertFalse(res["is_preheating_active"])
        self.assertIn("Überhitzungsschutz aktiv", res["decision_reason"])
        self.assertFalse(cache.get(f"device_relay_state_{self.dev_heating.id}"))

    def test_under_temp_comfort_protection(self):
        """Untertemperaturschutz: Bei T < 20.5°C (< Ziel - 0.5°C) heizt das System auf Komfortniveau."""
        cache.set(f"device:{self.dev_sensor.id}:temp_room", 19.8)
        cache.set(f"home_{self.home.id}_pv_surplus_w", 0.0)
        cache.set(f"device_relay_state_{self.dev_heating.id}", False)
        self.config.last_switched_at = timezone.now() - timedelta(hours=1)
        self.config.save()

        res = evaluate_floor_heating(self.home, config=self.config, force=False)

        self.assertTrue(res["relay_state"])
        self.assertIn("unter Komfortschwelle", res["decision_reason"])

    def test_dispatch_hub_integration_and_quick_action(self):
        """Prüft die Einbindung der Fußbodenheizung im zentralen Dispatch-Hub."""
        consumers = get_all_load_consumers(self.home)
        fh_consumer = next((c for c in consumers if c["category"] == "floor_heating"), None)

        self.assertIsNotNone(fh_consumer)
        self.assertEqual(fh_consumer["category_label"], "Fußbodenheizung & Estrich")
        self.assertIn("thermal_soc_pct", fh_consumer["details"])

        # Quick Action Boost über Dispatch-Hub auslösen
        action_res = execute_hub_device_action(self.home, category="floor_heating", action="boost_floor_heating")
        self.assertEqual(action_res["status"], "success")
        self.assertTrue(cache.get(f"device_relay_state_{self.dev_heating.id}"))

    def test_api_endpoints_status_and_config(self):
        """Testet die REST API Endpunkte für Floor-Heating."""
        # 1. GET Status
        res_get = self.client.get("/api/energy/floor-heating/")
        self.assertEqual(res_get.status_code, 200)
        self.assertEqual(res_get.data["control_mode"], "autopilot")

        # 2. POST Config
        res_cfg = self.client.post("/api/energy/floor-heating/config/", {
            "control_mode": "pv_only",
            "target_room_temp_c": 21.5,
            "boost_delta_k": 1.5,
            "estrich_area_sqm": 140.0,
            "heating_curve_slope": 0.55,
            "predictive_mpc_enabled": True,
            "solar_gain_compensation": True,
        }, format="json")
        self.assertEqual(res_cfg.status_code, 200)
        self.config.refresh_from_db()
        self.assertEqual(self.config.control_mode, "pv_only")
        self.assertEqual(self.config.target_room_temp_c, Decimal("21.5"))
        self.assertEqual(self.config.boost_delta_k, Decimal("1.5"))
        self.assertEqual(self.config.estrich_area_sqm, Decimal("140.0"))
        self.assertEqual(self.config.heating_curve_slope, Decimal("0.55"))
        self.assertTrue(self.config.predictive_mpc_enabled)
        self.assertTrue(self.config.solar_gain_compensation)

        # 3. POST Boost
        res_boost = self.client.post("/api/energy/floor-heating/boost/", {
            "duration_hours": 3.0,
        }, format="json")
        self.assertEqual(res_boost.status_code, 200)
        self.assertEqual(res_boost.data["status"], "success")
        self.assertTrue(cache.get(f"device_relay_state_{self.dev_heating.id}"))

        # 4. POST Toggle
        res_toggle = self.client.post("/api/energy/floor-heating/toggle/", {
            "state": False,
        }, format="json")
        self.assertEqual(res_toggle.status_code, 200)
        self.assertFalse(cache.get(f"device_relay_state_{self.dev_heating.id}"))

    def test_predictive_flow_temperature_mpc(self):
        """Testet die physikalisch korrekte Berechnung der Vorlauftemperatur nach Heizkurve + MPC."""
        # 1. Kaltes Wetter (5°C), keine Sonne, kein Vorladeboost
        calc_cold = calculate_predictive_flow_temperature(
            config=self.config,
            outdoor_temp_c=5.0,
            solar_radiation_wm2=0.0,
            is_preheat_eligible=False,
        )
        self.assertGreaterEqual(calc_cold["base_flow_temp_c"], 28.0)
        self.assertEqual(calc_cold["solar_offset_k"], 0.0)
        self.assertEqual(calc_cold["preheat_offset_k"], 0.0)

        # 2. Hohe Solarstrahlung (600 W/m²) -> Solares Absenken
        calc_sunny = calculate_predictive_flow_temperature(
            config=self.config,
            outdoor_temp_c=10.0,
            solar_radiation_wm2=600.0,
            is_preheat_eligible=False,
        )
        self.assertGreater(calc_sunny["solar_offset_k"], 1.0)
        self.assertLess(calc_sunny["opt_flow_temp_c"], calc_sunny["base_flow_temp_c"])

        # 3. PV-Vorladung aktiv -> Vorlaufanhebung
        calc_preheat = calculate_predictive_flow_temperature(
            config=self.config,
            outdoor_temp_c=8.0,
            solar_radiation_wm2=150.0,
            is_preheat_eligible=True,
        )
        self.assertEqual(calc_preheat["preheat_offset_k"], 1.5)
        self.assertGreater(calc_preheat["opt_flow_temp_c"], calc_preheat["base_flow_temp_c"])

    def test_predictive_24h_schedule_generation(self):
        """Testet die Generierung des 24h MPC-Fahrplans und der KI-Handlungsempfehlungen."""
        schedule = generate_24h_predictive_heating_schedule(
            home=self.home,
            config=self.config,
            current_room_temp=21.2,
            current_surplus_w=2500.0,
            current_spot_ct=10.5,
        )

        self.assertIn("timeline", schedule)
        self.assertEqual(len(schedule["timeline"]), 24)
        self.assertIn("ai_recommendation_title", schedule)
        self.assertIn("ai_recommendation_text", schedule)
        self.assertIn("best_preheat_window", schedule)
        self.assertIn("best_coast_window", schedule)

        first_slot = schedule["timeline"][0]
        self.assertIn("opt_flow_temp_c", first_slot)
        self.assertIn("action_badge", first_slot)
        self.assertIn("outdoor_temp_c", first_slot)
