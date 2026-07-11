"""Services for NPS Parks."""

from __future__ import annotations

from typing import TYPE_CHECKING

import voluptuous as vol
from homeassistant.helpers import config_validation as cv

from .const import DOMAIN, LOGGER

if TYPE_CHECKING:
    from collections.abc import Callable, Coroutine

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

    def make_handler(*, visited: bool) -> Callable[[ServiceCall], Coroutine]:
        mark = (
            coordinator.storage.async_mark_visited
            if visited
            else coordinator.storage.async_mark_unvisited
        )
        label = "visited" if visited else "unvisited"

        async def handle(call: ServiceCall) -> None:
            park_code = call.data["park_code"]
            await mark(park_code)
            coordinator.async_set_updated_data(coordinator.data)
            LOGGER.debug("Marked %s as %s", park_code, label)

        return handle

    hass.services.async_register(
        DOMAIN,
        SERVICE_MARK_VISITED,
        make_handler(visited=True),
        schema=SERVICE_SCHEMA,
    )
    hass.services.async_register(
        DOMAIN,
        SERVICE_MARK_UNVISITED,
        make_handler(visited=False),
        schema=SERVICE_SCHEMA,
    )


def async_unload_services(hass: HomeAssistant) -> None:
    """Remove NPS Parks services."""
    hass.services.async_remove(DOMAIN, SERVICE_MARK_VISITED)
    hass.services.async_remove(DOMAIN, SERVICE_MARK_UNVISITED)
