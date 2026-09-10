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
    export_device_timeseries_view,
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
    device_switch,
    device_baseline_profile_view,
    device_baseline_learn_view,
    device_baseline_evaluate_view,
)



from devices.views import (
    device_status_list,
    mqtt_status,
    send_device_config,
    device_metrics,
)
from .views_telemetry_push import telemetry_push
from .views_profiles import (
    list_cloud_profiles_view,
    list_user_cloud_integrations_view,
    manage_user_cloud_integration_view,
    test_cloud_credentials,
    test_cloud_connection_view,
    integrate_cloud_device_view,
    poll_cloud_device_now_view,
    get_cloud_integration_status_view,
    update_cloud_polling_interval_view,
)
from .views_sungrow_oauth import sungrow_oauth_start
from .views_self_test import device_self_test_view, device_self_test_simulate_view
from .views_shelly_cloud import ShellyCloudTestView, ShellyCloudImportView


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
    path("<int:device_id>/export/", export_device_timeseries_view),
    path("<int:device_id>/export", export_device_timeseries_view),
    path("<int:device_id>/timeseries/export/", export_device_timeseries_view),
    path("<int:device_id>/simulate/", simulate_telemetry),
    path("<int:device_id>/switch/", device_switch),
    path("<int:device_id>/profile/", device_baseline_profile_view),
    path("<int:device_id>/profile/learn/", device_baseline_learn_view),
    path("<int:device_id>/profile/evaluate/", device_baseline_evaluate_view),
    # ☁️ CLOUD WECHSELRICHTER & 3RD-PARTY PROFILE (SUNGROW, SOLAREDGE, FRONIUS, KOSTAL, GROWATT)
    path("cloud-profiles/", list_cloud_profiles_view, name="device_cloud_profiles_list"),
    path("cloud-integrations/", list_user_cloud_integrations_view, name="device_cloud_integrations_list"),
    path("cloud-integrations/<uuid:integration_id>/", manage_user_cloud_integration_view, name="device_cloud_integration_manage"),
    path("cloud-profiles/test/", test_cloud_connection_view, name="device_cloud_profiles_test"),
    path("cloud-profiles/integrate/", integrate_cloud_device_view, name="device_cloud_profiles_integrate"),
    path("cloud-profiles/polling-interval/", update_cloud_polling_interval_view, name="device_cloud_polling_interval"),
    path("sungrow/auth-url/", sungrow_oauth_start, name="sungrow_oauth_start"),
    path("<int:device_id>/cloud/poll-now/", poll_cloud_device_now_view, name="device_cloud_poll_now"),
    path("<int:device_id>/cloud/status/", get_cloud_integration_status_view, name="device_cloud_status"),
    # 🧪 1-KLICK HARDWARE-SELBSTTEST & DIAGNOSE
    path("<int:device_id>/self-test/", device_self_test_view, name="device_self_test"),
    path("self-test/simulate/", device_self_test_simulate_view, name="device_self_test_simulate"),
    # ⚡ SHELLY CLOUD 1-KLICK AUTO-DISCOVERY
    path("shelly-cloud/test/", ShellyCloudTestView.as_view(), name="shelly_cloud_test"),
    path("shelly-cloud/import/", ShellyCloudImportView.as_view(), name="shelly_cloud_import"),

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
    path("telemetry/push/", telemetry_push),
]

