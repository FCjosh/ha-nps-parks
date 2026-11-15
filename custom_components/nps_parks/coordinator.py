"""DataUpdateCoordinator for nps_parks."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

import aiohttp
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .const import (
    API_KEY,
    BASE_URL,
    CONF_UPDATE_INTERVAL,
    DEFAULT_UPDATE_INTERVAL,
    DOMAIN,
    LOGGER,
    REQUEST_TIMEOUT,
    UPDATE_INTERVAL_MAP,
)
from .data import NPSParksStorage

if TYPE_CHECKING:
    from homeassistant.config_entries import ConfigEntry
    from homeassistant.core import HomeAssistant


class NPSParksCoordinator(DataUpdateCoordinator[list[dict[str, Any]]]):
    """Class to manage fetching data from the NPS API."""

    def __init__(self, hass: HomeAssistant, entry: ConfigEntry) -> None:
        """Initialize the NPS Parks coordinator."""
        interval_key = entry.options.get(CONF_UPDATE_INTERVAL, DEFAULT_UPDATE_INTERVAL)
        super().__init__(
            hass=hass,
            logger=LOGGER,
            config_entry=entry,
            name=DOMAIN,
            update_interval=UPDATE_INTERVAL_MAP[interval_key],
        )
        self.api_key = entry.data[API_KEY]
        self.storage = NPSParksStorage(hass)
        self.tracked_park_codes: set[str] = set()
        self.selected_park_code: str | None = None

    async def _async_update_data(self) -> list[dict[str, Any]]:
        """Fetch data from NPS."""
        session = async_get_clientsession(self.hass)
        params = {"limit": 500, "api_key": self.api_key}
        try:
            async with session.get(
                BASE_URL,
                params=params,
                timeout=aiohttp.ClientTimeout(total=REQUEST_TIMEOUT),
            ) as response:
                if response.status in (401, 403):
                    msg = f"NPS API rejected the API key (HTTP {response.status})"
                    raise UpdateFailed(msg)
                if not response.ok:
                    msg = f"NPS API returned HTTP {response.status} {response.reason}"
                    raise UpdateFailed(msg)
                payload = await response.json(content_type=None)
        except TimeoutError as exception:
            msg = f"Timed out after {REQUEST_TIMEOUT}s waiting for the NPS API"
            raise UpdateFailed(msg) from exception
        except aiohttp.ClientError as exception:
            msg = f"Error communicating with the NPS API: {exception}"
            raise UpdateFailed(msg) from exception
        except ValueError as exception:
            msg = "NPS API returned a response that was not valid JSON"
            raise UpdateFailed(msg) from exception

        if not isinstance(payload, dict) or not isinstance(payload.get("data"), list):
            msg = "NPS API response did not contain a 'data' list"
            raise UpdateFailed(msg)
        return payload["data"]
