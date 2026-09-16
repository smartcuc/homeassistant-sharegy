"""
vpp/admin.py

Django-Admin für Virtuelles Kraftwerk (VPP), Pools und Dispatch-Aufträge.
"""

from django.contrib import admin
from django.utils.html import format_html
from django.utils.safestring import mark_safe
from vpp.models import (
    VPPFlexibilityPool,
    VPPDispatchOrder,
    VPPDispatchTelemetry,
    VPPAssetEnrollment,
    VPPAssetDispatch,
    VPPClearingStatement,
)


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


@admin.register(VPPDispatchTelemetry)
class VPPDispatchTelemetryAdmin(admin.ModelAdmin):
    list_display = ("timestamp", "dispatch_order_id", "target_power_kw", "measured_power_kw", "frequency_hz", "battery_soc_avg")
    list_filter = ("timestamp",)
    search_fields = ("dispatch_order__id", "dispatch_order__connect_plus_order_id")
    readonly_fields = ("timestamp", "dispatch_order", "target_power_kw", "measured_power_kw", "frequency_hz", "battery_soc_avg")

    def dispatch_order_id(self, obj):
        return str(obj.dispatch_order_id)[:8]
    dispatch_order_id.short_description = "Dispatch Order"


@admin.register(VPPAssetEnrollment)
class VPPAssetEnrollmentAdmin(admin.ModelAdmin):
    list_display = (
        "device_name",
        "user_email",
        "pool_display",
        "status_badge",
        "min_soc_reserve_pct",
        "payout_share_pct",
        "total_earned_display",
        "total_dispatches_count",
        "joined_at",
    )
    list_filter = ("status", "pool", "auto_spot_arbitrage", "auto_afrr_frequency")
    search_fields = ("device__name", "user__email", "user__username")
    readonly_fields = ("total_earned_eur", "total_dispatches_count", "joined_at", "updated_at")

    def device_name(self, obj):
        return obj.device.name if obj.device else "–"
    device_name.short_description = "Gerät"

    def user_email(self, obj):
        return obj.user.email if obj.user else "–"
    user_email.short_description = "Nutzer"

    def pool_display(self, obj):
        return obj.pool.name if obj.pool else "Standard-Pool"
    pool_display.short_description = "Pool"

    def status_badge(self, obj):
        colors = {
            "active": ("#10b981", "🟢 Aktiv"),
            "paused": ("#f59e0b", "🟡 Pausiert"),
            "opted_out": ("#94a3b8", "⚪ Abgemeldet"),
        }
        color, label = colors.get(obj.status, ("#64748b", obj.status))
        return format_html('<span style="color: {}; font-weight: bold;">{}</span>', color, label)
    status_badge.short_description = "Status"

    def total_earned_display(self, obj):
        return f"{obj.total_earned_eur:.2f} €"
    total_earned_display.short_description = "Erlöst"


@admin.register(VPPAssetDispatch)
class VPPAssetDispatchAdmin(admin.ModelAdmin):
    list_display = (
        "id_short",
        "device_name",
        "delivered_power_display",
        "energy_display",
        "customer_payout_display",
        "sharegy_fee_display",
        "soc_change_display",
        "is_cleared_badge",
        "created_at",
    )
    list_filter = ("is_cleared", "created_at")
    search_fields = ("device__name", "enrollment__user__email", "dispatch_order__id")
    readonly_fields = ("created_at",)

    def id_short(self, obj):
        return str(obj.id)[:8]
    id_short.short_description = "ID"

    def device_name(self, obj):
        return obj.device.name if obj.device else "–"
    device_name.short_description = "Gerät"

    def delivered_power_display(self, obj):
        return f"{obj.delivered_power_kw:.2f} kW"
    delivered_power_display.short_description = "Leistung"

    def energy_display(self, obj):
        return f"{obj.energy_kwh:.3f} kWh"
    energy_display.short_description = "Arbeit"

    def customer_payout_display(self, obj):
        return format_html('<span style="color: #10b981; font-weight: bold;">+{:.2f} €</span>', obj.customer_payout_eur)
    customer_payout_display.short_description = "Kunde (80%)"

    def sharegy_fee_display(self, obj):
        return f"{obj.sharegy_fee_eur:.2f} €"
    sharegy_fee_display.short_description = "Sharegy (20%)"

    def soc_change_display(self, obj):
        return f"{obj.soc_before_pct:.0f}% ➔ {obj.soc_after_pct:.0f}%"
    soc_change_display.short_description = "SoC"

    def is_cleared_badge(self, obj):
        if obj.is_cleared:
            return mark_safe('<span style="color: #059669; font-weight: bold;">✅ Abgerechnet</span>')
        return mark_safe('<span style="color: #f59e0b; font-weight: bold;">⏳ Offen</span>')
    is_cleared_badge.short_description = "Clearing"


@admin.register(VPPClearingStatement)
class VPPClearingStatementAdmin(admin.ModelAdmin):
    list_display = (
        "payment_reference",
        "user_email",
        "period_display",
        "dispatches_count",
        "total_energy_display",
        "customer_payout_display",
        "sharegy_fee_display",
        "status_badge",
        "credited_at",
    )
    list_filter = ("status", "period_start", "period_end")
    search_fields = ("payment_reference", "user__email", "user__username")
    readonly_fields = ("created_at", "updated_at")

    def user_email(self, obj):
        return obj.user.email if obj.user else "–"
    user_email.short_description = "Nutzer"

    def period_display(self, obj):
        return f"{obj.period_start.strftime('%d.%m.%Y')} - {obj.period_end.strftime('%d.%m.%Y')}"
    period_display.short_description = "Zeitraum"

    def total_energy_display(self, obj):
        return f"{obj.total_energy_kwh:.2f} kWh"
    total_energy_display.short_description = "Gesamtenergie"

    def customer_payout_display(self, obj):
        return format_html('<span style="color: #10b981; font-weight: bold;">+{:.2f} €</span>', obj.customer_payout_eur)
    customer_payout_display.short_description = "Gutschrift (80%)"

    def sharegy_fee_display(self, obj):
        return f"{obj.sharegy_fee_eur:.2f} €"
    sharegy_fee_display.short_description = "Marge (20%)"

    def status_badge(self, obj):
        colors = {
            "credited": ("#059669", "✅ Gutgeschrieben"),
            "paid_out": ("#2563eb", "💳 Ausgezahlt"),
            "pending": ("#f59e0b", "🟡 Ausstehend"),
        }
        color, label = colors.get(obj.status, ("#64748b", obj.status))
        return format_html('<span style="color: {}; font-weight: bold;">{}</span>', color, label)
    status_badge.short_description = "Status"

