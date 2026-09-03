###################################
# energy/tests_smart_charging.py
###################################

from decimal import Decimal
from django.test import TestCase
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from rest_framework import status

from devices.models import Home
from devices.models_ocpp import ChargingStation, ChargingSession
from energy.services.services_smart_charging import (
    calculate_smart_charging_current,
    dispatch_wallbox_charging_profile
)

User = get_user_model()


class SmartChargingServiceTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="evdriver",
            email="ev@sharegy.de",
            password="testpassword123"
        )
        self.home = Home.objects.create(
            user=self.user,
            name="Solar EV Home"
        )
        self.station = ChargingStation.objects.create(
            home=self.home,
            charge_point_id="WB-TEST-88",
            name="go-eCharger HOME",
            phases=3,
            max_current_a=16.0,
            min_current_a=6.0,
            smart_charging_mode="pv_surplus"
        )
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)

    def test_pv_surplus_calculation(self):
        # Fall 1: Sehr hoher PV-Überschuss (11 kW PV, 1 kW Hauslast, 0 kW Bat)
        # Netto-Überschuss = 10 kW. Bei 3 Phasen à 230V = 690V => 10.000 / 690 = 14.5 A
        current = calculate_smart_charging_current(
            station=self.station,
            pv_power_w=11000.0,
            load_power_w=1000.0,
            battery_charge_w=0.0
        )
        self.assertAlmostEqual(current, 14.5, delta=0.5)

        # Fall 2: Zu wenig PV-Überschuss (< 3.5 kW)
        # Reicht nicht für min 6A (4.14 kW) => 0.0 A
        current_low = calculate_smart_charging_current(
            station=self.station,
            pv_power_w=2000.0,
            load_power_w=1500.0,
            battery_charge_w=0.0
        )
        self.assertEqual(current_low, 0.0)

    def test_min_pv_mode(self):
        self.station.smart_charging_mode = "min_pv"
        # Auch bei 0 Watt Solar muss mindestens 6.0 A geliefert werden
        current = calculate_smart_charging_current(
            station=self.station,
            pv_power_w=0.0,
            load_power_w=2000.0
        )
        self.assertEqual(current, 6.0)

    def test_spot_price_mode(self):
        self.station.smart_charging_mode = "spot_price"
        self.station.price_threshold_ct = 12.0

        # Günstiger Preis (8 ct <= 12 ct) -> Max Power 16A
        current_cheap = calculate_smart_charging_current(
            station=self.station,
            spot_price_ct=8.0
        )
        self.assertEqual(current_cheap, 16.0)

        # Teurer Preis (25 ct > 12 ct) -> 0.0 A
        current_expensive = calculate_smart_charging_current(
            station=self.station,
            spot_price_ct=25.0
        )
        self.assertEqual(current_expensive, 0.0)

    def test_wallbox_rest_api_crud(self):
        # 1. Wallboxen auflisten
        res = self.client.get("/api/energy/wallboxes/")
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data["wallboxes"]), 1)
        self.assertEqual(res.data["wallboxes"][0]["charge_point_id"], "WB-TEST-88")

        # 2. Neue Wallbox registrieren
        res_create = self.client.post("/api/energy/wallboxes/", {
            "name": "Easee Garage",
            "vendor": "Easee",
            "model": "Charge",
            "phases": 3,
            "max_current_a": 16.0,
            "smart_charging_mode": "spot_price"
        })
        self.assertEqual(res_create.status_code, status.HTTP_201_CREATED)
        self.assertTrue("ocpp_url" in res_create.data)
        new_id = res_create.data["id"]

        # 3. Lademodus patchen
        res_patch = self.client.patch(f"/api/energy/wallboxes/{new_id}/", {
            "smart_charging_mode": "instant",
            "price_threshold_ct": 10.5
        })
        self.assertEqual(res_patch.status_code, status.HTTP_200_OK)
        self.assertEqual(res_patch.data["smart_charging_mode"], "instant")

        # 4. Remote Action (dispatch-now)
        res_dispatch = self.client.post(f"/api/energy/wallboxes/{new_id}/dispatch-now/")
        self.assertEqual(res_dispatch.status_code, status.HTTP_200_OK)
        self.assertEqual(res_dispatch.data["target_current_a"], 16.0)
