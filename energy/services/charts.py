###########################
# energy/services/charts.py
###########################

from datetime import timedelta
from zoneinfo import ZoneInfo
from collections import defaultdict

from django.utils import timezone
from django.db.models import Sum, Q
from django.core.cache import cache

from devices.models import (
    DeviceMetric,
    DeviceMetric1m,
    DeviceMetric5m,
    DeviceMetric15m,
    DeviceMetric1h,
)


def get_dashboard_chart(device_ids, metric_keys=None):
    """
    Sparkline für Dashboard-Kacheln (letzte 24h).
    """
    if not device_ids:
        return []

    cache_key = f"dash_chart:{','.join(map(str, sorted(device_ids)))}:{','.join(sorted(metric_keys or []))}"
    cached = cache.get(cache_key)
    if cached is not None:
        return cached

    since = timezone.now() - timedelta(hours=24)
    if metric_keys:
        key_filter = Q(metric_key__in=metric_keys)
    else:
        key_filter = Q(metric_key__in=["power", "value", "a_act_power", "apower", "load", "pv_power", "grid_power", "battery_power", "load_power"]) | Q(metric_key__isnull=True)

    # 1. Versuch: 1h Aggregationen
    rows = list(
        DeviceMetric1h.objects.filter(
            device_id__in=device_ids,
        )
        .filter(key_filter)
        .filter(bucket__gte=since)
        .values("bucket")
        .annotate(value=Sum("avg"))
        .order_by("bucket")
    )

    if not rows:
        # Fallback 1: 15m Aggregationen
        rows = list(
            DeviceMetric15m.objects.filter(
                device_id__in=device_ids,
            )
            .filter(key_filter)
            .filter(bucket__gte=since)
            .values("bucket")
            .annotate(value=Sum("avg"))
            .order_by("bucket")
        )

    if not rows:
        # Fallback 2: 1m Aggregationen
        rows = list(
            DeviceMetric1m.objects.filter(
                device_id__in=device_ids,
            )
            .filter(key_filter)
            .filter(bucket__gte=since)
            .values("bucket")
            .annotate(value=Sum("avg"))
            .order_by("bucket")
        )

    if not rows:
        # Fallback 3: Raw DeviceMetric
        rows = list(
            DeviceMetric.objects.filter(
                device_id__in=device_ids,
            )
            .filter(key_filter)
            .filter(timestamp__gte=since)
            .values("timestamp")
            .annotate(value=Sum("value"))
            .order_by("timestamp")
        )
        # Wenn sehr viele Punkte da sind, sub-samplen auf ca. 24-48 Punkte
        if len(rows) > 48:
            step = len(rows) // 48
            rows = rows[::step]

    res = [round(row["value"] or 0, 1) for row in rows]
    cache.set(cache_key, res, timeout=60)
    return res


def get_house_demand_chart(
    pv_ids,
    grid_ids,
    battery_ids,
):
    """
    Berechnet den Verlauf des physikalischen Hausbedarfs (letzte 24h).
    """
    cache_key = f"demand_chart:{','.join(map(str, sorted(pv_ids or [])))}:{','.join(map(str, sorted(grid_ids or [])))}:{','.join(map(str, sorted(battery_ids or [])))}"
    cached = cache.get(cache_key)
    if cached is not None:
        return cached

    since = timezone.now() - timedelta(hours=24)
    pv_data = defaultdict(float)
    grid_data = defaultdict(float)
    battery_data = defaultdict(float)

    # 1. PV
    if pv_ids:
        rows = (
            DeviceMetric1h.objects.filter(
                device_id__in=pv_ids,
                metric_key__in=["pv_power", "pv_power_w", "solar_power", "pv", "production", "power", "value", "a_act_power", "apower"]
            )
            .filter(bucket__gte=since)
            .values("bucket")
            .annotate(value=Sum("avg"))
        )
        for r in rows:
            pv_data[r["bucket"]] += max(0.0, r["value"] or 0.0)

    # 2. Grid
    if grid_ids:
        rows = (
            DeviceMetric1h.objects.filter(
                device_id__in=grid_ids,
                metric_key__in=["grid_power", "grid_power_w", "meter_power", "power_grid", "power", "value", "a_act_power", "apower"]
            )
            .filter(bucket__gte=since)
            .values("bucket")
            .annotate(value=Sum("avg"))
        )
        for r in rows:
            grid_data[r["bucket"]] += r["value"] or 0.0

    # 3. Battery
    if battery_ids:
        rows = (
            DeviceMetric1h.objects.filter(
                device_id__in=battery_ids,
                metric_key__in=["battery_power", "battery_power_w", "power_battery", "power", "value", "a_act_power", "apower"]
            )
            .filter(bucket__gte=since)
            .values("bucket")
            .annotate(value=Sum("avg"))
        )
        for r in rows:
            battery_data[r["bucket"]] += r["value"] or 0.0

    all_buckets = sorted(set(pv_data.keys()) | set(grid_data.keys()) | set(battery_data.keys()))
    if not all_buckets:
        cache.set(cache_key, [], timeout=60)
        return []

    res = []
    for b in all_buckets:
        pv_val = max(0.0, pv_data.get(b, 0.0))
        grid_val = grid_data.get(b, 0.0)  # > 0 import, < 0 export
        bat_val = battery_data.get(b, 0.0)  # > 0 discharge, < 0 charge

        imp_val = max(0.0, grid_val)
        exp_val = max(0.0, -grid_val)
        dis_val = max(0.0, bat_val)
        chg_val = max(0.0, -bat_val)

        # Unmeasured generation guardrail (z.B. 2. WR / BKW)
        if exp_val > (pv_val + dis_val):
            pv_val += (exp_val - (pv_val + dis_val))

        derived = pv_val + dis_val + imp_val - chg_val - exp_val
        res.append(round(max(0.0, derived), 1))

    cache.set(cache_key, res, timeout=60)
    return res



