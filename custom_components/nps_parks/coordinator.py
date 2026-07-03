"""DataUpdateCoordinator for nps_parks."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .const import (
    API_KEY,
    BASE_URL,
    CONF_UPDATE_INTERVAL,
    DEFAULT_UPDATE_INTERVAL,
    DOMAIN,
    LOGGER,
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
            name=DOMAIN,
            update_interval=UPDATE_INTERVAL_MAP[interval_key],
        )
        self.api_key = entry.data[API_KEY]
        self.storage = NPSParksStorage(hass)
        self.tracked_park_codes: set[str] = set()

    async def _async_update_data(self) -> list[dict[str, Any]]:
        """Fetch data from NPS."""
        try:
            session = async_get_clientsession(self.hass)
            params = {"limit": 500, "api_key": self.api_key}
            response = await session.get(BASE_URL, params=params)
            data = await response.json()
            samoa = next(
                (p for p in data["data"] if "samoa" in p["fullName"].lower()), None
            )
            LOGGER.warning(
                "Samoa entry: %s | %s",
                samoa["designation"] if samoa else "not found",
                samoa["parkCode"] if samoa else "",
            )
            return data["data"]

        except Exception as exception:
            raise UpdateFailed(exception) from exception
