from decimal import Decimal
from datetime import datetime, timezone as dt_timezone
from django.test import TestCase
from django.utils import timezone

from market.models import SpotPrice
from market.services_price_analysis import (
    get_hourly_prices,
    get_cheapest_hours,
    find_cheapest_window,
    get_price_insights,
)


class MarketAnalysisTest(TestCase):
    def setUp(self):
        now = timezone.now().replace(hour=0, minute=0, second=0, microsecond=0)
        # Create 24 hours of spot prices
        prices = [
            0.15, 0.12, 0.10, 0.08, 0.09, 0.14,
            0.20, 0.25, 0.22, 0.18, 0.15, 0.13,
            0.11, 0.10, 0.09, 0.12, 0.16, 0.24,
            0.28, 0.26, 0.21, 0.17, 0.14, 0.12,
        ]

        objs = []
        for hour, price in enumerate(prices):
            # 4 quarter-hours per hour
            for q in range(4):
                ts = now + timezone.timedelta(hours=hour, minutes=q * 15)
                objs.append(
                    SpotPrice(
                        timestamp=ts,
                        price_eur_per_kwh=Decimal(str(price)),
                        source="energy-charts",
                    )
                )

        SpotPrice.objects.bulk_create(
            objs,
            update_conflicts=True,
            unique_fields=["timestamp", "source"],
            update_fields=["price_eur_per_kwh"],
        )

    def test_get_hourly_prices(self):
        hourly = get_hourly_prices()
        self.assertGreater(len(hourly), 0)
        self.assertIn("hour", hourly[0])
        self.assertIn("price", hourly[0])

    def test_get_cheapest_hours(self):
        hourly = get_hourly_prices()
        cheapest = get_cheapest_hours(hourly)
        self.assertLessEqual(len(cheapest), 3)
        if len(cheapest) >= 2:
            self.assertLessEqual(cheapest[0]["price"], cheapest[1]["price"])

    def test_find_cheapest_window(self):
        hourly = get_hourly_prices()
        best_2h = find_cheapest_window(hourly, 2)
        self.assertIsNotNone(best_2h)
        self.assertIn("start", best_2h)
        self.assertIn("avg_price", best_2h)

    def test_get_price_insights(self):
        insights = get_price_insights()
        self.assertIn("cheapest_hours", insights)
        self.assertIn("best_2h", insights)
        self.assertIn("best_3h", insights)
        self.assertIn("best_5h", insights)


from django.contrib.auth import get_user_model
from devices.models import Home
from market.models_tariff import HomeTariff

User = get_user_model()


class HomeTariffAPITest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="tarifftestuser", password="password123")
        self.home = Home.objects.create(user=self.user, name="Tariff Test Home")
        self.client.force_login(self.user)

    def test_save_and_retrieve_feed_in_tariff(self):
        # 1. Save static feed-in tariff with custom value (e.g. 11.50 ct/kWh)
        post_data = {
            "tariff_type": "dynamic",
            "feed_in_tariff_type": "static",
            "feed_in_tariff_ct": 11.50,
        }
        res = self.client.post("/api/market/tariff/", post_data, content_type="application/json")
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertEqual(data["feed_in_tariff_type"], "static")
        self.assertEqual(data["feed_in_tariff_ct"], 11.50)

        # 2. Retrieve via GET
        get_res = self.client.get("/api/market/tariff/")
        self.assertEqual(get_res.status_code, 200)
        get_data = get_res.json()
        self.assertEqual(get_data["feed_in_tariff_type"], "static")
        self.assertEqual(get_data["feed_in_tariff_ct"], 11.50)

        # 3. Change to "none" (Nulleinspeisung)
        post_data_none = {
            "tariff_type": "static",
            "static_price_ct": 29.50,
            "feed_in_tariff_type": "none",
        }
        res_none = self.client.post("/api/market/tariff/", post_data_none, content_type="application/json")
        self.assertEqual(res_none.status_code, 200)
        data_none = res_none.json()
        self.assertEqual(data_none["tariff_type"], "static")
        self.assertEqual(data_none["static_price_ct"], 29.50)
        self.assertEqual(data_none["feed_in_tariff_type"], "none")
        self.assertEqual(data_none["feed_in_tariff_ct"], 0.0)


class GridCO2SignalTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="co2testuser", password="password123")
        self.home = Home.objects.create(user=self.user, name="CO2 Test Home")
        self.client.force_login(self.user)

    def test_grid_co2_intensity_calculation(self):
        res = self.client.get("/api/market/co2/")
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertIn("current_co2_intensity_g_per_kwh", data)
        self.assertIn("current_renewable_share_pct", data)
        self.assertIn("current_level", data)
        self.assertIn("timeline", data)
        self.assertGreater(len(data["timeline"]), 0)
        self.assertIn("best_eco_window", data)
