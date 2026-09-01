from django.contrib import admin
from django.utils.html import format_html
from .models import DeviceSubscription, NotificationPreference


@admin.register(DeviceSubscription)
class DeviceSubscriptionAdmin(admin.ModelAdmin):
    list_display = (
        "id_short",
        "user",
        "device_type_badge",
        "device_name",
        "is_active_badge",
        "last_used_at",
        "created_at",
    )
    list_filter = ("device_type", "is_active", "created_at")
    search_fields = ("user__email", "device_name", "endpoint", "registered_ip")
    raw_id_fields = ("user", "home")
    readonly_fields = ("created_at", "last_used_at", "unregistered_at")

    def id_short(self, obj):
        return str(obj.id)[:8] + "..."
    id_short.short_description = "ID"

    def device_type_badge(self, obj):
        icons = {
            "web_push": "🌐 Web-Push",
            "ios": "🍎 iOS (APNs)",
            "android": "🤖 Android (FCM)",
        }
        return icons.get(obj.device_type, obj.device_type)
    device_type_badge.short_description = "Plattform"

    def is_active_badge(self, obj):
        if obj.is_active:
            return format_html('<span style="color: #10b981; font-weight: bold;">🟢 Aktiv</span>')
        return format_html('<span style="color: #94a3b8;">⚪ Inaktiv</span>')
    is_active_badge.short_description = "Status"


@admin.register(NotificationPreference)
class NotificationPreferenceAdmin(admin.ModelAdmin):
    list_display = (
        "user",
        "push_enabled",
        "quiet_hours_enabled",
        "quiet_hours_start",
        "quiet_hours_end",
        "notify_battery",
        "notify_pv",
        "notify_prices",
        "updated_at",
    )
    list_filter = ("push_enabled", "quiet_hours_enabled")
    search_fields = ("user__email", "user__first_name", "user__last_name")
    raw_id_fields = ("user",)
