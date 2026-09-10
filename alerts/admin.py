from django.contrib import admin
from django.utils.html import format_html
from .models import AlertEvent


@admin.register(AlertEvent)
class AlertEventAdmin(admin.ModelAdmin):
    list_display = (
        "id_short",
        "home",
        "severity_badge",
        "alert_type",
        "title",
        "status_badge",
        "device",
        "created_at",
        "resolved_at",
    )
    list_filter = ("severity", "status", "alert_type", "created_at")
    search_fields = ("title", "message", "home__name", "device__identifier")
    raw_id_fields = ("home", "device")
    readonly_fields = ("created_at", "acknowledged_at", "resolved_at")

    def id_short(self, obj):
        return str(obj.id)[:8] + "..."
    id_short.short_description = "ID"

    def severity_badge(self, obj):
        colors = {
            "critical": ("#ef4444", "CRITICAL"),
            "warning": ("#f59e0b", "WARNUNG"),
            "info": ("#3b82f6", "INFO"),
        }
        color, label = colors.get(obj.severity, ("#64748b", obj.severity.upper()))
        return format_html(
            '<span style="background-color: {}; color: white; padding: 2px 7px; border-radius: 4px; font-weight: bold; font-size: 10px;">{}</span>',
            color,
            label,
        )
    severity_badge.short_description = "Schweregrad"

    def status_badge(self, obj):
        colors = {
            "active": ("#ef4444", "🔴 Aktiv"),
            "acknowledged": ("#eab308", "🟡 Gesehen"),
            "resolved": ("#10b981", "🟢 Behoben"),
        }
        color, label = colors.get(obj.status, ("#64748b", obj.status))
        return format_html(
            '<span style="color: {}; font-weight: bold; font-size: 11px;">{}</span>',
            color,
            label,
        )
    status_badge.short_description = "Status"

