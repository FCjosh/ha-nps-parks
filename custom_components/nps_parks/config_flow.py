"""Config Flow for NPS Parks."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

import aiohttp
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
    UPDATE_INTERVAL_OPTIONS,
)
from .designations import NPS_DESIGNATIONS

if TYPE_CHECKING:
    from homeassistant.config_entries import ConfigEntry


class NPSParksFlowHandler(config_entries.ConfigFlow, domain=DOMAIN):
    """Config flow for ha-nps-parks."""

    VERSION = 1

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> config_entries.ConfigFlowResult:
        """Handle the initial setup step."""
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
        """Return an error string if the API key is invalid, else None."""
        try:
            session = async_get_clientsession(self.hass)
            response = await session.get(
                BASE_URL,
                params={"limit": 1, "api_key": api_key},
            )
            if response.status in (401, 403):
                return "invalid_auth"
            response.raise_for_status()
        except aiohttp.ClientError, TimeoutError:
            return "connection"
        else:
            return None

    @staticmethod
    @callback
    def async_get_options_flow(
        _config_entry: ConfigEntry,
    ) -> NPSParksOptionsFlowHandler:
        """Return the options flow handler."""
        return NPSParksOptionsFlowHandler()


class NPSParksOptionsFlowHandler(config_entries.OptionsFlow):
    """Options flow for NPS Parks integration."""

    async def async_step_init(
        self, user_input: dict[str, Any] | None = None
    ) -> config_entries.ConfigFlowResult:
        """Handle the options step."""
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
