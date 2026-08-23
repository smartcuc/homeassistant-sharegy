import datetime
from decimal import Decimal
from zoneinfo import ZoneInfo

from django.utils import timezone

from rest_framework.decorators import api_view
from rest_framework.decorators import permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from market.models import SpotPrice
from market.models_tariff import HomeTariff
from market.services import get_current_spot_price
from market.services_tariff import calculate_effective_price, get_home_tariff, get_price_config


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def current_spot_price(request):

    home = request.user.homes.first()

    timezone_name = home.timezone if home and home.timezone else "Europe/Berlin"

    data = get_current_spot_price(timezone_name)

    if not data:
        return Response(
            {"detail": "no price found"},
            status=404,
        )

    return Response(data)


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def spot_price_chart(request):

    range_type = request.GET.get(
        "range",
        "2d",
    )

    home = request.user.homes.first()

    timezone_name = (
        home.timezone
        if home and home.timezone
        else "Europe/Berlin"
    )

    tz = ZoneInfo(timezone_name)

    local_now = timezone.now().astimezone(tz)

    today_start = local_now.replace(
        hour=0,
        minute=0,
        second=0,
        microsecond=0,
    )

    tomorrow_start = (
        today_start
        + timezone.timedelta(days=1)
    )

    day_after_tomorrow = (
        today_start
        + timezone.timedelta(days=2)
    )

    if range_type == "2d":

        start = today_start.astimezone(
            ZoneInfo("UTC")
        )

        end = day_after_tomorrow.astimezone(
            ZoneInfo("UTC")
        )

    elif range_type == "today":

        start = today_start.astimezone(
            ZoneInfo("UTC")
        )

        end = tomorrow_start.astimezone(
            ZoneInfo("UTC")
        )

    elif range_type == "tomorrow":

        start = tomorrow_start.astimezone(
            ZoneInfo("UTC")
        )

        end = day_after_tomorrow.astimezone(
            ZoneInfo("UTC")
        )

    elif range_type == "5d":

        start = (
            today_start
            - timezone.timedelta(days=4)
        ).astimezone(
            ZoneInfo("UTC")
        )

        end = day_after_tomorrow.astimezone(
            ZoneInfo("UTC")
        )

    else:

        start = today_start.astimezone(
            ZoneInfo("UTC")
        )

        end = day_after_tomorrow.astimezone(
            ZoneInfo("UTC")
        )

    rows = (
        SpotPrice.objects
        .filter(
            timestamp__gte=start,
            timestamp__lt=end,
        )
        .order_by("timestamp")
    )

    prices = [
        round(
            float(row.price_eur_per_kwh) * 100,
            2,
        )
        for row in rows
    ]

    effective_prices = []

    for row in rows:

        spot_ct = round(
            float(row.price_eur_per_kwh) * 100,
            2,
        )

        effective_price = calculate_effective_price(
            home=home,
            timestamp=row.timestamp,
            spot_price_ct=spot_ct,
        )

        effective_prices.append(effective_price)

    current_price = get_current_spot_price(
    timezone_name
    )

    # current = (
    #     current_price["price_ct"]
    #     if current_price
    #     else None
    # )

    min_price = (
    min(effective_prices)
    if effective_prices
    else None
    )

    max_price = (
        max(effective_prices)
        if effective_prices
        else None
    )

    avg_price = (
        round(
            sum(effective_prices)
            / len(effective_prices),
            2,
        )
        if effective_prices
        else None
    )

    # Aktuelle Viertelstunde bestimmen
    minute = (local_now.minute // 15) * 15

    current_slot = local_now.replace(
        minute=minute,
        second=0,
        microsecond=0,
    )

    current_effective = None

    if current_price:

        current_effective = calculate_effective_price(
            home=home,
            timestamp=timezone.now(),
            spot_price_ct=current_price["price_ct"],
        )

    return Response(
        {
            "range": range_type,
            "count": rows.count(),
            "now_label": current_slot.strftime("%d.%m %H:%M"),
            "tomorrow_label": tomorrow_start.strftime("%d.%m %H:%M"),
            "timestamps": [
                row.timestamp.astimezone(tz).strftime("%d.%m %H:%M") for row in rows
            ],
            "spot_values": prices,
            "effective_values": effective_prices,
            "min": min_price,
            "max": max_price,
            "avg": avg_price,
            "current_spot": (current_price["price_ct"] if current_price else None),
            "current_effective": current_effective,
        }
    )


@api_view(["GET", "POST"])
@permission_classes([IsAuthenticated])
def home_tariff_detail(request):
    """
    Liefert oder aktualisiert den konfigurierten Stromtarif (statisch oder dynamisch)
    des Haushalts inklusive der hinterlegten gesetzlichen Preisbestandteile.
    """
    home = request.user.homes.first()
    if not home:
        return Response(
            {"detail": "Kein Zuhause für diesen Benutzer gefunden."},
            status=404,
        )

    today = timezone.now().date()

    if request.method == "POST":
        tariff_type = request.data.get("tariff_type", HomeTariff.TARIFF_DYNAMIC)
        raw_static_price = request.data.get("static_price_ct")
        raw_valid_from = request.data.get("valid_from")

        valid_from = today
        if raw_valid_from:
            try:
                valid_from = datetime.date.fromisoformat(str(raw_valid_from))
            except ValueError:
                valid_from = today

        static_price_eur = None
        if tariff_type == HomeTariff.TARIFF_STATIC:
            if raw_static_price is None or raw_static_price == "":
                return Response(
                    {"detail": "Für statische Tarife muss ein Arbeitspreis in ct/kWh angegeben werden."},
                    status=400,
                )
            try:
                static_price_eur = Decimal(str(raw_static_price)) / Decimal("100")
            except Exception:
                return Response(
                    {"detail": "Ungültiger Preiswert."},
                    status=400,
                )

        tariff, _ = HomeTariff.objects.update_or_create(
            home=home,
            valid_from=valid_from,
            defaults={
                "tariff_type": tariff_type,
                "static_price_eur_per_kwh": static_price_eur,
            },
        )

        # Tibber Zugangsdaten auf dem User speichern (falls mitgesendet)
        user = request.user
        user_updated = False
        if "tibber_token" in request.data:
            user.tibber_token = (request.data.get("tibber_token") or "").strip() or None
            user_updated = True
        if "tibber_home_id" in request.data:
            user.tibber_home_id = (request.data.get("tibber_home_id") or "").strip() or None
            user_updated = True
        if user_updated:
            user.save(update_fields=["tibber_token", "tibber_home_id"])

    # GET oder Rückgabe nach POST
    active_tariff = get_home_tariff(home, today)
    price_config = get_price_config(today)

    config_data = None
    if price_config:
        config_data = {
            "grid_fee_ct": float(price_config.grid_fee_ct),
            "electricity_tax_ct": float(price_config.electricity_tax_ct),
            "concession_fee_ct": float(price_config.concession_fee_ct),
            "kwk_levy_ct": float(price_config.kwk_levy_ct),
            "special_grid_levy_ct": float(price_config.special_grid_levy_ct),
            "offshore_levy_ct": float(price_config.offshore_levy_ct),
            "vat_percent": float(price_config.vat_percent),
            "additional_costs_ct": float(price_config.additional_costs_ct()),
        }

    return Response(
        {
            "home_id": str(home.id),
            "home_name": home.name,
            "tariff_type": active_tariff.tariff_type if active_tariff else HomeTariff.TARIFF_DYNAMIC,
            "static_price_ct": round(float(active_tariff.static_price_eur_per_kwh) * 100, 2) if active_tariff and active_tariff.static_price_eur_per_kwh is not None else None,
            "valid_from": active_tariff.valid_from.isoformat() if active_tariff else today.isoformat(),
            "price_config": config_data,
            "tibber_token": request.user.tibber_token or "",
            "tibber_home_id": request.user.tibber_home_id or "",
            "tibber_connected": bool(request.user.tibber_token and request.user.tibber_home_id),
        }
    )


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def fetch_tibber_homes_view(request):
    """
    Testet das Tibber-API-Token und ruft die verfügbaren Tibber-Homes ab.
    """
    token = request.data.get("tibber_token") or getattr(request.user, "tibber_token", None)
    if not token:
        return Response(
            {"detail": "Bitte ein gültiges Tibber-API-Token angeben."},
            status=400,
        )

    from integrations.services_tibber import get_tibber_homes
    result = get_tibber_homes(token.strip())
    if result.get("status") == "error":
        return Response(
            {"detail": result.get("error", "Fehler beim Abrufen der Tibber-Daten. Bitte Token prüfen.")},
            status=400,
        )

    return Response(
        {
            "status": "ok",
            "homes": result.get("homes", []),
        }
    )

