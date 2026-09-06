###################################
# energy/test_ems_settings.py
###################################

from decimal import Decimal
from django.test import TestCase
from django.core.exceptions import ValidationError
from django.core.cache import cache

from energy.models import EMSGlobalSettings, InverterManufacturerPollingConfig
from energy.services.ems_settings import (
    get_ems_global_settings,
    get_manufacturer_polling_interval,
    get_all_manufacturer_intervals,
    seed_default_manufacturer_configs,
    DEFAULT_MANUFACTURER_POLLING_INTERVALS,
)


class EMSSettingsTests(TestCase):
    def setUp(self):
        cache.clear()
        EMSGlobalSettings.objects.all().delete()
        InverterManufacturerPollingConfig.objects.all().delete()

    def test_ems_global_settings_creation_and_defaults(self):
        settings = get_ems_global_settings()
        self.assertIsNotNone(settings)
        self.assertEqual(settings.default_grid_price_ct_kwh, Decimal("32.00"))
        self.assertEqual(settings.default_feed_in_tariff_ct_kwh, Decimal("8.20"))
        self.assertEqual(settings.default_spot_markup_ct_kwh, Decimal("1.50"))
        self.assertEqual(settings.battery_arbitrage_min_spread_ct_kwh, Decimal("8.00"))
        self.assertEqual(settings.vat_percent, Decimal("19.00"))

        # Test statutory total
        expected_total = (
            Decimal("9.5000")
            + Decimal("2.0500")
            + Decimal("1.6600")
            + Decimal("0.2750")
            + Decimal("0.6430")
            + Decimal("0.6560")
        )
        self.assertEqual(settings.total_statutory_levies_ct_kwh(), expected_total)

    def test_ems_global_settings_singleton_enforcement(self):
        get_ems_global_settings()
        # Trying to create a second instance should raise ValidationError
        second_instance = EMSGlobalSettings(default_grid_price_ct_kwh=Decimal("35.00"))
        with self.assertRaises(ValidationError):
            second_instance.save()

    def test_inverter_manufacturer_polling_config(self):
        sungrow = InverterManufacturerPollingConfig.objects.create(
            manufacturer_key="sungrow",
            manufacturer_name="Sungrow (iSolarCloud)",
            polling_interval_seconds=15,
            min_allowed_interval_seconds=10,
            is_active=True,
        )
        self.assertEqual(sungrow.polling_interval_seconds, 15)

        # Polling below minimum interval should fail validation
        invalid_config = InverterManufacturerPollingConfig(
            manufacturer_key="huawei",
            manufacturer_name="Huawei (FusionSolar)",
            polling_interval_seconds=5,
            min_allowed_interval_seconds=30,
        )
        with self.assertRaises(ValidationError):
            invalid_config.save()

    def test_get_manufacturer_polling_interval_service(self):
        InverterManufacturerPollingConfig.objects.create(
            manufacturer_key="sungrow",
            manufacturer_name="Sungrow (iSolarCloud)",
            polling_interval_seconds=12,
            min_allowed_interval_seconds=10,
            is_active=True,
        )
        InverterManufacturerPollingConfig.objects.create(
            manufacturer_key="huawei",
            manufacturer_name="Huawei (FusionSolar)",
            polling_interval_seconds=45,
            min_allowed_interval_seconds=30,
            is_active=True,
        )

        # Exact match
        self.assertEqual(get_manufacturer_polling_interval("sungrow"), 12)
        # Profile ID resolution with prefix/suffix
        self.assertEqual(get_manufacturer_polling_interval("sungrow_isolarcloud"), 12)
        self.assertEqual(get_manufacturer_polling_interval("huawei_fusionsolar"), 45)

        # Fallback to defaults when not in DB
        self.assertEqual(get_manufacturer_polling_interval("victron_vrm"), 30)
        self.assertEqual(get_manufacturer_polling_interval("unknown_vendor", default=90), 90)

    def test_seed_default_manufacturer_configs(self):
        created = seed_default_manufacturer_configs()
        self.assertEqual(created, len(DEFAULT_MANUFACTURER_POLLING_INTERVALS))
        self.assertEqual(
            InverterManufacturerPollingConfig.objects.count(),
            len(DEFAULT_MANUFACTURER_POLLING_INTERVALS),
        )

        # Second run should not duplicate
        second_run = seed_default_manufacturer_configs()
        self.assertEqual(second_run, 0)

    def test_get_all_manufacturer_intervals(self):
        seed_default_manufacturer_configs()
        all_intervals = get_all_manufacturer_intervals()
        self.assertIn("sungrow", all_intervals)
        self.assertEqual(all_intervals["sungrow"], 15)
        self.assertIn("huawei", all_intervals)
        self.assertEqual(all_intervals["huawei"], 60)
        self.assertIn("shelly", all_intervals)
        self.assertEqual(all_intervals["shelly"], 15)
