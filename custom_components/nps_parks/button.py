"""Button platform for NPS Parks."""

from __future__ import annotations

from typing import TYPE_CHECKING, ClassVar

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
            NPSParksMarkSelectedButton(coordinator, visited=True),
            NPSParksMarkSelectedButton(coordinator, visited=False),
        ]
    )


class NPSParksMarkSelectedButton(NPSParksEntity, ButtonEntity):
    """Button to mark the selected park as visited or unvisited."""

    BUTTON_CONFIG: ClassVar[dict[bool, tuple[str, str, str]]] = {
        True: (
            "Mark Selected Visited",
            "nps_parks_mark_selected_visited",
            "mdi:map-marker-check",
        ),
        False: (
            "Mark Selected Unvisited",
            "nps_parks_mark_selected_unvisited",
            "mdi:map-marker-remove",
        ),
    }

    def __init__(self, coordinator: NPSParksCoordinator, *, visited: bool) -> None:
        """Initialize the mark-selected button."""
        super().__init__(coordinator)
        self._visited = visited
        name, unique_id, icon = self.BUTTON_CONFIG[visited]
        self._attr_name = name
        self._attr_unique_id = unique_id
        self._attr_icon = icon

    async def async_press(self) -> None:
        """Mark the selected park as visited or unvisited."""
        code = self.coordinator.selected_park_code
        if not code:
            return
        if self._visited:
            await self.coordinator.storage.async_mark_visited(code)
        else:
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
