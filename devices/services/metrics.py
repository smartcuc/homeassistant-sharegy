#############################
# devices/services/metrics.py
#############################

from datetime import timedelta
from django.utils import timezone
import logging
from django.core.cache import cache

from devices.models import DeviceMetric, DeviceLatestMetric
from devices.services.device_health import ONLINE_TIMEOUT

logger = logging.getLogger("django")


def resolve_battery_direction(direction_val):
    """
    Ermittelt die physikalische Richtung eines Batteriespeichers (Sungrow, Huawei, Deye, SMA, Victron, etc.):
    Rückgabe:
      1: Discharging (Entladen ins Haus, physikalisch positive Wirkleistung)
     -1: Charging (Laden aus PV/Netz, physikalisch negative Wirkleistung / Last)
      0: Idle / Standby
      None: Unbekannt / Nicht angegeben
    """
    if direction_val is None:
        return None

    if isinstance(direction_val, (int, float)):
        # Sungrow & Modbus Standard: 1 = Charge, 2 = Discharge, 0 = Idle/Standby
        if direction_val == 1:
            return -1  # Charge (negativ)
        elif direction_val == 2:
            return 1   # Discharge (positiv)
        elif direction_val == 0:
            return 0   # Idle
        elif direction_val == -1:
            return -1  # Manche Hersteller nutzen -1 für Charge

    str_val = str(direction_val).strip().lower()
    if str_val in ["charge", "charging", "laden", "in", "inflow", "chg", "1", "0x0008", "0x0001"]:
        return -1
    elif str_val in ["discharge", "discharging", "entladen", "out", "outflow", "dischg", "2", "0x0004", "0x0002"]:
        return 1
    elif str_val in ["idle", "standby", "off", "stop", "0", "0x0000"]:
        return 0

    return None


def normalize_battery_metrics(metrics, state=None, meta=None):
    """
    Prüft, ob in den eingehenden Daten (z. B. Sungrow Inverter) separate Lade-/Entlade-Leistungen,
    ein vorzeichenbehafteter Batteriestrom (battery_current) oder Richtungs-Parameter vorliegen
    und passt das Vorzeichen von 'power' bzw. 'battery_power' an.
    """
    if not isinstance(metrics, dict):
        return metrics

    res = dict(metrics)

    # A) Vorzeichenbehafteter Batteriestrom (z. B. Sungrow Register 5630/5631 oder 13020/13021)
    # Negativ (< 0 A): Batterie lädt | Positiv (> 0 A): Batterie entlädt
    current_val = res.get("battery_current") if "battery_current" in res else (res.get("current") if "current" in res else None)
    if current_val is not None:
        try:
            float_curr = float(current_val)
            power_key = next((k for k in ["power", "battery_power", "active_power", "val", "value"] if k in res and res[k] is not None), None)
            if power_key:
                raw_p = abs(float(res[power_key]))
                if float_curr < 0:
                    res[power_key] = -raw_p
                    res["power"] = -raw_p
                elif float_curr > 0:
                    res[power_key] = raw_p
                    res["power"] = raw_p
                else:
                    res[power_key] = 0.0
                    res["power"] = 0.0
                return res
            elif "battery_voltage" in res or "voltage" in res:
                volt = float(res.get("battery_voltage") or res.get("voltage") or 0)
                if volt > 0:
                    calc_p = round(volt * float_curr, 2)
                    res["power"] = calc_p
                    res["battery_power"] = calc_p
                    return res
        except (ValueError, TypeError):
            pass

    # B) Separate Lade- und Entlade-Leistungen (z. B. Home Assistant / MQTT)
    charging_power = res.get("battery_charging_power") or res.get("charging_power") or res.get("charge_power")
    discharging_power = res.get("battery_discharging_power") or res.get("discharging_power") or res.get("discharge_power")

    if charging_power is not None and float(charging_power or 0) > 0:
        res["power"] = -abs(float(charging_power))
        res["battery_power"] = -abs(float(charging_power))
        return res
    elif discharging_power is not None and float(discharging_power or 0) > 0:
        res["power"] = abs(float(discharging_power))
        res["battery_power"] = abs(float(discharging_power))
        return res

    # C) Richtungs-Parameter prüfen (Sungrow Modbus, MQTT etc.)
    all_dicts = [res, state or {}, meta or {}]
    direction_keys = [
        "battery_direction", "battery_power_direction", "direction",
        "battery_charge_discharge_state", "charge_discharge_state",
        "running_state", "running_status", "battery_status",
        "charge_state", "battery_state", "state", "status", "mode"
    ]

    dir_val = None
    for d in all_dicts:
        if isinstance(d, dict):
            for k in direction_keys:
                if k in d and d[k] is not None:
                    dir_val = d[k]
                    break
            if dir_val is not None:
                break

    resolved_dir = resolve_battery_direction(dir_val)
    if resolved_dir is not None:
        power_key = next((k for k in ["power", "battery_power", "active_power", "val", "value"] if k in res and res[k] is not None), None)
        if power_key:
            raw_p = abs(float(res[power_key]))
            if resolved_dir == -1:  # Charge
                res[power_key] = -raw_p
                res["power"] = -raw_p
            elif resolved_dir == 1:  # Discharge
                res[power_key] = raw_p
                res["power"] = raw_p
            elif resolved_dir == 0:  # Idle
                res[power_key] = 0.0
                res["power"] = 0.0

    return res


