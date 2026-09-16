"""
vpp/urls.py

URL-Routen für das Virtuelle Kraftwerk (VPP) und Übertragungsnetzbetreiber (ÜNB/VNB).
"""

from django.urls import path
from vpp.views import (
    vpp_fleet_summary_view,
    vpp_flexibility_view,
    vpp_redispatch_schedule_view,
    vpp_pools_view,
    vpp_dispatch_orders_view,
    vpp_dispatch_order_detail_view,
    vpp_dispatch_order_cancel_view,
    vpp_user_enrollments_view,
    vpp_user_enrollment_detail_view,
    vpp_user_earnings_view,
    vpp_clearing_run_view,
    vpp_aggregator_webhook_view,
)

urlpatterns = [
    # ⚡ VPP Fleets & Flexibilität
    path("summary/", vpp_fleet_summary_view, name="vpp_fleet_summary"),
    path("flexibility/", vpp_flexibility_view, name="vpp_flexibility"),
    
    # 🔌 Redispatch 2.0 / Connect+ 96-Viertelstunden-Fahrplan
    path("redispatch-schedule/", vpp_redispatch_schedule_view, name="vpp_redispatch_schedule"),
    
    # 🏊‍♂️ Pools & Asset-Gruppen
    path("pools/", vpp_pools_view, name="vpp_pools"),
    
    # 🚀 Dispatching & Abruf-Steuerung
    path("dispatch/", vpp_dispatch_orders_view, name="vpp_dispatch_orders"),
    path("dispatch/<uuid:order_id>/", vpp_dispatch_order_detail_view, name="vpp_dispatch_order_detail"),
    path("dispatch/<uuid:order_id>/cancel/", vpp_dispatch_order_cancel_view, name="vpp_dispatch_order_cancel"),

    # 👥 Endkunden Opt-In & Erlöse
    path("enrollments/", vpp_user_enrollments_view, name="vpp_user_enrollments"),
    path("enrollments/<uuid:enrollment_id>/", vpp_user_enrollment_detail_view, name="vpp_user_enrollment_detail"),
    path("earnings/", vpp_user_earnings_view, name="vpp_user_earnings"),

    # ⚖️ Monetäres Clearing & Payouts
    path("clearing/run/", vpp_clearing_run_view, name="vpp_clearing_run"),

    # 🌐 Aggregator & ÜNB Webhook (Next Kraftwerke / 50Hertz / Connect+)
    path("aggregator/webhook/", vpp_aggregator_webhook_view, name="vpp_aggregator_webhook"),
]

