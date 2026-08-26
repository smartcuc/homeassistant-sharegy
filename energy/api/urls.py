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
    submeter_trends_view,
    energy_optimizer,
    battery_forecast_view,
    battery_arbitrage_view,
    seed_demo_data,
    export_chart_xlsx,
    export_chart_csv,
    export_chart_pdf,
)

urlpatterns = [
    path("fake-dashboard/", fake_dashboard),
]


urlpatterns += [
    path("dashboard/me/", dashboard_me),
    path("balance/", energy_balance),
    path("export/balance/", export_energy_balance_view),
    path("submeters/trends/", submeter_trends_view),
    path("optimizer/", energy_optimizer),
    path("battery-forecast/", battery_forecast_view),
    path("battery-arbitrage/", battery_arbitrage_view),
    path("seed-demo/", seed_demo_data),
    path("chart/", chart_data),
    path("chart/export/xlsx/", export_chart_xlsx),
    path("chart/export/csv/", export_chart_csv),
    path("chart/export/pdf/", export_chart_pdf),
    path("devices/<int:device_id>/configure/", configure_device),
]
