###########################
# market/services_tariff.py
###########################

from decimal import Decimal

from market.models_tariff import HomeTariff
from market.models_price_config import (
    ElectricityPriceConfig,
)


_home_tariff_cache = {}
_price_config_cache = {}


def get_home_tariff(
    home,
    date,
):
    if not home:
        return None

    home_id = getattr(home, "id", str(home))
    cache_key = (home_id, str(date))
    if cache_key in _home_tariff_cache:
        return _home_tariff_cache[cache_key]

    tariff = (
        HomeTariff.objects.filter(
            home=home,
            valid_from__lte=date,
        )
        .order_by("-valid_from")
        .first()
    )
    _home_tariff_cache[cache_key] = tariff
    return tariff


def get_price_config(
    date,
):
    year = date.year if hasattr(date, "year") else str(date)[:4]
    if year in _price_config_cache:
        return _price_config_cache[year]

    config = (
        ElectricityPriceConfig.objects.filter(
            valid_from__lte=date,
        )
        .order_by("-valid_from")
        .first()
    )
    if not config:
        config, _ = ElectricityPriceConfig.objects.get_or_create(
            valid_from=date.replace(month=1, day=1),
            defaults={
                "grid_fee_ct": Decimal("9.5000"),
                "electricity_tax_ct": Decimal("2.0500"),
                "concession_fee_ct": Decimal("1.6600"),
                "kwk_levy_ct": Decimal("0.2750"),
                "special_grid_levy_ct": Decimal("0.6430"),
                "offshore_levy_ct": Decimal("0.6560"),
                "vat_percent": Decimal("19.00"),
            },
        )
    _price_config_cache[year] = config
    return config


def calculate_effective_price(
    home,
    timestamp,
    spot_price_ct,
):
    """
    Liefert den tatsächlichen Strompreis
    in ct/kWh.
    """

    tariff = get_home_tariff(
        home,
        timestamp.date(),
    )

    if not tariff:
        return float(spot_price_ct)

    #
    # Fester Tarif
    #
    if tariff.tariff_type == HomeTariff.TARIFF_STATIC:

        return round(
            float(tariff.static_price_eur_per_kwh) * 100,
            2,
        )

    #
    # Dynamischer Tarif
    #
    config = get_price_config(
        timestamp.date(),
    )

    if not config:
        return float(spot_price_ct)

    netto = (
        Decimal(str(spot_price_ct))
        + config.grid_fee_ct
        + config.electricity_tax_ct
        + config.concession_fee_ct
        + config.kwk_levy_ct
        + config.special_grid_levy_ct
        + config.offshore_levy_ct
    )

    brutto = netto * (Decimal("1") + (config.vat_percent / Decimal("100")))

    return round(
        float(brutto),
        2,
    )
