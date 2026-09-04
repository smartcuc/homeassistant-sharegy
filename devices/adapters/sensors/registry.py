"""
devices/adapters/sensors/registry.py

Zentrale Registrierung und automatischer Router für Sensor- und SmartMeter-Adapter.
Erkennt eingehende Frames (Shelly RPC, Waveshare Modbus, Tasmota SML, Generic JSON)
vollautomatisch und delegiert an den zuständigen Adapter.
"""

import logging
from typing import Dict, Any, List, Optional

from devices.adapters.sensors.contracts import BaseSensorAdapter, CanonicalSensorReading
from devices.adapters.sensors.shelly import ShellySensorAdapter
from devices.adapters.sensors.waveshare import WaveshareModbusAdapter
from devices.adapters.sensors.tasmota import TasmotaSmlAdapter
from devices.adapters.sensors.generic import GenericJsonSensorAdapter

logger = logging.getLogger(__name__)


class SensorAdapterRegistry:
    _adapters: Dict[str, BaseSensorAdapter] = {}
    _ordered_adapters: List[BaseSensorAdapter] = []

    @classmethod
    def register(cls, adapter_cls):
        """
        Registriert eine neue Sensor-Adapterklasse.
        """
        adapter_instance = adapter_cls()
        cls._adapters[adapter_instance.adapter_id] = adapter_instance
        # Spezifische Adapter vor dem Generic Fallback einreihen
        if adapter_instance.adapter_id == "generic_json":
            cls._ordered_adapters.append(adapter_instance)
        else:
            cls._ordered_adapters.insert(0, adapter_instance)
        logger.info("Registered Sensor Adapter: %s (%s)", adapter_instance.adapter_id, adapter_instance.name)
        return adapter_cls

    @classmethod
    def get_adapter(cls, adapter_id: str) -> Optional[BaseSensorAdapter]:
        """
        Liefert den Sensor-Adapter anhand seiner ID zurück.
        """
        return cls._adapters.get(adapter_id)

    @classmethod
    def list_adapters(cls) -> List[Dict[str, Any]]:
        """
        Liefert Metadaten aller registrierten Sensor-Adapter.
        """
        return [
            {
                "adapter_id": a.adapter_id,
                "name": a.name,
                "vendor": a.vendor,
                "protocol": a.protocol,
            }
            for a in cls._ordered_adapters
        ]

    @classmethod
    def detect_and_parse(cls, payload: Dict[str, Any], preferred_adapter_id: Optional[str] = None) -> CanonicalSensorReading:
        """
        Erkennt den zuständigen Adapter automatisch und parst das Payload-Objekt
        in ein standardisiertes CanonicalSensorReading.
        """
        if preferred_adapter_id and preferred_adapter_id in cls._adapters:
            return cls._adapters[preferred_adapter_id].parse(payload)

        # Automatische Erkennung nach Priorität
        for adapter in cls._ordered_adapters:
            if adapter.supports_auto_detect(payload):
                try:
                    reading = adapter.parse(payload)
                    return reading
                except Exception as e:
                    logger.warning("Adapter %s failed to parse sensor frame: %s. Trying next.", adapter.adapter_id, e)

        # Universeller Fallback
        generic = cls._adapters.get("generic_json") or GenericJsonSensorAdapter()
        return generic.parse(payload)


# Automatische Registrierung der Standard-Adapter
SensorAdapterRegistry.register(GenericJsonSensorAdapter)
SensorAdapterRegistry.register(TasmotaSmlAdapter)
SensorAdapterRegistry.register(WaveshareModbusAdapter)
SensorAdapterRegistry.register(ShellySensorAdapter)
