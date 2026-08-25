from django.urls import path
from providers.matter.api.views import (
    matter_status,
    matter_commission,
    matter_node_command,
    matter_node_delete,
    matter_telemetry_report,
    matter_simulate,
)

urlpatterns = [
    path("status/", matter_status, name="matter_status"),
    path("commission/", matter_commission, name="matter_commission"),
    path("nodes/<int:node_id>/command/", matter_node_command, name="matter_node_command"),
    path("nodes/<int:node_id>/", matter_node_delete, name="matter_node_delete"),
    path("telemetry/report/", matter_telemetry_report, name="matter_telemetry_report"),
    path("simulate/", matter_simulate, name="matter_simulate"),
]

