#####################
# operations/admin.py
#####################

import json
from django.contrib import admin
from django.utils.html import format_html
from django.utils import timezone

from .models import HealthState
from .tasks import run_health_checks


@admin.register(HealthState)
class HealthStateAdmin(admin.ModelAdmin):

    list_display = (
        "service_name",
        "status_badge",
        "value",
        "last_checked",
    )

    list_filter = ("status",)
    search_fields = ("key", "value")

    readonly_fields = (
        "key",
        "status",
        "status_badge",
        "value",
        "pretty_details",
        "checked_at",
    )

    actions = [
        "trigger_health_checks",
        "trigger_backfill_aggregations",
        "trigger_spot_prices",
        "trigger_weather_sync",
        "trigger_tibber_sync",
    ]

    HUMAN_LABELS = {
        "mqtt": "📡 MQTT Ingress / Telemetrie",
        "active_devices": "⚡ Aktive EMS-Geräte",
        "spot_prices": "📈 EPEX Spot-Preise (Börse)",
        "weather_sync": "☀️ Wetter- & Solar-Prognose",
        "tibber_sync": "🔌 Tibber Zähler-Synchronisation",
        "aggregation_1m": "⏱️ 1m Aggregation",
        "aggregation_5m": "⏱️ 5m Aggregation",
        "aggregation_15m": "⏱️ 15m Aggregation",
        "aggregation_1h": "⏱️ 1h Aggregation",
        "celery_queue_fiscal": "💶 Celery: Fiscal & Billing (Prio 1)",
        "celery_queue_realtime": "⚡ Celery: EMS Realtime & Steuerung (Prio 2)",
        "celery_queue_analytics": "📊 Celery: EMS Analytics & Markt (Prio 3)",
        "celery_queue_background": "💤 Celery: Background & KI (Prio 4)",
        "celery_queue_celery": "⚙️ Celery: Default Fallback",
    }

    def service_name(self, obj):
        label = self.HUMAN_LABELS.get(obj.key, obj.key)
        return format_html("<b>{}</b><br><small style='color: #6B7280;'>{}</small>", label, obj.key)

    service_name.short_description = "System / Service"

    def status_badge(self, obj):
        if obj.status == "ok":
            bg, fg, icon = "#10B981", "#FFFFFF", "🟢 OK"
        elif obj.status == "warn":
            bg, fg, icon = "#F59E0B", "#FFFFFF", "🟡 WARN"
        else:
            bg, fg, icon = "#EF4444", "#FFFFFF", "🔴 ERROR"

        return format_html(
            '<span style="background-color: {}; color: {}; padding: 4px 10px; border-radius: 12px; font-weight: 600; font-size: 11px;">{}</span>',
            bg,
            fg,
            icon,
        )

    status_badge.short_description = "Status"

    def last_checked(self, obj):
        if not obj.checked_at:
            return "-"
        age = timezone.now() - obj.checked_at
        mins = int(age.total_seconds() // 60)
        if mins < 1:
            return "Gerade eben"
        elif mins < 60:
            return f"vor {mins} Min."
        else:
            return f"vor {int(mins // 60)} Std."

    last_checked.short_description = "Geprüft"

    def pretty_details(self, obj):
        if not obj.details:
            return "-"
        return format_html("<pre style='background: #1F2937; color: #F9FAFB; padding: 10px; border-radius: 6px;'>{}</pre>", json.dumps(obj.details, indent=2))

    pretty_details.short_description = "Details (JSON)"

    @admin.action(description="⚡ Health-Checks jetzt ausführen")
    def trigger_health_checks(self, request, queryset):
        run_health_checks()
        self.message_user(request, "Health-Checks wurden erfolgreich ausgeführt!")

    @admin.action(description="⏱️ Aggregationen (1m, 5m, 15m, 1h) für letzte 2h nachziehen")
    def trigger_backfill_aggregations(self, request, queryset):
        from devices.services.aggregation import backfill_aggregations
        backfill_aggregations(hours=2)
        run_health_checks()
        self.message_user(request, "Aggregationen der letzten 2 Stunden wurden nachgezogen und Health-Checks aktualisiert!")

    @admin.action(description="📈 EPEX Spotpreise jetzt fetchen")
    def trigger_spot_prices(self, request, queryset):
        from market.tasks import fetch_spot_prices_retry
        fetch_spot_prices_retry.delay()
        self.message_user(request, "Spotpreis-Fetch Task wurde in die Celery Queue eingereiht!")

    @admin.action(description="☀️ Wetter- & PV-Prognose jetzt aktualisieren")
    def trigger_weather_sync(self, request, queryset):
        from forecast.tasks import fetch_weather_and_solar_forecast
        fetch_weather_and_solar_forecast.delay()
        self.message_user(request, "Wetter- & Solarprognose Task wurde in die Celery Queue eingereiht!")

    @admin.action(description="🔌 Tibber Zählerdaten jetzt synchronisieren")
    def trigger_tibber_sync(self, request, queryset):
        from integrations.tasks import sync_tibber
        sync_tibber.delay()
        self.message_user(request, "Tibber Synchronisation wurde in die Celery Queue eingereiht!")
