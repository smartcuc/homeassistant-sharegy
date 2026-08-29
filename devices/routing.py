####################
# devices/routing.py
####################

from django.urls import path, re_path
from .consumers import EnergyConsumer

websocket_urlpatterns = [
    path("ws/energy/", EnergyConsumer.as_asgi()),
    re_path(r"^ws/energy/(?P<token>[\w-]+)/?$", EnergyConsumer.as_asgi()),
]

