"""Constants for usgs_water."""

from logging import Logger, getLogger

LOGGER: Logger = getLogger(__package__)

DOMAIN = "usgs_water"
CONF_RADIUS = "radius"
ATTRIBUTION = "Data provided by http://jsonplaceholder.typicode.com/"
USGS_PARAMETER_CODE = "62614"
BASE_URL = "https://api.waterdata.usgs.gov/ogcapi/v0/collections/daily/items"
