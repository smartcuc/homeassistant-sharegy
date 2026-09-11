"""
devices/adapters/contracts.py

Standardisierter, typisierter Vertrag (Contract) für alle Wechselrichter- und Speicher-Metriken.
Jeder Hersteller-Adapter (Sungrow, Growatt, SolarEdge, Fronius etc.) normalisiert seine Daten
ausschließlich in dieses Canonical-Schema.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field, asdict
from typing import Optional, Dict, Any
from django.utils import timezone


@dataclass
class CanonicalTelemetry:
    """
    Standardisiertes Datenmodell für Wechselrichter- und Batteriespeicher-Messwerte.
    Alle Werte sind garantiert in SI-Basiseinheiten (Watt [W], Kilowattstunden [kWh], Prozent [%]).
    """
    pv_power_w: Optional[float] = None           # Aktuelle PV-Erzeugungsleistung in Watt (>= 0.0)
    grid_power_w: Optional[float] = None         # Netzleistung in Watt (+ = Netzbezug, - = Netzeinspeisung)
    load_power_w: Optional[float] = None         # Hausverbrauch / Last in Watt (>= 0.0)
    battery_power_w: Optional[float] = None      # Batterieleistung in Watt (+ = Entladung, - = Ladung)
    battery_soc: Optional[float] = None          # Ladezustand der Batterie in % (0.0 bis 100.0)
    daily_yield_kwh: Optional[float] = None      # Tagesertrag der PV-Anlage in kWh (>= 0.0)
    total_yield_kwh: Optional[float] = None      # Gesamtertrag der PV-Anlage in kWh (>= 0.0)
    
    timestamp: Any = field(default_factory=timezone.now)
    raw_payload: Optional[Dict[str, Any]] = None # Original-Rohdaten für Debugging/Audit
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_metrics_dict(self) -> Dict[str, Optional[float]]:
        """
        Gibt ein Dictionary der Standard-Metriken zurück (kompatibel mit UI und EMS).
        """
        res = {
            "pv_power_w": self.pv_power_w,
            "power_w": self.pv_power_w,
            "pv_power": self.pv_power_w,
            "power": self.pv_power_w,
            "grid_power_w": self.grid_power_w,
            "grid_power": self.grid_power_w,
            "load_power_w": self.load_power_w,
            "load_power": self.load_power_w,
            "battery_power_w": self.battery_power_w,
            "battery_power": self.battery_power_w,
            "battery_soc": self.battery_soc,
            "soc": self.battery_soc,
            "daily_generation_kwh": self.daily_yield_kwh,
            "daily_yield_kwh": self.daily_yield_kwh,
            "daily_yield": self.daily_yield_kwh,
        }
        return res

    def validate(self) -> "CanonicalTelemetry":
        """
        Plausibilisiert und bereinigt Ausreißer oder Rundungsungenauigkeiten.
        """
        # 1. PV Power >= 0
        if self.pv_power_w is not None:
            self.pv_power_w = round(max(0.0, float(self.pv_power_w)), 2)

        # 2. Load Power >= 0
        if self.load_power_w is not None:
            self.load_power_w = round(max(0.0, float(self.load_power_w)), 2)

        # 3. Grid Power
        if self.grid_power_w is not None:
            self.grid_power_w = round(float(self.grid_power_w), 2)

        # 4. Battery Power
        if self.battery_power_w is not None:
            self.battery_power_w = round(float(self.battery_power_w), 2)

        # 5. Battery SoC (0.0 - 100.0%)
        if self.battery_soc is not None:
            soc = float(self.battery_soc)
            if 0.0 <= soc <= 1.0:
                soc = soc * 100.0
            self.battery_soc = round(max(0.0, min(100.0, soc)), 1)

        # 6. Tagesertrag >= 0
        if self.daily_yield_kwh is not None:
            self.daily_yield_kwh = round(max(0.0, float(self.daily_yield_kwh)), 2)

        return self


@dataclass
class AdapterTestResult:
    """
    Ergebnis eines Verbindungstests oder Handshakes mit der Hersteller-Cloud.
    """
    status: str                         # 'success' oder 'error'
    message: str
    live_metrics: Dict[str, Any]
    raw_sample: Dict[str, Any] = field(default_factory=dict)
    simulated: bool = False
    error: Optional[str] = None


class BaseInverterAdapter(ABC):
    """
    Abstrakte Basisklasse für alle Wechselrichter- und Cloud-Adapter.
    """
    profile_id: str = ""
    name: str = ""
    vendor: str = ""
    protocol: str = "http_cloud"
    category: str = "inverter_hybrid"

    @abstractmethod
    def test_connection(self, credentials: Dict[str, Any]) -> AdapterTestResult:
        """
        Führt einen Verbindungstest durch und liefert ein standardisiertes AdapterTestResult.
        """
        pass

    @abstractmethod
    def fetch_telemetry(self, credentials: Dict[str, Any]) -> CanonicalTelemetry:
        """
        Fragt die Live-Telemetrie vom Wechselrichter ab und konvertiert sie in CanonicalTelemetry.
        """
        pass

    @abstractmethod
    def parse_payload(self, raw_data: Dict[str, Any]) -> CanonicalTelemetry:
        """
        Überführt ein herstellerspezifisches Rohdaten-Dictionary in CanonicalTelemetry.
        """
        pass
