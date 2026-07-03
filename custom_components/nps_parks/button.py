"""Button platform for NPS Parks."""

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
    _hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback
) -> None:
    """Set up NPS Parks button entities."""
    coordinator: NPSParksCoordinator = entry.runtime_data
    async_add_entities(
        [
            NPSParksRefreshButton(coordinator),
            NPSParksMarkSelectedVisitedButton(coordinator),
            NPSParksMarkSelectedUnvisitedButton(coordinator),
        ]
    )


class NPSParksMarkSelectedVisitedButton(NPSParksEntity, ButtonEntity):
    """Button to mark the selected park as visited."""

    _attr_name = "Mark Selected Visited"
    _attr_unique_id = "nps_parks_mark_selected_visited"
    _attr_icon = "mdi:map-marker-check"

    async def async_press(self) -> None:
        """Mark the selected park as visited."""
        code = self.coordinator.selected_park_code
        if code:
            await self.coordinator.storage.async_mark_visited(code)
            self.coordinator.async_set_updated_data(self.coordinator.data)


class NPSParksMarkSelectedUnvisitedButton(NPSParksEntity, ButtonEntity):
    """Button to mark the selected park as unvisited."""

    _attr_name = "Mark Selected Unvisited"
    _attr_unique_id = "nps_parks_mark_selected_unvisited"
    _attr_icon = "mdi:map-marker-remove"

    async def async_press(self) -> None:
        """Mark the selected park as unvisited."""
        code = self.coordinator.selected_park_code
        if code:
            await self.coordinator.storage.async_mark_unvisited(code)
            self.coordinator.async_set_updated_data(self.coordinator.data)


class NPSParksRefreshButton(NPSParksEntity, ButtonEntity):
    """Button to manually refresh NPS Parks data."""

    _attr_name = "Refresh"
    _attr_unique_id = "nps_parks_refresh"
    _attr_icon = "mdi:refresh"

    async def async_press(self) -> None:
        """Trigger a data refresh."""
        await self.coordinator.async_request_refresh()
