"""
devices/adapters/sensors/tasmota.py

Isolierter Adapter für Tasmota SML (Smart Message Language) und IR-Leseköpfe (z.B. Hichi IR).
Unterstützt:
- OBIS Kennzahlen:
  - 16.7.0 (Momentanleistung in W / Wirkleistung)
  - 1.8.0 (Gesamter Wirkenergie-Bezug in kWh)
  - 2.8.0 (Gesamte Wirkenergie-Lieferung / Einspeisung in kWh)
  - 36.7.0 / 56.7.0 / 76.7.0 (Phasenleistungen L1, L2, L3)
- Tasmota SENSOR.SML Payload-Strukturen (Power_curr, Total_in, Total_out, MT175, LK13BE, eBZ DD3)
"""

import logging
from typing import Dict, Any, Optional
from django.utils import timezone

from devices.adapters.sensors.contracts import BaseSensorAdapter, CanonicalSensorReading

logger = logging.getLogger(__name__)


class TasmotaSmlAdapter(BaseSensorAdapter):
    adapter_id = "tasmota_sml"
    name = "Tasmota SML / IR-Lesekopf"
    vendor = "Tasmota"
    protocol = "mqtt_wss"

    def supports_auto_detect(self, payload: Dict[str, Any]) -> bool:
        """
        Prüft auf Tasmota SML und OBIS Kennzahlen.
        """
        if not isinstance(payload, dict):
            return False

        src = str(payload.get("src", "") or payload.get("device_id", "") or payload.get("Topic", "")).lower()
        if "tasmota" in src or "sml" in src or "hichi" in src:
            return True

        # Schlüsselwörter für OBIS Codes oder SML Strukturen
        container = payload.get("StatusSNS") or payload.get("SENSOR") or payload.get("params") or payload
        if isinstance(container, dict):
            # Prüfe auf OBIS Codes (16_7_0, 1_8_0, 2_8_0, 16.7.0, 1.8.0)
            obis_signatures = {
                "16_7_0", "1_8_0", "2_8_0", "16.7.0", "1.8.0", "2.8.0",
                "Power_curr", "Total_in", "Total_out", "SML", "OBIS"
            }
            if any(k in container for k in obis_signatures):
                return True
            for v in container.values():
                if isinstance(v, dict) and any(k in v for k in obis_signatures):
                    return True

        return False

    def parse(self, payload: Dict[str, Any]) -> CanonicalSensorReading:
        """
        Wandelt Tasmota SML / OBIS Daten in CanonicalSensorReading um.
        """
        container = payload.get("StatusSNS") or payload.get("SENSOR") or payload.get("params") or payload
        if not isinstance(container, dict):
            container = {}

        raw_src = (
            payload.get("src")
            or payload.get("device_id")
            or payload.get("Topic")
            or payload.get("id")
            or "tasmota_sml"
        )
        identifier = str(raw_src).strip()

        ts = timezone.now()
        raw_ts = container.get("Time") or payload.get("Time") or container.get("ts")
        if raw_ts and isinstance(raw_ts, (int, float)):
            try:
                ts = timezone.datetime.fromtimestamp(float(raw_ts), tz=timezone.utc)
            except Exception:
                ts = timezone.now()

        # Flaches Suchwörterbuch aufbauen (durchsucht alle verschachtelten Zähler-Objekte wie SML, MT175, LK13BE etc.)
        flat_map: Dict[str, Any] = {}
        for k, v in container.items():
            if isinstance(v, dict):
                for sub_k, sub_v in v.items():
                    norm_k = sub_k.replace(".", "_").lower()
                    flat_map[norm_k] = sub_v
                    flat_map[sub_k] = sub_v
            else:
                norm_k = k.replace(".", "_").lower()
                flat_map[norm_k] = v
                flat_map[k] = v

        def _get_num(*keys) -> Optional[float]:
            for k in keys:
                norm = k.replace(".", "_").lower()
                if norm in flat_map and flat_map[norm] is not None:
                    try:
                        return float(flat_map[norm])
                    except (ValueError, TypeError):
                        pass
                if k in flat_map and flat_map[k] is not None:
                    try:
                        return float(flat_map[k])
                    except (ValueError, TypeError):
                        pass
            return None

        # 1. Leistung (W) - OBIS 16.7.0 / Power_curr / curr_w / active_power
        power_w = _get_num(
            "16_7_0", "16.7.0", "power_curr", "power", "curr_w", "wirkleistung",
            "p", "active_power", "sm_power", "leistung"
        )
        # Fallback falls Summenleistung aus L1/L2/L3 (OBIS 36.7.0, 56.7.0, 76.7.0)
        p_l1 = _get_num("36_7_0", "36.7.0", "power_l1")
        p_l2 = _get_num("56_7_0", "56.7.0", "power_l2")
        p_l3 = _get_num("76_7_0", "76.7.0", "power_l3")
        if power_w is None and (p_l1 is not None or p_l2 is not None or p_l3 is not None):
            power_w = (p_l1 or 0.0) + (p_l2 or 0.0) + (p_l3 or 0.0)

        # 2. Netzbezug Energie (kWh) - OBIS 1.8.0 / Total_in / energy_in
        energy_import = _get_num(
            "1_8_0", "1.8.0", "total_in", "energy_in", "total_kwh", "zaehlerstand_bezug",
            "grid_import_kwh", "energy"
        )

        # 3. Netzeinspeisung Energie (kWh) - OBIS 2.8.0 / Total_out / energy_out
        energy_export = _get_num(
            "2_8_0", "2.8.0", "total_out", "energy_out", "zaehlerstand_einspeisung",
            "grid_export_kwh"
        )

        # 4. Spannungen & Ströme falls vorhanden (OBIS 32.7.0, 52.7.0, 72.7.0 für Volt; 31.7.0, 51.7.0, 71.7.0 für Ampere)
        v_l1 = _get_num("32_7_0", "32.7.0", "voltage_l1", "voltage")
        v_l2 = _get_num("52_7_0", "52.7.0", "voltage_l2")
        v_l3 = _get_num("72_7_0", "72.7.0", "voltage_l3")

        i_l1 = _get_num("31_7_0", "31.7.0", "current_l1", "current")
        i_l2 = _get_num("51_7_0", "51.7.0", "current_l2")
        i_l3 = _get_num("71_7_0", "71.7.0", "current_l3")

        reading = CanonicalSensorReading(
            device_identifier=identifier,
            power_w=power_w,
            energy_import_kwh=energy_import,
            energy_export_kwh=energy_export,
            voltage_l1_v=v_l1,
            voltage_l2_v=v_l2,
            voltage_l3_v=v_l3,
            current_l1_a=i_l1,
            current_l2_a=i_l2,
            current_l3_a=i_l3,
            timestamp=ts,
            raw_payload=payload,
        )
        return reading.validate()
