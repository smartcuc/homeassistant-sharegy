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
    path("community/cockpit/", community_cockpit_view, name="community_cockpit"),
    path("community/tariffs/", community_tariffs_view, name="community_tariffs"),
    path("community/statements/export/", statements_export_view, name="community_statements_export"),
    path("community/statements/generate/", generate_community_statements_view, name="community_statements_generate"),
    path("community/statements/<uuid:statement_id>/pdf/", statement_pdf_download_view, name="community_statement_pdf"),
    path("community/statements/", community_statements_view, name="community_statements"),
    path("communities/overview/", community_portfolio_overview_view, name="community_portfolio_overview"),
    path("communities/<uuid:tenant_id>/drilldown/", community_drilldown_view, name="community_drilldown"),
    path("communities/<uuid:tenant_id>/announcements/", community_announcements_view, name="community_announcements"),
    path("communities/<uuid:tenant_id>/settings/", community_settings_update_view, name="community_settings_update"),
]



