"""Custom integration to integrate USGS Water with Home Assistant."""

from __future__ import annotations

from typing import TYPE_CHECKING

from homeassistant.const import Platform

from .const import DOMAIN, LOGGER
from .coordinator import USGSWaterCoordinator

if TYPE_CHECKING:
    from homeassistant.config_entries import ConfigEntry
    from homeassistant.core import HomeAssistant

PLATFORMS: list[Platform] = [Platform.SENSOR]


# https://developers.home-assistant.io/docs/config_entries_index/#setting-up-an-entry
async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
) -> bool:
    """Set up USGS Water from a config entry."""
    coordinator = USGSWaterCoordinator(hass=hass, entry=entry)
    await coordinator.async_config_entry_first_refresh()
    entry.runtime_data = coordinator
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    return True


async def async_unload_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
) -> bool:
    """Handle removal of an entry."""
    return await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
