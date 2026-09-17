from django.urls import path
from billing.api.views import (
    consumption_view,
    subscription_me_view,
    update_billing_address_view,
    change_plan_view,
    cancel_subscription_view,
    reactivate_subscription_view,
    invoice_pdf_view,
    seed_demo_billing_view,
    validate_coupon_view,
    redeem_coupon_view,
)
from billing.api.views_community import (
    community_cockpit_view,
    community_tariffs_view,
    community_statements_view,
    generate_community_statements_view,
    community_portfolio_overview_view,
    community_drilldown_view,
    community_announcements_view,
    community_settings_update_view,
    statement_pdf_download_view,
    statements_export_view,
    community_member_shares_view,
    community_member_shares_bulk_view,
    community_allocation_preview_view,
    community_mscons_export_view,
    community_mscons_import_view,
    community_obis_ingest_view,
    community_msb_meters_view,
    community_virtual_master_meter_view,
)
from billing.api.views_cooperative import (
    cooperative_public_info_view,
    cooperative_submit_application_view,
    cooperative_admin_applications_view,
    cooperative_admin_approve_application_view,
    cooperative_admin_reject_application_view,
)

from billing.api.views_stripe import (
    StripeConfigView,
    StripeCheckoutView,
    StripeCustomerPortalView,
    StripeWebhookView,
)

urlpatterns = [
    path("consumption/", consumption_view, name="billing_consumption"),
    path("subscription/me/", subscription_me_view, name="subscription_me"),
    path("subscription/update-address/", update_billing_address_view, name="subscription_update_address"),
    path("subscription/change-plan/", change_plan_view, name="subscription_change_plan"),
    path("subscription/cancel/", cancel_subscription_view, name="subscription_cancel"),
    path("subscription/reactivate/", reactivate_subscription_view, name="subscription_reactivate"),
    path("subscription/invoices/<uuid:invoice_id>/pdf/", invoice_pdf_view, name="subscription_invoice_pdf"),
    path("subscription/seed-demo/", seed_demo_billing_view, name="subscription_seed_demo"),
    path("subscription/coupons/validate/", validate_coupon_view, name="subscription_coupon_validate"),
    path("subscription/coupons/redeem/", redeem_coupon_view, name="subscription_coupon_redeem"),
    # 💳 STRIPE PAYMENTS & SANDBOX
    path("stripe/config/", StripeConfigView.as_view(), name="stripe_config"),
    path("stripe/checkout/", StripeCheckoutView.as_view(), name="stripe_checkout"),
    path("stripe/portal/", StripeCustomerPortalView.as_view(), name="stripe_portal"),
    path("stripe/webhook/", StripeWebhookView.as_view(), name="stripe_webhook"),
    # ⚡ COMMUNITY & ENERGY SHARING
    path("community/cockpit/", community_cockpit_view, name="community_cockpit"),
    path("community/virtual-meter/", community_virtual_master_meter_view, name="community_virtual_meter"),
    path("community/tariffs/", community_tariffs_view, name="community_tariffs"),
    path("community/shares/", community_member_shares_view, name="community_member_shares"),
    path("community/shares/bulk/", community_member_shares_bulk_view, name="community_member_shares_bulk"),
    path("community/allocation-preview/", community_allocation_preview_view, name="community_allocation_preview"),
    path("community/msb-meters/", community_msb_meters_view, name="community_msb_meters"),
    path("community/mscons/export/", community_mscons_export_view, name="community_mscons_export"),
    path("community/mscons/import/", community_mscons_import_view, name="community_mscons_import"),
    path("community/obis/ingest/", community_obis_ingest_view, name="community_obis_ingest"),
    path("community/statements/export/", statements_export_view, name="community_statements_export"),
    path("community/statements/generate/", generate_community_statements_view, name="community_statements_generate"),
    path("community/statements/<uuid:statement_id>/pdf/", statement_pdf_download_view, name="community_statement_pdf"),
    path("community/statements/", community_statements_view, name="community_statements"),
    path("communities/overview/", community_portfolio_overview_view, name="community_portfolio_overview"),
    path("communities/<uuid:tenant_id>/drilldown/", community_drilldown_view, name="community_drilldown"),
    path("communities/<uuid:tenant_id>/virtual-meter/", community_virtual_master_meter_view, name="community_tenant_virtual_meter"),
    path("communities/<uuid:tenant_id>/announcements/", community_announcements_view, name="community_announcements"),
    path("communities/<uuid:tenant_id>/settings/", community_settings_update_view, name="community_settings_update"),
    # 🏛️ GENOSSENSCHAFTS-BEITRITT & MITGLIEDERBUCH (§§ 15b, 30 GenG)
    path("cooperative/join/<slug:slug>/", cooperative_submit_application_view, name="cooperative_submit_application"),
    path("cooperative/info/<slug:slug>/", cooperative_public_info_view, name="cooperative_public_info"),
    path("cooperative/applications/", cooperative_admin_applications_view, name="cooperative_admin_applications"),
    path("cooperative/applications/<uuid:application_id>/approve/", cooperative_admin_approve_application_view, name="cooperative_admin_approve"),
    path("cooperative/applications/<uuid:application_id>/reject/", cooperative_admin_reject_application_view, name="cooperative_admin_reject"),
]

# BNetzA AS4 Marktkommunikation
from billing.views_mako import MarketCommunicationExportView, MarketCommunicationLogsView

urlpatterns += [
    path("mako/export/", MarketCommunicationExportView.as_view(), name="mako_export"),
    path("mako/logs/", MarketCommunicationLogsView.as_view(), name="mako_logs"),
]

