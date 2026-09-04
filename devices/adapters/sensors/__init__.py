"""
devices/adapters/sensors/__init__.py

Modulare Sensor- und Smart-Meter-Adapter für Sharegy.
"""

from devices.adapters.sensors.contracts import BaseSensorAdapter, CanonicalSensorReading
from devices.adapters.sensors.shelly import ShellySensorAdapter
from devices.adapters.sensors.waveshare import WaveshareModbusAdapter
from devices.adapters.sensors.tasmota import TasmotaSmlAdapter
from devices.adapters.sensors.generic import GenericJsonSensorAdapter
from devices.adapters.sensors.registry import SensorAdapterRegistry
from devices.adapters.sensors.ingest_core import process_canonical_sensor_reading

__all__ = [
    "BaseSensorAdapter",
    "CanonicalSensorReading",
    "ShellySensorAdapter",
    "WaveshareModbusAdapter",
    "TasmotaSmlAdapter",
    "GenericJsonSensorAdapter",
    "SensorAdapterRegistry",
    "process_canonical_sensor_reading",
]
