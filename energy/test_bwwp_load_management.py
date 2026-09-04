"""
energy/test_bwwp_load_management.py

Automatisierte Unit-Tests für das BWWP- & Wärmepumpen-Lastmanagement (SG-Ready).
"""

from decimal import Decimal
from datetime import timedelta
from django.test import TestCase
from django.utils import timezone
from django.core.cache import cache
from rest_framework.test import APIClient

from accounts.models import User
from devices.models import Home, Device, DeviceRole, DeviceConfig, DeviceLatestMetric
from energy.models import BWWPLoadManagementConfig
from energy.services.bwwp_manager import evaluate_bwwp_load_management, find_or_create_bwwp_config
from market.models import SpotPrice


class BWWPLoadManagementTestCase(TestCase):
    def setUp(self):
        cache.clear()
        self.client = APIClient()
        self.user = User.objects.create_user(username="bwwp_user@sharegy.de", email="bwwp_user@sharegy.de", password="pw")
        self.home = Home.objects.create(name="BWWP Test Home", user=self.user)
        self.client.force_authenticate(user=self.user)

        # Rollen
        self.role_bwwp = DeviceRole.objects.create(key="bwwp", label="Brauchwasserwärmepumpe")
        self.role_pv = DeviceRole.objects.create(key="pv", label="PV Wechselrichter")

        # BWWP-Gerät
        self.dev_bwwp = Device.objects.create(home=self.home, identifier="shelly_bwwp", active=True)
        DeviceConfig.objects.create(
            device=self.dev_bwwp,
            home=self.home,
            name="Brauchwasserwärmepumpe",
            role=self.role_bwwp,
        )

        # Konfiguration
        self.bwwp_config = BWWPLoadManagementConfig.objects.create(
            home=self.home,
            device=self.dev_bwwp,
            active=True,
            control_mode="hybrid",
            min_temp_c=Decimal("45.0"),
            target_temp_c=Decimal("52.0"),
            boost_temp_c=Decimal("60.0"),
            max_safety_temp_c=Decimal("65.0"),
            min_pv_surplus_w=Decimal("800.0"),
            max_price_threshold_ct=Decimal("18.00"),
            battery_soc_reserve_pct=Decimal("50.0"),
            min_run_time_minutes=20,
            min_cooldown_minutes=15,
        )

    def test_comfort_protection_under_min_temp(self):
        """Wassertemperatur 42°C (< 45°C) erzwingt Einschalten zur Warmwassersicherung."""
        cache.set(f"device:{self.dev_bwwp.id}:temp_water", 42.0)
        cache.set(f"device_relay_state_{self.dev_bwwp.id}", False)
        self.bwwp_config.last_switched_at = timezone.now() - timedelta(hours=1)
        self.bwwp_config.save()

        res = evaluate_bwwp_load_management(self.home, config=self.bwwp_config, force=False)

        self.assertTrue(res["relay_state"])
        self.assertEqual(res["current_sg_state"], "4_force")
        self.assertIn("Komfort-Sicherung", res["decision_reason"])

    def test_overheat_safety_protection(self):
        """Wassertemperatur 66°C (>= 65°C) schaltet BWWP zum Überhitzungsschutz sofort ab."""
        cache.set(f"device:{self.dev_bwwp.id}:temp_water", 66.0)
        cache.set(f"device_relay_state_{self.dev_bwwp.id}", True)

        res = evaluate_bwwp_load_management(self.home, config=self.bwwp_config, force=False)

        self.assertFalse(res["relay_state"])
        self.assertEqual(res["current_sg_state"], "1_lock")
        self.assertIn("Überhitzungsschutz", res["decision_reason"])

    def test_pv_surplus_boost(self):
        """PV-Überschuss 1.500 W (> 800 W) und Temp 48°C schaltet SG-Ready Boost (60°C) ein."""
        cache.set(f"device:{self.dev_bwwp.id}:temp_water", 48.0)
        cache.set(f"device_relay_state_{self.dev_bwwp.id}", False)
        self.bwwp_config.last_switched_at = timezone.now() - timedelta(hours=1)
        self.bwwp_config.save()

        # PV-Signal simulieren
        now = timezone.now()
        dev_grid = Device.objects.create(home=self.home, identifier="smart_meter", active=True)
        DeviceLatestMetric.objects.create(device=dev_grid, metric_key="grid_power", value=-1500.0, timestamp=now)


        res = evaluate_bwwp_load_management(self.home, config=self.bwwp_config, force=False)

        self.assertTrue(res["relay_state"])
        self.assertEqual(res["current_sg_state"], "3_boost")
        self.assertIn("PV-Überschuss", res["decision_reason"])

    def test_cheap_spot_price_boost(self):
        """Börsenstrompreis 0.08 €/kWh (8 ct) triggert SG-Ready Boost im Hybrid-Modus."""
        cache.set(f"device:{self.dev_bwwp.id}:temp_water", 49.0)
        cache.set(f"device_relay_state_{self.dev_bwwp.id}", False)
        self.bwwp_config.last_switched_at = timezone.now() - timedelta(hours=1)
        self.bwwp_config.save()

        now = timezone.now()
        SpotPrice.objects.create(timestamp=now, price_eur_per_kwh=Decimal("0.0001"))

        res = evaluate_bwwp_load_management(self.home, config=self.bwwp_config, force=False)

        self.assertTrue(res["relay_state"])
        self.assertEqual(res["current_sg_state"], "3_boost")

    def test_compressor_protection_min_runtime(self):
        """Verdichterschutz: Eingeschaltete BWWP bleibt nach 5 Min (< 20 Min) aktiv."""
        cache.set(f"device:{self.dev_bwwp.id}:temp_water", 53.0)
        cache.set(f"device_relay_state_{self.dev_bwwp.id}", True)
        self.bwwp_config.last_switched_at = timezone.now() - timedelta(minutes=5)
        self.bwwp_config.save()

        res = evaluate_bwwp_load_management(self.home, config=self.bwwp_config, force=False)

        self.assertTrue(res["relay_state"])
        self.assertTrue(res["protection_active"])
        self.assertIn("Verdichterschutz", res["decision_reason"])

    def test_anti_cycling_min_cooldown(self):
        """Taktschutz: Abgeschaltete BWWP bleibt nach 5 Min (< 15 Min) im Ruhezustand."""
        cache.set(f"device:{self.dev_bwwp.id}:temp_water", 49.0)
        cache.set(f"device_relay_state_{self.dev_bwwp.id}", False)
        self.bwwp_config.last_switched_at = timezone.now() - timedelta(minutes=5)
        self.bwwp_config.save()

        res = evaluate_bwwp_load_management(self.home, config=self.bwwp_config, force=False)

        self.assertFalse(res["relay_state"])
        self.assertTrue(res["protection_active"])
        self.assertIn("Taktschutz", res["decision_reason"])

    def test_bwwp_rest_api_endpoints(self):
        """Testet GET status, POST config und POST switch Endpunkte."""
        # 1. Status
        res_status = self.client.get("/api/energy/bwwp/")
        self.assertEqual(res_status.status_code, 200)
        self.assertEqual(res_status.data["identifier"], "shelly_bwwp")

        # 2. Config Update
        res_cfg = self.client.post("/api/energy/bwwp/config/", {
            "boost_temp_c": 62.0,
            "min_pv_surplus_w": 1000.0,
            "control_mode": "pv_surplus",
        }, format="json")
        self.assertEqual(res_cfg.status_code, 200)
        self.bwwp_config.refresh_from_db()
        self.assertEqual(float(self.bwwp_config.boost_temp_c), 62.0)
        self.assertEqual(self.bwwp_config.control_mode, "pv_surplus")

        # 3. Manual Switch (Instant Boost)
        res_sw = self.client.post("/api/energy/bwwp/switch/", {
            "action": "boost",
            "duration_minutes": 30,
        }, format="json")
        self.assertEqual(res_sw.status_code, 200)
        self.assertTrue(cache.get(f"device_relay_state_{self.dev_bwwp.id}"))