def _query_period_data(device_ids, primary_model, fallback_model, since, time_field="bucket", val_field="avg", metric_keys=None):
    if metric_keys:
        key_filter = Q(metric_key__in=metric_keys)
    else:
        key_filter = Q(metric_key__in=["power", "value", "a_act_power", "apower"]) | Q(metric_key__isnull=True)

    rows = list(
        primary_model.objects.filter(
            device_id__in=device_ids,
        )
        .filter(key_filter)
        .filter(**{f"{time_field}__gte": since})
        .values(time_field)
        .annotate(value=Sum(val_field))
        .order_by(time_field)
    )

    if not rows and fallback_model:
        fb_time_field = "timestamp" if fallback_model == DeviceMetric else "bucket"
        fb_val_field = "value" if fallback_model == DeviceMetric else "avg"
        rows = list(
            fallback_model.objects.filter(
                device_id__in=device_ids,
            )
            .filter(key_filter)
            .filter(**{f"{fb_time_field}__gte": since})
            .values(fb_time_field)
            .annotate(value=Sum(fb_val_field))
            .order_by(fb_time_field)
        )
        time_field = fb_time_field

    return rows, time_field


def get_chart_data(
    device_ids,
    period="24h",
    timezone_name="UTC",
    start_date=None,
    end_date=None,
    metric_keys=None,
):
    """
    Modalchart für 1h, 6h, 24h, 5d, 7d, 30d, year und custom.
    """
    now = timezone.now()
    try:
        tz = ZoneInfo(timezone_name)
    except Exception:
        tz = ZoneInfo("UTC")

    if not device_ids:
        return {
            "period": period,
            "unit": "W",
            "timestamps": [],
            "export_timestamps": [],
            "values": [],
        }

    # Custom Zeitraum
    if period == "custom" and start_date:
        from datetime import datetime
        try:
            if isinstance(start_date, str):
                s_dt = datetime.fromisoformat(start_date) if "T" in start_date else datetime.strptime(start_date, "%Y-%m-%d")
                if timezone.is_naive(s_dt):
                    s_dt = s_dt.replace(tzinfo=tz)
            else:
                s_dt = start_date

            if end_date:
                if isinstance(end_date, str):
                    e_dt = datetime.fromisoformat(end_date) if "T" in end_date else datetime.strptime(end_date, "%Y-%m-%d").replace(hour=23, minute=59, second=59)
                    if timezone.is_naive(e_dt):
                        e_dt = e_dt.replace(tzinfo=tz)
                else:
                    e_dt = end_date
            else:
                e_dt = now

            dur_days = (e_dt - s_dt).days
            if dur_days <= 1:
                rows, time_field = _query_period_data(device_ids, DeviceMetric15m, DeviceMetric1h, s_dt, metric_keys=metric_keys)
                date_fmt = "%H:%M"
            elif dur_days <= 7:
                rows, time_field = _query_period_data(device_ids, DeviceMetric1h, DeviceMetric15m, s_dt, metric_keys=metric_keys)
                date_fmt = "%d.%m %H:%M"
            else:
                rows, time_field = _query_period_data(device_ids, DeviceMetric1h, None, s_dt, metric_keys=metric_keys)
                date_fmt = "%d.%m."
        except Exception:
            rows, time_field = [], "bucket"
            date_fmt = "%d.%m."

    # 1 Stunde (1m Aggregationen, Fallback Rohdaten)
    elif period == "1h":
        since = now - timedelta(hours=1)
        rows, time_field = _query_period_data(device_ids, DeviceMetric1m, DeviceMetric, since, metric_keys=metric_keys)
        date_fmt = "%H:%M"

    # 6 Stunden (5m Aggregationen, Fallback 1m)
    elif period == "6h":
        since = now - timedelta(hours=6)
        rows, time_field = _query_period_data(device_ids, DeviceMetric5m, DeviceMetric1m, since, metric_keys=metric_keys)
        date_fmt = "%H:%M"

    # 24 Stunden (15m Aggregationen, Fallback 1h oder 5m)
    elif period == "24h":
        since = now - timedelta(hours=24)
        rows, time_field = _query_period_data(device_ids, DeviceMetric15m, DeviceMetric1h, since, metric_keys=metric_keys)
        if not rows:
            rows, time_field = _query_period_data(device_ids, DeviceMetric5m, DeviceMetric1m, since, metric_keys=metric_keys)
        date_fmt = "%H:%M"

    # 5 Tage (1h Aggregationen, Fallback 15m)
    elif period == "5d":
        since = now - timedelta(days=5)
        rows, time_field = _query_period_data(device_ids, DeviceMetric1h, DeviceMetric15m, since, metric_keys=metric_keys)
        date_fmt = "%d.%m %H:%M"

    elif period in ("7d", "30d"):
        days = 7 if period == "7d" else 30
        since = now - timedelta(days=days)
        rows, time_field = _query_period_data(device_ids, DeviceMetric1h, DeviceMetric15m, since, metric_keys=metric_keys)
        date_fmt = "%d.%m."

    else:
        return {
            "period": period,
            "unit": "W",
            "timestamps": [],
            "export_timestamps": [],
            "values": [],
        }

    return {
        "period": period,
        "unit": "W",
        "timestamps": [
            row[time_field].astimezone(tz).strftime(date_fmt)
            for row in rows
        ],
        "export_timestamps": [
            row[time_field].astimezone(tz).strftime("%d.%m.%Y %H:%M")
            for row in rows
        ],
        "values": [
            round(float(row["value"] or 0), 1)
            for row in rows
        ],
    }
