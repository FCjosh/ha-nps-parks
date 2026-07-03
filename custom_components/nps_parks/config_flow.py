"""Config Flow for NPS Parks."""

from __future__ import annotations

import voluptuous as vol
from homeassistant import config_entries
from homeassistant.core import callback
from homeassistant.helpers import selector
from homeassistant.helpers.aiohttp_client import async_get_clientsession

from .const import (
    API_KEY,
    BASE_URL,
    CONF_DESIGNATIONS,
    CONF_UPDATE_INTERVAL,
    DEFAULT_UPDATE_INTERVAL,
    DOMAIN,
    NPS_DESIGNATIONS,
    UPDATE_INTERVAL_OPTIONS,
)


class NPSParksFlowHandler(config_entries.ConfigFlow, domain=DOMAIN):
    """Config flow for ha-nps-parks."""

    VERSION = 1

    async def async_step_user(
        self, user_input: dict | None = None
    ) -> config_entries.ConfigFlowResult:
        """Handle a flow initialized by the user."""
        _errors = {}
        if user_input is not None:
            error = await self._validate_api_key(user_input[API_KEY])
            if error:
                _errors["base"] = error
            else:
                return self.async_create_entry(title="NPS Parks", data=user_input)

        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema(
                {
                    vol.Required(
                        API_KEY, default=(user_input or {}).get(API_KEY, "")
                    ): selector.TextSelector()
                }
            ),
            errors=_errors,
        )

    async def _validate_api_key(self, api_key: str) -> str | None:
        """Return None if valid, or an error string if not."""
        try:
            session = async_get_clientsession(self.hass)
            response = await session.get(
                f"{BASE_URL}",
                params={"limit": 1, "api_key": api_key},
            )
            if response.status in (401, 403):
                return "invalid_auth"
            return None
        except Exception:
            return "connection"

    @staticmethod
    @callback
    def async_get_options_flow(config_entry):
        return NPSParksOptionsFlowHandler()


class NPSParksOptionsFlowHandler(config_entries.OptionsFlow):
    async def async_step_init(self, user_input=None):
        if user_input is not None:
            return self.async_create_entry(title="", data=user_input)

        current_interval = self.config_entry.options.get(
            CONF_UPDATE_INTERVAL, DEFAULT_UPDATE_INTERVAL
        )
        current_designations = self.config_entry.options.get(CONF_DESIGNATIONS, [])

        return self.async_show_form(
            step_id="init",
            data_schema=vol.Schema(
                {
                    vol.Required(
                        CONF_UPDATE_INTERVAL, default=current_interval
                    ): selector.SelectSelector(
                        selector.SelectSelectorConfig(
                            options=UPDATE_INTERVAL_OPTIONS,
                            translation_key=CONF_UPDATE_INTERVAL,
                        )
                    ),
                    vol.Optional(
                        CONF_DESIGNATIONS, default=current_designations
                    ): selector.SelectSelector(
                        selector.SelectSelectorConfig(
                            options=NPS_DESIGNATIONS,
                            multiple=True,
                        )
                    ),
                }
            ),
        )
