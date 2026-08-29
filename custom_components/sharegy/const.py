"""Constants for the Sharegy Cloud Energy Bridge integration."""

DOMAIN = "sharegy"

# Configuration Keys
CONF_HOST = "host"
CONF_HOME_TOKEN = "home_token"
CONF_PROTOCOL = "protocol"  # "websocket" or "rest"

# Entity Role Selectors
CONF_GRID_POWER_SENSOR = "grid_power_sensor"
CONF_GRID_ENERGY_SENSOR = "grid_energy_sensor"
CONF_PV_POWER_SENSOR = "pv_power_sensor"
CONF_PV_ENERGY_SENSOR = "pv_energy_sensor"
CONF_BATTERY_POWER_SENSOR = "battery_power_sensor"
CONF_BATTERY_SOC_SENSOR = "battery_soc_sensor"
CONF_LOAD_POWER_SENSOR = "load_power_sensor"
CONF_SUBMETER_SENSORS = "submeter_sensors"

# Buffer & Sync Options
CONF_SYNC_INTERVAL = "sync_interval"
CONF_OFFLINE_BUFFER_MAX_HOURS = "offline_buffer_max_hours"

DEFAULT_HOST = "https://sharegy.de"
DEFAULT_WS_HOST = "wss://sharegy.de"
DEFAULT_PROTOCOL = "websocket"
DEFAULT_SYNC_INTERVAL = 5  # Seconds
DEFAULT_OFFLINE_BUFFER_MAX_HOURS = 48  # 48 hours local store & forward
