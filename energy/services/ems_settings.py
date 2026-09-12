###################################
# energy/services/ems_settings.py
###################################

import logging
from decimal import Decimal
from django.core.cache import cache

logger = logging.getLogger(__name__)

CACHE_TIMEOUT_SETTINGS = 300  # 5 Minuten
CACHE_TIMEOUT_INTERVALS = 300


# Standard-Intervalle je Hersteller (Sekunden) für initiales Seeding & harten Fallback
DEFAULT_MANUFACTURER_POLLING_INTERVALS = {
    "sungrow": {
        "name": "Sungrow (iSolarCloud)",
        "interval": 15,
        "min_interval": 10,
        "notes": "iSolarCloud OpenAPI erlaubt bis zu 10s Abfrageintervall.",
    },
    "huawei": {
        "name": "Huawei (FusionSolar)",
        "interval": 60,
        "min_interval": 30,
        "notes": "FusionSolar OpenAPI - Limit: 100 API-Aufrufe/Std. empfohlen.",
    },
    "solaredge": {
        "name": "SolarEdge (Monitoring API)",
        "interval": 60,
        "min_interval": 30,
        "notes": "SolarEdge Monitoring API - Limit: 300 Aufrufe/Tag.",
    },
    "fronius": {
        "name": "Fronius (Solarweb API)",
        "interval": 60,
        "min_interval": 20,
        "notes": "Solarweb API v1 / Realtime Telemetrie.",
    },
    "sma": {
        "name": "SMA (Sunny Portal / WebConnect)",
        "interval": 30,
        "min_interval": 15,
        "notes": "SMA WebConnect / Sunny Portal REST API.",
    },
    "kostal": {
        "name": "Kostal (Solar Portal)",
        "interval": 60,
        "min_interval": 20,
        "notes": "Kostal Solar Portal REST Schnittstelle.",
    },
    "deye": {
        "name": "Deye / Solarman",
        "interval": 60,
        "min_interval": 30,
        "notes": "Solarman Business API v2.",
    },
    "goodwe": {
        "name": "GoodWe (SEMS Portal)",
        "interval": 60,
        "min_interval": 30,
        "notes": "GoodWe SEMS Cloud API.",
    },
    "growatt": {
        "name": "Growatt (ShineServer)",
        "interval": 60,
        "min_interval": 60,
        "notes": "Growatt OpenAPI v1 (Rate-Limit Schutz: mind. 60s Intervall empfohlen).",
    },
    "victron": {
        "name": "Victron Energy (VRM API)",
        "interval": 30,
        "min_interval": 15,
        "notes": "Victron VRM REST API.",
    },
    "solis": {
        "name": "Solis / Ginlong Cloud",
        "interval": 60,
        "min_interval": 30,
        "notes": "SolisCloud OpenAPI v1.",
    },
    "shelly": {
        "name": "Shelly (Cloud API / Pro EM)",
        "interval": 15,
        "min_interval": 5,
        "notes": "Shelly Cloud REST API / WebSocket.",
    },
    "enphase": {
        "name": "Enphase (Enlighten API)",
        "interval": 60,
        "min_interval": 30,
        "notes": "Enphase Enlighten API v4.",
    },
    "foxess": {
        "name": "FoxESS Cloud",
        "interval": 60,
        "min_interval": 30,
        "notes": "FoxESS Open API.",
    },
    "alphaess": {
        "name": "AlphaESS Cloud",
        "interval": 60,
        "min_interval": 30,
        "notes": "AlphaESS Open API.",
    },
    "generic": {
        "name": "Allgemeiner Standard / Fallback",
        "interval": 60,
        "min_interval": 15,
        "notes": "Allgemeiner Standard-Lesezyklus für nicht spezifizierte Profile.",
    },
}


