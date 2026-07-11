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
