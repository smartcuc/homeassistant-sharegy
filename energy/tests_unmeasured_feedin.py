####################################
# energy/tests_unmeasured_feedin.py
####################################

from django.test import TestCase
from django.contrib.auth import get_user_model
from django.core.cache import cache

from devices.models import Home, Device, DeviceConfig, DeviceRole, MetricDefinition
from devices.services.metrics import normalize_grid_metrics, resolve_grid_direction
from devices.services.ingest import ingest_metric_payload
from energy.ems.services import build_device_signals
from energy.flow_engine import calculate_energy_flow
from energy.services.balance import get_energy_balance

User = get_user_model()


class GridFeedinAndUnmeasuredInverterTest(TestCase):
    """
    Testet die Netzeinspeisungs-Normalisierung und den automatischen Schutz gegen ungemessene
    Wechselrichter (z. B. 2. Wechselrichter / Balkonkraftwerk) zur Vermeidung von negativem Hausverbrauch.
    """

    def setUp(self):
        cache.clear()
        self.user = User.objects.create_user(
            username="feedin_user",
            email="feedin@sharegy.local",
            password="password123"
        )
        self.home = Home.objects.create(user=self.user, name="Feedin Home")

        self.role_grid, _ = DeviceRole.objects.get_or_create(key="grid", defaults={"label": "Netzzähler"})
        self.role_pv, _ = DeviceRole.objects.get_or_create(key="producer", defaults={"label": "Photovoltaik"})
        self.role_load, _ = DeviceRole.objects.get_or_create(key="consumer", defaults={"label": "Verbraucher"})

        self.mdef_power, _ = MetricDefinition.objects.get_or_create(key="power", defaults={"name": "Wirkleistung", "unit": "W"})

        # Grid meter
        self.grid_dev = Device.objects.create(
            home=self.home,
            identifier="grid_meter_01",
            configured=True,
            active=True,
        )
        self.grid_cfg = DeviceConfig.objects.create(
            device=self.grid_dev,
            home=self.home,
            role=self.role_grid,
            metric_definition=self.mdef_power,
        )

        # 1. PV Inverter (produces 0 W or low wattage)
        self.pv_dev = Device.objects.create(
            home=self.home,
            identifier="pv_inverter_01",
            configured=True,
            active=True,
        )
        self.pv_cfg = DeviceConfig.objects.create(
            device=self.pv_dev,
            home=self.home,
            role=self.role_pv,
            metric_definition=self.mdef_power,
        )

        # Submeter consumer (e.g. 200 W load)
        self.load_dev = Device.objects.create(
            home=self.home,
            identifier="submeter_tv_01",
            configured=True,
            active=True,
        )
        self.load_cfg = DeviceConfig.objects.create(
            device=self.load_dev,
            home=self.home,
            role=self.role_load,
            metric_definition=self.mdef_power,
        )

    def test_normalize_grid_metrics(self):
        # 1. Test separate feedin power key
        res = normalize_grid_metrics({"feed_in_power": 1800, "import_power": 0})
        self.assertEqual(res.get("grid_power"), -1800)
        self.assertEqual(res.get("power"), -1800)

        # 2. Test grid_export key
        res2 = normalize_grid_metrics({"grid_export": 2500})
        self.assertEqual(res2.get("grid_power"), -2500)

        # 3. Test grid_import key
        res3 = normalize_grid_metrics({"grid_import": 1200})
        self.assertEqual(res3.get("grid_power"), 1200)

        # 4. Test direction string
        res4 = normalize_grid_metrics({"power": 900, "direction": "export"})
        self.assertEqual(res4.get("power"), -900)

    def test_unmeasured_inverter_live_ems_signals(self):
        """
        Szenario: 1. WR erzeugt 0 W. Ein ungemessener 2. WR erzeugt 1000 W.
        Submeter misst 200 W Last. Netzzähler misst 800 W Netzeinspeisung (-800 W).
        """
        # Ingest grid export
        ingest_metric_payload(self.grid_dev, {"grid_power": -800.0})
        # Ingest PV 0 W
        ingest_metric_payload(self.pv_dev, {"pv_power": 0.0})
        # Ingest Submeter 200 W
        ingest_metric_payload(self.load_dev, {"load_power": 200.0})

        signals = build_device_signals(self.user)

        # Netzeinspeisung muss 800 W sein
        self.assertEqual(signals["grid"]["export"], 800.0)
        self.assertEqual(signals["grid"]["import"], 0.0)

        # Ungemessene Erzeugung muss erkannt werden (800 W Export + 200 W Last = 1000 W)
        self.assertGreaterEqual(signals["pv"]["production"], 800.0)

        # Hauslast darf NIEMALS negativ sein, muss mindestens die gemessenen 200 W betragen
        self.assertGreaterEqual(signals["load"]["consumption"], 200.0)

    def test_flow_engine_with_unmeasured_export(self):
        """
        Testet, dass calculate_energy_flow bei reinem Export ohne PV-Signal
        keinen negativen Fluss oder negativen Hausverbrauch liefert.
        """
        raw_signals = {
            "pv": {"production": 0.0},
            "battery": {"charge": 0.0, "discharge": 0.0},
            "grid": {"import": 0.0, "export": 750.0},
            "load": {"consumption": 150.0},
        }

        flow = calculate_energy_flow(raw_signals)

        self.assertGreaterEqual(flow["total_consumption"], 150.0)
        self.assertGreaterEqual(flow["total_production"], 750.0)
        self.assertEqual(flow["pv_to_grid"], 750.0)
