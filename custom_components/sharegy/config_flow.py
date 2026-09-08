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
    CONF_BWWP_NAME,
    CONF_BWWP_POWER,
    CONF_BWWP_TEMP,
    CONF_BWWP_SWITCH,
    CONF_HEATPUMP_NAME,
    CONF_HEATPUMP_POWER,
    CONF_HEATPUMP_TEMP,
    CONF_HEATPUMP_SWITCH,
    CONF_FLOOR_HEATING_NAME,
    CONF_FLOOR_HEATING_POWER,
    CONF_FLOOR_HEATING_ROOM_TEMP,
    CONF_FLOOR_HEATING_FLOW_TEMP,
    CONF_FLOOR_HEATING_FLOOR_TEMP,
    CONF_FLOOR_HEATING_SWITCH,
    CONF_FLOOR_HEATING_FLOW_SETPOINT,
    CONF_FLOOR_HEATING_TARGET_ROOM_TEMP,
    CONF_FLOOR_HEATING_BOOST_DELTA_K,
    CONF_FLOOR_HEATING_MAX_FLOOR_TEMP,
    CONF_WALLBOX_NAME,
    CONF_WALLBOX_POWER,
    CONF_WALLBOX_SWITCH,
    CONF_SUBMETER_SENSORS,
    CONF_SYNC_INTERVAL,
    DEFAULT_WS_URL,
    DEFAULT_SYNC_INTERVAL,
    DEFAULT_FBH_TARGET_ROOM_TEMP,
    DEFAULT_FBH_BOOST_DELTA_K,
    DEFAULT_FBH_MAX_FLOOR_TEMP,
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
        """Step 2: Interactive Entity Selection for EMS and Unified Device Bundles."""
        if user_input is not None:
            final_data = {**self._auth_data, **user_input}
            token_display = self._auth_data.get(CONF_HOME_TOKEN, "")[:8]
            return self.async_create_entry(
                title=f"Sharegy ({token_display}...)",
                data=final_data,
            )

        entity_schema = vol.Schema(
            {
                # Core EMS Sensors
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
                # Floor Heating & Estrich-Speicher Bundle
                vol.Optional(CONF_FLOOR_HEATING_NAME, default="Fussbodenheizung"): str,
                vol.Optional(CONF_FLOOR_HEATING_ROOM_TEMP): selector.EntitySelector(
                    selector.EntitySelectorConfig(domain=["sensor"])
                ),
                vol.Optional(CONF_FLOOR_HEATING_FLOW_TEMP): selector.EntitySelector(
                    selector.EntitySelectorConfig(domain=["sensor"])
                ),
                vol.Optional(CONF_FLOOR_HEATING_FLOOR_TEMP): selector.EntitySelector(
                    selector.EntitySelectorConfig(domain=["sensor"])
                ),
                vol.Optional(CONF_FLOOR_HEATING_SWITCH): selector.EntitySelector(
                    selector.EntitySelectorConfig(
                        domain=["switch", "input_boolean", "light"]
                    )
                ),
                vol.Optional(CONF_FLOOR_HEATING_FLOW_SETPOINT): selector.EntitySelector(
                    selector.EntitySelectorConfig(domain=["number", "input_number", "sensor"])
                ),
                vol.Optional(CONF_FLOOR_HEATING_POWER): selector.EntitySelector(
                    selector.EntitySelectorConfig(domain=["sensor"])
                ),
                vol.Optional(CONF_FLOOR_HEATING_TARGET_ROOM_TEMP, default=DEFAULT_FBH_TARGET_ROOM_TEMP): selector.NumberSelector(
                    selector.NumberSelectorConfig(min=15.0, max=28.0, step=0.5, unit_of_measurement="°C")
                ),
                vol.Optional(CONF_FLOOR_HEATING_BOOST_DELTA_K, default=DEFAULT_FBH_BOOST_DELTA_K): selector.NumberSelector(
                    selector.NumberSelectorConfig(min=0.2, max=3.0, step=0.1, unit_of_measurement="K")
                ),
                vol.Optional(CONF_FLOOR_HEATING_MAX_FLOOR_TEMP, default=DEFAULT_FBH_MAX_FLOOR_TEMP): selector.NumberSelector(
                    selector.NumberSelectorConfig(min=20.0, max=35.0, step=0.5, unit_of_measurement="°C")
                ),
                # BWWP Bundle
                vol.Optional(CONF_BWWP_NAME, default="Brauchwasser"): str,
                vol.Optional(CONF_BWWP_POWER): selector.EntitySelector(
                    selector.EntitySelectorConfig(domain=["sensor"])
                ),
                vol.Optional(CONF_BWWP_TEMP): selector.EntitySelector(
                    selector.EntitySelectorConfig(domain=["sensor"])
                ),
                vol.Optional(CONF_BWWP_SWITCH): selector.EntitySelector(
                    selector.EntitySelectorConfig(
                        domain=["switch", "input_boolean", "light"]
                    )
                ),
                # Heatpump Bundle
                vol.Optional(CONF_HEATPUMP_NAME, default="Waermepumpe"): str,
                vol.Optional(CONF_HEATPUMP_POWER): selector.EntitySelector(
                    selector.EntitySelectorConfig(domain=["sensor"])
                ),
                vol.Optional(CONF_HEATPUMP_TEMP): selector.EntitySelector(
                    selector.EntitySelectorConfig(domain=["sensor"])
                ),
                vol.Optional(CONF_HEATPUMP_SWITCH): selector.EntitySelector(
                    selector.EntitySelectorConfig(
                        domain=["switch", "input_boolean", "light"]
                    )
                ),
                # Wallbox Bundle
                vol.Optional(CONF_WALLBOX_NAME, default="Wallbox"): str,
                vol.Optional(CONF_WALLBOX_POWER): selector.EntitySelector(
                    selector.EntitySelectorConfig(domain=["sensor"])
                ),
                vol.Optional(CONF_WALLBOX_SWITCH): selector.EntitySelector(
                    selector.EntitySelectorConfig(
                        domain=["switch", "input_boolean", "light"]
                    )
                ),
                # Other Submeters & Interval
                vol.Optional(CONF_SUBMETER_SENSORS): selector.EntitySelector(
                    selector.EntitySelectorConfig(
                        domain=["sensor"],
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
        # Core EMS Sensors
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

        # Floor Heating Bundle
        fields[vol.Optional(CONF_FLOOR_HEATING_NAME, default=data.get(CONF_FLOOR_HEATING_NAME, "Fussbodenheizung"))] = str
        for key in [CONF_FLOOR_HEATING_ROOM_TEMP, CONF_FLOOR_HEATING_FLOW_TEMP, CONF_FLOOR_HEATING_FLOOR_TEMP, CONF_FLOOR_HEATING_POWER]:
            if data.get(key):
                fields[vol.Optional(key, default=data[key])] = selector.EntitySelector(
                    selector.EntitySelectorConfig(domain=["sensor"])
                )
            else:
                fields[vol.Optional(key)] = selector.EntitySelector(
                    selector.EntitySelectorConfig(domain=["sensor"])
                )

        if data.get(CONF_FLOOR_HEATING_SWITCH):
            fields[vol.Optional(CONF_FLOOR_HEATING_SWITCH, default=data[CONF_FLOOR_HEATING_SWITCH])] = selector.EntitySelector(
                selector.EntitySelectorConfig(domain=["switch", "input_boolean", "light"])
            )
        else:
            fields[vol.Optional(CONF_FLOOR_HEATING_SWITCH)] = selector.EntitySelector(
                selector.EntitySelectorConfig(domain=["switch", "input_boolean", "light"])
            )

        if data.get(CONF_FLOOR_HEATING_FLOW_SETPOINT):
            fields[vol.Optional(CONF_FLOOR_HEATING_FLOW_SETPOINT, default=data[CONF_FLOOR_HEATING_FLOW_SETPOINT])] = selector.EntitySelector(
                selector.EntitySelectorConfig(domain=["number", "input_number", "sensor"])
            )
        else:
            fields[vol.Optional(CONF_FLOOR_HEATING_FLOW_SETPOINT)] = selector.EntitySelector(
                selector.EntitySelectorConfig(domain=["number", "input_number", "sensor"])
            )

        fields[vol.Optional(CONF_FLOOR_HEATING_TARGET_ROOM_TEMP, default=data.get(CONF_FLOOR_HEATING_TARGET_ROOM_TEMP, DEFAULT_FBH_TARGET_ROOM_TEMP))] = selector.NumberSelector(
            selector.NumberSelectorConfig(min=15.0, max=28.0, step=0.5, unit_of_measurement="°C")
        )
        fields[vol.Optional(CONF_FLOOR_HEATING_BOOST_DELTA_K, default=data.get(CONF_FLOOR_HEATING_BOOST_DELTA_K, DEFAULT_FBH_BOOST_DELTA_K))] = selector.NumberSelector(
            selector.NumberSelectorConfig(min=0.2, max=3.0, step=0.1, unit_of_measurement="K")
        )
        fields[vol.Optional(CONF_FLOOR_HEATING_MAX_FLOOR_TEMP, default=data.get(CONF_FLOOR_HEATING_MAX_FLOOR_TEMP, DEFAULT_FBH_MAX_FLOOR_TEMP))] = selector.NumberSelector(
            selector.NumberSelectorConfig(min=20.0, max=35.0, step=0.5, unit_of_measurement="°C")
        )

        # BWWP Bundle
        fields[vol.Optional(CONF_BWWP_NAME, default=data.get(CONF_BWWP_NAME, "Brauchwasser"))] = str
        for key in [CONF_BWWP_POWER, CONF_BWWP_TEMP]:
            if data.get(key):
                fields[vol.Optional(key, default=data[key])] = selector.EntitySelector(
                    selector.EntitySelectorConfig(domain=["sensor"])
                )
            else:
                fields[vol.Optional(key)] = selector.EntitySelector(
                    selector.EntitySelectorConfig(domain=["sensor"])
                )

        if data.get(CONF_BWWP_SWITCH):
            fields[vol.Optional(CONF_BWWP_SWITCH, default=data[CONF_BWWP_SWITCH])] = selector.EntitySelector(
                selector.EntitySelectorConfig(domain=["switch", "input_boolean", "light"])
            )
        else:
            fields[vol.Optional(CONF_BWWP_SWITCH)] = selector.EntitySelector(
                selector.EntitySelectorConfig(domain=["switch", "input_boolean", "light"])
            )

        # Heatpump Bundle
        fields[vol.Optional(CONF_HEATPUMP_NAME, default=data.get(CONF_HEATPUMP_NAME, "Waermepumpe"))] = str
        for key in [CONF_HEATPUMP_POWER, CONF_HEATPUMP_TEMP]:
            if data.get(key):
                fields[vol.Optional(key, default=data[key])] = selector.EntitySelector(
                    selector.EntitySelectorConfig(domain=["sensor"])
                )
            else:
                fields[vol.Optional(key)] = selector.EntitySelector(
                    selector.EntitySelectorConfig(domain=["sensor"])
                )

        if data.get(CONF_HEATPUMP_SWITCH):
            fields[vol.Optional(CONF_HEATPUMP_SWITCH, default=data[CONF_HEATPUMP_SWITCH])] = selector.EntitySelector(
                selector.EntitySelectorConfig(domain=["switch", "input_boolean", "light"])
            )
        else:
            fields[vol.Optional(CONF_HEATPUMP_SWITCH)] = selector.EntitySelector(
                selector.EntitySelectorConfig(domain=["switch", "input_boolean", "light"])
            )

        # Wallbox Bundle
        fields[vol.Optional(CONF_WALLBOX_NAME, default=data.get(CONF_WALLBOX_NAME, "Wallbox"))] = str
        if data.get(CONF_WALLBOX_POWER):
            fields[vol.Optional(CONF_WALLBOX_POWER, default=data[CONF_WALLBOX_POWER])] = selector.EntitySelector(
                selector.EntitySelectorConfig(domain=["sensor"])
            )
        else:
            fields[vol.Optional(CONF_WALLBOX_POWER)] = selector.EntitySelector(
                selector.EntitySelectorConfig(domain=["sensor"])
            )

        if data.get(CONF_WALLBOX_SWITCH):
            fields[vol.Optional(CONF_WALLBOX_SWITCH, default=data[CONF_WALLBOX_SWITCH])] = selector.EntitySelector(
                selector.EntitySelectorConfig(domain=["switch", "input_boolean", "light"])
            )
        else:
            fields[vol.Optional(CONF_WALLBOX_SWITCH)] = selector.EntitySelector(
                selector.EntitySelectorConfig(domain=["switch", "input_boolean", "light"])
            )

        # Other Submeters & Interval
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
