########################
# forecast/services_ml.py
########################

from pathlib import Path
from datetime import timedelta
import logging

import joblib
from sklearn.ensemble import RandomForestRegressor
from django.conf import settings
from django.db.models import Sum
from django.utils import timezone

from core.models import AggregatedReading
from devices.models import Device, DeviceMetric1h, DeviceMetric15m
from forecast.models import WeatherForecast, WeatherObservation
from forecast.services_ml_features import (
    build_training_matrix,
    build_generator_training_matrix,
    build_recursive_feature_vector,
)
from forecast.services_weather import get_weather_forecast, resolve_forecast_coordinates

logger = logging.getLogger(__name__)

MODEL_DIR = Path(settings.BASE_DIR) / "ml_models"
MODEL_DIR.mkdir(parents=True, exist_ok=True)


def model_path_for_tenant(tenant_id):
    return MODEL_DIR / f"tenant_{tenant_id}.joblib"


def model_path_for_generator_string(string_id):
    return MODEL_DIR / f"string_{string_id}.joblib"


def ceil_to_next_hour(dt):
    dt = dt.replace(second=0, microsecond=0)
    if dt.minute == 0:
        return dt
    return (dt + timedelta(hours=1)).replace(minute=0)


# ============================================================
# ☀️ GENERATOR STRING ML PIPELINE
# ============================================================

def _load_string_hourly_actuals(generator_string):
    """
    Laedt historische stuendliche Erzeugungsdaten (kW) fuer diesen GeneratorString.
    Verbindet Home -> PV Devices -> DeviceMetric1h.
    """
    home = generator_string.generator.home
    if not home:
        return []

    producer_devices = list(
        Device.objects.filter(
            home=home,
            active=True,
            pending_delete=False,
        ).filter(
            config__role__key__in=["producer", "pv", "solar"]
        ).values_list("id", flat=True)
    )

    if not producer_devices:
        from energy.models import EMSSignalSource
        producer_devices = list(
            EMSSignalSource.objects.filter(
                home=home,
                signal_type__key__in=["pv", "solar", "producer"]
            ).values_list("device_id", flat=True)
        )

    if not producer_devices:
        return []

    total_home_kwp = sum(
        float(s.peak_power_kwp or 0)
        for gen in home.generator_systems.all()
        for s in gen.strings.all()
    )
    string_kwp = float(generator_string.peak_power_kwp or 0)
    string_ratio = (string_kwp / total_home_kwp) if total_home_kwp > 0 else 1.0

    rows = list(
        DeviceMetric1h.objects.filter(
            device_id__in=producer_devices,
            metric_key__in=["power", "value"],
        )
        .values("bucket")
        .annotate(total_avg_w=Sum("avg"))
        .order_by("bucket")
    )

    if not rows:
        rows = list(
            DeviceMetric15m.objects.filter(
                device_id__in=producer_devices,
                metric_key__in=["power", "value"],
            )
            .values("bucket")
            .annotate(total_avg_w=Sum("avg"))
            .order_by("bucket")
        )

    results = []
    for r in rows:
        ts = r["bucket"]
        total_kw = (float(r["total_avg_w"] or 0) / 1000.0) * string_ratio
        results.append({
            "timestamp": ts,
            "value": max(0.0, total_kw),
        })

    return results


def _load_home_weather_map(home):
    weather_map = {}

    forecast_rows = (
        WeatherForecast.objects.filter(home=home)
        .order_by("ts")
        .values("ts", "temperature_c", "cloud_cover_pct", "shortwave_radiation_wm2")
    )
    for r in forecast_rows:
        weather_map[r["ts"].replace(minute=0, second=0, microsecond=0)] = {
            "temperature_c": r["temperature_c"],
            "cloud_cover_pct": r["cloud_cover_pct"],
            "shortwave_radiation_wm2": r["shortwave_radiation_wm2"],
        }

    obs_rows = (
        WeatherObservation.objects.filter(home=home)
        .order_by("timestamp")
        .values("timestamp", "temperature_c", "cloud_cover_pct", "shortwave_radiation_wm2")
    )
    for r in obs_rows:
        weather_map[r["timestamp"].replace(minute=0, second=0, microsecond=0)] = {
            "temperature_c": r["temperature_c"],
            "cloud_cover_pct": r["cloud_cover_pct"],
            "shortwave_radiation_wm2": r["shortwave_radiation_wm2"],
        }

    return weather_map


