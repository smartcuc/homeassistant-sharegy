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
from devices.services.metrics import should_record_metric, should_record_state, normalize_battery_metrics, normalize_grid_metrics

logger = logging.getLogger(__name__)

LEAD_POWER_KEYS = {
    "power",
    "active_power",
    "p_total",
    "p",
    "w",
    "watt",
    "grid_power",
    "grid_power_w",
    "pv_power",
    "pv_power_w",
    "load_power",
    "load_power_w",
    "battery_power",
    "battery_power_w",
    "battery_w",
    "apower",
    "a_act_power",
    "b_act_power",
    "c_act_power",
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


CANONICAL_METRIC_UNITS = {
    "power": "W",
    "active_power": "W",
    "p_total": "W",
    "p": "W",
    "w": "W",
    "watt": "W",
    "pv_power": "W",
    "pv_power_w": "W",
    "load_power": "W",
    "load_power_w": "W",
    "grid_power": "W",
    "grid_power_w": "W",
    "battery_power": "W",
    "battery_power_w": "W",
    "battery_w": "W",
    "apower": "W",
    "a_act_power": "W",
    "b_act_power": "W",
    "c_act_power": "W",
    "value": "W",
    "val": "W",
    "energy": "kWh",
    "energy_kwh": "kWh",
    "energy_wh": "Wh",
    "energy_in": "kWh",
    "energy_out": "kWh",
    "total_energy": "kWh",
    "total_energy_kwh": "kWh",
    "total_charge": "kWh",
    "total_discharge": "kWh",
    "total_yield": "kWh",
    "daily_yield": "kWh",
    "a_total_energy": "Wh",
    "b_total_energy": "Wh",
    "c_total_energy": "Wh",
    "voltage": "V",
    "battery_voltage": "V",
    "grid_voltage": "V",
    "a_voltage": "V",
    "b_voltage": "V",
    "c_voltage": "V",
    "current": "A",
    "battery_current": "A",
    "grid_current": "A",
    "a_current": "A",
    "b_current": "A",
    "c_current": "A",
    "soc": "%",
    "battery_soc": "%",
    "soh": "%",
    "battery_level": "%",
    "humidity": "%",
    "frequency": "Hz",
    "grid_frequency": "Hz",
    "temperature": "°C",
    "temp": "°C",
    "device_temp": "°C",
    "battery_temp": "°C",
}


VALID_PHYSICAL_UNITS = {
    "voltage": {"V", "kV", "mV", "v", "kv", "mv"},
    "current": {"A", "mA", "kA", "a", "ma", "ka"},
    "frequency": {"Hz", "kHz", "hz", "khz"},
    "temperature": {"°C", "C", "c", "K", "°F", "F"},
    "soc": {"%", "pct", "percent"},
    "soh": {"%", "pct", "percent"},
    "humidity": {"%", "pct", "percent"},
    "energy": {"kWh", "Wh", "MWh", "kwh", "wh", "mwh"},
    "power": {"W", "kW", "MW", "w", "kw", "mw"},
}


def _infer_canonical_unit(metric_key: str, given_unit: str, config: Any = None) -> str:
    k = (metric_key or "").strip().lower()
    u = (given_unit or "").strip()

    # 1. Bei generischen Keys (value, val) IMMER zuerst die Gerätekonfiguration befragen
    if k in ["value", "val", "main", "lead", ""]:
        if config and config.metric_definition:
            cfg_u = (config.metric_definition.unit or "").strip()
            cfg_k = (config.metric_definition.key or "").strip().lower()
            if cfg_u:
                return cfg_u
            if cfg_k in CANONICAL_METRIC_UNITS:
                return CANONICAL_METRIC_UNITS[cfg_k]
        if u:
            return u
        return "W"

    # 2. Spannungen (Voltage)
    if any(w in k for w in ["voltage", "volt", "spannung"]) and "power" not in k:
        if u in VALID_PHYSICAL_UNITS["voltage"]:
            return u
        return "V"

    # 3. Stromstärken (Current)
    if any(w in k for w in ["current", "strom", "amper"]) and "power" not in k:
        if u in VALID_PHYSICAL_UNITS["current"]:
            return u
        return "A"

    # 4. Frequenz (Frequency)
    if any(w in k for w in ["frequency", "frequenz", "freq"]):
        if u in VALID_PHYSICAL_UNITS["frequency"]:
            return u
        return "Hz"

    # 5. Temperatur (Temperature)
    if any(w in k for w in ["temp", "grad_c", "celsius"]):
        if u in VALID_PHYSICAL_UNITS["temperature"]:
            return u
        return "°C"

    # 6. Prozentwerte (SoC, SoH, Luftfeuchte)
    if any(w in k for w in ["soc", "soh", "humidity", "feuchte", "level", "percent", "pct"]):
        if u in VALID_PHYSICAL_UNITS["soc"]:
            return u
        return "%"

    # 7. Energie / Zählerstand (Energy / Yield)
    if any(w in k for w in ["energy", "yield", "ertrag", "zaehlerstand"]) or (k.endswith("_wh") or k.endswith("_kwh")):
        if u in VALID_PHYSICAL_UNITS["energy"]:
            return u
        if "wh" in k and "kwh" not in k:
            return "Wh"
        return "kWh"

    # 8. Leistung (Power)
    if any(w in k for w in ["power", "leistung", "wirkleistung", "watt"]) or k in LEAD_POWER_KEYS:
        if u in VALID_PHYSICAL_UNITS["power"]:
            return u
        if "kw" in k and "kwh" not in k:
            return "kW"
        return "W"

    # 9. Fallback auf konfigurierte MetricDefinition
    if config and config.metric_definition:
        cfg_u = (config.metric_definition.unit or "").strip()
        cfg_k = (config.metric_definition.key or "").strip().lower()
        if cfg_u:
            return cfg_u
        if cfg_k in CANONICAL_METRIC_UNITS:
            return CANONICAL_METRIC_UNITS[cfg_k]

    if u:
        return u

    return "W"


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

    # 1.5 Batterie- & Grid-Metriken bei Bedarf normalisieren (Sungrow, Modbus, MQTT Richtung)
    metrics = normalize_battery_metrics(metrics, state=state, meta=meta)
    metrics = normalize_grid_metrics(metrics, state=state, meta=meta)

        # 2. Metriken verarbeiten
    for key, val in metrics.items():
        float_val = _to_float(val)
        if float_val is None:
            continue

        raw_key = str(key).strip()
        raw_lower = raw_key.lower()

        # 1. Alias-Normalisierung: soc / battery_level -> battery_soc
        if raw_lower in ["soc", "battery_level"]:
            metric_key = "battery_soc"
        # 2. Generische Keys (value, val) auf konfigurierte Lead-Metrik mappen
        elif configured_lead_key and raw_lower in ["value", "val"]:
            metric_key = configured_lead_key
        # 3. Single-Channel Submeter/Verbraucher: generische 'power'/'temp' auf konfigurierte Lead-Metrik mappen
        elif configured_lead_key:
            cfg_lower = configured_lead_key.lower()
            if ("power" in cfg_lower or cfg_lower in ["aircon_power", "heatpump_power", "bwwp_power", "wallbox_power"]) and raw_lower in LEAD_POWER_KEYS:
                metric_key = configured_lead_key
            elif "temp" in cfg_lower and raw_lower in ["temperature", "temp", "device_temp"]:
                metric_key = configured_lead_key
            else:
                metric_key = raw_key
        else:
            metric_key = raw_key

        raw_unit = unit_map.get(raw_key, "")
        unit = _infer_canonical_unit(metric_key, raw_unit, config=config)

        # Lead-Metrik erkennen (inkl. Aliasse für Temperatur, Leistung etc.)
        is_lead = False
        if configured_lead_key:
            cfg_lower = configured_lead_key.lower()
            m_lower = metric_key.lower()
            if m_lower == cfg_lower or m_lower in ["value", "val"]:
                is_lead = True
            elif "temp" in cfg_lower and "temp" in m_lower:
                is_lead = True
            elif ("power" in cfg_lower or cfg_lower in LEAD_POWER_KEYS) and (m_lower in LEAD_POWER_KEYS or "power" in m_lower):
                is_lead = True
        else:
            is_lead = (metric_key.lower() in LEAD_POWER_KEYS) or (metric_key.lower() in ["value", "val"])

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

        # Temperatur-Metriken direkt im Redis-Cache ablegen
        if any(t in metric_key.lower() for t in ["temp", "temperature", "temp_water", "water_temp", "grad"]):
            cache.set(f"device:{device.id}:temperature", float_val, timeout=3600)
            cache.set(f"device:{device.id}:temp_water", float_val, timeout=3600)

        # ⚡ Sub-Kanäle (PV, Load, Batterie, Grid, SoC) direkt im Redis-Cache spiegeln (O(1))
        m_low = metric_key.lower()
        if m_low in ["pv_power", "solar_power", "power_pv", "yield_power", "production", "mppt_power", "pv_power_w", "pv"]:
            cache.set(f"device:{device.id}:pv_power", float_val, timeout=300)
        elif m_low in ["load_power", "house_power", "home_power", "consumption", "load_power_w", "load", "use_power"]:
            cache.set(f"device:{device.id}:load_power", float_val, timeout=300)
        elif m_low in ["battery_power", "power_battery", "bat_power", "battery_power_w", "battery"]:
            cache.set(f"device:{device.id}:battery_power", float_val, timeout=300)
        elif m_low in ["grid_power", "meter_power", "grid_power_w", "grid"]:
            cache.set(f"device:{device.id}:grid_power", float_val, timeout=300)

        if any(s in m_low for s in ["soc", "battery_soc", "battery_level"]):
            cache.set(f"device:{device.id}:battery_soc", float_val, timeout=300)
            cache.set(f"device:{device.id}:latest_soc", float_val, timeout=300)

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

        # Veraltete Alias-Rows in DeviceLatestMetric aufräumen
        if metric_key.lower() in ["grid_power", "pv_power", "battery_power", "load_power", "battery_soc"] or (configured_lead_key and metric_key.lower() == configured_lead_key.lower()):
            DeviceLatestMetric.objects.filter(device=device, metric_key__in=["power", "value", "val"]).delete()
        if metric_key != raw_key and raw_key.lower() in ["power", "value", "val", "soc"]:
            DeviceLatestMetric.objects.filter(device=device, metric_key=raw_key).delete()
        if metric_key == "battery_soc":
            DeviceLatestMetric.objects.filter(device=device, metric_key="soc").delete()

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
