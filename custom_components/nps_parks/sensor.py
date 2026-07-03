"""Sensor platform for nps_parks."""

from __future__ import annotations

import re
from typing import TYPE_CHECKING

from homeassistant.components.sensor import SensorEntity
from homeassistant.helpers import entity_registry as er

from .const import (
    CONF_DESIGNATIONS,
    DESIGNATION_GROUP_EXCEPTIONS,
    DESIGNATION_GROUPS,
    LOGGER,
)
from .entity import NPSParksEntity

if TYPE_CHECKING:
    from homeassistant.config_entries import ConfigEntry
    from homeassistant.core import HomeAssistant
    from homeassistant.helpers.entity_platform import AddEntitiesCallback

    from .coordinator import NPSParksCoordinator


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the sensor platform."""
    try:
        coordinator: NPSParksCoordinator = entry.runtime_data
        selected = entry.options.get(CONF_DESIGNATIONS, [])

        all_parks = coordinator.data
        if selected:
            included_designations: set[str] = set()
            included_exceptions: set[str] = set()
            for group in selected:
                included_designations |= DESIGNATION_GROUPS.get(group, set())
                included_exceptions |= DESIGNATION_GROUP_EXCEPTIONS.get(group, set())

            included = {
                p["parkCode"]
                for p in all_parks
                if p["designation"] in included_designations
                or p["parkCode"] in included_exceptions
            }
            excluded = {p["parkCode"] for p in all_parks} - included
        else:
            included = {p["parkCode"] for p in all_parks}
            excluded = set()

        if excluded:
            registry = er.async_get(hass)
            for entity_entry in er.async_entries_for_config_entry(
                registry, entry.entry_id
            ):
                if entity_entry.unique_id in excluded:
                    registry.async_remove(entity_entry.entity_id)

        async_add_entities(
            NPSParksSensor(coordinator=coordinator, site_data=site)
            for site in all_parks
            if site["parkCode"] in included
        )
    except Exception as e:
        LOGGER.error("Error setting up sensor: %s", e)
        raise


class NPSParksSensor(NPSParksEntity, SensorEntity):
    """NPS Parks sensor for a single monitoring location."""

    def __init__(self, coordinator: NPSParksCoordinator, site_data: dict) -> None:
        """Initialize the sensor class."""
        super().__init__(coordinator)
        self._attr_unique_id = site_data["parkCode"]
        self._attr_name = site_data["fullName"]
        self.site_data = site_data

    @property
    def native_value(self) -> str:
        return (
            "visited"
            if self.coordinator.storage.is_visited(self._attr_unique_id)
            else "unvisited"
        )

    @property
    def extra_state_attributes(self) -> dict:
        """Return the state attributes."""
        lat_long = self.site_data["latLong"]
        lat_match = re.search(r"lat:([-\d.]+)", lat_long)
        lon_match = re.search(r"long:([-\d.]+)", lat_long)
        return {
            "latitude": float(lat_match.group(1)) if lat_match else None,
            "longitude": float(lon_match.group(1)) if lon_match else None,
            "description": self.site_data["description"],
            "designation": self.site_data["designation"],
            "states": self.site_data["states"],
            "url": self.site_data["url"],
            "image": {
                "url": self.site_data["images"][0]["url"],
                "credit": self.site_data["images"][0]["credit"],
                "alt_text": self.site_data["images"][0]["altText"],
                "caption": self.site_data["images"][0]["caption"],
            }
            if self.site_data["images"]
            else None,
        }
