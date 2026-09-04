"""
devices/adapters/

Modulare, entkoppelte Adapter-Engine für Photovoltaik- und Hybrid-Wechselrichter.
"""

from devices.adapters.contracts import CanonicalTelemetry, BaseInverterAdapter, AdapterTestResult
from devices.adapters.registry import get_adapter, list_adapters, register_adapter
from devices.adapters.ingest_core import process_canonical_telemetry

__all__ = [
    "CanonicalTelemetry",
    "BaseInverterAdapter",
    "AdapterTestResult",
    "get_adapter",
    "list_adapters",
    "register_adapter",
    "process_canonical_telemetry",
]
