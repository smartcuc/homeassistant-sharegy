"""Constants for the Sharegy Cloud Energy Bridge integration."""

DOMAIN = "sharegy"
VERSION = "2.2.0"

# Configuration Keys
CONF_HOST = "host"
CONF_WS_URL = "ws_url"
CONF_HOME_TOKEN = "home_token"
CONF_PROTOCOL = "protocol"
CONF_BIDIRECTIONAL_ENABLED = "bidirectional_enabled"

# EMS Core Selectors
CONF_GRID_POWER_SENSOR = "grid_power_sensor"
CONF_PV_POWER_SENSOR = "pv_power_sensor"
CONF_BATTERY_POWER_SENSOR = "battery_power_sensor"
CONF_BATTERY_SOC_SENSOR = "battery_soc_sensor"
CONF_LOAD_POWER_SENSOR = "load_power_sensor"

# 1. BWWP (Brauchwasserwärmepumpe) Device Bundle
CONF_BWWP_NAME = "bwwp_name"
CONF_BWWP_POWER = "bwwp_power"
CONF_BWWP_TEMP = "bwwp_temp"
CONF_BWWP_SWITCH = "bwwp_switch"

# 2. Heatpump (Wärmepumpe) Device Bundle
CONF_HEATPUMP_NAME = "heatpump_name"
CONF_HEATPUMP_POWER = "heatpump_power"
CONF_HEATPUMP_TEMP = "heatpump_temp"
CONF_HEATPUMP_SWITCH = "heatpump_switch"

# 3. Floor Heating (Fußbodenheizung & Estrich-Speicher) Device Bundle
CONF_FLOOR_HEATING_NAME = "floor_heating_name"
CONF_FLOOR_HEATING_POWER = "floor_heating_power"
CONF_FLOOR_HEATING_ROOM_TEMP = "floor_heating_room_temp"
CONF_FLOOR_HEATING_FLOW_TEMP = "floor_heating_flow_temp"
CONF_FLOOR_HEATING_FLOOR_TEMP = "floor_heating_floor_temp"
CONF_FLOOR_HEATING_SWITCH = "floor_heating_switch"
CONF_FLOOR_HEATING_FLOW_SETPOINT = "floor_heating_flow_setpoint"
CONF_FLOOR_HEATING_TARGET_ROOM_TEMP = "floor_heating_target_room_temp"
CONF_FLOOR_HEATING_BOOST_DELTA_K = "floor_heating_boost_delta_k"
CONF_FLOOR_HEATING_MAX_FLOOR_TEMP = "floor_heating_max_floor_temp"

# 4. Wallbox (EV Charger) Device Bundle
CONF_WALLBOX_NAME = "wallbox_name"
CONF_WALLBOX_POWER = "wallbox_power"
CONF_WALLBOX_SWITCH = "wallbox_switch"

# 5. Other Submeters / Sensors
CONF_SUBMETER_SENSORS = "submeter_sensors"

# Buffer & Sync Options
CONF_SYNC_INTERVAL = "sync_interval"
CONF_OFFLINE_BUFFER_MAX_HOURS = "offline_buffer_max_hours"

DEFAULT_HOST = "https://sharegy.de"
DEFAULT_WS_URL = "wss://sharegy.de/ws/energy/"
DEFAULT_PROTOCOL = "websocket"
DEFAULT_SYNC_INTERVAL = 5  # Seconds
DEFAULT_OFFLINE_BUFFER_MAX_HOURS = 48
DEFAULT_BIDIRECTIONAL_ENABLED = True
DEFAULT_FBH_TARGET_ROOM_TEMP = 21.0
DEFAULT_FBH_BOOST_DELTA_K = 1.0
DEFAULT_FBH_MAX_FLOOR_TEMP = 24.5

