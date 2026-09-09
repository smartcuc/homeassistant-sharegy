#################################
# energy/tests_energy_profile.py
#################################

from django.test import TestCase
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from energy.services.energy_profile import calculate_energy_profile_data, get_user_energy_profile, save_user_energy_profile
from devices.models import Home

User = get_user_model()


class EnergyProfileServiceTests(TestCase):
    def test_tenant_profile_a1(self):
        """Profil A.1: Mieter ohne Solar"""
        data = calculate_energy_profile_data(
            solar_type="none",
            has_battery=False,
            has_ev=False,
            has_heatpump=False,
            tariff_type="static"
        )
        self.assertEqual(data["profile_code"], "A.1")
        self.assertEqual(data["recommended_tariff"], "static")
        self.assertGreaterEqual(data["estimated_savings_eur_year"], 50)

    def test_bkw_profile_b1(self):
        """Profil B.1: Balkonkraftwerk ohne Speicher"""
        data = calculate_energy_profile_data(
            solar_type="bkw",
            has_battery=False,
            has_ev=False,
            has_heatpump=False,
            tariff_type="static"
        )
        self.assertEqual(data["profile_code"], "B.1")
        self.assertEqual(data["recommended_tariff"], "static")
        self.assertGreaterEqual(data["estimated_savings_eur_year"], 150)

    def test_bkw_battery_profile_b2(self):
        """Profil B.2: Balkonkraftwerk mit Speicher"""
        data = calculate_energy_profile_data(
            solar_type="bkw",
            has_battery=True,
            has_ev=False,
            has_heatpump=False,
            tariff_type="static"
        )
        self.assertEqual(data["profile_code"], "B.2")

    def test_ev_profile_c1(self):
        """Profil C.1: E-Auto ohne PV -> Dynamischer Tarif empfohlen"""
        data = calculate_energy_profile_data(
            solar_type="none",
            has_battery=False,
            has_ev=True,
            has_heatpump=False,
            tariff_type="dynamic"
        )
        self.assertEqual(data["profile_code"], "C.1")
        self.assertEqual(data["recommended_tariff"], "dynamic")
        self.assertGreaterEqual(data["shiftable_kwh_year"], 2000)

    def test_heatpump_profile_d1(self):
        """Profil D.1: Wärmepumpe ohne PV"""
        data = calculate_energy_profile_data(
            solar_type="none",
            has_battery=False,
            has_ev=False,
            has_heatpump=True,
            tariff_type="static"
        )
        self.assertEqual(data["profile_code"], "D.1")
        self.assertEqual(data["recommended_tariff"], "dynamic")

    def test_prosumer_profile_e1_and_e2(self):
        """Profil E.1 & E.2: PV + Speicher"""
        data_e1 = calculate_energy_profile_data(
            solar_type="pv",
            has_battery=True,
            has_ev=False,
            has_heatpump=False,
            tariff_type="static"
        )
        self.assertEqual(data_e1["profile_code"], "E.1")

        data_e2 = calculate_energy_profile_data(
            solar_type="pv",
            has_battery=True,
            has_ev=True,
            has_heatpump=False,
            tariff_type="dynamic"
        )
        self.assertEqual(data_e2["profile_code"], "E.2")
        self.assertEqual(data_e2["recommended_tariff"], "dynamic")

    def test_pv_battery_heatpump_profile_f1(self):
        """Profil F.1: PV + Speicher + Wärmepumpe (ohne EV) -> Dynamischer Tarif empfohlen"""
        data = calculate_energy_profile_data(
            solar_type="pv",
            has_battery=True,
            has_ev=False,
            has_heatpump=True,
            tariff_type="static"
        )
        self.assertEqual(data["profile_code"], "F.1")
        self.assertEqual(data["recommended_tariff"], "dynamic")
        self.assertEqual(data["profile_name"], "PV-Anlage + Speicher + Wärmepumpe")
        self.assertIn("alternative_tariff_hint", data)
        self.assertGreaterEqual(data["estimated_savings_eur_year"], 1400)

    def test_all_in_profile_f1(self):
        """Profil F.1: PV + Speicher + E-Auto + WP"""
        data = calculate_energy_profile_data(
            solar_type="pv",
            has_battery=True,
            has_ev=True,
            has_heatpump=True,
            tariff_type="dynamic"
        )
        self.assertEqual(data["profile_code"], "F.1")
        self.assertEqual(data["recommended_tariff"], "dynamic")
        self.assertGreaterEqual(data["shiftable_kwh_year"], 6000)


class EnergyProfileAPITests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="test_profile_user",
            email="test_profile@sharegy.local",
            password="testpassword123"
        )
        self.home = Home.objects.create(user=self.user, name="Musterhaus")
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)

    def test_get_energy_profile(self):
        res = self.client.get("/api/energy/profile/")
        self.assertEqual(res.status_code, 200)
        self.assertIn("profile_code", res.data)
        self.assertIn("estimated_savings_eur_year", res.data)
        self.assertIn("recommended_tariff", res.data)

    def test_post_energy_profile(self):
        payload = {
            "solar_type": "bkw",
            "has_battery": False,
            "has_ev": True,
            "has_heatpump": False,
            "tariff_type": "dynamic",
        }
        res = self.client.post("/api/energy/profile/", payload, format="json")
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.data["profile_code"], "C.2")
        self.assertEqual(res.data["recommended_tariff"], "dynamic")
