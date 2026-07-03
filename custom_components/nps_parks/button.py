"""Button platform for nps_parks."""

from __future__ import annotations

from typing import TYPE_CHECKING

from homeassistant.components.button import ButtonEntity

from .entity import NPSParksEntity

if TYPE_CHECKING:
    from homeassistant.config_entries import ConfigEntry
    from homeassistant.core import HomeAssistant
    from homeassistant.helpers.entity_platform import AddEntitiesCallback

    from .coordinator import NPSParksCoordinator


async def async_setup_entry(
    hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback
) -> None:
    coordinator: NPSParksCoordinator = entry.runtime_data
    async_add_entities([NPSParksRefreshButton(coordinator)])


class NPSParksRefreshButton(NPSParksEntity, ButtonEntity):
    _attr_name = "Refresh"
    _attr_unique_id = "nps_parks_refresh"
    _attr_icon = "mdi:refresh"

    async def async_press(self) -> None:
        await self.coordinator.async_request_refresh()
