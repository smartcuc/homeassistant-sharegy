#################################
# devices/services/aggregation.py
#################################

from datetime import timedelta, datetime


from django.db import transaction
from django.db.models import (
    Avg,
    Min,
    Max,
    Count,
)

from django.utils import timezone

from devices.models import (
    DeviceMetric,
    DeviceMetric1m,
    DeviceMetric5m,
    DeviceMetric15m,
    DeviceMetric1h,
    DeviceConfig,
)


def floor_bucket(dt, seconds):

    epoch = int(dt.timestamp())

    floored = epoch - (epoch % seconds)

    return datetime.fromtimestamp(
        floored,
        tz=dt.tzinfo,
    )


def aggregate_1m(target_time=None):

    now = target_time or timezone.now()

    current_bucket = floor_bucket(
        now,
        60,
    )

    target = current_bucket - timedelta(
        minutes=1,
    )

    start = target
    end = target + timedelta(
        minutes=1,
    )

    rows = (
        DeviceMetric.objects
        .filter(
            timestamp__gte=start,
            timestamp__lt=end,
        )
        .values(
            "device_id",
            "metric_key",
        )
        .annotate(
            avg=Avg("value"),
            min=Min("value"),
            max=Max("value"),
            count=Count("id"),
        )
    )

    configs = dict(
        DeviceConfig.objects.filter(
            device__configured=True,
            metric_definition__isnull=False,
        ).values_list(
            "device_id",
            "metric_definition__key",
        )
    )

    objs_to_upsert = []

    for row in rows:
        metric_key = row.get("metric_key") or configs.get(row["device_id"]) or "power"

        energy_wh = None
        if metric_key in ["power", "value"] and row["avg"] is not None:
            energy_wh = row["avg"] / 60

        min_val = row["min"] if row["min"] is not None else row["avg"]
        max_val = row["max"] if row["max"] is not None else row["avg"]

        objs_to_upsert.append(
            DeviceMetric1m(
                device_id=row["device_id"],
                metric_key=metric_key,
                bucket=target,
                avg=row["avg"],
                min=min_val,
                max=max_val,
                count=row["count"],
                energy_wh=energy_wh,
            )
        )

    if objs_to_upsert:
        DeviceMetric1m.objects.bulk_create(
            objs_to_upsert,
            update_conflicts=True,
            unique_fields=["device", "metric_key", "bucket"],
            update_fields=["avg", "min", "max", "count", "energy_wh"],
        )


def rollup(
    source_model,
    target_model,
    bucket_seconds,
):
    """
    Generic rollup.

    - weighted avg
    - correct min/max
    - summed counts
    - summed energy
    """

    now = timezone.now()

    current_bucket = floor_bucket(
        now,
        bucket_seconds,
    )

    target = current_bucket - timedelta(
        seconds=bucket_seconds,
    )

    start = target
    end = target + timedelta(
        seconds=bucket_seconds,
    )

    rows = (
        source_model.objects
        .filter(
            bucket__gte=start,
            bucket__lt=end,
        )
        .order_by()
    )

    groups = {}

    for row in rows:

        key = (
            row.device_id,
            row.metric_key,
        )

        groups.setdefault(
            key,
            []
        ).append(row)

    objs_to_upsert = []

    for (
        device_id,
        metric_key,
    ), items in groups.items():

        total_count = sum(
            item.count or 0
            for item in items
        )

        if total_count == 0:
            continue

        weighted_sum = sum(
            (item.avg or 0)
            * (item.count or 0)
            for item in items
        )

        avg = (
            weighted_sum
            / total_count
        )

        min_value = min(
            (item.min for item in items if item.min is not None),
            default=avg,
        )

        max_value = max(
            (item.max for item in items if item.max is not None),
            default=avg,
        )

        energy_wh = sum(
            item.energy_wh or 0
            for item in items
        )

        objs_to_upsert.append(
            target_model(
                device_id=device_id,
                metric_key=metric_key,
                bucket=target,
                avg=avg,
                min=min_value,
                max=max_value,
                count=total_count,
                energy_wh=energy_wh,
            )
        )

    if objs_to_upsert:
        target_model.objects.bulk_create(
            objs_to_upsert,
            update_conflicts=True,
            unique_fields=["device", "metric_key", "bucket"],
            update_fields=["avg", "min", "max", "count", "energy_wh"],
        )

def aggregate_5m():

    rollup(
        source_model=DeviceMetric1m,
        target_model=DeviceMetric5m,
        bucket_seconds=300,
    )


def aggregate_15m():

    rollup(
        source_model=DeviceMetric5m,
        target_model=DeviceMetric15m,
        bucket_seconds=900,
    )


def aggregate_1h():

    rollup(
        source_model=DeviceMetric15m,
        target_model=DeviceMetric1h,
        bucket_seconds=3600,
    )


def backfill_aggregations(hours=2):
    """
    Holt fehlende 1m, 5m, 15m und 1h Aggregationen für die letzten `hours` Stunden nach.
    """
    now = timezone.now()
    start = now - timedelta(hours=hours)

    current = floor_bucket(start, 60)
    end = floor_bucket(now, 60)

    configs = dict(
        DeviceConfig.objects.filter(
            device__configured=True,
            metric_definition__isnull=False,
        ).values_list(
            "device_id",
            "metric_definition__key",
        )
    )

    while current < end:
        bucket_start = current
        bucket_end = current + timedelta(minutes=1)

        rows = (
            DeviceMetric.objects
            .filter(timestamp__gte=bucket_start, timestamp__lt=bucket_end)
            .values("device_id", "metric_key")
            .annotate(
                avg=Avg("value"),
                min=Min("value"),
                max=Max("value"),
                count=Count("id"),
            )
        )

        objs = []
        for r in rows:
            m_key = r.get("metric_key") or configs.get(r["device_id"]) or "power"
            energy_wh = (r["avg"] / 60) if m_key in ["power", "value"] and r["avg"] is not None else None
            objs.append(
                DeviceMetric1m(
                    device_id=r["device_id"],
                    metric_key=m_key,
                    bucket=bucket_start,
                    avg=r["avg"],
                    min=r["min"],
                    max=r["max"],
                    count=r["count"],
                    energy_wh=energy_wh,
                )
            )

        if objs:
            DeviceMetric1m.objects.bulk_create(
                objs,
                update_conflicts=True,
                unique_fields=["device", "metric_key", "bucket"],
                update_fields=["avg", "min", "max", "count", "energy_wh"],
            )

        current += timedelta(minutes=1)

    # 5m, 15m, 1h Rollups nachziehen
    aggregate_5m()
    aggregate_15m()
    aggregate_1h()
