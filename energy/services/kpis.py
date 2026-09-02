#########################
# energy/services/kpis.py
#########################

from datetime import datetime, time
from zoneinfo import ZoneInfo
from collections import defaultdict

from django.db.models import Sum, Q
from django.utils import timezone

from devices.models import (
    Device,
    DeviceMetric,
    DeviceMetric1m,
    DeviceMetric5m,
    DeviceMetric15m,
    DeviceMetric1h,
)
from energy.ems.models import EMSSignalSource

import logging

logger = logging.getLogger(__name__)


def get_today_consumption(user):
    """
    Ermittelt den heutigen Tagesverbrauch (kWh) und die stündlichen Verlaufswerte (history)
    für die KPI-Kachel 'Heute' im Dashboard.
    Funktioniert fehlertolerant für:
    - Konfigurierte Grid-/Load-Quellen
    - Einzelne Submeter & Smart Plugs (z. B. Shelly 1PM, Pro 3EM)
    - Timescale 1h/15m/5m/1m Continuous Aggregates sowie Roh-Telemetrie als Fallback.
    """
    home = user.homes.first() if hasattr(user, "homes") else None
    tz_str = (home.timezone if home and home.timezone else getattr(user, "timezone", "Europe/Berlin")) or "Europe/Berlin"
    try:
        tz = ZoneInfo(tz_str)
    except Exception:
        tz = ZoneInfo("Europe/Berlin")

    now_local = timezone.now().astimezone(tz)
    today_start = now_local.replace(hour=0, minute=0, second=0, microsecond=0)
    today_start_utc = today_start.astimezone(ZoneInfo("UTC"))

    # 1. Relevante Geräte für den Haushalt ermitteln
    # Priorität A: EMS-Signalquellen für Grid oder Load/Consumer
    grid_sources = list(
        EMSSignalSource.objects.filter(
            home__user=user,
            signal_type__key__in=["grid", "grid_import", "load", "consumer", "consumption"],
        ).values_list("device_id", flat=True)
    )

    # Priorität B: Alle relevanten Verbraucher-Geräte (keine reinen Erzeuger)
    consumer_devices = list(
        Device.objects.filter(
            home__user=user,
            active=True,
            pending_delete=False,
        ).exclude(config__role__key="producer").values_list("id", flat=True)
    )

    device_ids = grid_sources if grid_sources else consumer_devices

    if not device_ids:
        return {
            "value": 0.0,
            "source": None,
            "history": [],
        }

    # Nur echte Verbraucher-Metriken (bei Hybrid-Invertern load_power, niemals das Erzeugungs-Power)
    key_filter = Q(metric_key__in=["load_power", "load_power_w", "load", "a_act_power", "apower"]) | (
        Q(metric_key__in=["power", "value"]) & ~Q(device__config__role__key__in=["producer", "both", "hybrid"])
    )

    # 2. Versuch: DeviceMetric1h (Stunden-Aggregate)
    hourly_rows = list(
        DeviceMetric1h.objects.filter(
            device_id__in=device_ids,
            bucket__gte=today_start_utc,
        )
        .filter(key_filter)
        .values("bucket")
        .annotate(
            energy=Sum("energy_wh"),
            avg_w=Sum("avg"),
        )
        .order_by("bucket")
    )

    # Map von Stunde (0..now_local.hour) -> kWh
    hour_buckets = defaultdict(float)

    if hourly_rows:
        for r in hourly_rows:
            b_local = r["bucket"].astimezone(tz)
            h = b_local.hour
            wh = float(r["energy"] or 0)
            if wh > 0:
                kwh = wh / 1000.0
            else:
                kwh = max(0.0, float(r["avg_w"] or 0) / 1000.0)
            hour_buckets[h] += kwh
    else:
        # Fallback 1: DeviceMetric15m / DeviceMetric5m
        mid_rows = list(
            DeviceMetric15m.objects.filter(
                device_id__in=device_ids,
                bucket__gte=today_start_utc,
            )
            .filter(key_filter)
            .values("bucket")
            .annotate(
                energy=Sum("energy_wh"),
                avg_w=Sum("avg"),
            )
            .order_by("bucket")
        )
        if mid_rows:
            for r in mid_rows:
                b_local = r["bucket"].astimezone(tz)
                h = b_local.hour
                wh = float(r["energy"] or 0)
                if wh > 0:
                    kwh = wh / 1000.0
                else:
                    kwh = max(0.0, float(r["avg_w"] or 0) * 0.25 / 1000.0)
                hour_buckets[h] += kwh
        else:
            # Fallback 2: Raw DeviceMetric (letzte Messungen von heute)
            raw_rows = list(
                DeviceMetric.objects.filter(
                    device_id__in=device_ids,
                    timestamp__gte=today_start_utc,
                )
                .filter(key_filter)
                .values("timestamp", "value")
                .order_by("timestamp")
            )
            if raw_rows:
                hour_raw = defaultdict(list)
                for r in raw_rows:
                    t_local = r["timestamp"].astimezone(tz)
                    hour_raw[t_local.hour].append(max(0.0, float(r["value"] or 0)))

                for h, val_list in hour_raw.items():
                    if val_list:
                        avg_power_w = sum(val_list) / len(val_list)
                        kwh = (avg_power_w * (len(val_list) * 5 / 3600.0)) / 1000.0 if len(val_list) < 720 else avg_power_w / 1000.0
                        hour_buckets[h] = max(0.0, kwh)

    total_kwh = sum(hour_buckets.values())

    # 3. History-Array für die Sparkline aufbauen (von 0 bis zur aktuellen Stunde)
    current_hour = now_local.hour
    history = [round(hour_buckets[h], 3) for h in range(current_hour + 1)]

    if not history:
        history = [0.0]

    return {
        "value": round(total_kwh, 2),
        "source": "grid_or_devices",
        "history": history,
    }

