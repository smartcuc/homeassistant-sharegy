#################
# energy/admin.py
#################

from django.contrib import admin
from django.utils.html import format_html, mark_safe
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
from energy.models import GridDimmingSignal, SteuVEDeviceConfig, EnWG14aDimmingAuditLog


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


@admin.register(EnWG14aDimmingAuditLog)
class EnWG14aDimmingAuditLogAdmin(admin.ModelAdmin):
    list_display = (
        "created_at",
        "home",
        "action_badge",
        "steuve_type",
        "commanded_power_limit_kw",
        "response_time_badge",
        "compliance_badge",
        "reason",
    )
    list_filter = ("action", "steuve_type", "compliance_verified", "created_at")
    search_fields = ("home__name", "device__identifier", "reason", "vnb_operator_id")
    readonly_fields = ("id", "created_at")
    raw_id_fields = ("signal", "home", "device")
    ordering = ["-created_at"]

    def action_badge(self, obj):
        colors = {
            "DIMMING_TRIGGERED": "#ef4444",
            "DEVICE_DIMMED": "#f97316",
            "DEVICE_RESTORED": "#10b981",
            "LIMIT_CLEARED": "#3b82f6",
            "COMPLIANCE_VERIFIED": "#10b981",
            "OVERRIDE_REJECTED": "#8b5cf6",
        }
        color = colors.get(obj.action, "#64748b")
        return format_html(
            '<span style="background-color: {0}; color: white; padding: 2px 8px; border-radius: 5px; font-weight: bold; font-size: 11px;">{1}</span>',
            color,
            obj.get_action_display(),
        )
    action_badge.short_description = "Aktion"

    def response_time_badge(self, obj):
        color = "#10b981" if obj.response_time_ms < 5000 else "#f59e0b" if obj.response_time_ms < 30000 else "#ef4444"
        return format_html(
            '<span style="color: {0}; font-family: monospace; font-weight: bold;">{1} ms</span>',
            color,
            obj.response_time_ms,
        )
    response_time_badge.short_description = "Latenz"

    def compliance_badge(self, obj):
        if obj.compliance_verified:
            return mark_safe('<span style="color: #10b981; font-weight: bold;">✓ 4,2 kW OK</span>')
        return mark_safe('<span style="color: #ef4444; font-weight: bold;">✗ Verletzung</span>')
    compliance_badge.short_description = "VNB Compliance"


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
        formatted_total = f"{total:,.4f}"
        return format_html(
            '<strong style="color: #2563eb; font-size: 13px;">{} ct/kWh (netto)</strong>',
            formatted_total,
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


# =====================================================================
# SG-Ready / Intelligentes Lastmanagement (BWWP, Load Priority, Estrich)
# =====================================================================

from energy.models import (
    BWWPLoadManagementConfig,
    LoadPriorityConfig,
    LoadConsumerConfig,
    FloorHeatingConfig,
)


@admin.register(BWWPLoadManagementConfig)
class BWWPLoadManagementConfigAdmin(admin.ModelAdmin):
    list_display = (
        "device_name",
        "home_name",
        "control_mode_badge",
        "sg_state_badge",
        "temp_thresholds_display",
        "min_pv_surplus_display",
        "active_badge",
        "last_switched_at",
    )
    list_filter = ("active", "control_mode", "current_sg_state")
    search_fields = ("device__name", "home__name", "last_decision_reason")
    raw_id_fields = ("home", "device")

    def device_name(self, obj):
        return obj.device.name if obj.device else "–"
    device_name.short_description = "BWWP / Wärmepumpe"

    def home_name(self, obj):
        return obj.home.name if obj.home else "–"
    home_name.short_description = "Haushalt"

    def control_mode_badge(self, obj):
        colors = {
            "hybrid": "#2563eb",
            "pv_surplus": "#10b981",
            "spot_price": "#d97706",
            "manual": "#64748b",
        }
        color = colors.get(obj.control_mode, "#64748b")
        return format_html('<span style="background-color: {}; color: white; padding: 2px 7px; border-radius: 4px; font-weight: 600; font-size: 11px;">{}</span>', color, obj.get_control_mode_display())
    control_mode_badge.short_description = "Modus"

    def sg_state_badge(self, obj):
        colors = {
            "3_boost": ("#10b981", "🔥 SG-Ready Boost"),
            "2_normal": ("#2563eb", "⚡ Normalbetrieb"),
            "1_lock": ("#ef4444", "🔒 Sperre / Standby"),
            "4_force": ("#d97706", "⚠️ Zwangsanlauf"),
        }
        color, label = colors.get(obj.current_sg_state, ("#64748b", obj.current_sg_state))
        return format_html('<span style="color: {}; font-weight: bold;">{}</span>', color, label)
    sg_state_badge.short_description = "SG-Zustand"

    def temp_thresholds_display(self, obj):
        return f"{obj.min_temp_c:.0f}°C ➔ {obj.target_temp_c:.0f}°C (Boost: {obj.boost_temp_c:.0f}°C)"
    temp_thresholds_display.short_description = "Temperaturen"

    def min_pv_surplus_display(self, obj):
        return f"{obj.min_pv_surplus_w:.0f} W"
    min_pv_surplus_display.short_description = "Min PV"

    def active_badge(self, obj):
        if obj.active:
            return mark_safe('<span style="color: #10b981; font-weight: bold;">🟢 Aktiv</span>')
        return mark_safe('<span style="color: #ef4444; font-weight: bold;">🔴 Inaktiv</span>')
    active_badge.short_description = "Aktiv"


@admin.register(LoadPriorityConfig)
class LoadPriorityConfigAdmin(admin.ModelAdmin):
    list_display = ("home_name", "master_mode_badge", "min_pv_headroom_w", "auto_dispatch_badge", "updated_at")
    list_filter = ("master_mode", "auto_dispatch_enabled")
    search_fields = ("home__name",)
    raw_id_fields = ("home",)

    def home_name(self, obj):
        return obj.home.name if obj.home else "–"
    home_name.short_description = "Haushalt"

    def master_mode_badge(self, obj):
        colors = {
            "autopilot": "#10b981",
            "pv_only": "#2563eb",
            "price_saver": "#d97706",
            "manual": "#64748b",
        }
        color = colors.get(obj.master_mode, "#64748b")
        return format_html('<span style="background-color: {}; color: white; padding: 2px 7px; border-radius: 4px; font-weight: 600; font-size: 11px;">{}</span>', color, obj.get_master_mode_display())
    master_mode_badge.short_description = "Master Modus"

    def auto_dispatch_badge(self, obj):
        if obj.auto_dispatch_enabled:
            return mark_safe('<span style="color: #10b981; font-weight: bold;">🟢 Aktiv</span>')
        return mark_safe('<span style="color: #ef4444; font-weight: bold;">🔴 Aus</span>')
    auto_dispatch_badge.short_description = "Dispatch"


@admin.register(LoadConsumerConfig)
class LoadConsumerConfigAdmin(admin.ModelAdmin):
    list_display = ("name_display", "home_name", "category_badge", "rated_power_display", "mode_badge", "is_active_badge", "created_at")
    list_filter = ("category", "mode", "is_active")
    search_fields = ("name", "device__name", "home__name")
    raw_id_fields = ("home", "device")

    def name_display(self, obj):
        return obj.name or (obj.device.name if obj.device else "–")
    name_display.short_description = "Verbraucher"

    def home_name(self, obj):
        return obj.home.name if obj.home else "–"
    home_name.short_description = "Haushalt"

    def category_badge(self, obj):
        return format_html('<span style="background-color: #f1f5f9; color: #0f172a; padding: 2px 6px; border-radius: 4px; font-weight: 600; font-size: 11px;">{}</span>', obj.get_category_display())
    category_badge.short_description = "Kategorie"

    def rated_power_display(self, obj):
        return f"{obj.rated_power_w:.0f} W"
    rated_power_display.short_description = "Nennleistung"

    def mode_badge(self, obj):
        return obj.get_mode_display()
    mode_badge.short_description = "Modus"

    def is_active_badge(self, obj):
        if obj.is_active:
            return mark_safe('<span style="color: #10b981; font-weight: bold;">🟢 Aktiv</span>')
        return mark_safe('<span style="color: #ef4444; font-weight: bold;">🔴 Inaktiv</span>')
    is_active_badge.short_description = "Aktiv"


@admin.register(FloorHeatingConfig)
class FloorHeatingConfigAdmin(admin.ModelAdmin):
    list_display = ("home_name", "controller_device", "control_mode", "active_badge", "target_room_temp_c", "boost_delta_k", "is_preheating_active", "predictive_mpc_enabled")
    list_filter = ("active", "control_mode", "is_preheating_active", "predictive_mpc_enabled")
    search_fields = ("home__name", "device__identifier")
    raw_id_fields = ("home", "device", "temp_sensor_device")

    def home_name(self, obj):
        return obj.home.name if obj.home else "–"
    home_name.short_description = "Haushalt"

    def controller_device(self, obj):
        return obj.device.identifier if obj.device else "–"
    controller_device.short_description = "Aktor"

    def active_badge(self, obj):
        if obj.active:
            return mark_safe('<span style="color: #10b981; font-weight: bold;">🟢 Aktiv</span>')
        return mark_safe('<span style="color: #ef4444; font-weight: bold;">🔴 Inaktiv</span>')
    active_badge.short_description = "Aktiv"



