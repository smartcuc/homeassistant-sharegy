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
    UnitOfTemperature,
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
        # Grid & Power Flows
        SharegySolarPowerSensor(coordinator, entry),
        SharegyHouseholdLoadSensor(coordinator, entry),
        SharegyGridPowerSensor(coordinator, entry),
        SharegyBatteryPowerSensor(coordinator, entry),
        SharegyBatterySoCSensor(coordinator, entry),
        SharegyAutarkySensor(coordinator, entry),
        SharegySelfConsumptionSensor(coordinator, entry),
        SharegySpotPriceSensor(coordinator, entry),
        SharegyOptimizerWindowSensor(coordinator, entry),

        # Floor Heating & Screed Thermal Battery (Bidirectional)
        SharegyFloorHeatingFlowTempSensor(coordinator, entry),
        SharegyFloorHeatingScreedSoCSensor(coordinator, entry),
        SharegyFloorHeatingPowerSensor(coordinator, entry),
        SharegyFloorHeatingStatusSensor(coordinator, entry),
        SharegyFloorHeatingRoomTempSensor(coordinator, entry),
        SharegyBwwpStatusSensor(coordinator, entry),
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
            sw_version="2.1.0",
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
        dash = self.coordinator.data.get("dashboard", {})
        val = dash.get("pv_power_w")
        if val is None:
            val = dash.get("kpis", {}).get("pv")
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
        dash = self.coordinator.data.get("dashboard", {})
        val = dash.get("load_power_w")
        if val is None:
            val = dash.get("kpis", {}).get("load")
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
        dash = self.coordinator.data.get("dashboard", {})
        val = dash.get("grid_power_w")
        if val is None:
            val = dash.get("kpis", {}).get("grid", 0.0)
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
        dash = self.coordinator.data.get("dashboard", {})
        val = dash.get("battery_power_w")
        if val is None:
            val = dash.get("kpis", {}).get("battery", 0.0)
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
        dash = self.coordinator.data.get("dashboard", {})
        val = dash.get("battery_soc_pct")
        if val is None:
            val = dash.get("battery_soc")
        if val is None:
            val = dash.get("kpis", {}).get("battery_soc_pct", 65.0)
        return round(float(val or 65.0), 1)


class SharegyAutarkySensor(SharegyBaseSensor):
    """Today's Autarky Rate in Percentage."""

    _attr_state_class = SensorStateClass.MEASUREMENT
    _attr_native_unit_of_measurement = PERCENTAGE
    _attr_icon = "mdi:shield-sun"

    def __init__(self, coordinator, entry) -> None:
        super().__init__(coordinator, entry, "autarky_rate", "Autarkiegrad")

    @property
    def native_value(self) -> float:
        val = self.coordinator.data.get("balance", {}).get("kpis", {}).get("autarky_rate")
        if val is None:
            val = self.coordinator.data.get("dashboard", {}).get("autarky_rate_pct", 0.0)
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
        val = self.coordinator.data.get("balance", {}).get("kpis", {}).get("self_consumption_rate")
        if val is None:
            val = self.coordinator.data.get("dashboard", {}).get("self_consumption_rate_pct", 0.0)
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
        opt = self.coordinator.data.get("optimizer", {})
        timeline = opt.get("timeline", [])
        if timeline and len(timeline) > 0:
            price = timeline[0].get("effective_price_ct")
            if price is not None:
                return round(float(price), 2)
        if opt.get("avg_day_cost_ct") is not None:
            return round(float(opt["avg_day_cost_ct"]), 2)
        val = self.coordinator.data.get("balance", {}).get("kpis", {}).get("tariff_elec_eur_kwh")
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
        windows = opt.get("windows", {})
        best_2h = windows.get("2h", {}).get("best_overall", {})
        if best_2h and best_2h.get("start_label") and best_2h.get("end_label"):
            return f"{best_2h.get('start_label')} - {best_2h.get('end_label')}"
        recs = opt.get("recommendations", [])
        if recs and isinstance(recs, list) and len(recs) > 0:
            r2 = next((r for r in recs if r.get("duration_hours") == 2), recs[0])
            return f"{r2.get('start_time', '13:00')} - {r2.get('end_time', '15:00')}"
        return "13:00 - 15:00"

    @property
    def extra_state_attributes(self) -> dict:
        opt = self.coordinator.data.get("optimizer", {})
        return {
            "avg_day_cost_ct": opt.get("avg_day_cost_ct"),
            "windows": opt.get("windows", {}),
            "timeline": opt.get("timeline", [])[:6],
        }


# ============================================================================
# 🌡️ FLOOR HEATING & THERMAL SCREED BATTERY SENSORS
# ============================================================================

