"""
vpp/dto.py

Strukturierte Datentransferobjekte (DTOs) für das Virtuelle Kraftwerk (VPP),
Flottenaggregation, Regelleistung und Dispatching.
"""

from dataclasses import dataclass, field, asdict
from decimal import Decimal
from typing import Dict, Any, List, Optional


@dataclass(slots=True)
class BatteryFleetSummary:
    count: int
    total_capacity_kwh: float
    total_stored_kwh: float
    avg_soc_percent: float
    available_pos_power_kw: float
    available_neg_power_kw: float


@dataclass(slots=True)
class ControllableLoadsSummary:
    count: int
    curtailable_power_kw: float


@dataclass(slots=True)
class PVFleetSummary:
    count: int
    curtailable_power_kw: float


@dataclass(slots=True)
class FleetFlexibilityResult:
    timestamp: str
    filters: Dict[str, Any]
    total_devices: int
    positive_flex_kw: float
    negative_flex_kw: float
    battery_fleet: BatteryFleetSummary
    controllable_loads: ControllableLoadsSummary
    pv_fleet: PVFleetSummary

    def to_dict(self) -> Dict[str, Any]:
        """Konvertiert das DTO in ein JSON-serialisierbares Dictionary."""
        return asdict(self)


@dataclass(slots=True)
class DispatchDeviceTarget:
    device_id: str
    device_name: str
    device_role: str
    target_power_kw: float
    command: str


@dataclass(slots=True)
class DispatchExecutionResult:
    order_id: str
    status: str
    target_power_kw: float
    executed_devices_count: int
    targets: List[DispatchDeviceTarget]
    timestamp: str

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)
