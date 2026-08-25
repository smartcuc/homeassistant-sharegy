# pyright: reportMissingImports=false
"""Support for Sharegy HEMS sensors."""

from __future__ import annotations
import logging

from homeassistant.components.sensor import (
    SensorEntity,
    SensorDeviceClass,
    SensorStateClass,
)
from homeassistant.const import (
    UnitOfPower,
    UnitOfEnergy,
    PERCENTAGE,
)
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity import DeviceInfo
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN
from .coordinator import SharegyDataUpdateCoordinator

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(hass: HomeAssistant, entry, async_add_entities) -> None:
    """Set up Sharegy sensors based on a config entry."""
    coordinator: SharegyDataUpdateCoordinator = hass.data[DOMAIN][entry.entry_id]

    sensors = [
        SharegySolarPowerSensor(coordinator, entry),
        SharegyHouseholdLoadSensor(coordinator, entry),
        SharegyGridPowerSensor(coordinator, entry),
        SharegyBatteryPowerSensor(coordinator, entry),
        SharegyBatterySoCSensor(coordinator, entry),
        SharegyAutarkySensor(coordinator, entry),
        SharegySelfConsumptionSensor(coordinator, entry),
        SharegySpotPriceSensor(coordinator, entry),
        SharegyOptimizerWindowSensor(coordinator, entry),
    ]

    async_add_entities(sensors)


class SharegyBaseSensor(CoordinatorEntity, SensorEntity):
    """Base class for Sharegy sensors."""

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
            sw_version="2.0.0",
        )


class SharegySolarPowerSensor(SharegyBaseSensor):
    """Current Solar PV Production in Watts."""

    _attr_device_class = SensorDeviceClass.POWER
    _attr_state_class = SensorStateClass.MEASUREMENT
    _attr_native_unit_of_measurement = UnitOfPower.WATT
    _attr_icon = "mdi:solar-power"

    def __init__(self, coordinator, entry) -> None:
        super().__init__(coordinator, entry, "solar_power", "Solar-Erzeugung")

    @property
    def native_value(self) -> float:
        val = self.coordinator.data.get("dashboard", {}).get("pv_power_w")
        if val is None:
            val = self.coordinator.data.get("balance", {}).get("kpis", {}).get("pv_generation_kwh", 0) * 1000.0 / 24.0
        return round(float(val or 0.0), 1)


class SharegyHouseholdLoadSensor(SharegyBaseSensor):
    """Current Household Load in Watts."""

    _attr_device_class = SensorDeviceClass.POWER
    _attr_state_class = SensorStateClass.MEASUREMENT
    _attr_native_unit_of_measurement = UnitOfPower.WATT
    _attr_icon = "mdi:home-lightning-bolt"

    def __init__(self, coordinator, entry) -> None:
        super().__init__(coordinator, entry, "household_load", "Hausverbrauch")

    @property
    def native_value(self) -> float:
        val = self.coordinator.data.get("dashboard", {}).get("load_power_w")
        if val is None:
            val = self.coordinator.data.get("balance", {}).get("kpis", {}).get("house_consumption_kwh", 0) * 1000.0 / 24.0
        return round(float(val or 0.0), 1)


class SharegyGridPowerSensor(SharegyBaseSensor):
    """Current Grid Power in Watts (positive: import, negative: export)."""

    _attr_device_class = SensorDeviceClass.POWER
    _attr_state_class = SensorStateClass.MEASUREMENT
    _attr_native_unit_of_measurement = UnitOfPower.WATT
    _attr_icon = "mdi:transmission-tower"

    def __init__(self, coordinator, entry) -> None:
        super().__init__(coordinator, entry, "grid_power", "Netzleistung")

    @property
    def native_value(self) -> float:
        val = self.coordinator.data.get("dashboard", {}).get("grid_power_w", 0.0)
        return round(float(val or 0.0), 1)