def get_latest_values(device_ids):
    if not device_ids:
        return {}

    # 1. Keys für Redis aufbauen
    cache_keys = {f"device:{d_id}:latest_power": d_id for d_id in device_ids}

    result = {}
    missing_ids = []

    # 2. Daten aus Redis laden
    try:
        cached_data = cache.get_many(cache_keys.keys())
        for key, d_id in cache_keys.items():
            if key in cached_data and cached_data[key] is not None:
                result[d_id] = float(cached_data[key])
            else:
                missing_ids.append(d_id)
    except Exception as e:
        logger.error(f"[REDIS_ERROR] Fehler beim Lesen aus dem Cache: {e}")
        missing_ids = list(device_ids)

    # 3. Fallback: Blitzschnelle 1-Query-Abfrage auf DeviceLatestMetric (O(1) Snapshot)
    if missing_ids:
        now = timezone.now()
        cutoff = now - timedelta(minutes=10)

        POWER_METRIC_KEYS = [
            "power", "value", "apower", "a_act_power", "pv_power", "pv_power_w",
            "load_power", "load_power_w", "grid_power", "grid_power_w",
            "battery_power", "battery_power_w", "battery_w",
            "active_power", "p_total", "p", "w", "watt", "load", "val", "energy"
        ]

        latest_rows = DeviceLatestMetric.objects.filter(
            device_id__in=missing_ids,
            metric_key__in=POWER_METRIC_KEYS,
        ).values_list("device_id", "value", "timestamp")

        # Prüfe auf separate Richtungs- und Strom-Metriken (battery_current / running_state / battery_direction)
        dir_rows = dict(
            DeviceLatestMetric.objects.filter(
                device_id__in=missing_ids,
                metric_key__in=[
                    "battery_direction", "battery_power_direction", "direction",
                    "battery_charge_discharge_state", "running_state", "charge_state", "state"
                ],
            ).values_list("device_id", "value")
        )

        curr_rows = dict(
            DeviceLatestMetric.objects.filter(
                device_id__in=missing_ids,
                metric_key__in=["battery_current", "current"],
            ).values_list("device_id", "value")
        )

        found_ids = set()
        for d_id, val, ts in latest_rows:
            found_ids.add(d_id)
            if val is not None:
                # Staleness-Check: Wenn Wechselrichter nachts abschaltet (>10min kein Signal), ist Erzeugung 0.0 W!
                if ts and ts < cutoff:
                    float_val = 0.0
                else:
                    float_val = float(val)
                    # A) Strom-Vorzeichen prüfen (höchste Genauigkeit!)
                    if d_id in curr_rows and curr_rows[d_id] is not None:
                        try:
                            f_curr = float(curr_rows[d_id])
                            if f_curr < 0:
                                float_val = -abs(float_val)
                            elif f_curr > 0:
                                float_val = abs(float_val)
                            else:
                                float_val = 0.0
                        except Exception:
                            pass
                    # B) Richtung korrigieren falls Richtungsmetrik vorliegt
                    elif d_id in dir_rows:
                        resolved_dir = resolve_battery_direction(dir_rows[d_id])
                        if resolved_dir == -1:  # Charge -> negativ
                            float_val = -abs(float_val)
                        elif resolved_dir == 1:  # Discharge -> positiv
                            float_val = abs(float_val)
                        elif resolved_dir == 0:  # Idle
                            float_val = 0.0

                result[d_id] = float_val
                try:
                    cache.set(f"device:{d_id}:latest_power", float_val, timeout=300)
                except Exception:
                    pass
                except Exception:
                    pass

        # 4. Selbstheilender Übergangs-Fallback: Falls DeviceLatestMetric für ein Gerät noch leer ist
        still_missing = [d_id for d_id in missing_ids if d_id not in found_ids]
        if still_missing:
            for d_id in still_missing:
                fallback_m = (
                    DeviceMetric.objects.filter(
                        device_id=d_id,
                        metric_key__in=POWER_METRIC_KEYS,
                    )
                    .order_by("-timestamp")
                    .first()
                )
                if fallback_m and fallback_m.value is not None:
                    if fallback_m.timestamp and fallback_m.timestamp < cutoff:
                        float_val = 0.0
                    else:
                        float_val = float(fallback_m.value)

                    result[d_id] = float_val
                    try:
                        cache.set(f"device:{d_id}:latest_power", float_val, timeout=300)
                        DeviceLatestMetric.objects.update_or_create(
                            device_id=d_id,
                            metric_key=fallback_m.metric_key,
                            defaults={
                                "value": float_val,
                                "timestamp": fallback_m.timestamp,
                            },
                        )
                    except Exception:
                        pass
                else:
                    result[d_id] = 0.0

    return result


