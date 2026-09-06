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
from django.utils.safestring import mark_safe
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
        return mark_safe(
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
            '<span style="background-color: {0}; color: white; padding: 2px 7px; border-radius: 4px; font-weight: bold; font-size: 11px;">Prio {1}</span>',
            color,
            obj.priority,
        )
    priority_badge.short_description = "Priorität"

    def dimming_state_badge(self, obj):
        if obj.is_currently_dimmed:
            return format_html(
                '<span style="background-color: #f97316; color: white; padding: 2px 7px; border-radius: 4px; font-weight: bold; font-size: 11px;">⚠️ Gedrosselt ({0} kW)</span>',
                obj.current_power_limit_kw or 0.0,
            )
        return mark_safe(
            '<span style="background-color: #10b981; color: white; padding: 2px 7px; border-radius: 4px; font-weight: bold; font-size: 11px;">🟢 Aktiv (100%)</span>'
        )
    dimming_state_badge.short_description = "Aktorik Status"


# ---------------------------------------------------------------------
# ⚙️ EMS-SETTINGS: PREISE, TARIFE & WR-LESEZYKLEN
# ---------------------------------------------------------------------
from energy.models import EMSGlobalSettings, InverterManufacturerPollingConfig


@admin.register(EMSGlobalSettings)
class EMSGlobalSettingsAdmin(admin.ModelAdmin):
    """
    Zentrale Admin-Steuerung für alle globalen Preise, Tarife,
    Arbitrage-Schwellen und gesetzlichen Umlagen im EMS.
    """

    fieldsets = (
        (
            "💶 1. Sharegy Plattform-Umlage / Abrechnungsgebühr (Säule 2)",
            {
                "fields": (
                    "sharegy_platform_fee_ct_kwh",
                ),
                "description": "Betriebsgebühr / Plattform-Umlage pro geteilter kWh für automatisierte Zählererfassung, Clearing und Monatsabrechnungen gem. § 42b EnWG.",
            },
        ),
        (
            "🏛️ 2. Gesetzliche Abgaben, Netzentgelte & Steuern (Deutschland)",
            {
                "fields": (
                    ("grid_fee_ct_kwh", "electricity_tax_ct_kwh"),
                    ("concession_fee_ct_kwh", "kwk_levy_ct_kwh"),
                    ("special_grid_levy_ct_kwh", "offshore_levy_ct_kwh"),
                    "vat_percent",
                    "total_statutory_levies_display",
                ),
                "description": "Offizielle bundesweite Referenzwerte zur transparenten und rechtssicheren Aufschlüsselung dynamischer Börsentarife.",
            },
        ),
        (
            "💎 3. SaaS-Abonnements & Pro-Lizenzgebühren (Säule 1)",
            {
                "fields": (
                    ("saas_pricing_valid_from", "trial_days"),
                    ("pro_monthly_price_eur", "pro_yearly_price_eur"),
                    ("landlord_monthly_price_eur", "landlord_yearly_price_eur"),
                ),
                "description": "Zentrale Preissteuerung für Software-Lizenzen (Sharegy Pro & Vermieter-Quartiere) inkl. Gültigkeitsdatum und Testphase.",
            },
        ),
        (
            "⏱️ Metadaten",
            {
                "fields": ("created_at", "updated_at"),
                "classes": ("collapse",),
            },
        ),
    )

    list_display = (
        "__str__",
        "sharegy_platform_fee_ct_kwh",
        "pro_monthly_price_eur",
        "pro_yearly_price_eur",
        "updated_at",
    )
    readonly_fields = ("created_at", "updated_at", "total_statutory_levies_display")

    def changelist_view(self, request, extra_context=None):
        """
        Singleton-Komfort: Leitet direkt zum Bearbeitungsformular der globalen Einstellungen weiter.
        """
        from django.shortcuts import redirect
        from django.urls import reverse
        from energy.services.ems_settings import get_ems_global_settings

        settings_obj = get_ems_global_settings()
        return redirect(reverse("admin:energy_emsglobalsettings_change", args=[settings_obj.pk]))

    def total_statutory_levies_display(self, obj):
        if not obj:
            return "-"
        total = obj.total_statutory_levies_ct_kwh()
        return format_html(
            '<strong style="color: #2563eb; font-size: 13px;">{0:,.4f} ct/kWh (netto)</strong>',
            total,
        )
    total_statutory_levies_display.short_description = "Gesamte feste Abgaben (Summe netto)"

    def has_add_permission(self, request):
        # Singleton: Nur Hinzufügen erlauben, wenn noch kein Eintrag existiert
        if EMSGlobalSettings.objects.exists():
            return False
        return super().has_add_permission(request)

    def has_delete_permission(self, request, obj=None):
        # Löschen verhindern, um Systemkonsistenz zu wahren
        return False


@admin.register(InverterManufacturerPollingConfig)
class InverterManufacturerPollingConfigAdmin(admin.ModelAdmin):
    """
    Admin-Verwaltung für die API-Lesezyklen (Polling-Intervalle)
    je Wechselrichter- und Cloud-Hersteller.
    """

    list_display = (
        "manufacturer_name",
        "manufacturer_key",
        "polling_interval_badge",
        "min_allowed_interval_seconds",
        "is_active_badge",
        "rate_limit_notes",
        "updated_at",
    )

    list_filter = ("is_active",)
    search_fields = ("manufacturer_name", "manufacturer_key", "rate_limit_notes")
    ordering = ["manufacturer_name"]
    actions = ["activate_configs", "deactivate_configs", "set_to_fast_polling", "set_to_standard_polling"]

    def polling_interval_badge(self, obj):
        color = "#10b981" if obj.polling_interval_seconds <= 15 else "#3b82f6" if obj.polling_interval_seconds <= 30 else "#64748b"
        return format_html(
            '<span style="background-color: {0}; color: white; padding: 3px 9px; border-radius: 6px; font-weight: bold; font-size: 12px;">⏱️ {1}s</span>',
            color,
            obj.polling_interval_seconds,
        )
    polling_interval_badge.short_description = "Lesezyklus"

    def is_active_badge(self, obj):
        if obj.is_active:
            return mark_safe('<span style="color: #10b981; font-weight: 600;">🟢 Aktiv</span>')
        return mark_safe('<span style="color: #ef4444; font-weight: 600;">🔴 Pausiert</span>')
    is_active_badge.short_description = "Status"

    @admin.action(description="🟢 Ausgewählte Hersteller-Zyklen aktivieren")
    def activate_configs(self, request, queryset):
        count = queryset.update(is_active=True)
        self.message_user(request, f"{count} Hersteller-Polling-Konfigurationen aktiviert.")

    @admin.action(description="🔴 Ausgewählte Hersteller-Zyklen pausieren")
    def deactivate_configs(self, request, queryset):
        count = queryset.update(is_active=False)
        self.message_user(request, f"{count} Hersteller-Polling-Konfigurationen pausiert.")

    @admin.action(description="⚡ Auf schnellen Zyklus (15s) setzen")
    def set_to_fast_polling(self, request, queryset):
        for obj in queryset:
            interval = max(15, obj.min_allowed_interval_seconds)
            obj.polling_interval_seconds = interval
            obj.save()
        self.message_user(request, "Ausgewählte Hersteller auf schnellen Zyklus aktualisiert.")

    @admin.action(description="⏱️ Auf Standard-Zyklus (60s) setzen")
    def set_to_standard_polling(self, request, queryset):
        count = queryset.update(polling_interval_seconds=60)
        self.message_user(request, f"{count} Hersteller auf 60s Standard-Zyklus gesetzt.")

