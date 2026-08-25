#####################
# devices/api/urls.py
#####################

from django.urls import path
from .views import (
    device_setup_options,
    device_list,
    unconfigured_devices,
    latest_device_values,
    configure_device,
    device_available_metrics,
    device_timeseries,
    remove_devices,
    restore_devices,
    trash_devices,
    purge_devices,
    trash_count,
    sankey_data,
    list_homes,
    mqtt_profile_list,
    device_dashboard_values,
    simulate_telemetry,
    regenerate_mqtt_password,
)

from devices.views import (
    device_status_list,
    mqtt_status,
    send_device_config,
    device_metrics,
)

urlpatterns = [
    path("", device_list),
    path("status/", device_status_list),
    path("mqtt-status/", mqtt_status),
    path("send-config/", send_device_config),
    path("by-id/<int:device_id>/metrics/", device_metrics),
    path("setup-options/", device_setup_options),
    path("unconfigured/", unconfigured_devices),
    path("latest/", latest_device_values),
    path("<int:device_id>/", configure_device),
    path("<int:device_id>/config/", configure_device),
    path("by-id/<int:device_id>/configure/", configure_device),
    path("<int:device_id>/metrics/", device_available_metrics),
    path("<int:device_id>/timeseries/", device_timeseries),
    path("<int:device_id>/simulate/", simulate_telemetry),
    path("sankey/", sankey_data),
    path("homes/", list_homes),
    path("homes/regenerate-mqtt/", regenerate_mqtt_password),
    path("mqtt-profiles/", mqtt_profile_list),
    path("remove/", remove_devices),
    path("restore/", restore_devices),
    path("trash/", trash_devices),
    path("trash/count/", trash_count),
    path("purge/", purge_devices),
    path("dashboard/", device_dashboard_values),
]
