"""
devices/adapters/sensors/generic.py

Isolierter Adapter für generische JSON-Messwerte (Home Assistant REST/WSS, ioBroker, OpenHAB, Custom Webhooks).
Unterstützt:
- Flache und verschachtelte Payloads mit Standard-Keys (power, energy, voltage, current, etc.)
- ioBroker / SimpleAPI Format (val, value, v, ts, metric)
- Dynamische Metrik-Extraktion mit Einheitenerkennung
- Relais-Zustände (state, relay_state, ison, switch)
"""

import logging
from typing import Dict, Any, Optional
from django.utils import timezone

from devices.adapters.sensors.contracts import BaseSensorAdapter, CanonicalSensorReading

logger = logging.getLogger(__name__)


class GenericJsonSensorAdapter(BaseSensorAdapter):
    adapter_id = "generic_json"
    name = "Generic JSON Sensor (Home Assistant / ioBroker / Custom)"
    vendor = "Generic"
    protocol = "websocket_http"

    def supports_auto_detect(self, payload: Dict[str, Any]) -> bool:
        """
        Dient als universeller Fallback für beliebige wohlgeformte JSON-Payloads.
        """
        return isinstance(payload, dict)

    def parse(self, payload: Dict[str, Any]) -> CanonicalSensorReading:
        """
        Normalisiert generische JSON-Messwerte in ein CanonicalSensorReading.
        """
        container = payload.get("params") or payload.get("result") or payload.get("data") or payload
        if not isinstance(container, dict):
            container = {}

        raw_src = (
            payload.get("src")
            or payload.get("device_id")
            or payload.get("identifier")
            or payload.get("id")
            or "generic_sensor"
        )
        identifier = str(raw_src).strip()

        ts = timezone.now()
        raw_ts = container.get("ts") or payload.get("ts") or container.get("timestamp")
        if raw_ts and isinstance(raw_ts, (int, float)):
            try:
                ts = timezone.datetime.fromtimestamp(float(raw_ts), tz=timezone.utc)
            except Exception:
                ts = timezone.now()

        def _get_num(*keys) -> Optional[float]:
            for k in keys:
                if k in container and container[k] is not None:
                    try:
                        return float(container[k])
                    except (ValueError, TypeError):
                        pass
                if k in payload and payload[k] is not None:
                    try:
                        return float(payload[k])
                    except (ValueError, TypeError):
                        pass
            return None

        # 1. Leistung (W)
        power_w = _get_num("power", "power_w", "apower", "active_power", "p_total", "curr_power", "val_power")

        # 2. Energie (kWh)
        energy_kwh = _get_num("energy", "energy_kwh", "total_energy", "energy_import", "import_kwh", "val_energy")

        # 3. Spannung & Strom
        voltage = _get_num("voltage", "voltage_v", "u", "val_voltage")
        current = _get_num("current", "current_a", "i", "val_current")

        # 4. Frequenz & Temperatur & SoC
        freq = _get_num("frequency", "freq", "frequency_hz")
        temp = _get_num("temperature", "temp", "temperature_c")
        soc = _get_num("soc", "battery_soc", "charge_level")

        # 5. Explizite Einzelmetrik aus ioBroker/HomeAssistant (z.B. {"metric": "power", "val": 1500})
        explicit_metric = str(payload.get("metric") or container.get("metric") or "").strip().lower()
        explicit_val = None
        for vk in ("val", "value", "v", "state"):
            if vk in container and container[vk] is not None and not isinstance(container[vk], bool):
                try:
                    explicit_val = float(container[vk])
                    break
                except (ValueError, TypeError):
                    pass

        extra_metrics: Dict[str, float] = {}
        if explicit_metric and explicit_val is not None:
            if explicit_metric in ("power", "power_w", "leistung"):
                power_w = explicit_val
            elif explicit_metric in ("energy", "energy_kwh", "energie", "zaehlerstand"):
                energy_kwh = explicit_val
            elif explicit_metric in ("voltage", "spannung"):
                voltage = explicit_val
            elif explicit_metric in ("current", "strom"):
                current = explicit_val
            elif explicit_metric in ("soc", "battery_soc"):
                soc = explicit_val
            elif explicit_metric in ("temperature", "temp"):
                temp = explicit_val
            else:
                extra_metrics[explicit_metric] = explicit_val

        # 6. Relais Schaltzustand
        relay_state: Optional[bool] = None
        for rk in ("relay_state", "state", "output", "switch", "ison"):
            target = container.get(rk) if rk in container else payload.get(rk)
            if target is not None:
                if isinstance(target, bool):
                    relay_state = target
                    break
                elif str(target).lower() in ("true", "1", "on"):
                    relay_state = True
                    break
                elif str(target).lower() in ("false", "0", "off"):
                    relay_state = False
                    break

        reading = CanonicalSensorReading(
            device_identifier=identifier,
            power_w=power_w,
            energy_import_kwh=energy_kwh,
            voltage_l1_v=voltage,
            current_l1_a=current,
            frequency_hz=freq,
            temperature_c=temp,
            soc_percent=soc,
            relay_state=relay_state,
            timestamp=ts,
            extra_metrics=extra_metrics,
            raw_payload=payload,
        )
        return reading.validate()
