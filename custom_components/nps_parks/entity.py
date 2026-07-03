"""NPSParksEntity class."""

from __future__ import annotations

from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .coordinator import NPSParksCoordinator


class NPSParksEntity(CoordinatorEntity[NPSParksCoordinator]):
    """Base entity for NPS Parks."""

    _attr_attribution = "Data provided by the National Park Service"

    def __init__(self, coordinator: NPSParksCoordinator) -> None:
        """Initialize."""
        super().__init__(coordinator)
