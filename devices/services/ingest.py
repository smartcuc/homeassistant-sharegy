#############################
# devices/services/ingest.py
#############################

import logging
from typing import Any, Dict, Optional
from datetime import datetime, timezone as dt_timezone

from django.utils import timezone
from django.core.cache import cache
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync

from devices.models import (
    Device,
    DeviceMetric,
    DeviceLatestMetric,
    MetricDefinition,
)
from devices.services.metrics import should_record_metric, should_record_state, normalize_battery_metrics

logger = logging.getLogger(__name__)

LEAD_POWER_KEYS = {
    "power",
    "active_power",
    "p_total",
    "p",
    "w",
    "watt",
    "val",
    "value",
    "grid_power",
    "grid_power_w",
    "pv_power",
    "pv_power_w",
    "load_power",
    "load_power_w",
    "battery_power",
    "battery_power_w",
    "battery_w",
}


def _to_float(val: Any) -> Optional[float]:
    try:
        if val is None:
            return None
        return float(val)
    except (ValueError, TypeError):
        return None


def broadcast_live_update(device: Device, metric_key: str, value: float, unit: str, timestamp: datetime):
    """
    Sendet ein WebSocket Live-Update an eingeloggte Dashboard-User des Haushalts.
    Gedrosselt auf max 1 Event pro Sekunde pro User.
    """
    try:
        user_id = device.home.user_id
        cache_key = f"ws_update_{user_id}"
        if cache.get(cache_key):
            return
        cache.set(cache_key, True, timeout=1)

        channel_layer = get_channel_layer()
        if not channel_layer:
            return

        async_to_sync(channel_layer.group_send)(
            f"energy_{user_id}",
            {
                "type": "send_energy_update",
                "data": {
                    "type": "metric_update",
                    "device_id": device.id,
                    "metric": metric_key,
                    "value": value,
                    "unit": unit,
                    "timestamp": timestamp.isoformat(),
                },
            },
        )
    except Exception as e:
        logger.debug("WebSocket broadcast skipped: %s", e)


def ingest_metric_payload(
    device: Device,
    metrics: Dict[str, Any],
    timestamp: Optional[datetime] = None,
    source: str = "mqtt",
    meta: Optional[Dict[str, Any]] = None,
    state: Optional[Dict[str, Any]] = None,
    unit_map: Optional[Dict[str, str]] = None,
) -> Dict[str, Any]:
    """
    Zentrale, standardisierte Ingestion Pipeline für alle Sharegy Datenquellen.
    (MQTT, OpenTelemetry, Modbus, Webhooks, Buffer-Worker, Simulator).

    Ablauf:
    1. Zeitstempel normalisieren & Device.last_seen aktualisieren
    2. Lead-Wirkleistung identifizieren & Redis Live-Cache setzen
    3. DeviceLatestMetric O(1) Snapshot aktualisieren
    4. Enterprise Deadband & Heartbeat Deduplizierung anwenden
    5. Zeitreihen-Insert in DeviceMetric bei echten Änderungen
    6. State-Tracking (state.relay, state.error etc.)
    7. WebSocket Broadcast an das Frontend
    """
    if not device:
        raise ValueError("device is required for ingestion")

    if not metrics and not state:
        return {"status": "empty", "created_metrics": 0}

    # 1. Zeitstempel normalisieren
    if timestamp is None:
        ts = timezone.now()
    elif timezone.is_naive(timestamp):
        ts = timezone.make_aware(timestamp, dt_timezone.utc)
    else:
        ts = timestamp.astimezone(dt_timezone.utc)

    # Device last_seen aktualisieren
    device.last_seen = ts
    device.save(update_fields=["last_seen"])

    # Auto-Configuration falls noch unkonfiguriert
    if not device.configured:
        device.configured = True
        device.save(update_fields=["configured"])

    config = getattr(device, "config", None)
    configured_lead_key = (
        config.metric_definition.key
        if config and config.metric_definition
        else None
    )

    created_metrics = 0
    raw_meta = meta or {}
    unit_map = unit_map or {}

    # 1.5 Batterie-Metriken bei Bedarf normalisieren (Sungrow, Modbus, MQTT Richtung)
    metrics = normalize_battery_metrics(metrics, state=state, meta=meta)

    # 2. Metriken verarbeiten
    for key, val in metrics.items():
        float_val = _to_float(val)
        if float_val is None:
            continue

        metric_key = str(key).strip()
        unit = unit_map.get(metric_key, "")

        # Lead-Wirkleistung erkennen
        is_lead = (
            (configured_lead_key and metric_key == configured_lead_key)
            or (not configured_lead_key and metric_key.lower() in LEAD_POWER_KEYS)
        )

        # Falls Lead-Metrik: Sofort in Redis Live-Cache spiegeln (Echtzeit UI)
        if is_lead:
            cache.set(f"device:{device.id}:latest_power", float_val, timeout=3600)
            # Auto-Assign falls noch keine MetricDefinition verknüpft ist
            if config and not config.metric_definition:
                m_def, _ = MetricDefinition.objects.get_or_create(
                    key=metric_key,
                    defaults={"name": metric_key.replace("_", " ").title(), "unit": unit or "W"}
                )
                config.metric_definition = m_def
                config.save(update_fields=["metric_definition"])
                configured_lead_key = metric_key

        # 3. Snapshot-Tabelle DeviceLatestMetric aktualisieren (O(1))
        DeviceLatestMetric.objects.update_or_create(
            device=device,
            metric_key=metric_key,
            defaults={
                "value": float_val,
                "unit": unit,
                "data": {"source": source, "raw": raw_meta},
                "timestamp": ts,
            },
        )

        # 4. Zeitreihe mit Deadband- und Heartbeat-Deduplizierung schreiben
        if should_record_metric(device.id, metric_key, float_val, ts):
            DeviceMetric.objects.create(
                device=device,
                timestamp=ts,
                metric_key=metric_key,
                value=float_val,
                unit=unit,
                data={
                    "source": source,
                    "raw": raw_meta,
                },
            )
            created_metrics += 1

            if is_lead:
                broadcast_live_update(device, metric_key, float_val, unit, ts)

    # 5. State-Verarbeitung (z. B. Relay-Zustand, Modus, Fehlermeldungen)
    if state and isinstance(state, dict):
        for state_name, state_val in state.items():
            state_key = f"state.{state_name}"
            float_state = _to_float(state_val)

            DeviceLatestMetric.objects.update_or_create(
                device=device,
                metric_key=state_key,
                defaults={
                    "value": float_state,
                    "unit": "",
                    "data": {"source": source, "raw_state": state_val, "raw": raw_meta},
                    "timestamp": ts,
                },
            )

            if should_record_state(device.id, state_name, state_val, ts):
                DeviceMetric.objects.create(
                    device=device,
                    timestamp=ts,
                    metric_key=state_key,
                    value=float_state,
                    unit="",
                    data={
                        "source": source,
                        "raw_state": state_val,
                        "raw": raw_meta,
                    },
                )

    return {
        "status": "ok",
        "device_id": device.id,
        "created_metrics": created_metrics,
        "timestamp": ts.isoformat(),
    }
