"""
devices/adapters/sensors/contracts.py

Typisierte Datenstrukturen und Basis-Verträge für Sensor- und SmartMeter-Adapter.
Garantiert herstellerunabhängige Normalisierung heterogener Sensor-Frames
(Shelly Gen2/Gen3 RPC, Waveshare Modbus/TCP, Tasmota SML OBIS, Generic JSON).
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Dict, Any, Optional, List
from django.utils import timezone


@dataclass
class CanonicalSensorReading:
    """
    Standardisiertes Messwert-Objekt für einen Sensor/Smart-Meter.
    Alle Leistungswerte werden in W (Watt) und Energiewerte in kWh angegeben.
    """
    device_identifier: Optional[str] = None
    power_w: Optional[float] = None
    energy_import_kwh: Optional[float] = None
    energy_export_kwh: Optional[float] = None
    voltage_l1_v: Optional[float] = None
    voltage_l2_v: Optional[float] = None
    voltage_l3_v: Optional[float] = None
    current_l1_a: Optional[float] = None
    current_l2_a: Optional[float] = None
    current_l3_a: Optional[float] = None
    frequency_hz: Optional[float] = None
    temperature_c: Optional[float] = None
    soc_percent: Optional[float] = None
    relay_state: Optional[bool] = None
    timestamp: Any = field(default_factory=timezone.now)
    extra_metrics: Dict[str, float] = field(default_factory=dict)
    raw_payload: Optional[Dict[str, Any]] = None

    def validate(self) -> "CanonicalSensorReading":
        """
        Plausibilisiert die Sensor-Messwerte.
        """
        if self.power_w is not None:
            self.power_w = round(float(self.power_w), 2)
        if self.energy_import_kwh is not None:
            self.energy_import_kwh = round(max(0.0, float(self.energy_import_kwh)), 4)
        if self.energy_export_kwh is not None:
            self.energy_export_kwh = round(max(0.0, float(self.energy_export_kwh)), 4)
        if self.voltage_l1_v is not None:
            self.voltage_l1_v = round(float(self.voltage_l1_v), 2)
        if self.voltage_l2_v is not None:
            self.voltage_l2_v = round(float(self.voltage_l2_v), 2)
        if self.voltage_l3_v is not None:
            self.voltage_l3_v = round(float(self.voltage_l3_v), 2)
        if self.current_l1_a is not None:
            self.current_l1_a = round(float(self.current_l1_a), 3)
        if self.current_l2_a is not None:
            self.current_l2_a = round(float(self.current_l2_a), 3)
        if self.current_l3_a is not None:
            self.current_l3_a = round(float(self.current_l3_a), 3)
        if self.soc_percent is not None:
            self.soc_percent = round(max(0.0, min(100.0, float(self.soc_percent))), 1)
        if self.temperature_c is not None:
            self.temperature_c = round(float(self.temperature_c), 2)
        if self.frequency_hz is not None:
            self.frequency_hz = round(float(self.frequency_hz), 2)
        return self

    def to_metrics_dict(self) -> Dict[str, float]:
        """
        Wandelt das standardisierte Objekt in ein flaches Metrik-Dictionary
        für DB- und Redis-Persistierung um.
        """
        metrics = {}
        if self.power_w is not None:
            metrics["power"] = self.power_w
        if self.energy_import_kwh is not None:
            metrics["energy"] = self.energy_import_kwh
            metrics["energy_import"] = self.energy_import_kwh
        if self.energy_export_kwh is not None:
            metrics["energy_export"] = self.energy_export_kwh
        if self.voltage_l1_v is not None:
            metrics["voltage"] = self.voltage_l1_v
            metrics["voltage_l1"] = self.voltage_l1_v
        if self.voltage_l2_v is not None:
            metrics["voltage_l2"] = self.voltage_l2_v
        if self.voltage_l3_v is not None:
            metrics["voltage_l3"] = self.voltage_l3_v
        if self.current_l1_a is not None:
            # Wenn L2/L3 vorliegen, Summenstrom oder L1
            total_curr = (self.current_l1_a or 0.0) + (self.current_l2_a or 0.0) + (self.current_l3_a or 0.0)
            metrics["current"] = round(total_curr, 3)
            metrics["current_l1"] = self.current_l1_a
        if self.current_l2_a is not None:
            metrics["current_l2"] = self.current_l2_a
        if self.current_l3_a is not None:
            metrics["current_l3"] = self.current_l3_a
        if self.frequency_hz is not None:
            metrics["frequency"] = self.frequency_hz
        if self.temperature_c is not None:
            metrics["temperature"] = self.temperature_c
        if self.soc_percent is not None:
            metrics["battery_soc"] = self.soc_percent
            metrics["soc"] = self.soc_percent

        # Zusätzliche Metriken integrieren
        for k, v in self.extra_metrics.items():
            if k not in metrics:
                metrics[k] = v

        return metrics


class BaseSensorAdapter(ABC):
    """
    Abstrakte Basisklasse für alle Sensor- und Smart-Meter-Adapter.
    """
    adapter_id: str = "base"
    name: str = "Base Sensor Adapter"
    vendor: str = "Generic"
    protocol: str = "websocket"

    @abstractmethod
    def supports_auto_detect(self, payload: Dict[str, Any]) -> bool:
        """
        Ermittelt anhand von Signaturen / Keys im Payload, ob dieser Adapter
        zuständig ist.
        """
        pass

    @abstractmethod
    def parse(self, payload: Dict[str, Any]) -> CanonicalSensorReading:
        """
        Normalisiert den herstellerspezifischen Payload in ein CanonicalSensorReading.
        """
        pass
