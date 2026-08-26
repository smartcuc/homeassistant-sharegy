####################
# market/api/urls.py
####################

from django.urls import path
from .views import (
    current_spot_price,
    spot_price_chart,
    home_tariff_detail,
    delete_home_tariff_view,
    fetch_tibber_homes_view,
    grid_co2_view,
)

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
        "co2/",
        grid_co2_view,
        name="grid-co2",
    ),
    path(
        "tariff/",
        home_tariff_detail,
        name="home-tariff-detail",
    ),
    path(
        "tariff/<uuid:tariff_id>/",
        delete_home_tariff_view,
        name="delete-home-tariff",
    ),
    path(
        "tariff/tibber-homes/",
        fetch_tibber_homes_view,
        name="fetch-tibber-homes",
    ),
]
