#####################
# backend/urls.py
#####################
import logging

logger = logging.getLogger(__name__)

"""
URL configuration for backend project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/6.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

from django.contrib import admin
from django.urls import path, include
from django.shortcuts import render
from django.http import HttpResponse

from rest_framework.routers import DefaultRouter

from core.api.viewsets import (
    MeterViewSet,
    IntervalReadingViewSet,
    AggregatedReadingViewSet,
    BalanceSlotViewSet,
)

from .views import api_test, trigger_task
from billing.api.views import consumption_view
from accounts.api.views import track_magic_click, track_email_open

router = DefaultRouter()
router.register(r"meters", MeterViewSet, basename="meter")
router.register(r"readings", IntervalReadingViewSet, basename="reading")
router.register(r"aggregates", AggregatedReadingViewSet, basename="aggregate")
router.register(r"balances", BalanceSlotViewSet, basename="balance")


def home(request):
    return render(request, "home.html")

    #   path("api/test/", api_test),
    #   path("api/trigger-task/", trigger_task),

urlpatterns = [
    path("", home),
    path("admin/", admin.site.urls),
    # ✅ GLOBAL TRACKING ROUTES
    path("t/<uuid:token>/", track_magic_click),
    path("email/open/<uuid:token>/", track_email_open),
    # ✅ API zentrales include
    path(
        "api/",
        include(
            [
                path("", include("accounts.api.urls")),
                path("", include("integrations.urls")),
                path("", include("content.urls_public")),
                path("", include("providers.opentelemetry.urls")),
                path("energy/", include("energy.api.urls")),
                path("alerts/", include("alerts.urls")),
                path("forecast/", include("forecast.urls")),
                path("devices/", include("devices.api.urls")),
                path("market/", include("market.api.urls")),
                path("producer/", include("producer.api.urls")),
                path("user-settings/", include("user_settings.api.urls")),
                path("public/", include("forecast.urls_public")),
                path("track/", include("tracking.api_urls")),
                path("tracking/", include("tracking.api_urls")),
            ]
        ),
    ),
    # ✅ Generic / legacy
    #path("api/", include("integrations.urls")),
    #path("api/", include("accounts.api.urls")),
    #path("api/", include("content.urls_public")),
    #  path("api/devices/", include("devices.urls")),
    path("api/", include(router.urls)),
    path("public/billing/", include("billing.api.urls_public")),
    path("api/v1/", include("integrations.api_urls")),
    path("api/consumption/", consumption_view),
]
