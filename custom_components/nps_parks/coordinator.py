"""DataUpdateCoordinator for nps_parks."""

from __future__ import annotations

from datetime import timedelta
from typing import TYPE_CHECKING, Any

from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .const import API_KEY, BASE_URL, DOMAIN, LOGGER
from .data import NPSParksStorage

if TYPE_CHECKING:
    from homeassistant.config_entries import ConfigEntry
    from homeassistant.core import HomeAssistant


class NPSParksCoordinator(DataUpdateCoordinator):
    """Class to manage fetching data from the NPS API."""

    def __init__(self, hass: HomeAssistant, entry: ConfigEntry) -> None:
        """Initialize the coordinator."""
        super().__init__(
            hass=hass,
            logger=LOGGER,
            name=DOMAIN,
            update_interval=timedelta(weeks=1),
        )
        self.api_key = entry.data[API_KEY]
        self.storage = NPSParksStorage(hass)

    async def _async_update_data(self) -> Any:
        """Fetch data from NPS."""
        try:
            session = async_get_clientsession(self.hass)
            params = {"limit": 500, "api_key": self.api_key}
            response = await session.get(BASE_URL, params=params)
            data = await response.json()
            return data["data"]

        except Exception as exception:
            raise UpdateFailed(exception) from exception
