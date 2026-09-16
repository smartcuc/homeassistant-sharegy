####################
# accounts/admin.py
####################

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as DjangoUserAdmin
from .models import (
    User,
    UserProfile,
    UserSettings,
    TenantMembership,
    TenantInvite,
    AuditLog,
    MagicLoginToken,
)


class TenantMembershipInline(admin.TabularInline):
    model = TenantMembership
    extra = 1
    raw_id_fields = ("user",)
    fields = ("user", "role", "is_active", "created_at")
    readonly_fields = ("created_at",)


@admin.register(User)
class UserAdmin(DjangoUserAdmin):
    list_display = ("id", "email", "username", "platform_role", "is_active", "is_verified", "is_staff")
    list_filter = ("platform_role", "is_active", "is_verified", "is_staff", "is_superuser")
    search_fields = ("email", "username")
    ordering = ("email",)

    fieldsets = DjangoUserAdmin.fieldsets + (
        (
            "Sharegy Platform Role",
            {
                "fields": (
                    "platform_role",
                )
            },
        ),
        (
            "Tibber Integration",
            {
                "fields": (
                    "tibber_token",
                    "tibber_home_id",
                )
            },
        ),
        ("Verification", {"fields": ("is_verified",)}),
        ("Meta", {"fields": ("id", "created_at")}),
    )

    readonly_fields = ("id", "created_at")
    inlines = [TenantMembershipInline]

    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        if "tibber_token" in form.base_fields:
            form.base_fields["tibber_token"].widget.attrs["size"] = 80
        return form


@admin.register(TenantMembership)
class TenantMembershipAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "tenant", "role", "is_active", "created_at")
    list_filter = ("role", "is_active", "tenant")
    search_fields = ("user__email", "user__username", "tenant__name", "tenant__slug")
    raw_id_fields = ("user", "tenant")
    ordering = ("-created_at",)


@admin.register(TenantInvite)
class TenantInviteAdmin(admin.ModelAdmin):
    list_display = ("token", "tenant", "role", "max_uses", "used_count", "is_active", "created_at")
    list_filter = ("role", "is_active", "tenant")
    search_fields = ("token", "tenant__name")
    raw_id_fields = ("tenant",)
    ordering = ("-created_at",)


@admin.register(AuditLog)
class AuditLogAdmin(admin.ModelAdmin):
    list_display = ("created_at", "tenant", "user", "action", "target_user")
    list_filter = ("action", "tenant")
    search_fields = ("user__email", "target_user__email", "tenant__name")
    readonly_fields = ("created_at", "metadata", "action", "user", "tenant", "target_user")
    ordering = ("-created_at",)


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ("user", "city", "postal_code", "country", "customer_type")
    search_fields = ("user__email", "city", "postal_code", "company_name")


@admin.register(UserSettings)
class UserSettingsAdmin(admin.ModelAdmin):

    list_display = (
        "user",
        "has_timezone",
        "timezone",
        "language",
        "dashboard_mode",
        "usage_mode",
        "onboarding_step",
        "created_at",
    )

    list_filter = (
        "language",
        "usage_mode",
        "dashboard_mode",
        "onboarding_step",
    )

    search_fields = (
        "user__email",
        "user__username",
    )

    @admin.display(description="Timezone gesetzt")
    def has_timezone(self, obj):
        return bool(obj.timezone)


@admin.register(MagicLoginToken)
class MagicLoginTokenAdmin(admin.ModelAdmin):
    list_display = ("user", "created_at", "clicked_at", "used_at")

    def changelist_view(self, request, extra_context=None):
        total = MagicLoginToken.objects.count()
        clicked = MagicLoginToken.objects.filter(clicked_at__isnull=False).count()
        used = MagicLoginToken.objects.filter(used_at__isnull=False).count()

        extra_context = extra_context or {}
        extra_context["metrics"] = {
            "total": total,
            "clicked": clicked,
            "used": used,
        }

        return super().changelist_view(request, extra_context=extra_context)


# =====================================================================
# 🛡️ DSGVO-Zustimmungen & B2B2C Fachpartner-Flotte
# =====================================================================

from .models import (
    UserTermsConsent,
    PartnerCompany,
    PartnerMembership,
    MaintenanceConsent,
)


@admin.register(UserTermsConsent)
class UserTermsConsentAdmin(admin.ModelAdmin):
    list_display = ("user_email", "consent_type", "terms_version", "privacy_version", "ip_address", "created_at")
    list_filter = ("consent_type", "terms_version", "created_at")
    search_fields = ("user__email", "user__username", "ip_address")
    readonly_fields = ("id", "user", "terms_version", "privacy_version", "consent_type", "ip_address", "user_agent", "created_at")

    def user_email(self, obj):
        return obj.user.email if obj.user else "–"
    user_email.short_description = "Nutzer"


class PartnerMembershipInline(admin.TabularInline):
    model = PartnerMembership
    extra = 0
    raw_id_fields = ("user",)


class MaintenanceConsentInline(admin.TabularInline):
    model = MaintenanceConsent
    extra = 0
    raw_id_fields = ("home",)


@admin.register(PartnerCompany)
class PartnerCompanyAdmin(admin.ModelAdmin):
    list_display = ("name", "partner_tier", "contact_email", "phone", "city", "is_verified", "members_count", "created_at")
    list_filter = ("partner_tier", "is_verified", "city")
    search_fields = ("name", "slug", "contact_email", "city")
    prepopulated_fields = {"slug": ("name",)}
    inlines = [PartnerMembershipInline, MaintenanceConsentInline]

    def members_count(self, obj):
        return obj.members.count()
    members_count.short_description = "Techniker"


@admin.register(PartnerMembership)
class PartnerMembershipAdmin(admin.ModelAdmin):
    list_display = ("user_email", "partner_name", "role", "created_at")
    list_filter = ("role", "partner_company")
    search_fields = ("user__email", "user__username", "partner_company__name")
    raw_id_fields = ("user", "partner_company")

    def user_email(self, obj):
        return obj.user.email if obj.user else "–"
    user_email.short_description = "Techniker"

    def partner_name(self, obj):
        return obj.partner_company.name if obj.partner_company else "–"
    partner_name.short_description = "Fachbetrieb"


@admin.register(MaintenanceConsent)
class MaintenanceConsentAdmin(admin.ModelAdmin):
    list_display = ("partner_name", "home_name", "status", "allow_remote_control", "allow_telemetry_history", "granted_at")
    list_filter = ("status", "allow_remote_control", "allow_telemetry_history")
    search_fields = ("partner_company__name", "home__name")
    raw_id_fields = ("home", "partner_company")

    def partner_name(self, obj):
        return obj.partner_company.name if obj.partner_company else "–"
    partner_name.short_description = "Fachbetrieb"

    def home_name(self, obj):
        return obj.home.name if obj.home else "–"
    home_name.short_description = "Haushalt / Anlage"

