"""USGSWaterEntity class."""

from __future__ import annotations

from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .coordinator import USGSWaterCoordinator


class USGSWaterEntity(CoordinatorEntity[USGSWaterCoordinator]):
    """Base entity for USGS Water."""

    _attr_attribution = "Data provided by U.S. Geological Survey"

    def __init__(self, coordinator: USGSWaterCoordinator) -> None:
        """Initialize."""
        super().__init__(coordinator)