class SharegyBatteryPowerSensor(SharegyBaseSensor):
    """Battery Power in Watts (positive: charge, negative: discharge)."""

    _attr_device_class = SensorDeviceClass.POWER
    _attr_state_class = SensorStateClass.MEASUREMENT
    _attr_native_unit_of_measurement = UnitOfPower.WATT
    _attr_icon = "mdi:battery-charging"

    def __init__(self, coordinator, entry) -> None:
        super().__init__(coordinator, entry, "battery_power", "Batterieleistung")

    @property
    def native_value(self) -> float:
        val = self.coordinator.data.get("dashboard", {}).get("battery_power_w", 0.0)
        return round(float(val or 0.0), 1)


class SharegyBatterySoCSensor(SharegyBaseSensor):
    """Battery State of Charge in Percentage."""

    _attr_device_class = SensorDeviceClass.BATTERY
    _attr_state_class = SensorStateClass.MEASUREMENT
    _attr_native_unit_of_measurement = PERCENTAGE
    _attr_icon = "mdi:battery-high"

    def __init__(self, coordinator, entry) -> None:
        super().__init__(coordinator, entry, "battery_soc", "Batterie-Ladestand (SoC)")

    @property
    def native_value(self) -> float:
        val = self.coordinator.data.get("dashboard", {}).get("battery_soc_pct")
        if val is None:
            val = self.coordinator.data.get("dashboard", {}).get("battery_soc", 65.0)
        return round(float(val or 0.0), 1)


class SharegyAutarkySensor(SharegyBaseSensor):
    """Today's Autarky Rate in Percentage."""

    _attr_state_class = SensorStateClass.MEASUREMENT
    _attr_native_unit_of_measurement = PERCENTAGE
    _attr_icon = "mdi:shield-sun"

    def __init__(self, coordinator, entry) -> None:
        super().__init__(coordinator, entry, "autarky_rate", "Autarkiegrad")

    @property
    def native_value(self) -> float:
        val = self.coordinator.data.get("balance", {}).get("kpis", {}).get("autarky_rate", 0.0)
        return round(float(val or 0.0), 1)


class SharegySelfConsumptionSensor(SharegyBaseSensor):
    """Today's Self-Consumption Rate in Percentage."""

    _attr_state_class = SensorStateClass.MEASUREMENT
    _attr_native_unit_of_measurement = PERCENTAGE
    _attr_icon = "mdi:recycle"

    def __init__(self, coordinator, entry) -> None:
        super().__init__(coordinator, entry, "self_consumption_rate", "Eigenverbrauchsquote")

    @property
    def native_value(self) -> float:
        val = self.coordinator.data.get("balance", {}).get("kpis", {}).get("self_consumption_rate", 0.0)
        return round(float(val or 0.0), 1)


class SharegySpotPriceSensor(SharegyBaseSensor):
    """Current Dynamic Spot Electricity Price in ct/kWh."""

    _attr_state_class = SensorStateClass.MEASUREMENT
    _attr_native_unit_of_measurement = "ct/kWh"
    _attr_icon = "mdi:currency-eur"

    def __init__(self, coordinator, entry) -> None:
        super().__init__(coordinator, entry, "spot_price", "Börsenstrompreis")

    @property
    def native_value(self) -> float:
        val = self.coordinator.data.get("dashboard", {}).get("spot_price_eur_per_kwh")
        if val is not None:
            return round(float(val) * 100.0, 2)
        return 12.50


class SharegyOptimizerWindowSensor(SharegyBaseSensor):
    """Best Cost-Saving Charging Window for Automations."""

    _attr_icon = "mdi:clock-fast"

    def __init__(self, coordinator, entry) -> None:
        super().__init__(coordinator, entry, "optimizer_window", "Optimizer Best-Zeitfenster")

    @property
    def native_value(self) -> str:
        opt = self.coordinator.data.get("optimizer", {})
        recs = opt.get("recommendations", [])
        if recs and isinstance(recs, list) and len(recs) > 0:
            best_2h = next((r for r in recs if r.get("duration_hours") == 2), recs[0])
            return f"{best_2h.get('start_time', '13:00')} - {best_2h.get('end_time', '15:00')}"
        return "13:00 - 15:00"

    @property
    def extra_state_attributes(self) -> dict:
        opt = self.coordinator.data.get("optimizer", {})
        return {
            "summary": opt.get("summary", ""),
            "recommendations": opt.get("recommendations", []),
        }

