"""Sensor platform for Sharegy integration diagnostics & setpoints."""

from __future__ import annotations

from homeassistant.components.sensor import (
    SensorEntity,
    SensorDeviceClass,
    SensorStateClass,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import UnitOfTemperature, PERCENTAGE
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import DOMAIN


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up Sharegy status and control setpoint sensors."""
    bridge = hass.data[DOMAIN][entry.entry_id]["bridge"]

    sensors = [
        SharegyStatusSensor(entry, bridge),
        SharegyBufferCountSensor(entry, bridge),
        SharegyFlowTempSetpointSensor(entry, bridge),
        SharegyScreedSoCSensor(entry, bridge),
        SharegyOperatingModeSensor(entry, bridge),
        SharegySpotPriceSensor(entry, bridge),
    ]

    async_add_entities(sensors, True)


class SharegyStatusSensor(SensorEntity):
    """Representation of the Sharegy Cloud connection state."""

    _attr_icon = "mdi:cloud-sync"
    _attr_has_entity_name = True
    _attr_name = "Cloud Verbindung"

    def __init__(self, entry: ConfigEntry, bridge):
        self._entry = entry
        self._bridge = bridge
        self._attr_unique_id = f"{entry.entry_id}_status"

    @property
    def native_value(self) -> str:
        """Return state."""
        return "online" if self._bridge.is_connected else "offline"

    @property
    def extra_state_attributes(self) -> dict:
        return {
            "host": self._bridge.host,
            "protocol": self._bridge.protocol,
            "token_prefix": self._bridge.token[:8] if self._bridge.token else "-",
        }


class SharegyBufferCountSensor(SensorEntity):
    """Representation of local offline buffer size."""

    _attr_icon = "mdi:database-clock"
    _attr_has_entity_name = True
    _attr_name = "Offline Puffer (Warteschlange)"
    _attr_native_unit_of_measurement = "Einträge"

    def __init__(self, entry: ConfigEntry, bridge):
        self._entry = entry
        self._bridge = bridge
        self._attr_unique_id = f"{entry.entry_id}_buffer_count"

    @property
    def native_value(self) -> int:
        """Return number of pending queued records."""
        return self._bridge.buffer.count_pending()


class SharegyFlowTempSetpointSensor(SensorEntity):
    """Flow Temperature Setpoint calculated by Sharegy according to DIN EN 12831."""

    _attr_icon = "mdi:water-thermometer"
    _attr_device_class = SensorDeviceClass.TEMPERATURE
    _attr_state_class = SensorStateClass.MEASUREMENT
    _attr_native_unit_of_measurement = UnitOfTemperature.CELSIUS
    _attr_has_entity_name = True
    _attr_name = "FBH Vorlauf-Solltemperatur"

    def __init__(self, entry: ConfigEntry, bridge):
        self._entry = entry
        self._bridge = bridge
        self._attr_unique_id = f"{entry.entry_id}_flow_temp_setpoint"

    @property
    def native_value(self) -> float:
        return round(float(getattr(self._bridge, "flow_temp_setpoint_c", 30.0)), 1)


class SharegyScreedSoCSensor(SensorEntity):
    """Screed Thermal Battery State of Charge in %."""

    _attr_icon = "mdi:battery-arrow-up"
    _attr_state_class = SensorStateClass.MEASUREMENT
    _attr_native_unit_of_measurement = PERCENTAGE
    _attr_has_entity_name = True
    _attr_name = "FBH Estrich-Speicher Ladestand (SoC)"

    def __init__(self, entry: ConfigEntry, bridge):
        self._entry = entry
        self._bridge = bridge
        self._attr_unique_id = f"{entry.entry_id}_screed_soc"

    @property
    def native_value(self) -> float:
        return round(float(getattr(self._bridge, "screed_soc_pct", 50.0)), 1)


class SharegyOperatingModeSensor(SensorEntity):
    """Operating mode received from Sharegy Optimizer."""

    _attr_icon = "mdi:tune-vertical"
    _attr_has_entity_name = True
    _attr_name = "FBH Betriebsmodus"

    def __init__(self, entry: ConfigEntry, bridge):
        self._entry = entry
        self._bridge = bridge
        self._attr_unique_id = f"{entry.entry_id}_operating_mode"

    @property
    def native_value(self) -> str:
        mode = getattr(self._bridge, "operating_mode", "STANDBY")
        mode_labels = {
            "pv_boost": "PV-Überschuss Boost",
            "grid_arbitrage": "Netz-Arbitrage (Niedrigpreis)",
            "comfort": "Komfortbetrieb",
            "eco": "Eco-Absenkung",
            "standby": "Standby / Deaktiviert",
            "manual_boost": "Manueller Boost",
        }
        return mode_labels.get(str(mode).lower(), str(mode).upper())


class SharegySpotPriceSensor(SensorEntity):
    """Dynamic Electricity Spot Price in ct/kWh."""

    _attr_icon = "mdi:currency-eur"
    _attr_state_class = SensorStateClass.MEASUREMENT
    _attr_native_unit_of_measurement = "ct/kWh"
    _attr_has_entity_name = True
    _attr_name = "Börsenstrompreis"

    def __init__(self, entry: ConfigEntry, bridge):
        self._entry = entry
        self._bridge = bridge
        self._attr_unique_id = f"{entry.entry_id}_spot_price"

    @property
    def native_value(self) -> float:
        return round(float(getattr(self._bridge, "spot_price_ct", 15.0)), 2)
