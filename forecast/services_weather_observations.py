###########################################
# forecast/services_weather_observations.py
###########################################

from forecast.models import WeatherObservation
from datetime import timezone as dt_timezone
from django.utils.dateparse import parse_datetime
import logging

from math import radians
from math import sin
from math import cos
from math import sqrt
from math import atan2

from forecast.providers.sensor_community import (
    fetch_nearby_observations,
)


logger = logging.getLogger(__name__)

def distance_km(
    lat1,
    lon1,
    lat2,
    lon2,
):

    r = 6371

    dlat = radians(lat2 - lat1)
    dlon = radians(lon2 - lon1)

    a = (
        sin(dlat / 2) ** 2
        + cos(radians(lat1)) * cos(radians(lat2)) * sin(dlon / 2) ** 2
    )

    c = 2 * atan2(
        sqrt(a),
        sqrt(1 - a),
    )

    return r * c


def store_sensor_community_observations(
    home,
):

    lat = home.latitude
    lon = home.longitude

    rows = fetch_nearby_observations(
        lat=lat,
        lon=lon,
    )

    logger.info(
        "SensorCommunity rows=%s",
        len(rows),
    )

    objs_to_save = []

    for row in rows:

        location = row.get("location")

        if not location:
            continue

        try:

            obs_lat = float(location["latitude"])
            obs_lon = float(location["longitude"])

            distance = distance_km(
                lat,
                lon,
                obs_lat,
                obs_lon,
            )

            if distance > 25:
                continue

        except Exception:
            continue

        timestamp = parse_datetime(row.get("timestamp"))

        if timestamp is None:
            continue

        if timestamp.tzinfo is None:
            timestamp = timestamp.replace(tzinfo=dt_timezone.utc)
        else:
            timestamp = timestamp.astimezone(dt_timezone.utc)

        timestamp = timestamp.replace(microsecond=0)

        sensor = row.get("sensor") or {}
        location_obj = row.get("location") or {}

        station_id = str(sensor.get("id")) if sensor.get("id") else (str(location_obj.get("id")) if location_obj.get("id") else "unknown")

        temperature_c = None
        humidity_pct = None

        for item in row.get(
            "sensordatavalues",
            [],
        ):

            value_type = item.get("value_type")

            raw_value = item.get("value")

            try:
                numeric_value = float(raw_value)
            except Exception:
                continue

            if value_type == "temperature":
                temperature_c = numeric_value

            elif value_type == "humidity":
                humidity_pct = numeric_value

        if (
            temperature_c is None
            and humidity_pct is None
        ):
            continue

        objs_to_save.append(
            WeatherObservation(
                provider="sensor_community",
                station_id=station_id,
                timestamp=timestamp,
                home=home,
                latitude=obs_lat,
                longitude=obs_lon,
                temperature_c=temperature_c,
                humidity_pct=humidity_pct,
            )
        )

    # In-Memory Deduplizierung nach (provider, station_id, timestamp-epoch) gegen PostgreSQL CardinalityViolation
    unique_map = {}
    for obj in objs_to_save:
        ts_epoch = int(obj.timestamp.timestamp()) if hasattr(obj.timestamp, "timestamp") else str(obj.timestamp)
        key = (str(obj.provider), str(obj.station_id or ""), ts_epoch)
        if key in unique_map:
            existing = unique_map[key]
            if existing.temperature_c is None and obj.temperature_c is not None:
                existing.temperature_c = obj.temperature_c
            if existing.humidity_pct is None and obj.humidity_pct is not None:
                existing.humidity_pct = obj.humidity_pct
        else:
            unique_map[key] = obj

    deduped_objs = list(unique_map.values())

    if deduped_objs:
        WeatherObservation.objects.bulk_create(
            deduped_objs,
            update_conflicts=True,
            unique_fields=["provider", "station_id", "timestamp"],
            update_fields=[
                "home",
                "latitude",
                "longitude",
                "temperature_c",
                "humidity_pct",
            ],
            batch_size=500,
        )

    return {
        "saved": len(deduped_objs),
    }
