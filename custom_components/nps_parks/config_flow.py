"""Config Flow for NPS Parks."""

from __future__ import annotations

import voluptuous as vol
from homeassistant import config_entries
from homeassistant.helpers import selector
from homeassistant.helpers.aiohttp_client import async_get_clientsession

from .const import API_KEY, BASE_URL, DOMAIN


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
                    vol.Required(API_KEY, default=None): selector.TextSelector(),
                }
            ),
        )

    async def _validate_api_key(self, api_key: str) -> str | None:
        """Return None if valid, or an error string if not."""
        try:
            session = async_get_clientsession(self.hass)
            response = await session.get(
                f"{BASE_URL}parks",
                params={"limit": 1, "api_key": api_key},
            )
            if response.status in (401, 403):
                return "invalid_auth"
            return None
        except Exception:
            return "connection"
