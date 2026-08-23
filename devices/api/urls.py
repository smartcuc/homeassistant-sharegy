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
)

urlpatterns = [
    path("", device_list),
    path("setup-options/", device_setup_options),
    path("unconfigured/", unconfigured_devices),
    path("latest/", latest_device_values),
    path("<int:device_id>/", configure_device),
    path("<int:device_id>/metrics/", device_available_metrics),
    path("<int:device_id>/timeseries/", device_timeseries),
    path("sankey/", sankey_data),
    path("homes/", list_homes),
    path("mqtt-profiles/", mqtt_profile_list),
    path("remove/", remove_devices),
    path("restore/", restore_devices),
    path("trash/", trash_devices),
    path("trash/count/", trash_count),
    path("purge/", purge_devices),
    path("dashboard/", device_dashboard_values),
]
