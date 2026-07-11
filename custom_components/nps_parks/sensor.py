"""Sensor platform for nps_parks."""

from __future__ import annotations

import re
from typing import TYPE_CHECKING, Any, ClassVar

from homeassistant.components.sensor import SensorEntity, SensorStateClass
from homeassistant.helpers import entity_registry as er

from .const import CONF_DESIGNATIONS
from .designations import filter_parks
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
    coordinator: NPSParksCoordinator = entry.runtime_data
    selected = entry.options.get(CONF_DESIGNATIONS, [])

    all_parks = coordinator.data
    tracked_parks = filter_parks(all_parks, selected)
    included = {p["parkCode"] for p in tracked_parks}
    excluded = {p["parkCode"] for p in all_parks} - included

    coordinator.tracked_park_codes = included

    if excluded:
        registry = er.async_get(hass)
        for entity_entry in er.async_entries_for_config_entry(registry, entry.entry_id):
            if entity_entry.unique_id in excluded:
                registry.async_remove(entity_entry.entity_id)

    entities = [
        NPSParksSensor(coordinator=coordinator, site_data=site)
        for site in tracked_parks
    ]
    entities += [
        NPSParksStatsSensor(coordinator, stat)
        for stat in NPSParksStatsSensor.STAT_CONFIG
    ]
    async_add_entities(entities)


class NPSParksSensor(NPSParksEntity, SensorEntity):
    """NPS Parks sensor for a single monitoring location."""

    _attr_has_entity_name = False

    def __init__(
        self, coordinator: NPSParksCoordinator, site_data: dict[str, Any]
    ) -> None:
        """Initialize the sensor class."""
        super().__init__(coordinator)
        self._park_code: str = site_data["parkCode"]
        self._attr_unique_id = self._park_code
        self._attr_name = site_data["fullName"]

    @property
    def site_data(self) -> dict[str, Any]:
        """Return this park's current data from the coordinator."""
        return next(
            (p for p in self.coordinator.data if p["parkCode"] == self._park_code),
            {},
        )

    @property
    def native_value(self) -> str:
        """Return the sensor value."""
        return (
            "visited"
            if self.coordinator.storage.is_visited(self._park_code)
            else "unvisited"
        )

    @property
    def extra_state_attributes(self) -> dict:
        """Return the state attributes."""
        site_data = self.site_data
        lat_long = site_data.get("latLong", "")
        lat_match = re.search(r"lat:([-\d.]+)", lat_long)
        lon_match = re.search(r"long:([-\d.]+)", lat_long)
        images = site_data.get("images") or []
        return {
            "park_code": self._park_code,
            "latitude": float(lat_match.group(1)) if lat_match else None,
            "longitude": float(lon_match.group(1)) if lon_match else None,
            "description": site_data.get("description"),
            "designation": site_data.get("designation"),
            "states": site_data.get("states"),
            "url": site_data.get("url"),
            "image": {
                "url": images[0]["url"],
                "credit": images[0]["credit"],
                "alt_text": images[0]["altText"],
                "caption": images[0]["caption"],
            }
            if images
            else None,
        }


class NPSParksStatsSensor(NPSParksEntity, SensorEntity):
    """Sensor for aggregate stats."""

    _attr_state_class = SensorStateClass.MEASUREMENT
    STAT_CONFIG: ClassVar[dict[str, tuple[str, str, str]]] = {
        "total": ("Total Parks", "mdi:forest", "parks"),
        "visited": ("Parks Visited", "mdi:check-circle", "parks"),
        "unvisited": ("Parks Remaining", "mdi:circle-outline", "parks"),
        "percentage": ("Percentage Visited", "mdi:percent", "%"),
    }

    def __init__(self, coordinator: NPSParksCoordinator, stat: str) -> None:
        """Initialize the stats sensor."""
        super().__init__(coordinator)
        self._stat = stat
        name, icon, unit = self.STAT_CONFIG[stat]
        self._attr_unique_id = f"nps_parks_stats_{stat}"
        self._attr_name = name
        self._attr_icon = icon
        self._attr_native_unit_of_measurement = unit

    @property
    def native_value(self) -> float:
        """Return the current statistic value."""
        parks = [
            p
            for p in self.coordinator.data
            if p["parkCode"] in self.coordinator.tracked_park_codes
        ]
        total = len(parks)
        visited = sum(
            1 for p in parks if self.coordinator.storage.is_visited(p["parkCode"])
        )
        values = {
            "total": total,
            "visited": visited,
            "unvisited": total - visited,
            "percentage": round(visited / total * 100, 1) if total else 0.0,
        }
        return values[self._stat]
