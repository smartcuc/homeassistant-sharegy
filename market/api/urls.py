####################
# market/api/urls.py
####################

from django.urls import path
from .views import current_spot_price, spot_price_chart, home_tariff_detail, fetch_tibber_homes_view

urlpatterns = [
    path(
        "current/",
        current_spot_price,
        name="current-spot-price",
    ),
    path(
        "chart/",
        spot_price_chart,
        name="spot-price-chart",
    ),
    path(
        "tariff/",
        home_tariff_detail,
        name="home-tariff-detail",
    ),
    path(
        "tariff/tibber-homes/",
        fetch_tibber_homes_view,
        name="fetch-tibber-homes",
    ),
]
