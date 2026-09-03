##########################
# integrations/api_urls.py
##########################

import logging

logger = logging.getLogger(__name__)

from django.urls import path

from integrations.views.ingest import ingest_readings
from integrations.views.events import EventListView
from integrations.views.energy_flow import EnergyFlowView
from devices.api.views_sungrow_oauth import sungrow_oauth_callback, sungrow_oauth_start
from devices.api.views_sungrow_webhook import sungrow_webhook_receiver

urlpatterns = [
    path("webhooks/meter-readings/", ingest_readings),
    path("events/", EventListView.as_view()),
    path("energy-flow/<slug:tenant_slug>/", EnergyFlowView.as_view()),

    # ☀️ Offizieller Sungrow iSolarCloud OAuth2.0 Callback
    path("integrations/sungrow/callback", sungrow_oauth_callback, name="sungrow_oauth_callback"),
    path("integrations/sungrow/callback/", sungrow_oauth_callback),
    path("integrations/sungrow/authorize", sungrow_oauth_start, name="sungrow_oauth_authorize"),
    path("integrations/sungrow/authorize/", sungrow_oauth_start),

    # 🔔 Sungrow Webhook Event Receiver
    path("webhooks/sungrow", sungrow_webhook_receiver, name="sungrow_webhook_receiver"),
    path("webhooks/sungrow/", sungrow_webhook_receiver),
]
