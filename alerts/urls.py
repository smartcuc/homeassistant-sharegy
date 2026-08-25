##################
# alerts/urls.py
##################

from django.urls import path
from alerts.views import (
    alerts_list,
    acknowledge_alert,
    resolve_alert,
    seed_demo_alerts,
)

urlpatterns = [
    path("", alerts_list, name="alerts-list"),
    path("seed-demo/", seed_demo_alerts, name="alerts-seed-demo"),
    path("<uuid:alert_id>/acknowledge/", acknowledge_alert, name="alert-acknowledge"),
    path("<uuid:alert_id>/resolve/", resolve_alert, name="alert-resolve"),
]

