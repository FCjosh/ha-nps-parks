"""Services for NPS Parks."""

from __future__ import annotations

from typing import TYPE_CHECKING

import voluptuous as vol
from homeassistant.helpers import config_validation as cv

from .const import DOMAIN, LOGGER

if TYPE_CHECKING:
    from homeassistant.core import HomeAssistant, ServiceCall

    from .coordinator import NPSParksCoordinator

SERVICE_MARK_VISITED = "mark_visited"
SERVICE_MARK_UNVISITED = "mark_unvisited"

SERVICE_SCHEMA = vol.Schema(
    {
        vol.Required("park_code"): cv.string,
    }
)


async def async_setup_services(
    hass: HomeAssistant, coordinator: NPSParksCoordinator
) -> None:
    """Register NPS Parks services."""

    async def handle_mark_visited(call: ServiceCall) -> None:
        park_code = call.data["park_code"]
        await coordinator.storage.async_mark_visited(park_code)
        coordinator.async_set_updated_data(coordinator.data)
        LOGGER.debug("Marked %s as visited", park_code)

    async def handle_mark_unvisited(call: ServiceCall) -> None:
        park_code = call.data["park_code"]
        await coordinator.storage.async_mark_unvisited(park_code)
        coordinator.async_set_updated_data(coordinator.data)
        LOGGER.debug("Marked %s as unvisited", park_code)

    hass.services.async_register(
        DOMAIN, SERVICE_MARK_VISITED, handle_mark_visited, schema=SERVICE_SCHEMA
    )
    hass.services.async_register(
        DOMAIN, SERVICE_MARK_UNVISITED, handle_mark_unvisited, schema=SERVICE_SCHEMA
    )


def async_unload_services(hass: HomeAssistant) -> None:
    """Remove NPS Parks services."""
    hass.services.async_remove(DOMAIN, SERVICE_MARK_VISITED)
    hass.services.async_remove(DOMAIN, SERVICE_MARK_UNVISITED)
