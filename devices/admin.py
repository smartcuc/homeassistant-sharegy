##################
# devices/admin.py
##################

from django.contrib import admin
from .models import *


from django.utils.html import format_html
from django.utils import timezone
from datetime import timedelta


@admin.register(Device)
class DeviceAdmin(admin.ModelAdmin):
    list_display = (
        "identifier",
        "role_badge",
        "live_power",
        "online_status",
        "get_user",
        "home",
        "configured",
        "active",
        "last_seen",
    )

    list_filter = (
        "active",
        "configured",
        "config__role",
        "mqtt_profile",
        "home__user",
    )

    search_fields = (
        "identifier",
        "home__user__username",
        "home__user__email",
        "home__name",
    )

    readonly_fields = ("last_seen",)
    actions = ["activate_devices", "deactivate_devices", "mark_as_configured"]

    # ⚡ Performance-Turbo: Verhindert N+1-Queries in der Admin-Liste
    select_related = ("home__user", "mqtt_profile", "config__role")

    @admin.display(ordering="home__user", description="User")
    def get_user(self, obj):
        if obj.home and obj.home.user:
            return obj.home.user.email or obj.home.user.username
        return "-"

    @admin.display(description="Rolle")
    def role_badge(self, obj):
        cfg = getattr(obj, "config", None)
        role = cfg.role.key if (cfg and cfg.role) else "unbekannt"
        colors = {
            "producer": ("#FEF3C7", "#D97706", "☀️ Erzeuger"),
            "consumer": ("#FCE7F3", "#DB2777", "🔌 Last"),
            "battery": ("#D1FAE5", "#059669", "🔋 Speicher"),
            "grid": ("#DBEAFE", "#2563EB", "⚡ Netz"),
        }
        bg, fg, label = colors.get(role, ("#F3F4F6", "#6B7280", role))
        return format_html(
            '<span style="background-color: {}; color: {}; padding: 3px 8px; border-radius: 8px; font-weight: 600; font-size: 11px;">{}</span>',
            bg, fg, label
        )

    @admin.display(description="⚡ Live-Leistung")
    def live_power(self, obj):
        from devices.services.metrics import get_latest_values
        vals = get_latest_values([obj.id])
        val = vals.get(obj.id)
        if val is None:
            return format_html('<span style="color: #9CA3AF;">-</span>')
        
        cfg = getattr(obj, "config", None)
        role = cfg.role.key if (cfg and cfg.role) else ""
        color = "#10B981" if role == "battery" else "#D97706" if role == "producer" else "#2563EB" if role == "grid" else "#374151"
        formatted_val = f"{float(val):,.1f} W"
        return format_html('<span style="font-weight: 700; color: {};">{}</span>', color, formatted_val)

    @admin.display(description="Status")
    def online_status(self, obj):
        if not obj.last_seen:
            return format_html('<span style="color: #9CA3AF;">⚪ Nie gesehen</span>')
        age = timezone.now() - obj.last_seen
        if age < timedelta(minutes=15):
            return format_html('<span style="color: #10B981; font-weight: bold;">🟢 Online</span>')
        elif age < timedelta(hours=24):
            return format_html('<span style="color: #F59E0B;">🟡 Vor {} Min.</span>', int(age.total_seconds() // 60))
        else:
            return format_html('<span style="color: #EF4444;">🔴 Offline ({} T.)</span>', int(age.days))

    @admin.action(description="🟢 Ausgewählte Geräte aktivieren")
    def activate_devices(self, request, queryset):
        count = queryset.update(active=True)
        self.message_user(request, f"{count} Geräte aktiviert.")

    @admin.action(description="🔴 Ausgewählte Geräte deaktivieren")
    def deactivate_devices(self, request, queryset):
        count = queryset.update(active=False)
        self.message_user(request, f"{count} Geräte deaktiviert.")

    @admin.action(description="⚙️ Als konfiguriert markieren")
    def mark_as_configured(self, request, queryset):
        count = queryset.update(configured=True)
        self.message_user(request, f"{count} Geräte als konfiguriert markiert.")


@admin.register(DeviceConfig)
class DeviceConfigAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "device",
        "name",
        "role",
        "generator_type",
        "energy_signal_type",
    )

    list_filter = (
        "role",
        "generator_type",
        "energy_signal_type",
        "home",
    )
    search_fields = ("name", "device__identifier")


@admin.register(DeviceMetric)
class DeviceMetricAdmin(admin.ModelAdmin):
    list_display = ("id", "device", "metric_key", "value", "unit", "timestamp")
    list_filter = ("metric_key",)
    search_fields = ("device__identifier",)
    date_hierarchy = "timestamp"


@admin.register(DeviceLatestMetric)
class DeviceLatestMetricAdmin(admin.ModelAdmin):
    list_display = ("device", "metric_key", "formatted_value", "updated_at", "age")
    list_filter = ("metric_key",)
    search_fields = ("device__identifier", "metric_key")
    readonly_fields = ("updated_at",)

    @admin.display(description="Messwert")
    def formatted_value(self, obj):
        unit = obj.unit or ("W" if obj.metric_key in ["power", "value"] else "")
        return f"{obj.value:,.2f} {unit}"

    @admin.display(description="Alter")
    def age(self, obj):
        if not obj.updated_at:
            return "-"
        diff = int((timezone.now() - obj.updated_at).total_seconds())
        if diff < 60:
            return f"{diff}s"
        return f"{diff // 60}m"


@admin.register(Home)
class HomeAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "user",
        "name",
        "timezone",
        "mqtt_token",
        "mqtt_username",
        "mqtt_provisioned",
    )

    readonly_fields = (
        "mqtt_token",
        "mqtt_username",
    )

    search_fields = (
        "name",
        "user__username",
        "user__email",
        "mqtt_token",
        "mqtt_username",
    )

    list_filter = (
        "timezone",
        "mqtt_provisioned",
    )


@admin.register(Floor)
class FloorAdmin(admin.ModelAdmin):
    list_display = ("id", "name")
    search_fields = ("name",)


@admin.register(Room)
class RoomAdmin(admin.ModelAdmin):
    list_display = ("id", "name")
    search_fields = ("name",)


@admin.register(DeviceRole)
class DeviceRoleAdmin(admin.ModelAdmin):
    list_display = ("id", "key", "label")


@admin.register(MetricDefinition)
class MetricDefinitionAdmin(admin.ModelAdmin):
    list_display = ("id", "key", "name", "unit")

@admin.register(MQTTProfile)
class MQTTProfileAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "slug",
        "active",
    )

    list_filter = (
        "active",
    )

    search_fields = (
        "name",
        "slug",
    )
