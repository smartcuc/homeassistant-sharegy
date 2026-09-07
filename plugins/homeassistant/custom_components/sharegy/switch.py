# pyright: reportMissingImports=false
"""Support for Sharegy HEMS switches (bidirectional control)."""

from __future__ import annotations
import logging

from homeassistant.components.switch import SwitchEntity, SwitchDeviceClass
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity import DeviceInfo
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN
from .coordinator import SharegyDataUpdateCoordinator

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(hass: HomeAssistant, entry, async_add_entities) -> None:
    """Set up Sharegy switches based on a config entry."""
    coordinator: SharegyDataUpdateCoordinator = hass.data[DOMAIN][entry.entry_id]

    switches = [
        SharegyBidirectionalControlSwitch(coordinator, entry),
        SharegyFloorHeatingBoostSwitch(coordinator, entry),
        SharegyFloorHeatingEnableSwitch(coordinator, entry),
        SharegyBwwpBoostSwitch(coordinator, entry),
    ]

    async_add_entities(switches)


class SharegyBaseSwitch(CoordinatorEntity, SwitchEntity):
    """Base class for Sharegy switch entities."""

    def __init__(self, coordinator: SharegyDataUpdateCoordinator, entry, key: str, name: str) -> None:
        super().__init__(coordinator)
        self.entry = entry
        self._key = key
        self._attr_name = f"Sharegy {name}"
        self._attr_unique_id = f"{entry.entry_id}_{key}"

    @property
    def device_info(self) -> DeviceInfo:
        return DeviceInfo(
            identifiers={(DOMAIN, self.entry.entry_id)},
            name="Sharegy HEMS",
            manufacturer="Sharegy",
            model="Energy Management System",
            sw_version="2.1.0",
        )


class SharegyBidirectionalControlSwitch(SharegyBaseSwitch):
    """Global switch to enable/pause bidirectional dispatch & control."""

    _attr_icon = "mdi:sync"

    def __init__(self, coordinator, entry) -> None:
        super().__init__(coordinator, entry, "bidirectional_control_enabled", "Bidirektionale Steuerung")

    @property
    def is_on(self) -> bool:
        return getattr(self.coordinator, "bidirectional_enabled", True)

    async def async_turn_on(self, **kwargs) -> None:
        self.coordinator.bidirectional_enabled = True
        self.async_write_ha_state()

    async def async_turn_off(self, **kwargs) -> None:
        self.coordinator.bidirectional_enabled = False
        self.async_write_ha_state()


class SharegyFloorHeatingBoostSwitch(SharegyBaseSwitch):
    """Switch to activate screed preheating thermal boost."""

    _attr_icon = "mdi:radiator"

    def __init__(self, coordinator, entry) -> None:
        super().__init__(coordinator, entry, "floor_heating_boost", "Fußbodenheizung Boost")

    @property
    def is_on(self) -> bool:
        fh = self.coordinator.data.get("floor_heating", {})
        return bool(fh.get("is_active") and fh.get("mode") in ["pv_boost", "grid_arbitrage", "manual_boost"])

    async def async_turn_on(self, **kwargs) -> None:
        if not getattr(self.coordinator, "bidirectional_enabled", True):
            _LOGGER.warning("Bidirektionale Steuerung ist pausiert.")
            return
        await self.coordinator.async_set_floor_heating_boost(True)

    async def async_turn_off(self, **kwargs) -> None:
        await self.coordinator.async_set_floor_heating_boost(False)


class SharegyFloorHeatingEnableSwitch(SharegyBaseSwitch):
    """Switch to enable or disable the floor heating dispatch module."""

    _attr_icon = "mdi:heating-coil"

    def __init__(self, coordinator, entry) -> None:
        super().__init__(coordinator, entry, "floor_heating_enabled", "Fußbodenheizung Modul Aktiv")

    @property
    def is_on(self) -> bool:
        fh = self.coordinator.data.get("floor_heating", {})
        return bool(fh.get("is_active", True))

    async def async_turn_on(self, **kwargs) -> None:
        await self.coordinator.async_toggle_floor_heating(True)

    async def async_turn_off(self, **kwargs) -> None:
        await self.coordinator.async_toggle_floor_heating(False)


class SharegyBwwpBoostSwitch(SharegyBaseSwitch):
    """Switch for Brauchwasser-Wärmepumpe SG-Ready boost."""

    _attr_icon = "mdi:water-boiler"

    def __init__(self, coordinator, entry) -> None:
        super().__init__(coordinator, entry, "bwwp_boost", "Brauchwasser WP Boost")

    @property
    def is_on(self) -> bool:
        bwwp = self.coordinator.data.get("bwwp", {})
        return bool(bwwp.get("is_active") or bwwp.get("status") == "boost")

    async def async_turn_on(self, **kwargs) -> None:
        if not getattr(self.coordinator, "bidirectional_enabled", True):
            _LOGGER.warning("Bidirektionale Steuerung ist pausiert.")
            return
        await self.coordinator.async_set_bwwp_switch(True, reason="Home Assistant Switch ON")

    async def async_turn_off(self, **kwargs) -> None:
        await self.coordinator.async_set_bwwp_switch(False, reason="Home Assistant Switch OFF")