def train_generator_string_model(generator_string):
    home = generator_string.generator.home
    if not home:
        return {"status": "no_home", "string_id": str(generator_string.id)}

    actual_rows = _load_string_hourly_actuals(generator_string)
    if len(actual_rows) < 24:
        return {
            "status": "not_enough_data",
            "string_id": str(generator_string.id),
            "samples": len(actual_rows),
        }

    weather_map = _load_home_weather_map(home)

    peak_power = float(generator_string.peak_power_kwp or 0)
    shading_factor = 1.0 - float(generator_string.shading_percent or 0) / 100.0
    tilt = int(generator_string.tilt_deg or 35)
    tilt_factor = 1.0 if 20 <= tilt <= 40 else 0.9

    physics_map = {}
    for ts, w in weather_map.items():
        rad = float(w.get("shortwave_radiation_wm2") or 0.0)
        physics_map[ts] = max(0.0, peak_power * (rad / 1000.0) * tilt_factor * shading_factor)

    X, y = build_generator_training_matrix(actual_rows, weather_map, physics_map)

    if len(X) < 24:
        return {
            "status": "not_enough_training_rows",
            "string_id": str(generator_string.id),
            "samples": len(X),
        }

    model = RandomForestRegressor(
        n_estimators=100,
        max_depth=10,
        min_samples_split=3,
        random_state=42,
        n_jobs=-1,
    )
    model.fit(X, y)

    path = model_path_for_generator_string(generator_string.id)
    joblib.dump(model, path)

    logger.info(f"ML-Modell fuer GeneratorString {generator_string.id} erfolgreich trainiert ({len(X)} Samples).")

    return {
        "status": "trained",
        "string_id": str(generator_string.id),
        "samples": len(X),
        "model_path": str(path),
    }


def load_generator_string_model(generator_string_id):
    path = model_path_for_generator_string(generator_string_id)
    if not path.exists():
        return None
    try:
        return joblib.load(path)
    except Exception as e:
        logger.warning(f"Fehler beim Laden des ML-Modells {path}: {e}")
        return None


def predict_next_24h_ml_for_generator_string(generator_string, horizon_hours: int = 72):
    home = generator_string.generator.home
    if not home:
        return []

    model = load_generator_string_model(generator_string.id)
    if model is None:
        train_res = train_generator_string_model(generator_string)
        if train_res.get("status") != "trained":
            return []
        model = load_generator_string_model(generator_string.id)
        if model is None:
            return []

    weather_rows = list(
        WeatherForecast.objects.filter(
            home=home,
            ts__gte=timezone.now(),
        ).order_by("ts")[:horizon_hours]
    )

    if not weather_rows:
        return []

    actuals = _load_string_hourly_actuals(generator_string)
    history_values = [r["value"] for r in actuals[-48:]] if actuals else [0.0] * 48

    peak_power = float(generator_string.peak_power_kwp or 0)
    shading_factor = 1.0 - float(generator_string.shading_percent or 0) / 100.0
    tilt = int(generator_string.tilt_deg or 35)
    tilt_factor = 1.0 if 20 <= tilt <= 40 else 0.9

    results = []

    for row in weather_rows:
        future_dt = row.ts.replace(minute=0, second=0, microsecond=0)
        radiation = float(row.shortwave_radiation_wm2 or 0.0)

        if radiation <= 0:
            results.append({
                "timestamp": row.ts,
                "forecast_kw": 0.0,
            })
            history_values.append(0.0)
            continue

        phys_est = max(0.0, peak_power * (radiation / 1000.0) * tilt_factor * shading_factor)

        weather_dict = {
            "temperature_c": row.temperature_c,
            "cloud_cover_pct": row.cloud_cover_pct,
            "shortwave_radiation_wm2": radiation,
        }

        X_future = build_recursive_feature_vector(
            history_values=history_values,
            future_dt=future_dt,
            weather=weather_dict,
            physics_kw=phys_est,
        )

        try:
            pred = float(model.predict(X_future)[0])
        except Exception:
            pred = phys_est

        pred = max(0.0, min(pred, peak_power * 1.2))

        history_values.append(pred)
        results.append({
            "timestamp": row.ts,
            "forecast_kw": round(pred, 3),
        })

    return results


