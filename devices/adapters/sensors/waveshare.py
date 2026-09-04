"""
devices/adapters/sensors/waveshare.py

Isolierter Adapter für Waveshare Modbus/TCP & RS485-to-ETH/WSS Gateways sowie
direkt angebundene Modbus-Energiezähler (Eastron SDM630, CHINT DTSU666, Finder, etc.).
Unterstützt:
- Modbus Register-Payloads (z.B. reg_30001, reg_30012, registers, modbus_data)
- Normalisierte Modbus-JSON Formate (active_power, total_active_power, import_kwh, export_kwh)
- 3-Phasen Spannungen und Ströme (voltage_l1, voltage_l2, voltage_l3, current_l1, etc.)
"""

import logging
from typing import Dict, Any, Optional
from django.utils import timezone

from devices.adapters.sensors.contracts import BaseSensorAdapter, CanonicalSensorReading

logger = logging.getLogger(__name__)


class WaveshareModbusAdapter(BaseSensorAdapter):
    adapter_id = "waveshare_modbus"
    name = "Waveshare Modbus / RS485 Gateway"
    vendor = "Waveshare"
    protocol = "modbus_tcp_wss"

    def supports_auto_detect(self, payload: Dict[str, Any]) -> bool:
        """
        Prüft auf Modbus / Waveshare Signaturen im Payload.
        """
        if not isinstance(payload, dict):
            return False

        src = str(payload.get("src", "") or payload.get("device_id", "")).lower()
        if "waveshare" in src or "modbus" in src or "sdm630" in src or "dtsu666" in src:
            return True

        # Schlüsselwörter für Modbus-Register
        container = payload.get("params") or payload.get("data") or payload
        if isinstance(container, dict):
            modbus_keys = {
                "registers", "modbus_data", "holding_registers", "input_registers",
                "active_power_l1", "active_power_total", "total_active_power",
                "import_kwh", "export_kwh", "grid_import_kwh", "grid_export_kwh"
            }
            if any(k in container for k in modbus_keys):
                return True
            # Prüfe auf registerartige Keys (reg_30001, reg_30012, etc.)
            if any(k.startswith("reg_") or k.startswith("reg3") or k.startswith("reg4") for k in container.keys()):
                return True

        return False

    def parse(self, payload: Dict[str, Any]) -> CanonicalSensorReading:
        """
        Wandelt Modbus Register und Bezeichner in CanonicalSensorReading um.
        """
        container = payload.get("params") or payload.get("data") or payload
        if not isinstance(container, dict):
            container = {}

        raw_src = payload.get("src") or payload.get("device_id") or payload.get("id") or "waveshare_modbus"
        identifier = str(raw_src).strip()

        ts = timezone.now()
        raw_ts = container.get("ts") or payload.get("ts")
        if raw_ts:
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
                # Check within sub-dictionaries like "registers" or "data"
                for sub_key in ("registers", "modbus_data", "values"):
                    sub = container.get(sub_key)
                    if isinstance(sub, dict) and k in sub and sub[k] is not None:
                        try:
                            return float(sub[k])
                        except (ValueError, TypeError):
                            pass
            return None

        # 1. Leistung (W)
        power_w = _get_num(
            "power", "total_power", "total_active_power", "active_power_total",
            "active_power", "p_total", "power_w", "reg_30053", "reg_30013"
        )
        # Falls nur Phasenleistungen gemeldet werden (z.B. SDM630 / DTSU666)
        p_l1 = _get_num("active_power_l1", "power_l1", "p_l1", "reg_30013")
        p_l2 = _get_num("active_power_l2", "power_l2", "p_l2", "reg_30015")
        p_l3 = _get_num("active_power_l3", "power_l3", "p_l3", "reg_30017")
        if power_w is None and (p_l1 is not None or p_l2 is not None or p_l3 is not None):
            power_w = (p_l1 or 0.0) + (p_l2 or 0.0) + (p_l3 or 0.0)

        # 2. Energie (kWh)
        energy_import = _get_num(
            "energy_import_kwh", "import_kwh", "total_import_kwh", "grid_import_kwh",
            "total_active_energy", "energy_import", "reg_30343", "reg_30073"
        )
        energy_export = _get_num(
            "energy_export_kwh", "export_kwh", "total_export_kwh", "grid_export_kwh",
            "total_export_energy", "energy_export", "reg_30345", "reg_30075"
        )

        # 3. Spannungen (V)
        v_l1 = _get_num("voltage_l1", "v_l1", "voltage_a", "voltage", "reg_30001")
        v_l2 = _get_num("voltage_l2", "v_l2", "voltage_b", "reg_30003")
        v_l3 = _get_num("voltage_l3", "v_l3", "voltage_c", "reg_30005")

        # 4. Ströme (A)
        i_l1 = _get_num("current_l1", "i_l1", "current_a", "current", "reg_30007")
        i_l2 = _get_num("current_l2", "i_l2", "current_b", "reg_30009")
        i_l3 = _get_num("current_l3", "i_l3", "current_c", "reg_30011")

        # 5. Frequenz (Hz)
        freq = _get_num("frequency", "freq", "freq_hz", "reg_30071")

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
            frequency_hz=freq,
            timestamp=ts,
            raw_payload=payload,
        )
        return reading.validate()
