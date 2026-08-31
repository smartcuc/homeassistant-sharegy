###########################
# forecast/services_store.py
###########################

from forecast.services_compare import build_hybrid_series
from producer.models import GeneratorString
from forecast.services_physics import predict_next_24h_physics_for_generator_string
from forecast.services_ml import predict_next_24h_ml_for_generator_string
from django.utils import timezone

from forecast.models import (
    SolarForecast,
    ForecastRun,
    ForecastValue,
)

def _store_series(generator_string, rows, source):
    rows = rows or []
    if not rows:
        return 0

    objs = [
        SolarForecast(
            generator_string=generator_string,
            timestamp=row["timestamp"],
            source=source,
            forecast_kwh=row["forecast_kw"],
        )
        for row in rows
    ]

    SolarForecast.objects.bulk_create(
        objs,
        update_conflicts=True,
        unique_fields=["generator_string", "timestamp", "source"],
        update_fields=["forecast_kwh"],
    )

    return len(objs)


def _store_forecast_run(
    generator_string,
    rows,
    source,
    horizon_hours: int = 72,
):
    rows = rows or []

    if not rows:
        return None

    run = ForecastRun.objects.create(
        generator_string=generator_string,
        source=source,
        generated_at=timezone.now(),
        horizon_hours=horizon_hours,
        resolution_minutes=60,
    )

    ForecastValue.objects.bulk_create(
        [
            ForecastValue(
                forecast_run=run,
                timestamp=row["timestamp"],
                forecast_kwh=row["forecast_kw"],
            )
            for row in rows
        ]
    )

    return run


def save_all_forecasts_for_generator_string(generator_string, horizon_hours: int = 72):

    phys = (
        predict_next_24h_physics_for_generator_string(
            generator_string,
            horizon_hours=horizon_hours,
        )
        or []
    )

    ml = (
        predict_next_24h_ml_for_generator_string(
            generator_string,
            horizon_hours=horizon_hours,
        )
        or []
    )

    # ✅ kein Input → fertig
    if not ml and not phys:
        return {
            "status": "no_data",
            "counts": {"physics": 0, "ml": 0, "hybrid": 0},
        }

    # ✅ Hybrid sauber ableiten
    if not ml:
        hybrid = phys
    elif not phys:
        hybrid = ml
    else:
        hybrid = build_hybrid_series(ml, phys, use_dynamic_weight=True)

    _store_forecast_run(
        generator_string,
        phys,
        "physics",
    )

    _store_forecast_run(
        generator_string,
        ml,
        "ml",
    )

    _store_forecast_run(
        generator_string,
        hybrid,
        "hybrid",
    )

    SolarForecast.objects.filter(
        generator_string=generator_string,
        source__in=["physics", "hybrid", "ml"],
    ).delete()

    saved_phys = _store_series(
        generator_string,
        phys,
        "physics",
    )

    saved_ml = _store_series(
        generator_string,
        ml,
        "ml",
    )

    saved_hybrid = _store_series(
        generator_string,
        hybrid,
        "hybrid",
    )

    return {
        "status": "ok",
        "counts": {
            "physics": saved_phys,
            "ml": saved_ml,
            "hybrid": saved_hybrid,
        },
    }
