"""Constants for the Sharegy HEMS integration."""

DOMAIN = "sharegy"

CONF_HOST = "host"
CONF_API_KEY = "api_key"
CONF_SCAN_INTERVAL = "scan_interval"
CONF_BIDIRECTIONAL_ENABLED = "bidirectional_enabled"

DEFAULT_NAME = "Sharegy HEMS"
DEFAULT_HOST = "https://sharegy.de"
DEFAULT_SCAN_INTERVAL = 10  # seconds
DEFAULT_BIDIRECTIONAL_ENABLED = True

# API Endpoints
ENDPOINT_DASHBOARD = "/api/energy/dashboard/me/"
ENDPOINT_BALANCE = "/api/energy/balance/?period=today"
ENDPOINT_OPTIMIZER = "/api/energy/optimizer/"
ENDPOINT_TELEMETRY_PUSH = "/api/devices/telemetry/push/"

# Smart Load & Heating Control Endpoints (Bidirectional)
ENDPOINT_FLOOR_HEATING = "/api/energy/floor-heating/"
ENDPOINT_FLOOR_HEATING_CONFIG = "/api/energy/floor-heating/config/"
ENDPOINT_FLOOR_HEATING_BOOST = "/api/energy/floor-heating/boost/"
ENDPOINT_FLOOR_HEATING_TOGGLE = "/api/energy/floor-heating/toggle/"

ENDPOINT_BWWP = "/api/energy/bwwp/"
ENDPOINT_BWWP_CONFIG = "/api/energy/bwwp/config/"
ENDPOINT_BWWP_SWITCH = "/api/energy/bwwp/switch/"
