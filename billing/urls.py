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
]

