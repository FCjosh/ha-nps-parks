"""DataUpdateCoordinator for usgs_water."""

from __future__ import annotations

import math
from datetime import date, timedelta
from typing import TYPE_CHECKING, Any

from homeassistant.const import CONF_LATITUDE, CONF_LONGITUDE
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .const import BASE_URL, CONF_RADIUS, DOMAIN, LOGGER, USGS_PARAMETER_CODE

if TYPE_CHECKING:
    from homeassistant.config_entries import ConfigEntry
    from homeassistant.core import HomeAssistant

MONITORING_LOCATION_URL = (
    "https://api.waterdata.usgs.gov/ogcapi/v0/collections/monitoring-locations/items"
)


class USGSWaterCoordinator(DataUpdateCoordinator):
    """Class to manage fetching data from the USGS API."""

    def __init__(self, hass: HomeAssistant, entry: ConfigEntry) -> None:
        """Initialize the coordinator."""
        super().__init__(
            hass=hass,
            logger=LOGGER,
            name=DOMAIN,
            update_interval=timedelta(minutes=60),
        )
        self.lat = entry.data[CONF_LATITUDE]
        self.lon = entry.data[CONF_LONGITUDE]
        self.radius = entry.data[CONF_RADIUS]

    async def _async_update_data(self) -> Any:
        """Fetch data from USGS."""
        lat_delta = self.radius / 69
        lon_delta = self.radius / (69 * math.cos(math.radians(self.lat)))

        min_lat = self.lat - lat_delta
        max_lat = self.lat + lat_delta
        min_lon = self.lon - lon_delta
        max_lon = self.lon + lon_delta

        today = date.today()
        thirty_days_ago = today - timedelta(days=30)
        datetime_param = f"{thirty_days_ago}/{today}"

        try:
            session = async_get_clientsession(self.hass)

            # Fetch water level readings
            params = {
                "f": "json",
                "bbox": f"{min_lon:.4f},{min_lat:.4f},{max_lon:.4f},{max_lat:.4f}",
                "parameter_code": USGS_PARAMETER_CODE,
                "datetime": datetime_param,
                "limit": 100,
            }
            response = await session.get(BASE_URL, params=params)
            data = await response.json()
            features = data["features"]

            # Fetch human-readable names for each unique site
            unique_ids = set(
                f["properties"]["monitoring_location_id"] for f in features
            )
            site_names = {}
            for site_id in unique_ids:
                resp = await session.get(
                    f"{MONITORING_LOCATION_URL}/{site_id}",
                    params={"f": "json"},
                )
                location = await resp.json()
                site_names[site_id] = location["properties"][
                    "monitoring_location_name"
                ].title()

            return {"features": features, "site_names": site_names}

        except Exception as exception:
            raise UpdateFailed(exception) from exception
