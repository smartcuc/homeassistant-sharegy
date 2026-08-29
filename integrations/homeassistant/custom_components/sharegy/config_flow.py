"""Config Flow for Sharegy Cloud Energy Bridge."""

from __future__ import annotations

import logging
from typing import Any
import voluptuous as vol

from homeassistant import config_entries
from homeassistant.core import callback
from homeassistant.helpers import selector

from .const import (
    DOMAIN,
    CONF_HOST,
    CONF_HOME_TOKEN,
    CONF_PROTOCOL,
    CONF_GRID_POWER_SENSOR,
    CONF_GRID_ENERGY_SENSOR,
    CONF_PV_POWER_SENSOR,
    CONF_PV_ENERGY_SENSOR,
    CONF_BATTERY_POWER_SENSOR,
    CONF_BATTERY_SOC_SENSOR,
    CONF_LOAD_POWER_SENSOR,
    CONF_SUBMETER_SENSORS,
    CONF_SYNC_INTERVAL,
    DEFAULT_HOST,
    DEFAULT_PROTOCOL,
    DEFAULT_SYNC_INTERVAL,
)

_LOGGER = logging.getLogger(__name__)


class SharegyConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Sharegy."""

    VERSION = 1

    def __init__(self):
        self._auth_data: dict[str, Any] = {}

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> config_entries.FlowResult:
        """Step 1: Authenticate with Sharegy Token."""
        errors: dict[str, str] = {}

        if user_input is not None:
            token = user_input.get(CONF_HOME_TOKEN, "").strip()
            if not token:
                errors["base"] = "invalid_auth"
            else:
                self._auth_data = user_input
                return await self.async_step_entities()

        data_schema = vol.Schema(
            {
                vol.Required(CONF_HOST, default=DEFAULT_HOST): str,
                vol.Required(CONF_HOME_TOKEN): str,
                vol.Optional(CONF_PROTOCOL, default=DEFAULT_PROTOCOL): selector.SelectSelector(
                    selector.SelectSelectorConfig(
                        options=[
                            {"value": "websocket", "label": "WebSocket (Live Real-Time / WSS)"},
                            {"value": "rest", "label": "REST API (HTTP Ingest)"},
                        ],
                        mode=selector.SelectSelectorMode.DROPDOWN,
                    )
                ),
            }
        )

        return self.async_show_form(
            step_id="user",
            data_schema=data_schema,
            errors=errors,
            description_placeholders={"docs_url": "https://sharegy.de/docs"},
        )

    async def async_step_entities(
        self, user_input: dict[str, Any] | None = None
    ) -> config_entries.FlowResult:
        """Step 2: Interactive Entity Selection via native HA Selectors."""
        if user_input is not None:
            final_data = {**self._auth_data, **user_input}
            return self.async_create_entry(
                title=f"Sharegy ({self._auth_data.get(CONF_HOME_TOKEN, '')[:8]}...)",
                data=final_data,
            )

        # Build schema with rich Entity Selectors
        entity_schema = vol.Schema(
            {
                vol.Optional(CONF_GRID_POWER_SENSOR): selector.EntitySelector(
                    selector.EntitySelectorConfig(
                        domain=["sensor"],
                        device_class=["power"],
                    )
                ),
                vol.Optional(CONF_PV_POWER_SENSOR): selector.EntitySelector(
                    selector.EntitySelectorConfig(
                        domain=["sensor"],
                        device_class=["power"],
                    )
                ),
                vol.Optional(CONF_BATTERY_POWER_SENSOR): selector.EntitySelector(
                    selector.EntitySelectorConfig(
                        domain=["sensor"],
                        device_class=["power"],
                    )
                ),
                vol.Optional(CONF_BATTERY_SOC_SENSOR): selector.EntitySelector(
                    selector.EntitySelectorConfig(
                        domain=["sensor"],
                        device_class=["battery"],
                    )
                ),
                vol.Optional(CONF_LOAD_POWER_SENSOR): selector.EntitySelector(
                    selector.EntitySelectorConfig(
                        domain=["sensor"],
                        device_class=["power"],
                    )
                ),
                vol.Optional(CONF_SUBMETER_SENSORS): selector.EntitySelector(
                    selector.EntitySelectorConfig(
                        domain=["sensor"],
                        device_class=["power", "energy"],
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
            description_placeholders={"host": self._auth_data.get(CONF_HOST, "")},
        )

    @staticmethod
    @callback
    def async_get_options_flow(
        config_entry: config_entries.ConfigEntry,
    ) -> config_entries.OptionsFlow:
        """Get the options flow for this handler."""
        return SharegyOptionsFlowHandler(config_entry)


class SharegyOptionsFlowHandler(config_entries.OptionsFlow):
    """Handle options for updating entity mapping live in HA."""

    def __init__(self, config_entry: config_entries.ConfigEntry) -> None:
        self.config_entry = config_entry

    async def async_step_init(
        self, user_input: dict[str, Any] | None = None
    ) -> config_entries.FlowResult:
        """Manage entity selectors."""
        if user_input is not None:
            # Update config entry data directly
            self.hass.config_entries.async_update_entry(
                self.config_entry,
                data={**self.config_entry.data, **user_input},
            )
            return self.async_create_entry(title="", data={})

        data = self.config_entry.data

        options_schema = vol.Schema(
            {
                vol.Optional(
                    CONF_GRID_POWER_SENSOR,
                    default=data.get(CONF_GRID_POWER_SENSOR),
                ): selector.EntitySelector(
                    selector.EntitySelectorConfig(domain=["sensor"])
                ),
                vol.Optional(
                    CONF_PV_POWER_SENSOR,
                    default=data.get(CONF_PV_POWER_SENSOR),
                ): selector.EntitySelector(
                    selector.EntitySelectorConfig(domain=["sensor"])
                ),
                vol.Optional(
                    CONF_BATTERY_POWER_SENSOR,
                    default=data.get(CONF_BATTERY_POWER_SENSOR),
                ): selector.EntitySelector(
                    selector.EntitySelectorConfig(domain=["sensor"])
                ),
                vol.Optional(
                    CONF_BATTERY_SOC_SENSOR,
                    default=data.get(CONF_BATTERY_SOC_SENSOR),
                ): selector.EntitySelector(
                    selector.EntitySelectorConfig(domain=["sensor"])
                ),
                vol.Optional(
                    CONF_LOAD_POWER_SENSOR,
                    default=data.get(CONF_LOAD_POWER_SENSOR),
                ): selector.EntitySelector(
                    selector.EntitySelectorConfig(domain=["sensor"])
                ),
                vol.Optional(
                    CONF_SUBMETER_SENSORS,
                    default=data.get(CONF_SUBMETER_SENSORS, []),
                ): selector.EntitySelector(
                    selector.EntitySelectorConfig(
                        domain=["sensor"],
                        multiple=True,
                    )
                ),
                vol.Optional(
                    CONF_SYNC_INTERVAL,
                    default=data.get(CONF_SYNC_INTERVAL, DEFAULT_SYNC_INTERVAL),
                ): selector.NumberSelector(
                    selector.NumberSelectorConfig(
                        min=1,
                        max=60,
                        unit_of_measurement="s",
                    )
                ),
            }
        )

        return self.async_show_form(step_id="init", data_schema=options_schema)
