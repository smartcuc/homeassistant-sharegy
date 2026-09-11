"""
vpp/admin.py

Django-Admin für Virtuelles Kraftwerk (VPP), Pools und Dispatch-Aufträge.
"""

from django.contrib import admin
from django.utils.html import format_html
from django.utils.safestring import mark_safe
from vpp.models import VPPFlexibilityPool, VPPDispatchOrder, VPPDispatchTelemetry


class VPPDispatchTelemetryInline(admin.TabularInline):
    model = VPPDispatchTelemetry
    extra = 0
    readonly_fields = ("timestamp", "target_power_kw", "measured_power_kw", "frequency_hz", "battery_soc_avg")
    can_delete = False


@admin.register(VPPFlexibilityPool)
class VPPFlexibilityPoolAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "tso_badge",
        "market_product_badge",
        "postal_code_prefix",
        "min_activation_power_kw",
        "max_activation_power_kw",
        "is_active",
        "created_at",
    )
    list_filter = ("tso_operator", "market_product", "is_active")
    search_fields = ("name", "grid_region", "postal_code_prefix")

    def tso_badge(self, obj):
        colors = {
            "50hertz": "#dc2626",
            "tennet": "#2563eb",
            "amprion": "#059669",
            "transnetbw": "#d97706",
            "local_dso": "#475569",
        }
        color = colors.get(obj.tso_operator, "#64748b")
        return format_html(
            '<span style="background-color: {}; color: white; padding: 2px 8px; border-radius: 4px; font-weight: 600; font-size: 11px;">{}</span>',
            color,
            obj.get_tso_operator_display(),
        )
    tso_badge.short_description = "Netzbetreiber (ÜNB)"

    def market_product_badge(self, obj):
        return format_html(
            '<span style="background-color: #f1f5f9; color: #0f172a; padding: 2px 6px; border-radius: 4px; font-weight: 500; font-size: 11px;">{}</span>',
            obj.get_market_product_display(),
        )
    market_product_badge.short_description = "Produkt"


@admin.register(VPPDispatchOrder)
class VPPDispatchOrderAdmin(admin.ModelAdmin):
    list_display = (
        "order_id_short",
        "dispatch_type_badge",
        "target_power_display",
        "delivered_power_display",
        "duration_minutes",
        "status_badge",
        "requested_by",
        "remuneration_eur",
        "created_at",
    )
    list_filter = ("dispatch_type", "status", "requested_by")
    search_fields = ("id", "connect_plus_order_id", "requested_by")
    inlines = [VPPDispatchTelemetryInline]
    readonly_fields = ("created_at", "updated_at")

    def order_id_short(self, obj):
        return str(obj.id)[:8] + "..."
    order_id_short.short_description = "ID"

    def dispatch_type_badge(self, obj):
        if obj.dispatch_type == "positive_flex":
            return mark_safe('<span style="color: #10b981; font-weight: bold;">⚡ Positiv (+kW)</span>')
        return mark_safe('<span style="color: #3b82f6; font-weight: bold;">🔋 Negativ (-kW)</span>')
    dispatch_type_badge.short_description = "Typ"

    def target_power_display(self, obj):
        return f"{obj.target_power_kw:.1f} kW"
    target_power_display.short_description = "Soll"

    def delivered_power_display(self, obj):
        return f"{obj.delivered_power_kw:.1f} kW"
    delivered_power_display.short_description = "Ist"

    def status_badge(self, obj):
        colors = {
            "active": ("#10b981", "🟢 Aktiv"),
            "completed": ("#059669", "✅ Abgeschlossen"),
            "pending": ("#f59e0b", "🟡 Ausstehend"),
            "failed": ("#ef4444", "🔴 Fehlgeschlagen"),
            "cancelled": ("#94a3b8", "⚪ Storniert"),
        }
        color, label = colors.get(obj.status, ("#64748b", obj.status))
        return format_html(
            '<span style="color: {}; font-weight: bold;">{}</span>',
            color,
            label,
        )
    status_badge.short_description = "Status"
