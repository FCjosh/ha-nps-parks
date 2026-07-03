"""Storage for NPS Parks visited state."""

from __future__ import annotations

from typing import TYPE_CHECKING

from homeassistant.helpers.storage import Store

if TYPE_CHECKING:
    from homeassistant.core import HomeAssistant

STORAGE_KEY = "nps_parks.visited"
STORAGE_VERSION = 1


class NPSParksStorage:
    """Manages persistent storage of visited park state."""

    def __init__(self, hass: HomeAssistant) -> None:
        """Initialize the NPS Parks storage."""
        self._store: Store = Store(hass, STORAGE_VERSION, STORAGE_KEY)
        self._visited: set[str] = set()

    async def async_load(self) -> None:
        """Load visited state from disk."""
        data = await self._store.async_load()
        if data:
            self._visited = set(data.get("visited", []))

    def is_visited(self, park_code: str) -> bool:
        """Return True if the park has been visited."""
        return park_code in self._visited

    async def async_mark_visited(self, park_code: str) -> None:
        """Mark a park as visited and persist."""
        self._visited.add(park_code)
        await self._save()

    async def async_mark_unvisited(self, park_code: str) -> None:
        """Mark a park as unvisited and persist."""
        self._visited.discard(park_code)
        await self._save()

    async def _save(self) -> None:
        await self._store.async_save({"visited": list(self._visited)})
