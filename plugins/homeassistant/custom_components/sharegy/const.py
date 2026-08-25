"""Constants for the Sharegy HEMS integration."""

DOMAIN = "sharegy"

CONF_HOST = "host"
CONF_API_KEY = "api_key"
CONF_SCAN_INTERVAL = "scan_interval"

DEFAULT_NAME = "Sharegy HEMS"
DEFAULT_SCAN_INTERVAL = 10  # seconds

ENDPOINT_DASHBOARD = "/api/energy/dashboard/me/"
ENDPOINT_BALANCE = "/api/energy/balance/?period=today"
ENDPOINT_OPTIMIZER = "/api/energy/optimizer/"
ENDPOINT_TELEMETRY_PUSH = "/api/devices/telemetry/push/"

