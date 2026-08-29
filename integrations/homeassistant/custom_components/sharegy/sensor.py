"""Sensor platform for Sharegy integration diagnostics."""

from __future__ import annotations

from homeassistant.components.sensor import SensorEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import DOMAIN


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up Sharegy status sensors."""
    bridge = hass.data[DOMAIN][entry.entry_id]["bridge"]

    sensors = [
        SharegyStatusSensor(entry, bridge),
        SharegyBufferCountSensor(entry, bridge),
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
