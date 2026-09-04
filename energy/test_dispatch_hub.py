"""
energy/test_dispatch_hub.py

Unit-Tests für die zentrale Dispatch- & Lastmanagement-Engine (/api/energy/load-management/hub/).
"""

from decimal import Decimal
from django.test import TestCase
from django.utils import timezone
from django.core.cache import cache
from rest_framework.test import APIClient

from accounts.models import User
from devices.models import Home, Device, DeviceRole, DeviceConfig
from energy.models import LoadPriorityConfig, LoadConsumerConfig, BWWPLoadManagementConfig
from energy.services.dispatch_hub import get_load_management_hub_data


class DispatchHubTestCase(TestCase):
    def setUp(self):
        cache.clear()
        self.client = APIClient()
        self.user = User.objects.create_user(username="hub_user@sharegy.de", email="hub_user@sharegy.de", password="pw")
        self.home = Home.objects.create(name="Dispatch Test Home", user=self.user)
        self.client.force_authenticate(user=self.user)

        # 1. BWWP
        self.role_bwwp = DeviceRole.objects.create(key="bwwp", label="Brauchwasserwärmepumpe")
        self.dev_bwwp = Device.objects.create(home=self.home, identifier="shelly_bwwp", active=True)
        DeviceConfig.objects.create(device=self.dev_bwwp, home=self.home, name="BWWP Keller", role=self.role_bwwp)
        BWWPLoadManagementConfig.objects.create(
            home=self.home,
            device=self.dev_bwwp,
            active=True,
            control_mode="hybrid",
        )

        # 2. Poolpumpe (Custom Consumer)
        self.role_pool = DeviceRole.objects.create(key="pool", label="Poolpumpe")
        self.dev_pool = Device.objects.create(home=self.home, identifier="shelly_pool", active=True)
        DeviceConfig.objects.create(device=self.dev_pool, home=self.home, name="Pool Filteranlage", role=self.role_pool)
        self.cc_pool = LoadConsumerConfig.objects.create(
            home=self.home,
            device=self.dev_pool,
            category="pool",
            name="Pool Filteranlage",
            rated_power_w=Decimal("650.0"),
            min_daily_runtime_minutes=300,
            mode="hybrid",
        )

    def test_load_management_hub_data_aggregation(self):
        """Prüft Live-Budget, Geräteliste und 24h-Fahrplan-Generierung."""
        res = self.client.get("/api/energy/load-management/hub/")
        self.assertEqual(res.status_code, 200)

        data = res.data
        self.assertIn("live_budget", data)
        self.assertIn("consumers", data)
        self.assertIn("dispatch_schedule", data)
        self.assertEqual(len(data["dispatch_schedule"]), 24)

        consumer_cats = [c["category"] for c in data["consumers"]]
        self.assertIn("bwwp", consumer_cats)
        self.assertIn("pool", consumer_cats)

    def test_priority_cascade_update(self):
        """Prüft das Speichern geänderter Prioritäten und des Master-Modus."""
        new_order = ["pool", "bwwp", "wallbox", "battery", "ac", "appliances", "heating_rod"]
        res = self.client.post("/api/energy/load-management/hub/priorities/", {
            "priority_order": new_order,
            "master_mode": "pv_only",
            "auto_dispatch_enabled": True,
        }, format="json")

        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.data["master_mode"], "pv_only")
        self.assertEqual(res.data["priority_order"], new_order)

        # In DB verifizieren
        prio_cfg = LoadPriorityConfig.objects.get(home=self.home)
        self.assertEqual(prio_cfg.master_mode, "pv_only")
        self.assertEqual(prio_cfg.priority_order, new_order)

    def test_quick_action_execution(self):
        """Prüft das Ausführen von Sofort-Schaltungen über den Hub."""
        # 1. Poolpumpe einschalten
        res_pool = self.client.post("/api/energy/load-management/hub/action/", {
            "category": "pool",
            "action": "start",
            "device_id": f"custom_{self.cc_pool.id}",
        }, format="json")
        self.assertEqual(res_pool.status_code, 200)
        self.assertTrue(cache.get(f"device_relay_state_{self.dev_pool.id}"))

        # 2. BWWP Boost auslösen
        res_bwwp = self.client.post("/api/energy/load-management/hub/action/", {
            "category": "bwwp",
            "action": "boost",
        }, format="json")
        self.assertEqual(res_bwwp.status_code, 200)
        self.assertTrue(cache.get(f"device_relay_state_{self.dev_bwwp.id}"))
