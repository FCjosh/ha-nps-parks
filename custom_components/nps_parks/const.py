"""Constants for nps_parks."""

from datetime import timedelta
from logging import Logger, getLogger

LOGGER: Logger = getLogger(__package__)

DOMAIN = "nps_parks"
API_KEY = "api_key"
BASE_URL = "https://developer.nps.gov/api/v1/parks"

CONF_UPDATE_INTERVAL = "update_interval"
CONF_DESIGNATIONS = "designations"

UPDATE_INTERVAL_OPTIONS = ["hourly", "twice_daily", "daily", "weekly", "monthly"]

UPDATE_INTERVAL_MAP = {
    "hourly": timedelta(hours=1),
    "twice_daily": timedelta(hours=12),
    "daily": timedelta(days=1),
    "weekly": timedelta(weeks=1),
    "monthly": timedelta(days=30),
}

DEFAULT_UPDATE_INTERVAL = "weekly"

DESIGNATION_GROUPS: dict[str, set[str]] = {
    "National Park": {
        "National Park",
        "National Park & Preserve",
        "National Parks",
        "National and State Parks",
    },
    "National Monument": {
        "National Monument",
        "National Monument & Preserve",
        "National Monument and Historic Shrine",
        "Part of Statue of Liberty National Monument",
    },
    "National Historical Park / Historic Site": {
        "National Historic Site",
        "National Historical Park",
        "National Historical Park and Ecological Preserve",
        "National Historical Park and Preserve",
        "National Historical Reserve",
        "National Historic Area",
        "National Historic Trail",
        "National Monument and Historic Shrine",
        "Part of Colonial National Historical Park",
        "Part of Statue of Liberty National Monument",
        "International Historic Site",
        "Ecological & Historic Preserve",
    },
    "National Recreation Area": {
        "National Recreation Area",
        "National River & Recreation Area",
    },
    "National Memorial": {
        "National Memorial",
        "Memorial",
        "Memorial Parkway",
    },
    "National Battlefield": {
        "National Battlefield",
        "National Battlefield Park",
        "National Battlefield Site",
        "National Military Park",
    },
    "National Seashore": {
        "National Seashore",
    },
    "National Parkway": {
        "National Parkway",
        "Parkway",
        "Memorial Parkway",
    },
    "National Preserve": {
        "National Preserve",
        "National Park & Preserve",
        "National Monument & Preserve",
        "National Historical Park and Preserve",
        "National Historical Park and Ecological Preserve",
        "Ecological & Historic Preserve",
    },
    "National Lakeshore": {
        "National Lakeshore",
    },
    "National Trail": {
        "National Scenic Trail",
        "National Geologic Trail",
        "National Historic Trail",
    },
    "National River / Waterway": {
        "National River",
        "National Scenic River",
        "National Scenic Riverway",
        "National Scenic Riverways",
        "National Recreational River",
        "National Wild and Scenic River",
        "Wild & Scenic River",
        "Wild River",
        "Scenic & Recreational River",
        "National River & Recreation Area",
    },
    "International": {
        "International Historic Site",
        "International Park",
    },
    "Other": {
        "Affiliated Area",
        "National Reserve",
        "National Historical Reserve",
        "Park",
        "",
    },
}

# Park codes that belong to a group despite having no designation in the API
DESIGNATION_GROUP_EXCEPTIONS: dict[str, set[str]] = {
    "National Park": {"npsa"},
}

NPS_DESIGNATIONS = list(DESIGNATION_GROUPS.keys())
