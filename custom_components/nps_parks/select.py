"""Select platform for nps_parks."""

from __future__ import annotations

from typing import TYPE_CHECKING

from homeassistant.components.select import SelectEntity

from .const import CONF_DESIGNATIONS, DESIGNATION_GROUP_EXCEPTIONS, DESIGNATION_GROUPS
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
        selected = entry.options.get(CONF_DESIGNATIONS, [])
        all_parks = coordinator.data

        if selected:
            included_designations: set[str] = set()
            included_exceptions: set[str] = set()
            for group in selected:
                included_designations |= DESIGNATION_GROUPS.get(group, set())
                included_exceptions |= DESIGNATION_GROUP_EXCEPTIONS.get(group, set())
            parks = [
                p
                for p in all_parks
                if p["designation"] in included_designations
                or p["parkCode"] in included_exceptions
            ]
        else:
            parks = list(all_parks)

        parks.sort(key=lambda p: p["fullName"])
        self._name_to_code: dict[str, str] = {
            p["fullName"]: p["parkCode"] for p in parks
        }
        self._attr_options = [_PLACEHOLDER] + [p["fullName"] for p in parks]

    async def async_select_option(self, option: str) -> None:
        """Store the selected park code on the coordinator."""
        self.coordinator.selected_park_code = (
            None if option == _PLACEHOLDER else self._name_to_code.get(option)
        )
        self._attr_current_option = option
        self.async_write_ha_state()
