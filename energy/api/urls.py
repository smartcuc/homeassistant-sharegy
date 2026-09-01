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

urlpatterns += [
    path("dashboard/me/", dashboard_me),
    path("balance/", energy_balance),
    path("export/balance/", export_energy_balance_view),
    path("battery-arbitrage/", battery_arbitrage_view),
    path("submeters/trends/", submeter_trends_view),
    path("optimizer/", energy_optimizer),
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
]
