###################
# forecast/tasks.py
###################

from celery import shared_task
from django.utils import timezone

from devices.models import Home
from producer.models import GeneratorString

# from forecast.services_ml import train_tenant_model
from forecast.services_store import save_all_forecasts_for_generator_string

from forecast.tasks_weather import fetch_weather_data
from forecast.tasks_weather_observations import (
    fetch_weather_observations,
)

# 🔥 NEU IMPORTIEREN
from forecast.services_weather import (
    group_homes_by_location,
    fetch_and_store_weather_for_group,
)

@shared_task
def update_all_forecasts():
    """
    Zentrale Forecast-Pipeline:
    - Weather
    - ML
    - Forecast
    """

    # ✅ STEP 2 → HIER REIN
    homes = list(Home.objects.all())

    if not homes:
        return {"status": "no homes"}

    location_groups = group_homes_by_location(homes)

    results = []

    for location_key, home_group in location_groups.items():

        try:
            weather_result = fetch_and_store_weather_for_group(
                home_group,
                hours=96,
            )

        except Exception as e:
            for home in home_group:
                results.append(
                    {
                        "home_id": str(home.id),
                        "status": "error",
                        "stage": "weather",
                        "error": str(e),
                    }
                )
            continue

        # ✅ zweiter try (Forecast)
        for home in home_group:

            for generator in home.generator_systems.all():

                for generator_string in generator.strings.all():

                    try:

                        forecast_result = (
                            save_all_forecasts_for_generator_string(
                                generator_string,
                            )
                        )

                        results.append(
                            {
                                "home_id": str(home.id),
                                "generator_string": str(generator_string.id),
                                "status": "ok",
                                "location_key": str(location_key),
                                "weather_points": weather_result.get("count"),
                                "counts": forecast_result.get("counts"),
                            }
                        )

                    except Exception as e:

                        results.append(
                            {
                                "home_id": str(home.id),
                                "generator_string": str(generator_string.id),
                                "status": "error",
                                "stage": "forecast",
                                "error": str(e),
                            }
                        )

    return {
        "run_at": str(timezone.now()),
        "results": results,
    }


@shared_task
def train_all_generator_ml_models():
    """
    Trainiert wöchentlich/nächtlich die ML-Modelle aller aktiven GeneratorStrings.
    """
    from producer.models import GeneratorString
    from forecast.services_ml import train_generator_string_model

    strings = list(GeneratorString.objects.filter(generator__home__isnull=False))
    results = []

    for s in strings:
        try:
            res = train_generator_string_model(s)
            results.append(res)
        except Exception as e:
            results.append({
                "string_id": str(s.id),
                "status": "error",
                "error": str(e),
            })

    return {
        "trained_at": str(timezone.now()),
        "results": results,
    }


@shared_task
def fetch_weather_and_solar_forecast():
    """
    Alias-Task für Admin-Actions und Periodic Schedule.
    """
    return update_all_forecasts()
