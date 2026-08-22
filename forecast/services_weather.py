##############################
# forecast/services_weather.py
##############################

import requests
from decimal import Decimal
from collections import defaultdict

from django.conf import settings
from django.utils import timezone
from django.utils.dateparse import parse_datetime

from forecast.models import WeatherForecast
from forecast.services_bias import calculate_bias, apply_bias
from datetime import date, timedelta

DEFAULT_LAT = getattr(settings, "DEFAULT_WEATHER_LAT", 50.9)
DEFAULT_LON = getattr(settings, "DEFAULT_WEATHER_LON", 6.97)


# =========================
# 📍 COORDINATES
# =========================


def geocode_location(postal_code=None, city=None):
    """
    Ermittelt Koordinaten über Open-Meteo Geocoding anhand von PLZ und Ort.
    """
    query = f"{postal_code or ''} {city or ''}".strip()
    if not query:
        return None, None
    try:
        url = "https://geocoding-api.open-meteo.com/v1/search"
        params = {"name": query, "count": 1, "language": "de", "format": "json"}
        resp = requests.get(url, params=params, timeout=5)
        if resp.status_code == 200:
            results = resp.json().get("results", [])
            if results:
                return float(results[0]["latitude"]), float(results[0]["longitude"])
    except Exception:
        pass
    return None, None


def resolve_forecast_coordinates(home):
    lat = getattr(home, "latitude", None)
    lon = getattr(home, "longitude", None)

    if (lat is None or lon is None) and (getattr(home, "postal_code", None) or getattr(home, "city", None)):
        geo_lat, geo_lon = geocode_location(home.postal_code, home.city)
        if geo_lat is not None and geo_lon is not None:
            try:
                home.latitude = geo_lat
                home.longitude = geo_lon
                home.save(update_fields=["latitude", "longitude"])
            except Exception:
                pass
            lat, lon = geo_lat, geo_lon

    if lat is None or lon is None:
        lat = DEFAULT_LAT
        lon = DEFAULT_LON

    return float(lat), float(lon)


# =========================
# 📍 GROUPING
# =========================


def get_location_group_key(home):
    lat, lon = resolve_forecast_coordinates(home)
    return (round(lat, 2), round(lon, 2))


def group_homes_by_location(homes):
    groups = defaultdict(list)

    for home in homes:
        key = get_location_group_key(home)
        groups[key].append(home)

    return groups


# =========================
# 🌦️ FETCH FORECAST
# =========================


def get_weather_forecast(lat, lon, hours=96):
    url = "https://api.open-meteo.com/v1/forecast"

    params = {
        "latitude": lat,
        "longitude": lon,
        "hourly": "shortwave_radiation,cloud_cover,temperature_2m",
        "forecast_days": 5,
        "timezone": "UTC",
    }

    response = requests.get(url, params=params, timeout=15)
    response.raise_for_status()

    data = response.json()
    hourly = data.get("hourly", {})

    return {
        "timestamps": hourly.get("time", [])[:hours],
        "radiation": hourly.get("shortwave_radiation", [])[:hours],
        "temperature": hourly.get("temperature_2m", [])[:hours],
        "cloud_cover": hourly.get("cloud_cover", [])[:hours],
    }


# =========================
# ✅ VALIDATION
# =========================


def validate_weather_payload(payload):

    timestamps = payload.get("timestamps", [])

    expected_delta = timezone.timedelta(hours=1)

    gaps = 0
    invalid_intervals = 0

    prev = None

    for ts in timestamps:
        dt = parse_datetime(ts)

        if dt is not None and timezone.is_naive(dt):
            dt = timezone.make_aware(dt, timezone.UTC)

        if dt is None:
            continue

        if prev:
            delta = dt - prev

            if delta != expected_delta:
                invalid_intervals += 1

                if delta > expected_delta:
                    gaps += 1

        prev = dt

    return {
        "count": len(timestamps),
        "gaps": gaps,
        "invalid_intervals": invalid_intervals,
        "status": "ok" if gaps == 0 and invalid_intervals == 0 else "warning",
    }


# =========================
# 💾 STORE DATA
# =========================


def store_weather_payload_for_home(
    home,
    payload,
):
    timestamps = payload.get("timestamps", [])
    radiation = payload.get("radiation", [])
    temperature = payload.get("temperature", [])
    cloud_cover = payload.get("cloud_cover", [])

    total = len(timestamps)
    skipped = 0
    missing_values = 0
    objs_to_create = []

    for i in range(total):
        dt = parse_datetime(timestamps[i])

        if dt is None:
            skipped += 1
            continue

        if timezone.is_naive(dt):
            dt = timezone.make_aware(dt, timezone.utc)

        rad = (
            float(radiation[i])
            if i < len(radiation) and radiation[i] is not None
            else None
        )
        temp = (
            float(temperature[i])
            if i < len(temperature) and temperature[i] is not None
            else None
        )
        clouds = (
            float(cloud_cover[i])
            if i < len(cloud_cover) and cloud_cover[i] is not None
            else None
        )

        if rad is None or temp is None or clouds is None:
            missing_values += 1

        objs_to_create.append(
            WeatherForecast(
                home=home,
                ts=dt,
                temperature_c=temp,
                cloud_cover_pct=clouds,
                shortwave_radiation_wm2=rad,
            )
        )

    if objs_to_create:
        WeatherForecast.objects.bulk_create(
            objs_to_create,
            update_conflicts=True,
            unique_fields=["home", "ts"],
            update_fields=[
                "temperature_c",
                "cloud_cover_pct",
                "shortwave_radiation_wm2",
            ],
        )

    return {
        "written": len(objs_to_create),
        "total": total,
        "skipped": skipped,
        "missing_values": missing_values,
    }


# =========================
# 🚀 MAIN ENTRY
# =========================


def fetch_and_store_weather_for_group(homes, hours=96):

    homes = list(homes)
    if not homes:
        return {
            "status": "ok",
            "count": 0,
            "home_count": 0,
        }

    lat, lon = resolve_forecast_coordinates(homes[0])

    payload = get_weather_forecast(lat, lon, hours=hours)

    # ✅ VALIDATION hinzufügen
    validation = validate_weather_payload(payload)

    total_written = 0
    per_home_stats = []

    for home in homes:
        stats = store_weather_payload_for_home(
            home,
            payload,
        )

        total_written += stats["written"]
        per_home_stats.append(stats)

    return {
        "status": "ok",
        "count": len(payload["timestamps"]),
        "home_count": len(homes),
        "lat": lat,
        "lon": lon,
        "written_total": total_written,
        "validation": validation,
        "home_stats": per_home_stats,
    }
