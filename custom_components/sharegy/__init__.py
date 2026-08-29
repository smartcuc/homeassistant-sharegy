"""The Sharegy Cloud Energy Bridge Home Assistant Integration."""

from __future__ import annotations

import logging
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant

from .const import DOMAIN
from .bridge import SharegyBridge

_LOGGER = logging.getLogger(__name__)

PLATFORMS: list[str] = ["sensor"]


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up Sharegy from a config entry."""
    hass.data.setdefault(DOMAIN, {})

    db_path = hass.config.path("sharegy_offline_buffer.db")
    bridge = SharegyBridge(hass, entry.data, db_path)

    hass.data[DOMAIN][entry.entry_id] = {
        "bridge": bridge,
    }

    # Start background telemetry streaming
    await bridge.start()

    # Forward entry setup to sensor platform (for status sensors)
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)

    entry.async_on_unload(entry.add_update_listener(async_reload_entry))

    _LOGGER.info("Sharegy Cloud Energy Bridge started successfully!")
    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
    if unload_ok:
        data = hass.data[DOMAIN].pop(entry.entry_id, None)
        if data and "bridge" in data:
            await data["bridge"].stop()

    return unload_ok


async def async_reload_entry(hass: HomeAssistant, entry: ConfigEntry) -> None:
    """Reload config entry when options change."""
    await hass.config_entries.async_reload(entry.entry_id)
