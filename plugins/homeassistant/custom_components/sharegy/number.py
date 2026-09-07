# pyright: reportMissingImports=false
"""Support for Sharegy HEMS number entities (setpoints & parameters)."""

from __future__ import annotations
import logging

from homeassistant.components.number import NumberEntity, NumberMode
from homeassistant.const import UnitOfTemperature
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity import DeviceInfo
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN
from .coordinator import SharegyDataUpdateCoordinator

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(hass: HomeAssistant, entry, async_add_entities) -> None:
    """Set up Sharegy number entities based on a config entry."""
    coordinator: SharegyDataUpdateCoordinator = hass.data[DOMAIN][entry.entry_id]

    numbers = [
        SharegyFloorHeatingTargetTempNumber(coordinator, entry),
        SharegyFloorHeatingOverheatToleranceNumber(coordinator, entry),
    ]

    async_add_entities(numbers)


class SharegyBaseNumber(CoordinatorEntity, NumberEntity):
    """Base class for Sharegy number entities."""

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


class SharegyFloorHeatingTargetTempNumber(SharegyBaseNumber):
    """Desired Comfort Room Temperature in °C."""

    _attr_mode = NumberMode.SLIDER
    _attr_native_min_value = 18.0
    _attr_native_max_value = 24.0
    _attr_native_step = 0.5
    _attr_native_unit_of_measurement = UnitOfTemperature.CELSIUS
    _attr_icon = "mdi:thermometer-auto"

    def __init__(self, coordinator, entry) -> None:
        super().__init__(coordinator, entry, "floor_heating_target_temp", "FBH Soll-Raumtemperatur")

    @property
    def native_value(self) -> float:
        fh = self.coordinator.data.get("floor_heating", {})
        cfg = fh.get("config", {})
        return float(cfg.get("target_temp_comfort", 21.0))

    async def async_set_native_value(self, value: float) -> None:
        if not getattr(self.coordinator, "bidirectional_enabled", True):
            _LOGGER.warning("Bidirektionale Steuerung ist pausiert.")
            return
        await self.coordinator.async_set_floor_heating_config({"target_temp_comfort": float(value)})


class SharegyFloorHeatingOverheatToleranceNumber(SharegyBaseNumber):
    """Max Screed Storage Overheating Delta in Kelvin."""

    _attr_mode = NumberMode.SLIDER
    _attr_native_min_value = 0.5
    _attr_native_max_value = 3.0
    _attr_native_step = 0.1
    _attr_native_unit_of_measurement = "K"
    _attr_icon = "mdi:thermometer-plus"

    def __init__(self, coordinator, entry) -> None:
        super().__init__(coordinator, entry, "floor_heating_overheat_delta", "FBH Estrich Überhitzungs-Toleranz")

    @property
    def native_value(self) -> float:
        fh = self.coordinator.data.get("floor_heating", {})
        cfg = fh.get("config", {})
        return float(cfg.get("max_overheat_delta_k", 1.5))

    async def async_set_native_value(self, value: float) -> None:
        if not getattr(self.coordinator, "bidirectional_enabled", True):
            _LOGGER.warning("Bidirektionale Steuerung ist pausiert.")
            return
        await self.coordinator.async_set_floor_heating_config({"max_overheat_delta_k": float(value)})
