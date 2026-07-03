"""Sensor platform for nps_parks."""

from __future__ import annotations

import re
from typing import TYPE_CHECKING

from homeassistant.components.sensor import SensorEntity

from .const import LOGGER
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

        async_add_entities(
            NPSParksSensor(coordinator=coordinator, site_data=site)  # type: ignore
            for site in coordinator.data
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
    def native_value(self) -> str | None:
        """Return "visited" or "unvisited"."""
        return "unvisited"

    @property
    def extra_state_attributes(self) -> dict:
        """Return the state attributes."""
        lat_long = self.site_data["latLong"]
        lat_match = re.search(r"lat:([-\d.]+)", lat_long)
        lon_match = re.search(r"long:([-\d.]+)", lat_long)
        latitude = float(lat_match.group(1)) if lat_match else None
        longitude = float(lon_match.group(1)) if lon_match else None
        return {
            "latitude": latitude,
            "longitude": longitude,
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
