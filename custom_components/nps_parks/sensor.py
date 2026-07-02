"""Sensor platform for nps_parks."""

from __future__ import annotations

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
        LOGGER.debug("Coordinator data: %s", coordinator.data["features"])

        unique_sites = set(
            f["properties"]["monitoring_location_id"]
            for f in coordinator.data["features"]
        )
        LOGGER.warning(
            "Coordinator data length: %s",
            len(coordinator.data["features"])
            if coordinator.data["features"]
            else "None",
        )
        LOGGER.warning("Unique sites: %s", unique_sites)

        async_add_entities(
            NPSParksSensor(coordinator=coordinator, site_id=site_id)
            for site_id in unique_sites
        )
    except Exception as e:
        LOGGER.error("Error setting up sensor: %s", e)
        raise


class NPSParksSensor(NPSParksEntity, SensorEntity):
    """NPS Parks sensor for a single monitoring location."""

    def __init__(self, coordinator: NPSParksCoordinator, site_id: str) -> None:
        """Initialize the sensor class."""
        super().__init__(coordinator)
        self.site_id = site_id
        self._attr_unique_id = site_id
        self._attr_name = coordinator.data["site_names"].get(site_id, site_id)
        self._attr_native_unit_of_measurement = "ft"

    @property
    def native_value(self) -> float | None:
        """Return the most recent elevation value for this site."""
        site_features = [
            f
            for f in self.coordinator.data["features"]
            if f["properties"]["monitoring_location_id"] == self.site_id
        ]
        if not site_features:
            return None
        latest = sorted(
            site_features, key=lambda f: f["properties"]["time"], reverse=True
        )[0]
        value = latest["properties"]["value"]
        if value is None:
            return None
        return float(value)