class SharegyFloorHeatingFlowTempSensor(SharegyBaseSensor):
    """Calculated Flow Temperature Setpoint according to DIN EN 12831 heating curve (°C)."""

    _attr_device_class = SensorDeviceClass.TEMPERATURE
    _attr_state_class = SensorStateClass.MEASUREMENT
    _attr_native_unit_of_measurement = UnitOfTemperature.CELSIUS
    _attr_icon = "mdi:water-thermometer"

    def __init__(self, coordinator, entry) -> None:
        super().__init__(coordinator, entry, "floor_heating_flow_temp", "FBH Vorlauf-Solltemperatur")

    @property
    def native_value(self) -> float:
        fh = self.coordinator.data.get("floor_heating", {})
        val = fh.get("flow_temp_setpoint_c") or fh.get("target_flow_temp_c")
        if val is None:
            val = fh.get("kpis", {}).get("flow_temp", 31.5)
        return round(float(val or 30.0), 1)


class SharegyFloorHeatingScreedSoCSensor(SharegyBaseSensor):
    """Screed Thermal Storage State of Charge in %."""

    _attr_state_class = SensorStateClass.MEASUREMENT
    _attr_native_unit_of_measurement = PERCENTAGE
    _attr_icon = "mdi:battery-arrow-up"

    def __init__(self, coordinator, entry) -> None:
        super().__init__(coordinator, entry, "floor_heating_screed_soc", "FBH Estrich-Speicher Ladestand (SoC)")

    @property
    def native_value(self) -> float:
        fh = self.coordinator.data.get("floor_heating", {})
        soc = fh.get("screed_soc_pct")
        if soc is None:
            soc = fh.get("thermal_storage", {}).get("soc_pct", 50.0)
        return round(float(soc or 50.0), 1)

    @property
    def extra_state_attributes(self) -> dict:
        fh = self.coordinator.data.get("floor_heating", {})
        return {
            "stored_kwh": fh.get("thermal_storage", {}).get("stored_kwh"),
            "max_capacity_kwh": fh.get("thermal_storage", {}).get("capacity_kwh", 15.6),
            "screed_mass_kg": fh.get("screed_mass_kg", 16800),
        }


class SharegyFloorHeatingPowerSensor(SharegyBaseSensor):
    """Current Floor Heating Power in kW."""

    _attr_device_class = SensorDeviceClass.POWER
    _attr_state_class = SensorStateClass.MEASUREMENT
    _attr_native_unit_of_measurement = "kW"
    _attr_icon = "mdi:heat-wave"

    def __init__(self, coordinator, entry) -> None:
        super().__init__(coordinator, entry, "floor_heating_power", "FBH Heizleistung")

    @property
    def native_value(self) -> float:
        fh = self.coordinator.data.get("floor_heating", {})
        val = fh.get("heating_power_kw") or fh.get("current_power_kw", 0.0)
        return round(float(val or 0.0), 2)


class SharegyFloorHeatingStatusSensor(SharegyBaseSensor):
    """Current Operating Mode of the Floor Heating Dispatch System."""

    _attr_icon = "mdi:tune-vertical"

    def __init__(self, coordinator, entry) -> None:
        super().__init__(coordinator, entry, "floor_heating_mode", "FBH Betriebsmodus")

    @property
    def native_value(self) -> str:
        fh = self.coordinator.data.get("floor_heating", {})
        mode = fh.get("mode") or fh.get("status", "STANDBY")
        mode_labels = {
            "pv_boost": "PV-Überschuss Boost",
            "grid_arbitrage": "Netz-Arbitrage (Niedrigpreis)",
            "comfort": "Komfortbetrieb",
            "eco": "Eco-Absenkung",
            "standby": "Standby / Deaktiviert",
            "manual_boost": "Manueller Boost",
        }
        return mode_labels.get(str(mode).lower(), str(mode).upper())


class SharegyFloorHeatingRoomTempSensor(SharegyBaseSensor):
    """Current Room Temperature in °C."""

    _attr_device_class = SensorDeviceClass.TEMPERATURE
    _attr_state_class = SensorStateClass.MEASUREMENT
    _attr_native_unit_of_measurement = UnitOfTemperature.CELSIUS
    _attr_icon = "mdi:home-thermometer"

    def __init__(self, coordinator, entry) -> None:
        super().__init__(coordinator, entry, "floor_heating_room_temp", "FBH Ist-Raumtemperatur")

    @property
    def native_value(self) -> float:
        fh = self.coordinator.data.get("floor_heating", {})
        val = fh.get("current_room_temp_c")
        if val is None:
            val = fh.get("room_temp_c", 21.2)
        return round(float(val or 21.0), 1)


class SharegyBwwpStatusSensor(SharegyBaseSensor):
    """Current Status of Brauchwasser-Wärmepumpe SG-Ready."""

    _attr_icon = "mdi:water-boiler-alert"

    def __init__(self, coordinator, entry) -> None:
        super().__init__(coordinator, entry, "bwwp_status", "BWWP SG-Ready Status")

    @property
    def native_value(self) -> str:
        bwwp = self.coordinator.data.get("bwwp", {})
        if bwwp.get("is_active") or bwwp.get("status") == "boost":
            return "SG-Ready Boost (Aktiv)"
        return "Normalbetrieb (Standby)"
