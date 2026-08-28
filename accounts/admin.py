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
