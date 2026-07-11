"""Select platform for nps_parks."""

from __future__ import annotations

from typing import TYPE_CHECKING

from homeassistant.components.select import SelectEntity

from .const import CONF_DESIGNATIONS
from .designations import filter_parks
from .entity import NPSParksEntity

if TYPE_CHECKING:
    from homeassistant.config_entries import ConfigEntry
    from homeassistant.core import HomeAssistant
    from homeassistant.helpers.entity_platform import AddEntitiesCallback

    from .coordinator import NPSParksCoordinator

_PLACEHOLDER = "— Select a park —"


async def async_setup_entry(
    _hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up NPS Parks select entity."""
    coordinator: NPSParksCoordinator = entry.runtime_data
    async_add_entities([NPSParkSelectEntity(coordinator, entry)])


class NPSParkSelectEntity(NPSParksEntity, SelectEntity):
    """Searchable dropdown for selecting a park to mark visited/unvisited."""

    _attr_name = "Select Park"
    _attr_unique_id = "nps_parks_select"
    _attr_icon = "mdi:map-search"
    _attr_current_option = _PLACEHOLDER

    def __init__(self, coordinator: NPSParksCoordinator, entry: ConfigEntry) -> None:
        """Initialize the park select entity."""
        super().__init__(coordinator)
        self._selected_groups = entry.options.get(CONF_DESIGNATIONS, [])

    def _parks(self) -> list[dict]:
        """Return the currently tracked parks, filtered and sorted by name."""
        parks = filter_parks(self.coordinator.data, self._selected_groups)
        parks.sort(key=lambda p: p["fullName"])
        return parks

    @property
    def options(self) -> list[str]:
        """Return the current list of selectable park names."""
        return [_PLACEHOLDER] + [p["fullName"] for p in self._parks()]

    async def async_select_option(self, option: str) -> None:
        """Store the selected park code on the coordinator."""
        name_to_code = {p["fullName"]: p["parkCode"] for p in self._parks()}
        self.coordinator.selected_park_code = (
            None if option == _PLACEHOLDER else name_to_code.get(option)
        )
        self._attr_current_option = option
        self.async_write_ha_state()
