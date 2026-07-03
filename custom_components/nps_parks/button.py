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
    async_add_entities([NPSParksRefreshButton(coordinator)])


class NPSParksRefreshButton(NPSParksEntity, ButtonEntity):
    """Button to manually refresh NPS Parks data."""

    _attr_name = "Refresh"
    _attr_unique_id = "nps_parks_refresh"
    _attr_icon = "mdi:refresh"

    async def async_press(self) -> None:
        """Trigger a data refresh."""
        await self.coordinator.async_request_refresh()
