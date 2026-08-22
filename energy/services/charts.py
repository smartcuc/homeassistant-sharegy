###########################
# energy/services/charts.py
###########################

from datetime import timedelta
from zoneinfo import ZoneInfo
from collections import defaultdict

from django.utils import timezone
from django.db.models import Sum, Q

from devices.models import (
    DeviceMetric,
    DeviceMetric1m,
    DeviceMetric5m,
    DeviceMetric15m,
    DeviceMetric1h,
)


def get_dashboard_chart(device_ids):
    """
    Sparkline für Dashboard-Kacheln (letzte 24h).
    """
    if not device_ids:
        return []

    since = timezone.now() - timedelta(hours=24)

    # 1. Versuch: 1h Aggregationen
    rows = list(
        DeviceMetric1h.objects.filter(
            device_id__in=device_ids,
        )
        .filter(Q(metric_key__in=["power", "value"]) | Q(metric_key__isnull=True))
        .filter(bucket__gte=since)
        .values("bucket")
        .annotate(value=Sum("avg"))
        .order_by("bucket")
    )

    if not rows:
        # Fallback: 15m Aggregationen
        rows = list(
            DeviceMetric15m.objects.filter(
                device_id__in=device_ids,
            )
            .filter(Q(metric_key__in=["power", "value"]) | Q(metric_key__isnull=True))
            .filter(bucket__gte=since)
            .values("bucket")
            .annotate(value=Sum("avg"))
            .order_by("bucket")
        )

    if not rows:
        # Fallback: 1m Aggregationen
        rows = list(
            DeviceMetric1m.objects.filter(
                device_id__in=device_ids,
            )
            .filter(Q(metric_key__in=["power", "value"]) | Q(metric_key__isnull=True))
            .filter(bucket__gte=since)
            .values("bucket")
            .annotate(value=Sum("avg"))
            .order_by("bucket")
        )

    return [round(row["value"] or 0, 1) for row in rows]


def get_house_demand_chart(
    pv_ids,
    grid_ids,
    battery_ids,
):
    """
    Berechnet den Verlauf des Hausbedarfs (letzte 24h).
    """
    since = timezone.now() - timedelta(hours=24)
    data = defaultdict(float)

    for dev_ids in [pv_ids, battery_ids, grid_ids]:
        if not dev_ids:
            continue
        rows = (
            DeviceMetric1h.objects.filter(
                device_id__in=dev_ids,
            )
            .filter(Q(metric_key__in=["power", "value"]) | Q(metric_key__isnull=True))
            .filter(bucket__gte=since)
            .values("bucket")
            .annotate(value=Sum("avg"))
        )
        for r in rows:
            data[r["bucket"]] += r["value"] or 0

    if not data:
        # Fallback 15m
        for dev_ids in [pv_ids, battery_ids, grid_ids]:
            if not dev_ids:
                continue
            rows = (
                DeviceMetric15m.objects.filter(
                    device_id__in=dev_ids,
                )
                .filter(Q(metric_key__in=["power", "value"]) | Q(metric_key__isnull=True))
                .filter(bucket__gte=since)
                .values("bucket")
                .annotate(value=Sum("avg"))
            )
            for r in rows:
                data[r["bucket"]] += r["value"] or 0

    return [round(value, 1) for _, value in sorted(data.items())]


def _query_period_data(device_ids, primary_model, fallback_model, since, time_field="bucket", val_field="avg"):
    key_filter = Q(metric_key__in=["power", "value"]) | Q(metric_key__isnull=True)

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
):
    """
    Modalchart für 1h, 6h, 24h, 5d.
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

    # 1 Stunde (1m Aggregationen, Fallback Rohdaten)
    if period == "1h":
        since = now - timedelta(hours=1)
        rows, time_field = _query_period_data(device_ids, DeviceMetric1m, DeviceMetric, since)
        date_fmt = "%H:%M"

    # 6 Stunden (5m Aggregationen, Fallback 1m)
    elif period == "6h":
        since = now - timedelta(hours=6)
        rows, time_field = _query_period_data(device_ids, DeviceMetric5m, DeviceMetric1m, since)
        date_fmt = "%H:%M"

    # 24 Stunden (15m Aggregationen, Fallback 1h oder 5m)
    elif period == "24h":
        since = now - timedelta(hours=24)
        rows, time_field = _query_period_data(device_ids, DeviceMetric15m, DeviceMetric1h, since)
        if not rows:
            rows, time_field = _query_period_data(device_ids, DeviceMetric5m, DeviceMetric1m, since)
        date_fmt = "%H:%M"

    # 5 Tage (1h Aggregationen, Fallback 15m)
    elif period == "5d":
        since = now - timedelta(days=5)
        rows, time_field = _query_period_data(device_ids, DeviceMetric1h, DeviceMetric15m, since)
        date_fmt = "%d.%m %H:%M"

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
