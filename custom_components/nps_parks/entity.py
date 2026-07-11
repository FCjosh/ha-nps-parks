"""NPSParksEntity class."""

from __future__ import annotations

from typing import TYPE_CHECKING

from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN

if TYPE_CHECKING:
    from .coordinator import NPSParksCoordinator


class NPSParksEntity(CoordinatorEntity["NPSParksCoordinator"]):
    """Base entity for NPS Parks."""

    _attr_attribution = "Data provided by the National Park Service"
    _attr_has_entity_name = True

    def __init__(self, coordinator: NPSParksCoordinator) -> None:
        """Initialize the NPS Parks entity."""
        super().__init__(coordinator)

    @property
    def device_info(self) -> DeviceInfo:
        """Return device info."""
        return DeviceInfo(
            identifiers={(DOMAIN, DOMAIN)},
            name="NPS Parks",
            manufacturer="National Park Service",
            configuration_url="https://www.nps.gov",
        )