# ============================================================
# TENANT ML PIPELINE (ENERGY SHARING)
# ============================================================

def _load_tenant_hourly_actuals(tenant):
    rows = list(
        AggregatedReading.objects.filter(
            tenant=tenant,
            period_type="hourly",
        )
        .values("period_start")
        .annotate(total_value=Sum("value"))
        .order_by("period_start")
    )

    if len(rows) < 2:
        return []

    result = []
    prev = None

    for row in rows:
        ts = row["period_start"]
        total_value = float(row["total_value"] or 0)

        if prev is None:
            prev = total_value
            continue

        diff = total_value - prev
        if diff < 0:
            diff = 0.0

        result.append({
            "timestamp": ts,
            "value": diff,
        })
        prev = total_value

    return result


def _load_historical_weather_map(tenant):
    rows = (
        WeatherForecast.objects.filter(tenant=tenant)
        .order_by("ts")
        .values("ts", "temperature_c", "cloud_cover_pct", "shortwave_radiation_wm2")
    )
    return {
        row["ts"]: {
            "temperature_c": row["temperature_c"],
            "cloud_cover_pct": row["cloud_cover_pct"],
            "shortwave_radiation_wm2": row["shortwave_radiation_wm2"],
        }
        for row in rows
    }


def _load_future_weather_map(tenant):
    lat, lon = resolve_forecast_coordinates(tenant)
    weather = get_weather_forecast(lat, lon)

    result = {}
    for ts, rad, temp, clouds in zip(
        weather["timestamps"],
        weather["radiation"],
        weather["temperature"],
        weather["cloud_cover"],
    ):
        from datetime import datetime
        dt = datetime.fromisoformat(ts)
        if timezone.is_naive(dt):
            dt = timezone.make_aware(dt, timezone=timezone.UTC)

        result[dt] = {
            "temperature_c": temp,
            "cloud_cover_pct": clouds,
            "shortwave_radiation_wm2": rad,
        }
    return result


def train_tenant_model(tenant):
    prod_rows = _load_tenant_hourly_actuals(tenant)
    weather_map = _load_historical_weather_map(tenant)

    X, y = build_training_matrix(prod_rows, weather_map)

    if len(X) == 0:
        return {
            "status": "not_enough_data",
            "tenant_id": str(tenant.id),
        }

    model = RandomForestRegressor(
        n_estimators=200,
        random_state=42,
        n_jobs=-1,
    )
    model.fit(X, y)

    path = model_path_for_tenant(tenant.id)
    joblib.dump(model, path)

    return {
        "status": "trained",
        "tenant_id": str(tenant.id),
        "samples": len(X),
        "model_path": str(path),
    }


def load_model(tenant_id):
    path = model_path_for_tenant(tenant_id)
    if not path.exists():
        return None
    return joblib.load(path)


def predict_next_24h_ml_for_tenant(tenant):
    model = load_model(tenant.id)

    if model is None:
        train_result = train_tenant_model(tenant)
        if train_result.get("status") != "trained":
            return None
        model = load_model(tenant.id)

    prod_rows = _load_tenant_hourly_actuals(tenant)
    if len(prod_rows) < 60:
        return None

    future_weather_map = _load_future_weather_map(tenant)

    history_values = [float(r["value"]) for r in prod_rows]
    history_timestamps = [r["timestamp"] for r in prod_rows]

    last_ts = history_timestamps[-1]
    start_ts = ceil_to_next_hour(last_ts)

    results = []

    for step in range(24):
        future_dt = start_ts + timedelta(hours=step)
        future_dt = future_dt.replace(minute=0, second=0, microsecond=0)

        weather = future_weather_map.get(future_dt)

        X_future = build_recursive_feature_vector(
            history_values=history_values,
            future_dt=future_dt,
            weather=weather,
        )

        pred = float(model.predict(X_future)[0])
        pred = max(0.0, pred)

        history_values.append(pred)

        results.append({
            "timestamp": future_dt,
            "forecast_kw": pred,
        })

    return results
