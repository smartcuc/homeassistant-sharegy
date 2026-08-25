# pyright: reportMissingImports=false
"""Config flow for Sharegy HEMS integration."""

from __future__ import annotations
import logging
import aiohttp
import voluptuous as vol

from homeassistant import config_entries
from homeassistant.core import HomeAssistant
from homeassistant.data_entry_flow import FlowResult

from .const import (
    DOMAIN,
    CONF_HOST,
    CONF_API_KEY,
    CONF_SCAN_INTERVAL,
    DEFAULT_SCAN_INTERVAL,
    ENDPOINT_DASHBOARD,
)

_LOGGER = logging.getLogger(__name__)


async def validate_input(hass: HomeAssistant, data: dict) -> dict:
    """Validate the user input allows us to connect."""
    host = data[CONF_HOST].rstrip("/")
    api_key = data[CONF_API_KEY]

    headers = {
        "Authorization": f"Bearer {api_key}",
        "X-API-Key": api_key,
        "Accept": "application/json",
    }

    url = f"{host}{ENDPOINT_DASHBOARD}"

    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url, headers=headers, timeout=8) as resp:
                if resp.status in (401, 403):
                    return {"error": "invalid_auth"}
                if resp.status != 200:
                    return {"error": "cannot_connect"}
                json_data = await resp.json()
                return {"title": json_data.get("home_name", "Sharegy HEMS")}
    except Exception as err:
        _LOGGER.error("Validation error: %s", err)
        return {"error": "cannot_connect"}


class SharegyConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Sharegy HEMS."""

    VERSION = 1

    async def async_step_user(self, user_input=None) -> FlowResult:
        """Handle the initial step."""
        errors = {}

        if user_input is not None:
            res = await validate_input(self.hass, user_input)
            if "error" not in res:
                return self.async_create_entry(
                    title=res.get("title", "Sharegy HEMS"),
                    data=user_input,
                )
            errors["base"] = res["error"]

        data_schema = vol.Schema(
            {
                vol.Required(CONF_HOST, default="http://192.168.1.100:8000"): str,
                vol.Required(CONF_API_KEY): str,
                vol.Optional(CONF_SCAN_INTERVAL, default=DEFAULT_SCAN_INTERVAL): vol.All(
                    vol.Coerce(int), vol.Range(min=5, max=300)
                ),
            }
        )

        return self.async_show_form(
            step_id="user",
            data_schema=data_schema,
            errors=errors,
        )

