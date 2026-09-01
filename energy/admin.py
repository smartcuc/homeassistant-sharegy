#################
# energy/admin.py
#################

from django.contrib import admin
from energy.models import (
    Location,
    EnergyAsset,
    EnergyAssetPV,
    EnergyAssetBattery,
    EnergyAssetEV,
    AssetMeter,
    SmartEnergySettings,
    EMSSignalSource,
    EMSSignalType,
)


@admin.register(Location)
class LocationAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "name",
        "tenant",
        "owner_user",
        "owner_membership",
        "city",
        "postal_code",
    )
    list_filter = ("tenant", "city", "country")
    search_fields = ("name", "street", "city", "postal_code")
    raw_id_fields = ("tenant", "owner_user", "owner_membership")


@admin.register(EnergyAsset)
class EnergyAssetAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "name",
        "asset_type",
        "tenant",
        "owner_user",
        "owner_membership",
        "installed_power_kw",
        "installed_at",
    )
    list_filter = ("asset_type", "tenant")
    search_fields = ("name",)
    raw_id_fields = ("tenant", "owner_user", "owner_membership", "location")


@admin.register(EnergyAssetPV)
class EnergyAssetPVAdmin(admin.ModelAdmin):
    list_display = (
        "asset",
        "module_manufacturer",
        "inverter_manufacturer",
        "tilt_angle",
        "azimuth",
    )
    search_fields = ("module_manufacturer", "inverter_manufacturer")
    raw_id_fields = ("asset",)


@admin.register(EnergyAssetBattery)
class EnergyAssetBatteryAdmin(admin.ModelAdmin):
    list_display = (
        "asset",
        "capacity_kwh",
        "usable_capacity_kwh",
        "max_charge_kw",
        "max_discharge_kw",
        "efficiency",
    )
    search_fields = ("manufacturer", "model")
    raw_id_fields = ("asset",)


@admin.register(EnergyAssetEV)
class EnergyAssetEVAdmin(admin.ModelAdmin):
    list_display = ("asset", "battery_capacity_kwh", "max_charging_power_kw")
    raw_id_fields = ("asset",)


@admin.register(AssetMeter)
class AssetMeterAdmin(admin.ModelAdmin):
    list_display = ("id", "asset", "meter", "relation_type", "created_at")
    list_filter = ("relation_type",)
    search_fields = ("asset__name", "meter__serial_number")
    raw_id_fields = ("asset", "meter")


@admin.register(SmartEnergySettings)
class SmartEnergySettingsAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "tenant",
        "owner_user",
        "owner_membership",
        "optimization_mode",
        "allow_direct_control",
        "optimize_ev",
        "optimize_battery",
    )
    list_filter = ("optimization_mode", "allow_direct_control")
    raw_id_fields = ("tenant", "owner_user", "owner_membership")


@admin.register(EMSSignalSource)
class EMSSignalSourceAdmin(admin.ModelAdmin):

    list_display = (
        "home",
        "signal_type",
        "device",
        "created_at",
    )

    list_filter = ("signal_type",)

    search_fields = (
        "home__name",
        "device__identifier",
        "signal_type__key",
        "signal_type__label",
    )

    raw_id_fields = (
        "home",
        "device",
    )

    autocomplete_fields = ("signal_type",)


@admin.register(EMSSignalType)
class EMSSignalTypeAdmin(admin.ModelAdmin):

    list_display = (
        "key",
        "label",
        "active",
        "created_at",
    )

    list_filter = ("active",)

    search_fields = (
        "key",
        "label",
    )

    ordering = ("label",)


# ---------------------------------------------------------------------
# § 14a EnWG Admin Registrierungen
# ---------------------------------------------------------------------
from django.utils.html import format_html
from energy.models import GridDimmingSignal, SteuVEDeviceConfig


@admin.register(GridDimmingSignal)
class GridDimmingSignalAdmin(admin.ModelAdmin):
    list_display = (
        "id_short",
        "home",
        "source",
        "target_max_grid_kw",
        "status_badge",
        "started_at",
        "expires_at",
        "cleared_at",
    )
    list_filter = ("is_active", "source", "started_at")
    search_fields = ("home__name", "owner_user__email", "source")
    readonly_fields = ("created_at", "started_at")
    raw_id_fields = ("home", "owner_user", "tenant")

    def id_short(self, obj):
        return str(obj.id)[:8] + "..."
    id_short.short_description = "ID"

    def status_badge(self, obj):
        if obj.is_active:
            return format_html(
                '<span style="background-color: #ef4444; color: white; padding: 3px 8px; border-radius: 6px; font-weight: bold; font-size: 11px;">🔴 GEDIMMT ({0} kW)</span>',
                obj.target_max_grid_kw,
            )
        return format_html(
            '<span style="background-color: #10b981; color: white; padding: 3px 8px; border-radius: 6px; font-weight: bold; font-size: 11px;">🟢 NORMALBETRIEB</span>'
        )
    status_badge.short_description = "§ 14a Status"


@admin.register(SteuVEDeviceConfig)
class SteuVEDeviceConfigAdmin(admin.ModelAdmin):
    list_display = (
        "device_display",
        "steuve_type",
        "priority_badge",
        "rated_power_kw",
        "minimum_power_kw",
        "dimming_state_badge",
        "is_dimmable",
        "updated_at",
    )
    list_filter = ("steuve_type", "priority", "is_currently_dimmed", "is_dimmable")
    search_fields = ("device__identifier", "device__config__name", "device__home__name")
    raw_id_fields = ("device",)

    def device_display(self, obj):
        name = obj.device.config.name if hasattr(obj.device, "config") and obj.device.config and obj.device.config.name else obj.device.identifier
        home_name = obj.device.home.name if obj.device.home else "-"
        return f"{name} ({home_name})"
    device_display.short_description = "Gerät (Haushalt)"

    def priority_badge(self, obj):
        colors = {1: "#10b981", 2: "#3b82f6", 3: "#f59e0b", 4: "#64748b"}
        color = colors.get(obj.priority, "#64748b")
        return format_html(
            f'<span style="background-color: {color}; color: white; padding: 2px 7px; border-radius: 4px; font-weight: bold; font-size: 11px;">Prio {obj.priority}</span>'
        )
    priority_badge.short_description = "Priorität"

    def dimming_state_badge(self, obj):
        if obj.is_currently_dimmed:
            return format_html(
                '<span style="background-color: #f97316; color: white; padding: 2px 7px; border-radius: 4px; font-weight: bold; font-size: 11px;">⚠️ Gedrosselt ({0} kW)</span>',
                obj.current_power_limit_kw or 0.0,
            )
        return format_html(
            '<span style="background-color: #10b981; color: white; padding: 2px 7px; border-radius: 4px; font-weight: bold; font-size: 11px;">🟢 Aktiv (100%)</span>'
        )
    dimming_state_badge.short_description = "Aktorik Status"