def get_ems_global_settings():
    """
    Liefert die gecachte Singleton-Instanz der globalen EMS-Preiseinstellungen.
    Erstellt automatisch Standard-Einstellungen, falls noch keine existieren.
    """
    cache_key = "ems_global_settings_singleton"
    settings_obj = cache.get(cache_key)
    if settings_obj is not None:
        return settings_obj

    from energy.models import EMSGlobalSettings

    settings_obj = EMSGlobalSettings.objects.first()
    if not settings_obj:
        settings_obj = EMSGlobalSettings.objects.create(
            sharegy_platform_fee_ct_kwh=Decimal("2.00"),
            grid_fee_ct_kwh=Decimal("9.5000"),
            electricity_tax_ct_kwh=Decimal("2.0500"),
            concession_fee_ct_kwh=Decimal("1.6600"),
            kwk_levy_ct_kwh=Decimal("0.2750"),
            special_grid_levy_ct_kwh=Decimal("0.6430"),
            offshore_levy_ct_kwh=Decimal("0.6560"),
            vat_percent=Decimal("19.00"),
            pro_monthly_price_eur=Decimal("4.99"),
            pro_yearly_price_eur=Decimal("49.99"),
            landlord_monthly_price_eur=Decimal("14.99"),
            landlord_yearly_price_eur=Decimal("149.99"),
            trial_days=14,
        )

    cache.set(cache_key, settings_obj, timeout=CACHE_TIMEOUT_SETTINGS)
    return settings_obj


def get_manufacturer_polling_interval(manufacturer_key: str, default: int = 60) -> int:
    """
    Liefert den konfigurierten Lesezyklus in Sekunden für einen bestimmten Hersteller.
    Erkennt Aliase (z. B. 'sungrow_isolarcloud' -> 'sungrow') und prüft DB + Cache.
    """
    if not manufacturer_key:
        return default

    normalized_key = str(manufacturer_key).strip().lower()
    # Entferne eventuelle Suffixe wie _cloud, _isolarcloud, _server etc.
    for known in DEFAULT_MANUFACTURER_POLLING_INTERVALS.keys():
        if normalized_key == known or normalized_key.startswith(f"{known}_") or f"_{known}" in normalized_key:
            normalized_key = known
            break

    cache_key = f"mfg_polling_interval_{normalized_key}"
    cached_val = cache.get(cache_key)
    if cached_val is not None:
        return int(cached_val)

    from energy.models import InverterManufacturerPollingConfig

    config = InverterManufacturerPollingConfig.objects.filter(
        manufacturer_key=normalized_key,
        is_active=True,
    ).first()

    if config:
        interval = config.polling_interval_seconds
    else:
        # Fallback auf Default-Map oder Parameter
        default_info = DEFAULT_MANUFACTURER_POLLING_INTERVALS.get(normalized_key)
        interval = default_info["interval"] if default_info else default

    cache.set(cache_key, interval, timeout=CACHE_TIMEOUT_INTERVALS)
    return interval


def get_all_manufacturer_intervals() -> dict:
    """
    Liefert ein Dictionary aller aktiven Hersteller-Abfrageintervalle in Sekunden.
    Format: {'sungrow': 15, 'huawei': 60, ...}
    """
    cache_key = "all_mfg_polling_intervals"
    cached = cache.get(cache_key)
    if cached is not None:
        return cached

    from energy.models import InverterManufacturerPollingConfig

    configs = InverterManufacturerPollingConfig.objects.filter(is_active=True)
    res = {}
    for cfg in configs:
        res[cfg.manufacturer_key] = cfg.polling_interval_seconds

    # Ergänze fehlende aus Defaults
    for key, info in DEFAULT_MANUFACTURER_POLLING_INTERVALS.items():
        if key not in res:
            res[key] = info["interval"]

    cache.set(cache_key, res, timeout=CACHE_TIMEOUT_INTERVALS)
    return res


def seed_default_manufacturer_configs():
    """
    Stellt sicher, dass alle bekannten Hersteller in der DB angelegt sind.
    """
    from energy.models import InverterManufacturerPollingConfig

    created_count = 0
    for key, info in DEFAULT_MANUFACTURER_POLLING_INTERVALS.items():
        obj, created = InverterManufacturerPollingConfig.objects.get_or_create(
            manufacturer_key=key,
            defaults={
                "manufacturer_name": info["name"],
                "polling_interval_seconds": info["interval"],
                "min_allowed_interval_seconds": info["min_interval"],
                "rate_limit_notes": info["notes"],
                "is_active": True,
            },
        )
        if created:
            created_count += 1

    return created_count
