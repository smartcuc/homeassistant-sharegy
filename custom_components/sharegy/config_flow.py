"""Config Flow for Sharegy Cloud Energy Bridge."""

from __future__ import annotations

import logging
import re
from typing import Any
import voluptuous as vol

from homeassistant import config_entries
from homeassistant.core import callback
from homeassistant.helpers import selector

from .const import (
    DOMAIN,
    CONF_WS_URL,
    CONF_HOME_TOKEN,
    CONF_GRID_POWER_SENSOR,
    CONF_PV_POWER_SENSOR,
    CONF_BATTERY_POWER_SENSOR,
    CONF_BATTERY_SOC_SENSOR,
    CONF_LOAD_POWER_SENSOR,
    CONF_SUBMETER_SENSORS,
    CONF_CONTROL_SWITCHES,
    CONF_SYNC_INTERVAL,
    DEFAULT_WS_URL,
    DEFAULT_SYNC_INTERVAL,
)

_LOGGER = logging.getLogger(__name__)


def extract_token(user_input: dict[str, Any]) -> str:
    """Extract clean token from either URL or token input field."""
    ws_url = (user_input.get(CONF_WS_URL) or "").strip()
    token_input = (user_input.get(CONF_HOME_TOKEN) or "").strip()

    for candidate in [ws_url, token_input]:
        if candidate:
            match = re.search(r"/ws/energy/([a-zA-Z0-9_-]+)", candidate)
            if match:
                return match.group(1).strip()

    return token_input


class SharegyConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Sharegy."""

    VERSION = 1

    def __init__(self):
        self._auth_data: dict[str, Any] = {}

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> config_entries.FlowResult:
        """Step 1: Authenticate with Sharegy Token or 1-Click WSS URL."""
        errors: dict[str, str] = {}

        if user_input is not None:
            token = extract_token(user_input)
            if not token:
                errors["base"] = "invalid_auth"
            else:
                user_input[CONF_HOME_TOKEN] = token
                self._auth_data = user_input
                return await self.async_step_entities()

        data_schema = vol.Schema(
            {
                vol.Required(CONF_WS_URL, default=DEFAULT_WS_URL): str,
                vol.Optional(CONF_HOME_TOKEN, default=""): str,
            }
        )

        return self.async_show_form(
            step_id="user",
            data_schema=data_schema,
            errors=errors,
        )

    async def async_step_entities(
        self, user_input: dict[str, Any] | None = None
    ) -> config_entries.FlowResult:
        """Step 2: Interactive Entity Selection for EMS, Sensors, and Bidirectional Control."""
        if user_input is not None:
            final_data = {**self._auth_data, **user_input}
            token_display = self._auth_data.get(CONF_HOME_TOKEN, "")[:8]
            return self.async_create_entry(
                title=f"Sharegy ({token_display}...)",
                data=final_data,
            )

        entity_schema = vol.Schema(
            {
                vol.Optional(CONF_GRID_POWER_SENSOR): selector.EntitySelector(
                    selector.EntitySelectorConfig(domain=["sensor"])
                ),
                vol.Optional(CONF_PV_POWER_SENSOR): selector.EntitySelector(
                    selector.EntitySelectorConfig(domain=["sensor"])
                ),
                vol.Optional(CONF_BATTERY_POWER_SENSOR): selector.EntitySelector(
                    selector.EntitySelectorConfig(domain=["sensor"])
                ),
                vol.Optional(CONF_BATTERY_SOC_SENSOR): selector.EntitySelector(
                    selector.EntitySelectorConfig(domain=["sensor"])
                ),
                vol.Optional(CONF_LOAD_POWER_SENSOR): selector.EntitySelector(
                    selector.EntitySelectorConfig(domain=["sensor"])
                ),
                vol.Optional(CONF_SUBMETER_SENSORS): selector.EntitySelector(
                    selector.EntitySelectorConfig(
                        domain=["sensor"],
                        multiple=True,
                    )
                ),
                vol.Optional(CONF_CONTROL_SWITCHES): selector.EntitySelector(
                    selector.EntitySelectorConfig(
                        domain=["switch", "input_boolean", "light"],
                        multiple=True,
                    )
                ),
                vol.Optional(CONF_SYNC_INTERVAL, default=DEFAULT_SYNC_INTERVAL): selector.NumberSelector(
                    selector.NumberSelectorConfig(
                        min=1,
                        max=60,
                        unit_of_measurement="s",
                        mode=selector.NumberSelectorMode.SLIDER,
                    )
                ),
            }
        )

        return self.async_show_form(
            step_id="entities",
            data_schema=entity_schema,
        )

    @staticmethod
    @callback
    def async_get_options_flow(
        config_entry: config_entries.ConfigEntry,
    ) -> config_entries.OptionsFlow:
        """Get the options flow for this handler."""
        return SharegyOptionsFlowHandler()


class SharegyOptionsFlowHandler(config_entries.OptionsFlow):
    """Handle options for updating entity mapping live in HA."""

    async def async_step_init(
        self, user_input: dict[str, Any] | None = None
    ) -> config_entries.FlowResult:
        """Manage entity selectors."""
        if user_input is not None:
            self.hass.config_entries.async_update_entry(
                self.config_entry,
                data={**self.config_entry.data, **user_input},
            )
            return self.async_create_entry(title="", data={})

        data = self.config_entry.data

        fields = {}
        for key in [
            CONF_GRID_POWER_SENSOR,
            CONF_PV_POWER_SENSOR,
            CONF_BATTERY_POWER_SENSOR,
            CONF_BATTERY_SOC_SENSOR,
            CONF_LOAD_POWER_SENSOR,
        ]:
            if data.get(key):
                fields[vol.Optional(key, default=data[key])] = selector.EntitySelector(
                    selector.EntitySelectorConfig(domain=["sensor"])
                )
            else:
                fields[vol.Optional(key)] = selector.EntitySelector(
                    selector.EntitySelectorConfig(domain=["sensor"])
                )

        if data.get(CONF_SUBMETER_SENSORS):
            fields[vol.Optional(CONF_SUBMETER_SENSORS, default=data[CONF_SUBMETER_SENSORS])] = (
                selector.EntitySelector(
                    selector.EntitySelectorConfig(domain=["sensor"], multiple=True)
                )
            )
        else:
            fields[vol.Optional(CONF_SUBMETER_SENSORS)] = selector.EntitySelector(
                selector.EntitySelectorConfig(domain=["sensor"], multiple=True)
            )

        if data.get(CONF_CONTROL_SWITCHES):
            fields[vol.Optional(CONF_CONTROL_SWITCHES, default=data[CONF_CONTROL_SWITCHES])] = (
                selector.EntitySelector(
                    selector.EntitySelectorConfig(
                        domain=["switch", "input_boolean", "light"], multiple=True
                    )
                )
            )
        else:
            fields[vol.Optional(CONF_CONTROL_SWITCHES)] = selector.EntitySelector(
                selector.EntitySelectorConfig(
                    domain=["switch", "input_boolean", "light"], multiple=True
                )
            )

        fields[vol.Optional(CONF_SYNC_INTERVAL, default=data.get(CONF_SYNC_INTERVAL, DEFAULT_SYNC_INTERVAL))] = (
            selector.NumberSelector(
                selector.NumberSelectorConfig(
                    min=1,
                    max=60,
                    unit_of_measurement="s",
                    mode=selector.NumberSelectorMode.SLIDER,
                )
            )
        )

        return self.async_show_form(
            step_id="init",
            data_schema=vol.Schema(fields),
        )
