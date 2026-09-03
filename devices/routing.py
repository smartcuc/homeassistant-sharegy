####################
# devices/routing.py
####################

from django.urls import path, re_path
from .consumers import EnergyConsumer
from .consumers_ocpp import OcppConsumer

websocket_urlpatterns = [
    # OCPP 1.6-J / 2.0.1 Wallbox Routes
    re_path(r"^ocpp/(?P<cp_id>[\w-]+)/?$", OcppConsumer.as_asgi()),
    re_path(r"^ws/ocpp/(?P<cp_id>[\w-]+)/?$", OcppConsumer.as_asgi()),

    # Shelly & Home Assistant Outbound Routes
    re_path(r"^ws/energy/(?P<token>[\w-]+)/.*$", EnergyConsumer.as_asgi()),
    re_path(r"^ws/energy/(?P<token>[\w-]+)/?$", EnergyConsumer.as_asgi()),
    re_path(r"^ws/energy/?.*$", EnergyConsumer.as_asgi()),
    re_path(r"^ws/shelly/(?P<token>[\w-]+)/?$", EnergyConsumer.as_asgi()),
    re_path(r"^ws/shelly/?.*$", EnergyConsumer.as_asgi()),
    path("ws/energy/", EnergyConsumer.as_asgi()),
]
