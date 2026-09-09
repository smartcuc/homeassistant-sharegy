##################
# energy/models.py
##################

import uuid
from decimal import Decimal
from django.db import models
from django.db.models import Q
from django.utils import timezone

from .ems.models import EMSSignalSource
from .ems.models_signal_type import EMSSignalType
from .models_ems_settings import EMSGlobalSettings, InverterManufacturerPollingConfig



# ---------------------------------------------------------------------
# Helper: wiederverwendbare Check-Constraints pro Model (unique names!)
# ---------------------------------------------------------------------
def owner_xor_constraints(prefix: str):
    return [
        models.CheckConstraint(
            name=f"{prefix}_owner_xor",
            condition=(
                (Q(owner_user__isnull=False) & Q(owner_membership__isnull=True))
                | (Q(owner_user__isnull=True) & Q(owner_membership__isnull=False))
            ),
        ),
        models.CheckConstraint(
            name=f"{prefix}_user_requires_no_tenant",
            condition=(Q(owner_user__isnull=True) | Q(tenant__isnull=True)),
        ),
        models.CheckConstraint(
            name=f"{prefix}_membership_requires_tenant",
            condition=(Q(owner_membership__isnull=True) | Q(tenant__isnull=False)),
        ),
    ]


# ---------------------------------------------------------------------
# Location
# ---------------------------------------------------------------------
class Location(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    tenant = models.ForeignKey(
        "core.Tenant", on_delete=models.CASCADE, null=True, blank=True
    )

    owner_user = models.ForeignKey(
        "accounts.User",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="energy_locations",
    )

    owner_membership = models.ForeignKey(
        "accounts.TenantMembership",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="energy_locations",
    )

    name = models.CharField(max_length=255, blank=True)

    street = models.CharField(max_length=255, blank=True)
    house_number = models.CharField(max_length=20, blank=True)
    postal_code = models.CharField(max_length=20, blank=True)
    city = models.CharField(max_length=100, blank=True)
    country = models.CharField(max_length=50, default="DE")

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        indexes = [
            models.Index(fields=["tenant", "city"]),
        ]
        constraints = owner_xor_constraints("location")

    def __str__(self):
        return (
            self.name
            or f"{self.street} {self.house_number}, {self.postal_code} {self.city}"
        )


# ---------------------------------------------------------------------
# EnergyAsset (Basis)
# ---------------------------------------------------------------------
class EnergyAsset(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    tenant = models.ForeignKey(
        "core.Tenant", on_delete=models.CASCADE, null=True, blank=True
    )

    owner_user = models.ForeignKey(
        "accounts.User",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="energy_assets",
    )

    owner_membership = models.ForeignKey(
        "accounts.TenantMembership",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="energy_assets",
    )

    location = models.ForeignKey(
        Location, on_delete=models.SET_NULL, null=True, blank=True
    )

    ASSET_TYPE = [
        ("pv", "PV"),
        ("battery", "Battery"),
        ("ev", "EV"),
        ("other", "Other"),
    ]
    asset_type = models.CharField(max_length=20, choices=ASSET_TYPE)

    name = models.CharField(max_length=255)

    installed_power_kw = models.DecimalField(
        max_digits=10, decimal_places=2, null=True, blank=True
    )

    installed_at = models.DateField(null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        indexes = [
            models.Index(fields=["tenant", "asset_type"]),
            models.Index(fields=["owner_user", "asset_type"]),
            models.Index(fields=["owner_membership", "asset_type"]),
        ]
        constraints = owner_xor_constraints("energyasset")

    def __str__(self):
        return f"{self.name} ({self.asset_type})"


# ---------------------------------------------------------------------
# PV Details
# ---------------------------------------------------------------------
class EnergyAssetPV(models.Model):
    asset = models.OneToOneField(
        EnergyAsset, on_delete=models.CASCADE, related_name="pv"
    )

    module_manufacturer = models.CharField(max_length=100, blank=True)
    module_type = models.CharField(max_length=100, blank=True)

    inverter_manufacturer = models.CharField(max_length=100, blank=True)
    inverter_type = models.CharField(max_length=100, blank=True)

    tilt_angle = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    azimuth = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)

    number_of_modules = models.IntegerField(null=True, blank=True)

    def __str__(self):
        return f"PV Details for {self.asset_id}"


# ---------------------------------------------------------------------
# Battery Details
# ---------------------------------------------------------------------
class EnergyAssetBattery(models.Model):
    asset = models.OneToOneField(
        EnergyAsset, on_delete=models.CASCADE, related_name="battery"
    )

    capacity_kwh = models.DecimalField(max_digits=10, decimal_places=2)
    usable_capacity_kwh = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)

    max_charge_kw = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    max_discharge_kw = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)

    efficiency = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)

    manufacturer = models.CharField(max_length=100, blank=True)
    model = models.CharField(max_length=100, blank=True)

    def __str__(self):
        return f"Battery Details for {self.asset_id}"


