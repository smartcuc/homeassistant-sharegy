from django.urls import path
from operations.views import system_health_status_view

urlpatterns = [
    path("health/", system_health_status_view, name="system_health_status"),
]
