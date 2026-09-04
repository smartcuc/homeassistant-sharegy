"""
devices/adapters/sensors/shelly.py

Isolierter Adapter für Shelly Gen2/Gen3/Pro Geräte über WebSocket RPC (NotifyStatus, Shelly.GetStatus).
Unterstützt:
- Shelly Pro 3EM / Shelly 3EM (3-Phasen Messung: em:0, emdata:0, a_act_power, total_act_power)
- Shelly Plus 1PM / Pro 1PM / 1PM Gen3 / PlugS (pm1:0, switch:0, apower, aenergy)
- Relais-Zustände (switch:0.output, state, ison)
- Automatische Erkennung anhand von RPC-Signaturen und Channel-Strukturen
"""

import logging
from typing import Dict, Any, Optional
from django.utils import timezone

from devices.adapters.sensors.contracts import BaseSensorAdapter, CanonicalSensorReading

logger = logging.getLogger(__name__)


class ShellySensorAdapter(BaseSensorAdapter):
    adapter_id = "shelly_rpc"
    name = "Shelly RPC (Gen2/Gen3/Pro)"
    vendor = "Shelly"
    protocol = "websocket_rpc"

    def supports_auto_detect(self, payload: Dict[str, Any]) -> bool:
        """
        Prüft auf typische Shelly RPC Signaturen.
        """
        if not isinstance(payload, dict):
            return False

        src = str(payload.get("src", "")).lower()
        method = str(payload.get("method", "")).lower()

        if "shelly" in src:
            return True
        if method in ("notifystatus", "shelly.getstatus", "shelly.getconfig"):
            return True

        container = payload.get("params") or payload.get("result") or payload
        if isinstance(container, dict):
            # Prüfen auf Shelly-spezifische Keys
            shelly_keys = {"em:0", "em:1", "emdata:0", "emdata:1", "pm1:0", "pm1:1", "switch:0", "switch:1", "cover:0", "sys"}
            if any(k in container for k in shelly_keys):
                return True
            if "a_act_power" in container or "total_act_power" in container:
                return True

        return False

    def parse(self, payload: Dict[str, Any]) -> CanonicalSensorReading:
        """
        Extrahiert Leistung, Energie, Spannung, Strom und Schaltzustand aus Shelly RPC Frames.
        """
        container = payload.get("params") or payload.get("result") or payload
        if not isinstance(container, dict):
            container = {}

        raw_src = payload.get("src") or payload.get("device_id") or payload.get("id") or "shelly_device"
        identifier = str(raw_src).strip()

        # Zeitstempel ermitteln
        ts = timezone.now()
        raw_ts = container.get("ts") or payload.get("ts")
        if raw_ts:
            try:
                ts = timezone.datetime.fromtimestamp(float(raw_ts), tz=timezone.utc)
            except Exception:
                ts = timezone.now()

        total_power: Optional[float] = None
        energy_import_kwh: Optional[float] = None
        voltage_l1: Optional[float] = None
        voltage_l2: Optional[float] = None
        voltage_l3: Optional[float] = None
        current_l1: Optional[float] = None
        current_l2: Optional[float] = None
        current_l3: Optional[float] = None
        frequency: Optional[float] = None
        temperature: Optional[float] = None
        relay_state: Optional[bool] = None

        accumulated_power = 0.0
        has_power_components = False

        accumulated_energy = 0.0
        has_energy_components = False

        for key, val in container.items():
            if isinstance(val, dict):
                # 1. 3-Phasen Energiemessung (Pro 3EM, 3EM)
                if "total_act_power" in val and val["total_act_power"] is not None:
                    accumulated_power += float(val["total_act_power"])
                    has_power_components = True
                elif "a_act_power" in val:
                    pa = float(val.get("a_act_power") or 0.0)
                    pb = float(val.get("b_act_power") or 0.0)
                    pc = float(val.get("c_act_power") or 0.0)
                    accumulated_power += (pa + pb + pc)
                    has_power_components = True

                # 2. Einphasige Messung (Plus 1PM, 1PM Gen3, PlugS)
                if "apower" in val and val["apower"] is not None:
                    accumulated_power += float(val["apower"])
                    has_power_components = True
                elif "power" in val and val["power"] is not None:
                    accumulated_power += float(val["power"])
                    has_power_components = True

                # Phasen-Spannungen
                if "a_voltage" in val and val["a_voltage"] is not None:
                    voltage_l1 = float(val["a_voltage"])
                elif "voltage" in val and val["voltage"] is not None and voltage_l1 is None:
                    voltage_l1 = float(val["voltage"])

                if "b_voltage" in val and val["b_voltage"] is not None:
                    voltage_l2 = float(val["b_voltage"])
                if "c_voltage" in val and val["c_voltage"] is not None:
                    voltage_l3 = float(val["c_voltage"])

                # Phasen-Ströme
                if "a_current" in val and val["a_current"] is not None:
                    current_l1 = float(val["a_current"])
                elif "current" in val and val["current"] is not None and current_l1 is None:
                    current_l1 = float(val["current"])

                if "b_current" in val and val["b_current"] is not None:
                    current_l2 = float(val["b_current"])
                if "c_current" in val and val["c_current"] is not None:
                    current_l3 = float(val["c_current"])

                # Frequenz & Temperatur
                if "freq" in val and val["freq"] is not None:
                    frequency = float(val["freq"])
                if "temperature" in val and isinstance(val["temperature"], dict) and "tC" in val["temperature"]:
                    temperature = float(val["temperature"]["tC"])
                elif "temperature" in val and isinstance(val["temperature"], (int, float)):
                    temperature = float(val["temperature"])

                # Energiezähler
                if "total_act_energy" in val and val["total_act_energy"] is not None:
                    # Shelly liefert emdata Wh -> in kWh umrechnen
                    accumulated_energy += float(val["total_act_energy"]) / 1000.0
                    has_energy_components = True
                elif "total_act" in val and val["total_act"] is not None:
                    accumulated_energy += float(val["total_act"]) / 1000.0
                    has_energy_components = True
                elif "aenergy" in val and isinstance(val["aenergy"], dict):
                    if "total" in val["aenergy"] and val["aenergy"]["total"] is not None:
                        accumulated_energy += float(val["aenergy"]["total"]) / 1000.0
                        has_energy_components = True

                # Relais-Schaltzustand (switch:0 -> output / state / ison)
                if "output" in val and val["output"] is not None:
                    relay_state = bool(val["output"])
                elif "state" in val and isinstance(val["state"], bool):
                    relay_state = val["state"]
                elif "ison" in val and val["ison"] is not None:
                    relay_state = bool(val["ison"])

            elif isinstance(val, (int, float)):
                if key in ("power", "apower", "total_act_power"):
                    accumulated_power += float(val)
                    has_power_components = True
                elif key in ("energy", "total_act_energy"):
                    accumulated_energy += float(val) / 1000.0 if float(val) > 5000.0 else float(val)
                    has_energy_components = True
                elif key == "voltage" and voltage_l1 is None:
                    voltage_l1 = float(val)
                elif key == "current" and current_l1 is None:
                    current_l1 = float(val)
                elif key in ("temp", "temperature") and temperature is None:
                    temperature = float(val)
                elif key in ("freq", "frequency") and frequency is None:
                    frequency = float(val)

        # Flache Relais-Eigenschaften prüfen
        if relay_state is None:
            if "relay_state" in container and container["relay_state"] is not None:
                relay_state = bool(container["relay_state"])
            elif "state" in container and isinstance(container["state"], bool):
                relay_state = container["state"]

        if has_power_components:
            total_power = round(accumulated_power, 2)
        if has_energy_components:
            energy_import_kwh = round(accumulated_energy, 4)

        reading = CanonicalSensorReading(
            device_identifier=identifier,
            power_w=total_power,
            energy_import_kwh=energy_import_kwh,
            voltage_l1_v=voltage_l1,
            voltage_l2_v=voltage_l2,
            voltage_l3_v=voltage_l3,
            current_l1_a=current_l1,
            current_l2_a=current_l2,
            current_l3_a=current_l3,
            frequency_hz=frequency,
            temperature_c=temperature,
            relay_state=relay_state,
            timestamp=ts,
            raw_payload=payload,
        )
        return reading.validate()
