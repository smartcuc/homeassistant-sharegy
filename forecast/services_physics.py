##############################
# forecast/services_physics.py
##############################

from datetime import timedelta, timezone as dt_timezone
from django.utils import timezone


from forecast.models import WeatherForecast


def predict_next_24h_physics_for_generator_string(
    generator_string,
    horizon_hours: int = 72,
):
    """
    Erste echte Producer-basierte Physics-Version.

    Nutzt:
    - WeatherForecast
    - peak_power_kwp
    - shading_percent

    Orientierung und Dachneigung folgen im
    nächsten Schritt.
    """

    home = generator_string.generator.home

    weather_rows = WeatherForecast.objects.filter(
        home=home,
        ts__gte=timezone.now(),
    ).order_by("ts")[:horizon_hours]

    if not weather_rows:
        return []

    peak_power = float(generator_string.peak_power_kwp or 0)

    shading_factor = 1.0 - float(generator_string.shading_percent or 0) / 100.0

    azimuth = generator_string.orientation.azimuth_deg

    if azimuth == 180:
        orientation_factor = 1.0
    elif azimuth in (135, 225):
        orientation_factor = 0.9
    elif azimuth in (90, 270):
        orientation_factor = 0.8
    elif azimuth in (45, 315):
        orientation_factor = 0.65
    else:
        orientation_factor = 0.5

    tilt = int(generator_string.tilt_deg or 35)

    if tilt <= 10:
        tilt_factor = 0.85
    elif tilt <= 20:
        tilt_factor = 0.95
    elif tilt <= 40:
        tilt_factor = 1.00
    elif tilt <= 60:
        tilt_factor = 0.90
    else:
        tilt_factor = 0.75

    results = []

    for row in weather_rows:

        radiation = float(row.shortwave_radiation_wm2 or 0)

        forecast_kw = (
            peak_power
            * (radiation / 1000.0)
            * orientation_factor
            * tilt_factor
            * shading_factor
        )

        results.append(
            {
                "timestamp": row.ts,
                "forecast_kw": max(
                    0.0,
                    forecast_kw,
                ),
                "radiation_wm2": radiation,
                "orientation_factor": orientation_factor,
                "tilt_factor": tilt_factor,
                "shading_factor": shading_factor,
                "temperature_c": row.temperature_c,
                "cloud_cover_pct": row.cloud_cover_pct,
            }
        )

    return results
