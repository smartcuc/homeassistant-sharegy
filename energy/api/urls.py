####################
# energy/api/urls.py
####################

from django.urls import path
from .views_fake import fake_dashboard
from .views import (
    dashboard_me,
    configure_device,
    chart_data,
    energy_balance,
    export_energy_balance_view,
    battery_arbitrage_view,
    submeter_trends_view,
    energy_optimizer,
    battery_forecast_view,
    seed_demo_data,
    export_chart_xlsx,
    export_chart_csv,
    export_chart_pdf,
    system_setup_status_view,
    energy_profile_view,
)


urlpatterns = [
    path("fake-dashboard/", fake_dashboard),
]


from .views_grid import (
    grid_dimming_status_view,
    grid_dimming_signal_webhook,
    grid_dimming_clear_view,
    steuve_devices_config_view,
)
from .views_ocpp import (
    WallboxListCreateView,
    WallboxDetailView,
    WallboxRemoteActionView,
    WallboxSessionsView,
    RfidTagListCreateView,
    RfidTagDetailView,
)

from .views_bwwp import (
    bwwp_status_view,
    bwwp_config_view,
    bwwp_switch_view,
)
from .views_floor_heating import (
    floor_heating_status_view,
    floor_heating_config_view,
    floor_heating_boost_view,
    floor_heating_toggle_view,
)
from .views_fuel_radar import (
    fuel_radar_view,
)
from .views_dispatch_hub import (
    load_management_hub_view,
    load_management_priorities_view,
    load_management_action_view,
)

urlpatterns += [
    # ⛽ Mobilitäts- & Spritpreis-Radar (Tankerkönig / MTS-K)
    path("fuel-radar/", fuel_radar_view),
    path("mobility/fuel-radar/", fuel_radar_view),
    path("dashboard/me/", dashboard_me),
    path("balance/", energy_balance),
    path("export/balance/", export_energy_balance_view),
    path("battery-arbitrage/", battery_arbitrage_view),
    path("submeters/trends/", submeter_trends_view),
    path("optimizer/", energy_optimizer),
    # 🎛️ Zentraler Smart Load Management & Dispatch Hub
    path("load-management/hub/", load_management_hub_view),
    path("load-management/hub/priorities/", load_management_priorities_view),
    path("load-management/hub/action/", load_management_action_view),
    # ♨️ BWWP & Wärmepumpen SG-Ready Lastmanagement
    path("bwwp/", bwwp_status_view),
    path("bwwp/config/", bwwp_config_view),
    path("bwwp/switch/", bwwp_switch_view),
    # 🌡️ Fußbodenheizung & Estrich-Speicher
    path("floor-heating/", floor_heating_status_view),
    path("floor-heating/config/", floor_heating_config_view),
    path("floor-heating/boost/", floor_heating_boost_view),
    path("floor-heating/toggle/", floor_heating_toggle_view),

    path("battery-forecast/", battery_forecast_view),
    path("seed-demo/", seed_demo_data),
    path("chart/", chart_data),
    path("chart/export/xlsx/", export_chart_xlsx),
    path("chart/export/csv/", export_chart_csv),
    path("chart/export/pdf/", export_chart_pdf),
    path("devices/<int:device_id>/configure/", configure_device),
    # ⚡ § 14a EnWG Steuerbox & Dimm-Engine Routes
    path("grid/dimming/status/", grid_dimming_status_view),
    path("grid/dimming/signal/", grid_dimming_signal_webhook),
    path("grid/dimming/clear/", grid_dimming_clear_view),
    path("grid/steuve/", steuve_devices_config_view),
    # 🎯 Onboarding & System Readiness Check (Omi-Test)
    path("setup-status/", system_setup_status_view),
    # 🏡 Energie-Profil & Ersparnis-Kompass
    path("profile/", energy_profile_view),
    # 🚗 OCPP 1.6-J Wallbox & Smart-Charging Endpunkte
    path("wallboxes/", WallboxListCreateView.as_view()),
    path("wallboxes/<uuid:pk>/", WallboxDetailView.as_view()),
    path("wallboxes/<uuid:pk>/<str:action>/", WallboxRemoteActionView.as_view()),
    path("wallboxes/<uuid:pk>/sessions/", WallboxSessionsView.as_view()),
    # 💳 RFID-Tag Management Endpunkte
    path("rfid-tags/", RfidTagListCreateView.as_view()),
    path("rfid-tags/<uuid:pk>/", RfidTagDetailView.as_view()),
]