# ---------------------------------------------------------------------
# EV Details
# ---------------------------------------------------------------------
class EnergyAssetEV(models.Model):
    asset = models.OneToOneField(
        EnergyAsset, on_delete=models.CASCADE, related_name="ev"
    )

    battery_capacity_kwh = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    max_charging_power_kw = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)

    def __str__(self):
        return f"EV Details for {self.asset_id}"


# ---------------------------------------------------------------------
# Mapping Asset ↔ Meter
# ---------------------------------------------------------------------
class AssetMeter(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    asset = models.ForeignKey(
        EnergyAsset, on_delete=models.CASCADE, related_name="meter_links"
    )

    meter = models.ForeignKey(
        "core.Meter", on_delete=models.CASCADE, related_name="asset_links"
    )

    RELATION_TYPE = [
        ("generation", "Generation"),
        ("consumption", "Consumption"),
        ("net", "Net (grid)"),
        ("other", "Other"),
    ]

    relation_type = models.CharField(max_length=20, choices=RELATION_TYPE, default="other")

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("asset", "meter", "relation_type")
        indexes = [
            models.Index(fields=["meter", "relation_type"]),
        ]

    def __str__(self):
        return f"{self.asset} ↔ {self.meter} ({self.relation_type})"


# ---------------------------------------------------------------------
# SmartEnergySettings
# ---------------------------------------------------------------------
class SmartEnergySettings(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    tenant = models.ForeignKey(
        "core.Tenant", on_delete=models.CASCADE, null=True, blank=True
    )

    owner_user = models.ForeignKey(
        "accounts.User",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="energy_settings",
    )

    owner_membership = models.ForeignKey(
        "accounts.TenantMembership",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="energy_settings",
    )

    MODE = [
        ("info", "Information only"),
        ("auto", "Automatic control"),
        ("hybrid", "Hybrid"),
    ]

    optimization_mode = models.CharField(max_length=20, choices=MODE, default="info")

    allow_direct_control = models.BooleanField(default=False)

    optimize_ev = models.BooleanField(default=True)
    optimize_battery = models.BooleanField(default=True)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = owner_xor_constraints("smartenergy")

    def __str__(self):
        scope = "standalone" if self.owner_user_id else "tenant"
        return f"SmartEnergySettings({scope}, mode={self.optimization_mode})"


# ---------------------------------------------------------------------
# § 14a EnWG: GridDimmingSignal (Netzbetreiber-Dimmsignal)
# ---------------------------------------------------------------------
class GridDimmingSignal(models.Model):
    """
    Protokolliert und verwaltet Netzbetreiber-Dimmsignale gem. § 14a EnWG
    (Reduzierung des Netzbezugs auf 4,2 kW bei lokaler Netzüberlastung).
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    tenant = models.ForeignKey(
        "core.Tenant", on_delete=models.CASCADE, null=True, blank=True, related_name="grid_dimming_signals"
    )
    owner_user = models.ForeignKey(
        "accounts.User", on_delete=models.CASCADE, null=True, blank=True, related_name="grid_dimming_signals"
    )
    home = models.ForeignKey(
        "devices.Home", on_delete=models.CASCADE, null=True, blank=True, related_name="grid_dimming_signals"
    )

    SOURCE_CHOICES = [
        ("vnb_api", "VNB Inbound REST API"),
        ("wmsb_cls", "Smart Meter Gateway (CLS-Kanal)"),
        ("shelly_input", "Shelly Koppelrelais Digital-Input"),
        ("manual_test", "Manueller Test / Installateur-Audit"),
    ]
    source = models.CharField(max_length=30, choices=SOURCE_CHOICES, default="vnb_api")

    target_max_grid_kw = models.DecimalField(
        max_digits=6, decimal_places=2, default=Decimal("4.20"),
        help_text="Maximal erlaubter Netzbezug in kW gem. § 14a EnWG"
    )

    started_at = models.DateTimeField(default=timezone.now)
    expires_at = models.DateTimeField(null=True, blank=True)

    is_active = models.BooleanField(default=True)
    cleared_at = models.DateTimeField(null=True, blank=True)

    raw_payload = models.JSONField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "§ 14a Netz-Dimmsignal"
        verbose_name_plural = "§ 14a Netz-Dimmsignale (Netzbetreiber-Drosselung)"
        ordering = ["-started_at"]
        indexes = [
            models.Index(fields=["is_active", "started_at"]),
            models.Index(fields=["home", "is_active"]),
        ]

    def __str__(self):
        status = "🔴 AKTIV" if self.is_active else "🟢 BEENDET"
        return f"§ 14a Dimmsignal ({self.target_max_grid_kw} kW, {self.source}) - {status}"


# ---------------------------------------------------------------------
# § 14a EnWG: SteuVEDeviceConfig (Steuerbare Verbrauchseinrichtung)
# ---------------------------------------------------------------------
class SteuVEDeviceConfig(models.Model):
    """
    Konfiguration einer steuerbaren Verbrauchseinrichtung (SteuVE gem. § 14a EnWG:
    Wärmepumpe, private Wallbox, Batteriespeicher oder Klimaanlage >= 4,2 kW).
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    device = models.OneToOneField(
        "devices.Device", on_delete=models.CASCADE, related_name="steuve_config"
    )

    TYPE_CHOICES = [
        ("heat_pump", "Wärmepumpe"),
        ("wallbox", "Wallbox (Ladeeinrichtung)"),
        ("battery_storage", "Batteriespeicher (Netzladen)"),
        ("ac_cooling", "Klimagerät / Raumkühlung"),
    ]
    steuve_type = models.CharField(max_length=30, choices=TYPE_CHOICES, default="wallbox")

    rated_power_kw = models.DecimalField(
        max_digits=6, decimal_places=2, default=Decimal("11.00"),
        help_text="Nennleistung in kW"
    )
    minimum_power_kw = models.DecimalField(
        max_digits=6, decimal_places=2, default=Decimal("1.40"),
        help_text="Minimale Dimmleistung (z. B. 1-phasig 6A = 1,4 kW)"
    )

    priority = models.PositiveSmallIntegerField(
        default=2,
        help_text="1: Höchste Priorität (Wärme), 2: Speicher, 3: Nachrangig / Drosselbar (Wallbox)"
    )

    is_dimmable = models.BooleanField(default=True)
    is_currently_dimmed = models.BooleanField(default=False)
    current_power_limit_kw = models.DecimalField(
        max_digits=6, decimal_places=2, null=True, blank=True
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "§ 14a SteuVE-Konfiguration"
        verbose_name_plural = "§ 14a SteuVE-Geräte (Steuerbare Verbrauchseinrichtungen)"
        ordering = ["priority", "-rated_power_kw"]

    def __str__(self):
        dim_state = f"⚠️ Gedimmt auf {self.current_power_limit_kw} kW" if self.is_currently_dimmed else "🟢 Normalbetrieb"
        return f"SteuVE: {self.device.name} ({self.get_steuve_type_display()}) - {dim_state}"


# ---------------------------------------------------------------------
# § 14a EnWG: Audit-Logging für Netzdrosselungs- und Steuerungseingriffe
# ---------------------------------------------------------------------
class EnWG14aDimmingAuditLog(models.Model):
    """
    Revisionssicheres Audit-Log für alle netz- und steuerungsrelevanten Eingriffe
    gem. § 14a EnWG (BNetzA Festlegung BK6-22-300).
    Dokumentiert Dimmsignale, Soll-/Ist-Leistungen, Reaktionszeiten und Compliance-Status
    für den Nachweis gegenüber Verteilnetzbetreibern (VNB).
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    signal = models.ForeignKey(
        GridDimmingSignal,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="audit_logs",
    )

    home = models.ForeignKey(
        "devices.Home",
        on_delete=models.CASCADE,
        related_name="enwg_dimming_audit_logs",
    )

    device = models.ForeignKey(
        "devices.Device",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="enwg_dimming_audit_logs",
    )

    ACTION_CHOICES = [
        ("DIMMING_TRIGGERED", "Dimmsignal empfangen & aktiviert"),
        ("DEVICE_DIMMED", "SteuVE-Leistung gedrosselt"),
        ("DEVICE_RESTORED", "SteuVE-Drosselung aufgehoben"),
        ("LIMIT_CLEARED", "Netzdrosselung beendet"),
        ("COMPLIANCE_VERIFIED", "4,2 kW Compliance am Netzanschlusspunkt bestätigt"),
        ("OVERRIDE_REJECTED", "Manueller Eingriff abgewiesen (Netzsicherheitsvorrang)"),
    ]
    action = models.CharField(max_length=40, choices=ACTION_CHOICES, db_index=True)

    steuve_type = models.CharField(max_length=30, blank=True, default="")
    commanded_power_limit_kw = models.DecimalField(max_digits=6, decimal_places=2, null=True, blank=True)
    power_before_kw = models.DecimalField(max_digits=6, decimal_places=2, null=True, blank=True)
    power_after_kw = models.DecimalField(max_digits=6, decimal_places=2, null=True, blank=True)

    pv_power_kw = models.DecimalField(max_digits=6, decimal_places=2, null=True, blank=True)
    battery_power_kw = models.DecimalField(max_digits=6, decimal_places=2, null=True, blank=True)
    grid_power_kw = models.DecimalField(max_digits=6, decimal_places=2, null=True, blank=True)

    response_time_ms = models.PositiveIntegerField(
        default=0,
        help_text="Aktor-Reaktionszeit in Millisekunden (Nachweis der < 30s Frist)",
    )

    compliance_verified = models.BooleanField(
        default=True,
        help_text="Gesetzliches 4,2 kW Netzkontingent am Netzanschlusspunkt eingehalten",
    )

    vnb_operator_id = models.CharField(max_length=100, blank=True, default="")
    reason = models.CharField(max_length=255, blank=True, default="")
    metadata = models.JSONField(default=dict, blank=True)

    created_at = models.DateTimeField(auto_now_add=True, db_index=True)

    class Meta:
        verbose_name = "§ 14a EnWG Dimm-Audit-Log"
        verbose_name_plural = "§ 14a EnWG Dimm-Audit-Logs (Revisionsnachweis)"
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["home", "-created_at"]),
            models.Index(fields=["action", "-created_at"]),
            models.Index(fields=["compliance_verified", "-created_at"]),
        ]

    def __str__(self):
        return f"AuditLog: {self.home.name} - {self.get_action_display()} ({self.created_at.strftime('%d.%m.%Y %H:%M:%S')})"


# ---------------------------------------------------------------------
# SG-Ready / Lastmanagement: BWWPLoadManagementConfig
# ---------------------------------------------------------------------
class BWWPLoadManagementConfig(models.Model):
    """
    Konfiguration für intelligentes Lastmanagement von Brauchwasserwärmepumpen (BWWP)
    und Wärmepumpen (SG-Ready State 2 / State 3, PV-Überschuss, dynamische Börsentarife,
    Temperatur-Grenzwerte und Verdichterschutz).
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    home = models.ForeignKey(
        "devices.Home", on_delete=models.CASCADE, related_name="bwwp_configs"
    )

    device = models.OneToOneField(
        "devices.Device", on_delete=models.CASCADE, related_name="bwwp_config"
    )

    active = models.BooleanField(
        default=True,
        help_text="Aktiviert das automatische BWWP-Lastmanagement"
    )

    MODE_CHOICES = [
        ("hybrid", "Hybrid (PV-Überschuss & Günstige Börsenstunden)"),
        ("pv_surplus", "Nur PV-Überschuss"),
        ("spot_price", "Nur Börsenstrompreis (Spotmarkt)"),
        ("manual", "Manuell (Keine Automatik)"),
    ]
    control_mode = models.CharField(
        max_length=20, choices=MODE_CHOICES, default="hybrid"
    )

    # Temperaturschwellen (°C)
    min_temp_c = models.DecimalField(
        max_digits=4, decimal_places=1, default=Decimal("45.0"),
        help_text="Minimale Wohlfühltemperatur (°C) – darunter wird unabhängig vom Preis geheizt"
    )
    target_temp_c = models.DecimalField(
        max_digits=4, decimal_places=1, default=Decimal("52.0"),
        help_text="Standard-Solltemperatur (°C)"
    )
    boost_temp_c = models.DecimalField(
        max_digits=4, decimal_places=1, default=Decimal("60.0"),
        help_text="Erhöhte Solltemperatur für SG-Ready Boost (°C)"
    )
    max_safety_temp_c = models.DecimalField(
        max_digits=4, decimal_places=1, default=Decimal("65.0"),
        help_text="Absoluter Überhitzungsschutz (°C) – schaltet Relais sofort ab"
    )

    # PV & Preis Schwellenwerte
    min_pv_surplus_w = models.DecimalField(
        max_digits=6, decimal_places=1, default=Decimal("800.0"),
        help_text="Mindest-PV-Überschuss (W) zur Aktivierung des SG-Ready Boost"
    )
    max_price_threshold_ct = models.DecimalField(
        max_digits=5, decimal_places=2, default=Decimal("18.00"),
        help_text="Maximaler Strompreis (ct/kWh) für preisgesteuertes Heizen"
    )
    battery_soc_reserve_pct = models.DecimalField(
        max_digits=4, decimal_places=1, default=Decimal("50.0"),
        help_text="Mindest-Akkustand (%), bevor PV-Überschuss in die BWWP fließt"
    )

    # Verdichter- und Taktschutz (Compressor Protection)
    min_run_time_minutes = models.PositiveSmallIntegerField(
        default=20,
        help_text="Mindestlaufzeit (Minuten) nach dem Einschalten zum Verdichterschutz"
    )
    min_cooldown_minutes = models.PositiveSmallIntegerField(
        default=15,
        help_text="Mindestruhezeit (Minuten) nach dem Abschalten gegen Takten"
    )

    # Laufzeit-Zustand & Telemetrie
    SG_STATE_CHOICES = [
        ("1_lock", "Sperre / Standby"),
        ("2_normal", "Normalbetrieb"),
        ("3_boost", "SG-Ready Boost (Verstärkter Betrieb)"),
        ("4_force", "Zwangsanlauf"),
    ]
    current_sg_state = models.CharField(
        max_length=20, choices=SG_STATE_CHOICES, default="2_normal"
    )

    last_switched_at = models.DateTimeField(null=True, blank=True)
    last_decision_reason = models.CharField(max_length=255, blank=True, default="")
    manual_override_until = models.DateTimeField(null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["home", "active"]),
        ]

    def __str__(self):
        mode_str = self.get_control_mode_display()
        return f"BWWP Lastmanagement: {self.device.name} ({mode_str}) - {self.get_current_sg_state_display()}"


# ---------------------------------------------------------------------
# Smart Load Management: LoadPriorityConfig & LoadConsumerConfig
# ---------------------------------------------------------------------
def default_priority_order():
    return ["battery", "bwwp", "floor_heating", "wallbox", "heatpump", "pool", "ac", "appliances", "heating_rod"]


class LoadPriorityConfig(models.Model):
    """
    Zentrale Prioritäten-Kaskade (Merit-Order) und Master-Modus für alle
    steuerbaren Lasten eines Haushalts.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    home = models.OneToOneField(
        "devices.Home", on_delete=models.CASCADE, related_name="load_priority_config"
    )

    MASTER_MODE_CHOICES = [
        ("autopilot", "Autopilot (KI, PV-Überschuss & Börsenpreise)"),
        ("pv_only", "Nur PV-Überschuss (Maximale Autarkie)"),
        ("price_saver", "Sparfuchs (Börsen-Tiefstpreise & Spotmarkt)"),
        ("manual", "Manuell / Urlaub (Automatik pausiert)"),
    ]
    master_mode = models.CharField(
        max_length=20, choices=MASTER_MODE_CHOICES, default="autopilot"
    )

    priority_order = models.JSONField(
        default=default_priority_order,
        help_text="Reihenfolge der Lasten für die Zuteilung von PV-Überschuss und Schaltfenstern"
    )

    min_pv_headroom_w = models.DecimalField(
        max_digits=6, decimal_places=1, default=Decimal("200.0"),
        help_text="Sicherheits-Reserve (W) beim Schalten von Zusatzlasten"
    )

    auto_dispatch_enabled = models.BooleanField(
        default=True,
        help_text="Aktiviert die globale Dispatch-Engine für alle Verbraucher"
    )

    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Prioritäten-Kaskade ({self.home.name}): {self.get_master_mode_display()}"


class LoadConsumerConfig(models.Model):
    """
    Konfiguration für flexible Großverbraucher (Poolpumpen, Klimaanlagen,
    White Goods / Haushaltsgeräte, Heizstäbe, Fußbodenheizung).
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    home = models.ForeignKey(
        "devices.Home", on_delete=models.CASCADE, related_name="load_consumers"
    )

    device = models.ForeignKey(
        "devices.Device", on_delete=models.CASCADE, related_name="load_consumer_configs"
    )

    CATEGORY_CHOICES = [
        ("pool", "Pool- & Filterpumpe"),
        ("ac", "Klimaanlage / Raumkühlung"),
        ("floor_heating", "Fußbodenheizung & Estrich-Speicher"),
        ("appliances", "Haushaltsgerät (Waschmaschine/Spüler)"),
        ("heating_rod", "Heizstab / Power-to-Heat"),
        ("bwwp", "Brauchwasserwärmepumpe"),
        ("wallbox", "Wallbox / E-Auto"),
        ("battery", "Heimspeicher"),
        ("other", "Sonstiger flexibler Verbraucher"),
    ]
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES, default="pool")

    name = models.CharField(max_length=100, blank=True)

    rated_power_w = models.DecimalField(
        max_digits=7, decimal_places=1, default=Decimal("1000.0"),
        help_text="Typische Nennleistung in Watt"
    )

    MODE_CHOICES = [
        ("hybrid", "Hybrid (Solar & Börsenpreis)"),
        ("pv_surplus", "Nur Solarüberschuss"),
        ("spot_price", "Nur Börsenpreise"),
        ("manual", "Manuell"),
    ]
    mode = models.CharField(max_length=20, choices=MODE_CHOICES, default="hybrid")

    min_daily_runtime_minutes = models.PositiveIntegerField(
        default=0,
        help_text="Garantierte tägliche Mindestlaufzeit (z. B. 300 Min für 5h Poolfilterung)"
    )
    daily_runtime_completed_minutes = models.PositiveIntegerField(default=0)
    last_run_reset_date = models.DateField(default=timezone.now)

    custom_settings = models.JSONField(
        default=dict, blank=True,
        help_text="Kategoriespezifische Parameter (z.B. pre_cool_delta_c, ready_to_start)"
    )

    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["category", "name"]
        indexes = [
            models.Index(fields=["home", "category"]),
        ]

    def __str__(self):
        return f"{self.name or self.device.name} ({self.get_category_display()})"


# ---------------------------------------------------------------------
# FloorHeatingConfig: Intelligente Fußbodenheizung & thermischer Estrich-Speicher
# ---------------------------------------------------------------------
class FloorHeatingConfig(models.Model):
    """
    Konfiguration und State-Machine für Fußbodenheizungen & thermische Bauteilaktivierung (Estrich).
    Nutzt den Estrich als thermischen Puffer (+0,5°C bis +1,5°C Vorladung bei PV-Überschuss / Negativpreisen).
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    home = models.OneToOneField(
        "devices.Home", on_delete=models.CASCADE, related_name="floor_heating_config"
    )

    # Schaltrelais / Heizkreisverteiler oder Wärmepumpen-Modbus
    device = models.ForeignKey(
        "devices.Device", on_delete=models.SET_NULL, null=True, blank=True,
        related_name="floor_heating_controllers",
        help_text="Heizkreispumpe, Shelly Relais oder Stellantrieb-Aktor"
    )

    # Optionaler Raum-/Estrich-Temperatursensor
    temp_sensor_device = models.ForeignKey(
        "devices.Device", on_delete=models.SET_NULL, null=True, blank=True,
        related_name="floor_heating_sensors",
        help_text="Temperatursensor im Referenzraum oder Estrich-Fühler"
    )

    active = models.BooleanField(default=True)

    CONTROL_MODE_CHOICES = [
        ("autopilot", "Autopilot (Solar- & Börsenpreis-Vorladung)"),
        ("pv_only", "Nur PV-Überschuss"),
        ("price_saver", "Sparfuchs (Günstigste Börsenstunden)"),
        ("comfort", "Komfortbetrieb (Feste Solltemperatur)"),
        ("manual", "Manuell"),
    ]
    control_mode = models.CharField(
        max_length=20, choices=CONTROL_MODE_CHOICES, default="autopilot"
    )

    target_room_temp_c = models.DecimalField(
        max_digits=4, decimal_places=1, default=Decimal("21.0"),
        help_text="Standard-Zieltemperatur im Raum (°C)"
    )

    boost_delta_k = models.DecimalField(
        max_digits=3, decimal_places=1, default=Decimal("1.0"),
        help_text="Thermische Vorladung / Überwärmungs-Delta (+K, z. B. +1,0°C bei Überschuss)"
    )

    max_floor_temp_c = models.DecimalField(
        max_digits=4, decimal_places=1, default=Decimal("24.5"),
        help_text="Überhitzungsschutz: Maximale Raum-/Estrich-Temperatur (°C)"
    )

    min_pv_surplus_w = models.DecimalField(
        max_digits=6, decimal_places=1, default=Decimal("1000.0"),
        help_text="Mindest-Solarüberschuss (W) für automatische Vorladung"
    )

    max_spot_price_ct_kwh = models.DecimalField(
        max_digits=5, decimal_places=2, default=Decimal("16.00"),
        help_text="Maximaler Strompreis (ct/kWh) für netzbasierte Vorladung"
    )

    estrich_area_sqm = models.DecimalField(
        max_digits=6, decimal_places=1, default=Decimal("120.0"),
        help_text="Beheizte Estrich-Fläche in m² zur Kapazitätsberechnung"
    )

    # 🧠 Prädiktive KI-Wetter & MPC Vorlauf-Regelung
    predictive_mpc_enabled = models.BooleanField(
        default=True,
        help_text="Aktiviert KI-Wetter-Vorhersagen & dynamische Vorlauf-Optimierung (MPC)"
    )
    heating_curve_slope = models.DecimalField(
        max_digits=3, decimal_places=2, default=Decimal("0.60"),
        help_text="Heizkurven-Steilheit für Fußbodenheizung (typisch 0.4 bis 0.8)"
    )
    solar_gain_compensation = models.BooleanField(
        default=True,
        help_text="Automatische Vorlaufabsenkung bei starker prognostizierter Sonneneinstrahlung"
    )

    # Runtime & Safety States
    is_preheating_active = models.BooleanField(
        default=False,
        help_text="Gibt an, ob aktuell eine thermische Vorladung aktiv ist"
    )
    last_switched_at = models.DateTimeField(null=True, blank=True)
    min_run_minutes = models.PositiveIntegerField(
        default=30,
        help_text="Mindestlaufzeit (Min) zur Vermeidung von Pumpen-/Ventiltakten"
    )
    min_rest_minutes = models.PositiveIntegerField(
        default=15,
        help_text="Mindestruhezeit (Min) vor erneutem Einschalten"
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"Fußbodenheizung ({self.home.name}) - {self.get_control_mode_display()} (Soll {self.target_room_temp_c}°C)"
