# pyright: reportMissingImports=false
"""The Sharegy HEMS integration."""

from __future__ import annotations
import logging
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant, ServiceCall

from .const import DOMAIN
from .coordinator import SharegyDataUpdateCoordinator

_LOGGER = logging.getLogger(__name__)

PLATFORMS: list[Platform] = [Platform.SENSOR]


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up Sharegy HEMS from a config entry."""
    hass.data.setdefault(DOMAIN, {})

    coordinator = SharegyDataUpdateCoordinator(hass, entry)
    await coordinator.async_config_entry_first_refresh()

    hass.data[DOMAIN][entry.entry_id] = coordinator

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)

    # Register custom service: sharegy.push_telemetry
    async def handle_push_telemetry(call: ServiceCall):
        devices = call.data.get("devices", [])
        if not devices and "identifier" in call.data:
            devices = [call.data]
        success = await coordinator.async_push_telemetry(devices)
        if not success:
            _LOGGER.warning("Konnte Telemetrie nicht an Sharegy übertragen.")

    hass.services.async_register(DOMAIN, "push_telemetry", handle_push_telemetry)

    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
    if unload_ok:
        hass.data[DOMAIN].pop(entry.entry_id)

    return unload_ok

