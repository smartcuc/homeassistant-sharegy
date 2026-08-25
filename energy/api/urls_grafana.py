###############################
# energy/api/urls_grafana.py
###############################

from django.urls import path
from energy.api.views_grafana import (
    grafana_root,
    grafana_search,
    grafana_query,
    grafana_annotations,
)

urlpatterns = [
    path("", grafana_root, name="grafana_root"),
    path("search", grafana_search, name="grafana_search"),
    path("query", grafana_query, name="grafana_query"),
    path("annotations", grafana_annotations, name="grafana_annotations"),
]

