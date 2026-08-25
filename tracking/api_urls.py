######################
# tracking/api_urls.py
######################

from django.urls import path
from .api import (
    TrackEventView,
    TrackEventBatchView,
    KPIView,
    FunnelView
)

urlpatterns = [
    path("", TrackEventView.as_view()),
    path("track/", TrackEventView.as_view()),
    path("track/batch/", TrackEventBatchView.as_view()),
    path("batch/", TrackEventBatchView.as_view()),
    path("stats/", KPIView.as_view()),
    path("kpis/", KPIView.as_view()),
    path("funnel/", FunnelView.as_view()),
]
