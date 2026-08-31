##################
# billing/admin.py
##################

from django.contrib import admin
from .models import BankAccount, Contract, EMSSubscription, EMSInvoice, Coupon, CouponRedemption


@admin.register(EMSSubscription)
class EMSSubscriptionAdmin(admin.ModelAdmin):
    list_display = (
        "user",
        "plan",
        "status",
        "is_pro_active",
        "current_period_start",
        "current_period_end",
        "cancel_at_period_end",
        "created_at",
    )
    list_filter = ("plan", "status", "cancel_at_period_end")
    search_fields = ("user__email", "user__first_name", "user__last_name", "stripe_customer_id")
    raw_id_fields = ("user",)


@admin.register(EMSInvoice)
class EMSInvoiceAdmin(admin.ModelAdmin):
    list_display = (
        "invoice_number",
        "subscription",
        "plan_name",
        "amount_gross_eur",
        "status",
        "paid_at",
        "created_at",
    )
    list_filter = ("status", "payment_method")
    search_fields = ("invoice_number", "recipient_name", "user__email")
    raw_id_fields = ("subscription", "user")


@admin.register(Coupon)
class CouponAdmin(admin.ModelAdmin):
    list_display = (
        "code",
        "discount_type",
        "discount_value",
        "is_active",
        "redemptions_count",
        "max_redemptions",
        "valid_until",
    )
    list_filter = ("is_active", "discount_type")
    search_fields = ("code", "description")


@admin.register(CouponRedemption)
class CouponRedemptionAdmin(admin.ModelAdmin):
    list_display = ("coupon", "user", "applied_discount", "redeemed_at")
    search_fields = ("coupon__code", "user__email")
    raw_id_fields = ("coupon", "user", "subscription")


@admin.register(BankAccount)
class BankAccountAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "account_holder",
        "iban",
        "tenant",
        "owner_user",
        "owner_membership",
        "is_active",
        "created_at",
    )
    list_filter = ("is_active", "tenant")
    search_fields = ("account_holder", "iban", "bic")
    raw_id_fields = ("tenant", "owner_user", "owner_membership")


@admin.register(Contract)
class ContractAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "contract_type",
        "supplier_name",
        "start_date",
        "end_date",
        "tenant",
        "owner_user",
        "owner_membership",
    )
    list_filter = ("contract_type", "tenant")
    search_fields = ("supplier_name",)
    raw_id_fields = ("tenant", "owner_user", "owner_membership")