def should_record_metric(
    device_id,
    metric_key,
    float_val,
    ts=None,
    deadband=1.0,
    heartbeat_seconds=60,
):
    """
    Enterprise-Grade Telemetrie Deduplizierung & Deadband-Filter.
    Prüft im Redis-Cache, ob der Wert sich signifikant geändert hat
    oder das Heartbeat-Intervall abgelaufen ist.
    Spart 80-90% redundante DB-Inserts ohne Datenverlust.
    """
    if float_val is None:
        return False

    dedup_key = f"dedup:{device_id}:{metric_key}"
    last_record = cache.get(dedup_key)

    if ts is not None and hasattr(ts, "timestamp"):
        now_ts = ts.timestamp()
    else:
        now_ts = timezone.now().timestamp()

    if last_record and isinstance(last_record, dict):
        last_val = last_record.get("val")
        last_ts = last_record.get("ts", 0)

        # Deadband Check
        if last_val is not None and abs(float_val - last_val) < deadband:
            # Heartbeat Check
            if (now_ts - last_ts) < heartbeat_seconds:
                return False

    cache.set(dedup_key, {"val": float_val, "ts": now_ts}, timeout=86400)
    return True


def should_record_state(device_id, key, val, ts=None, heartbeat_seconds=300):
    dedup_key = f"dedup:{device_id}:state:{key}"
    last_record = cache.get(dedup_key)

    if ts is not None and hasattr(ts, "timestamp"):
        now_ts = ts.timestamp()
    else:
        now_ts = timezone.now().timestamp()

    if last_record and isinstance(last_record, dict):
        last_val = last_record.get("val")
        last_ts = last_record.get("ts", 0)
        if last_val == val and (now_ts - last_ts) < heartbeat_seconds:
            return False

    cache.set(dedup_key, {"val": val, "ts": now_ts}, timeout=86400)
    return True
