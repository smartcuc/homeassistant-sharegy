from django.contrib import admin
from django.utils.html import format_html
from django.utils.safestring import mark_safe
from .models import (
    BankAccount,
    Contract,
    UserMeterAssignment,
    UserBalanceSlot,
    EMSSubscription,
    EMSInvoice,
    Coupon,
    CouponRedemption,
    CommunityTariff,
    CommunityMemberShare,
    CommunityMonthlyStatement,
    CommunityAnnouncement,
)


@admin.register(CommunityMemberShare)
class CommunityMemberShareAdmin(admin.ModelAdmin):
    list_display = (
        "tenant",
        "user",
        "share_percent_display",
        "mea_display",
        "assigned_kwp",
        "is_active",
        "valid_from",
        "valid_to",
    )
    list_filter = ("tenant", "is_active")
    search_fields = ("user__email", "tenant__name")
    raw_id_fields = ("tenant", "membership", "user")

    def share_percent_display(self, obj):
        val = f"{float(obj.share_percent):.4f}"
        return format_html("<b>{} %</b>", val)
    share_percent_display.short_description = "Quote (%)"

    def mea_display(self, obj):
        if obj.mea_numerator:
            return f"{obj.mea_numerator} / {obj.mea_denominator} MEA"
        return "-"
    mea_display.short_description = "Miteigentum (MEA)"


@admin.register(CommunityTariff)
class CommunityTariffAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "tenant",
        "allocation_model_badge",
        "sharing_price_ct_kwh",
        "producer_payout_ct_kwh",
        "community_fee_ct_kwh",
        "grid_fee_saved_ct_kwh",
        "is_active",
        "valid_from",
        "created_at",
    )
    list_filter = ("tenant", "allocation_model", "is_active")
    search_fields = ("name", "tenant__name")
    raw_id_fields = ("tenant",)

    def allocation_model_badge(self, obj):
        colors = {
            "dynamic": "green",
            "static": "blue",
            "hybrid": "purple",
        }
        color = colors.get(obj.allocation_model, "gray")
        return format_html("<span style='color: {}; font-weight: bold;'>{}</span>", color, obj.get_allocation_model_display())
    allocation_model_badge.short_description = "Allokationsmodell"



@admin.register(CommunityMonthlyStatement)
class CommunityMonthlyStatementAdmin(admin.ModelAdmin):
    list_display = (
        "statement_number",
        "tenant",
        "user",
        "period_start",
        "period_end",
        "produced_total_kwh",
        "consumed_total_kwh",
        "shared_imported_kwh",
        "shared_exported_kwh",
        "balance_colored",
        "status",
        "finalized_at",
    )
    list_filter = ("tenant", "status", "period_start")
    search_fields = ("statement_number", "user__email", "tenant__name")
    raw_id_fields = ("tenant", "membership", "user", "tariff")
    date_hierarchy = "period_start"

    def balance_colored(self, obj):
        val = float(obj.net_balance_eur)
        if val > 0:
            return format_html("<b style='color:green;'>+{} €</b>", f"{val:.2f}")
        elif val < 0:
            return format_html("<b style='color:red;'>{} €</b>", f"{val:.2f}")
        return mark_safe("<span>0.00 €</span>")
    balance_colored.short_description = "Netto-Saldo (€)"


@admin.register(UserMeterAssignment)
class UserMeterAssignmentAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "user",
        "meter",
        "valid_from",
        "valid_to",
        "is_active",
        "created_at",
    )
    list_filter = ("is_active",)
    search_fields = ("user__email", "meter__serial_number")
    raw_id_fields = ("user", "meter")


@admin.register(UserBalanceSlot)
class UserBalanceSlotAdmin(admin.ModelAdmin):
    list_display = (
        "period_start",
        "user",
        "meter",
        "tenant",
        "consumption_kwh",
        "generation_kwh",
        "self_consumption_kwh",
        "grid_import_kwh",
        "grid_export_kwh",
    )
    list_filter = ("tenant",)
    search_fields = ("user__email", "meter__serial_number")
    raw_id_fields = ("tenant", "user", "meter")
    date_hierarchy = "period_start"


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


@admin.register(CommunityAnnouncement)
class CommunityAnnouncementAdmin(admin.ModelAdmin):
    list_display = ("title", "tenant", "author", "category", "is_active", "created_at")
    list_filter = ("tenant", "category", "is_active")
    search_fields = ("title", "message", "tenant__name", "author__email")
    raw_id_fields = ("tenant", "author")


