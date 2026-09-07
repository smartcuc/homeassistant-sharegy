"""
energy/test_fuel_radar.py

Unit- und Integrationstests für das Mobilitäts- & Spritpreis-Radar:
1. Geokoordinaten-Ermittlung (PLZ / Home-Location).
2. Tankerkönig-Service / Simulations-Engine für Tankstellen im Umkreis.
3. 100-km Real-Kostenvergleich (EV Solar vs. EV Spot vs. Diesel vs. E10).
4. Tageszeit-Tankempfehlungen.
5. REST API Endpunkt /api/energy/fuel-radar/.
"""

from django.test import TestCase
from django.core.cache import cache
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient

from devices.models import Home
from energy.services.tankerkoenig import (
    get_home_coordinates,
    fetch_fuel_radar_data,
    generate_simulated_stations,
)

User = get_user_model()


class FuelRadarTests(TestCase):
    def setUp(self):
        cache.clear()
        self.user = User.objects.create_user(
            username="mobility_tester@sharegy.cloud",
            email="mobility_tester@sharegy.cloud",
            password="securePassword123!",
        )
        self.home = Home.objects.create(
            name="Mobilhaus Berlin",
            user=self.user,
            postal_code="10115",
            city="Berlin",
            latitude=52.5200,
            longitude=13.4050,
        )
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)

    def tearDown(self):
        cache.clear()

    def test_get_home_coordinates(self):
        """Prüft das Auslesen und Fallbacken von Geokoordinaten."""
        lat, lng = get_home_coordinates(self.home)
        self.assertAlmostEqual(lat, 52.5200, places=3)
        self.assertAlmostEqual(lng, 13.4050, places=3)

        # Home ohne Koordinaten aber mit PLZ 80xxx (München)
        home_muc = Home.objects.create(
            name="München Haus",
            user=self.user,
            postal_code="80331",
            city="München",
        )
        lat_m, lng_m = get_home_coordinates(home_muc)
        self.assertAlmostEqual(lat_m, 48.1351, places=2)
        self.assertAlmostEqual(lng_m, 11.5820, places=2)

    def test_simulated_stations_generation(self):
        """Prüft die Generierung realistischer Tankstellen im Umkreis."""
        stations = generate_simulated_stations(52.5200, 13.4050, radius_km=5.0)
        self.assertGreaterEqual(len(stations), 3)

        first_st = stations[0]
        self.assertIn("brand", first_st)
        self.assertIn("diesel", first_st)
        self.assertIn("e5", first_st)
        self.assertIn("e10", first_st)
        self.assertGreater(first_st["e10"], 1.40)
        self.assertLess(first_st["e10"], 2.20)
        self.assertLessEqual(first_st["dist_km"], 5.0)

    def test_fetch_fuel_radar_data_and_cost_comparison(self):
        """Prüft die Gesamtergebnisse inkl. 100km-Kostenvergleich."""
        data = fetch_fuel_radar_data(self.home, radius_km=10.0, fuel_type="e10")

        self.assertEqual(data["status"], "success")
        self.assertEqual(data["radius_km"], 10.0)
        self.assertIn("best_prices", data)
        self.assertIn("e10", data["best_prices"])
        self.assertIn("diesel", data["best_prices"])

        # 100km-Kostenvergleich prüfen
        comp = data["cost_comparison_100km"]
        self.assertIn("ev_solar_cost_eur", comp)
        self.assertIn("gasoline_e10_cost_eur", comp)
        self.assertIn("savings_vs_gasoline_per_100km_eur", comp)

        # E-Auto Solar (~1.44 €) muss drastisch günstiger sein als Benziner (~12 €)
        self.assertLess(comp["ev_solar_cost_eur"], 2.50)
        self.assertGreater(comp["gasoline_e10_cost_eur"], 8.00)
        self.assertGreater(comp["savings_vs_gasoline_per_100km_eur"], 5.00)

        # Tageszeit-Tipp
        timing = data["timing_advice"]
        self.assertIn("badge", timing)
        self.assertIn("best_window", timing)

    def test_api_fuel_radar_endpoint(self):
        """Testet den REST API Endpunkt /api/energy/fuel-radar/."""
        response = self.client.get("/api/energy/fuel-radar/?radius_km=5.0&fuel_type=diesel")
        self.assertEqual(response.status_code, 200)

        res_data = response.data
        self.assertEqual(res_data["status"], "success")
        self.assertIn("stations", res_data)
        self.assertGreaterEqual(len(res_data["stations"]), 1)
        self.assertIn("cost_comparison_100km", res_data)
