from decimal import Decimal
from datetime import datetime, date, timedelta
from django.test import TestCase
from django.contrib.auth import get_user_model
from django.utils import timezone

from devices.models import Home
from producer.models import GeneratorSystem, GeneratorString, GeneratorType, Orientation
from forecast.models import WeatherForecast, SolarForecast
from forecast.services_weather import store_weather_payload_for_home
from forecast.services_physics import predict_next_24h_physics_for_generator_string
from forecast.services_forecast_accuracy import calculate_forecast_accuracy

User = get_user_model()


class ForecastServiceTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="forecasttestuser",
            email="forecast@example.com",
            password="testpassword123",
        )
        self.home = Home.objects.create(
            user=self.user,
            name="Test Solar Home",
            latitude=50.9375,
            longitude=6.9603,
        )
        self.gen_type = GeneratorType.objects.create(key="pv", name="Photovoltaik")
        self.orientation = Orientation.objects.create(
            key="south",
            name="Süd",
            azimuth_deg=180,
        )
        self.generator = GeneratorSystem.objects.create(
            home=self.home,
            name="Dachanlage",
            generator_type=self.gen_type,
            peak_power_kw=Decimal("10.0"),
        )
        self.string = GeneratorString.objects.create(
            generator=self.generator,
            name="String 1",
            peak_power_kwp=Decimal("5.0"),
            orientation=self.orientation,
            tilt_deg=35,
            shading_percent=Decimal("0.0"),
        )

    def test_store_weather_payload_for_home(self):
        now = timezone.now().replace(minute=0, second=0, microsecond=0)
        timestamps = [(now + timedelta(hours=i)).isoformat() for i in range(24)]
        payload = {
            "timestamps": timestamps,
            "radiation": [500.0] * 24,
            "temperature": [20.0] * 24,
            "cloud_cover": [10.0] * 24,
        }

        result = store_weather_payload_for_home(self.home, payload)
        self.assertEqual(result["written"], 24)
        self.assertEqual(result["skipped"], 0)

        count = WeatherForecast.objects.filter(home=self.home).count()
        self.assertEqual(count, 24)

    def test_predict_next_24h_physics_for_generator_string(self):
        base_now = timezone.now()
        weather_objs = [
            WeatherForecast(
                home=self.home,
                ts=base_now + timedelta(hours=i),
                temperature_c=22.0,
                cloud_cover_pct=0.0,
                shortwave_radiation_wm2=800.0,
            )
            for i in range(24)
        ]
        WeatherForecast.objects.bulk_create(weather_objs)

        physics_preds = predict_next_24h_physics_for_generator_string(self.string)
        self.assertGreaterEqual(len(physics_preds), 1)
        self.assertIn("forecast_kw", physics_preds[0])
        self.assertGreater(physics_preds[0]["forecast_kw"], 0)

    def test_ml_feature_vector_generation(self):
        from forecast.services_ml_features import build_solar_feature_vector
        now = timezone.now()
        feat = build_solar_feature_vector(
            dt=now,
            weather={"shortwave_radiation_wm2": 600, "temperature_c": 25, "cloud_cover_pct": 20},
            physics_kw=3.5,
            lag_24=3.2,
            lag_48=3.0,
            lag_1=3.4,
        )
        self.assertEqual(len(feat), 13)
        self.assertEqual(feat[0], 3.5)  # physics_kw
        self.assertEqual(feat[1], 600.0)  # radiation

    def test_save_all_forecasts_hybrid_pipeline(self):
        from forecast.services_store import save_all_forecasts_for_generator_string
        from devices.models import Device, DeviceConfig, DeviceRole, DeviceMetric1h

        base_now = timezone.now().replace(minute=0, second=0, microsecond=0)

        # 1. Wetterdaten für Vergangenheit & Zukunft anlegen
        weather_objs = [
            WeatherForecast(
                home=self.home,
                ts=base_now - timedelta(hours=48) + timedelta(hours=i),
                temperature_c=20.0,
                cloud_cover_pct=10.0,
                shortwave_radiation_wm2=700.0 if 6 <= (i % 24) <= 18 else 0.0,
            )
            for i in range(72)
        ]
        WeatherForecast.objects.bulk_create(weather_objs, ignore_conflicts=True)

        # 2. PV Device & historische Erzeugungsdaten anlegen
        role_producer = DeviceRole.objects.create(key="producer", label="Producer")
        pv_dev = Device.objects.create(home=self.home, identifier="pv_inv_test", configured=True)
        DeviceConfig.objects.create(device=pv_dev, home=self.home, role=role_producer)

        metric_objs = [
            DeviceMetric1h(
                device=pv_dev,
                metric_key="power",
                bucket=base_now - timedelta(hours=48) + timedelta(hours=i),
                avg=3500.0 if 6 <= (i % 24) <= 18 else 0.0,
                min=3000.0 if 6 <= (i % 24) <= 18 else 0.0,
                max=4000.0 if 6 <= (i % 24) <= 18 else 0.0,
                count=60,
                energy_wh=3500.0 if 6 <= (i % 24) <= 18 else 0.0,
            )
            for i in range(48)
        ]
        DeviceMetric1h.objects.bulk_create(metric_objs, ignore_conflicts=True)

        # 3. Hybrid Forecast Pipeline ausführen
        result = save_all_forecasts_for_generator_string(self.string)
        self.assertEqual(result["status"], "ok")
        self.assertGreater(result["counts"]["hybrid"], 0)
        self.assertGreater(result["counts"]["physics"], 0)

        # 4. Überprüfen, ob SolarForecast Einträge existieren
        hybrid_forecasts = SolarForecast.objects.filter(generator_string=self.string, source="hybrid")
        self.assertGreaterEqual(hybrid_forecasts.count(), 1)

    def test_household_load_forecast_api(self):
        self.client.force_login(self.user)
        response = self.client.get("/api/forecast/load/?horizon=24")
        self.assertEqual(response.status_code, 200)
        data = response.json()

        self.assertIn("kpis", data)
        self.assertIn("timeline", data)
        self.assertEqual(len(data["timeline"]), 24)

        kpis = data["kpis"]
        self.assertIn("total_load_kwh", kpis)
        self.assertIn("total_pv_kwh", kpis)
        self.assertIn("total_surplus_kwh", kpis)
        self.assertIn("autarky_pct", kpis)

        first_slot = data["timeline"][0]
        self.assertIn("total_load_kw", first_slot)
        self.assertIn("pv_forecast_kw", first_slot)
        self.assertIn("net_surplus_kw", first_slot)
        self.assertIn("net_grid_import_kw", first_slot)


