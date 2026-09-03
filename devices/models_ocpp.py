########################
# devices/models_ocpp.py
########################

import uuid
from decimal import Decimal
from django.db import models
from django.contrib.auth import get_user_model
from django.utils import timezone

User = get_user_model()


class ChargingStation(models.Model):
    """
    Repräsentiert eine physische oder virtuelle OCPP 1.6-J / 2.0.1 Wallbox / Ladesäule.
    """
    CHARGING_MODES = [
        ("pv_surplus", "☀️ Nur Solarüberschuss"),
        ("min_pv", "⛅ Min + PV-Überschuss"),
        ("spot_price", "💶 Börsenpreisgeführt"),
        ("instant", "⚡ Sofortladen (Max. Power)"),
        ("off", "🛑 Gesperrt / Pausiert"),
    ]

    OCPP_STATUS_CHOICES = [
        ("Available", "Verfügbar"),
        ("Preparing", "Fahrzeug verbunden"),
        ("Charging", "Lädt aktiv"),
        ("SuspendedEVSE", "Pausiert (Station)"),
        ("SuspendedEV", "Pausiert (Fahrzeug voll)"),
        ("Finishing", "Ladevorgang beendet"),
        ("Reserved", "Reserviert"),
        ("Unavailable", "Nicht verfügbar"),
        ("Faulted", "Fehler / Störung"),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    home = models.ForeignKey(
        "devices.Home",
        on_delete=models.CASCADE,
        related_name="charging_stations"
    )
    
    # Eindeutige Charge Point ID in der URL (z.B. wss://sharegy.de/ocpp/<charge_point_id>)
    charge_point_id = models.CharField(
        max_length=64,
        unique=True,
        db_index=True,
        help_text="Eindeutige OCPP ChargePoint-Kennung"
    )
    
    name = models.CharField(max_length=120, default="Wallbox")
    vendor = models.CharField(max_length=100, blank=True, default="")
    model = models.CharField(max_length=100, blank=True, default="")
    serial_number = models.CharField(max_length=100, blank=True, default="")
    firmware_version = models.CharField(max_length=100, blank=True, default="")
    
    # Status & Live-Werte
    status = models.CharField(
        max_length=32,
        choices=OCPP_STATUS_CHOICES,
        default="Available",
        db_index=True
    )
    error_code = models.CharField(max_length=64, blank=True, default="NoError")
    is_online = models.BooleanField(default=False, db_index=True)
    last_heartbeat = models.DateTimeField(null=True, blank=True)
    
    # Elektrische Eigenschaften & Grenzwerte
    connectors_count = models.PositiveIntegerField(default=1)
    phases = models.PositiveIntegerField(default=3, choices=[(1, "1-phasig"), (3, "3-phasig")])
    max_current_a = models.FloatField(default=16.0, help_text="Maximaler Ladestrom je Phase in A (z.B. 16A = 11kW, 32A = 22kW)")
    min_current_a = models.FloatField(default=6.0, help_text="Minimaler Ladestrom nach IEC 61851 (Standard 6A)")
    
    # Intelligente Lademodi & Regelparameter
    smart_charging_mode = models.CharField(
        max_length=32,
        choices=CHARGING_MODES,
        default="pv_surplus"
    )
    price_threshold_ct = models.FloatField(
        default=15.0,
        help_text="Preisschwelle in ct/kWh für börsenpreisgeführtes Laden"
    )
    min_soc_target_pct = models.PositiveIntegerField(
        default=50,
        help_text="Mindest-Ziel-SoC, bis zu dem unabhängig vom Sonnenstand geladen wird"
    )

    # Telemetrie & Live-Messwerte
    active_power_w = models.FloatField(default=0.0, help_text="Aktuelle Ladeleistung in Watt")
    current_l1 = models.FloatField(default=0.0, help_text="Strom L1 in Ampere")
    current_l2 = models.FloatField(default=0.0, help_text="Strom L2 in Ampere")
    current_l3 = models.FloatField(default=0.0, help_text="Strom L3 in Ampere")
    voltage_v = models.FloatField(default=230.0, help_text="Spannung in Volt")
    
    # Aktiver Sollwert, der an die Wallbox gesendet wurde
    target_current_a = models.FloatField(default=0.0, help_text="Aktueller Soll-Ladestrom je Phase")
    
    # Zählerstände & Session-Tracking
    active_transaction_id = models.IntegerField(null=True, blank=True)
    session_energy_kwh = models.FloatField(default=0.0, help_text="Geladene Energie der aktuellen Session in kWh")
    total_energy_kwh = models.FloatField(default=0.0, help_text="Gesamter Zählerstand der Wallbox in kWh")
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "OCPP Ladestation"
        verbose_name_plural = "OCPP Ladestationen"

    def __str__(self):
        return f"{self.name} ({self.charge_point_id}) - {self.status}"

    @property
    def is_charging(self):
        return self.status == "Charging" and self.active_power_w > 50.0

    @property
    def current_power_kw(self):
        return round(self.active_power_w / 1000.0, 2)


class ChargingSession(models.Model):
    """
    Dokumentiert einen vollständigen Ladevorgang mit Beginn, Ende, Zählerständen,
    Solarer Deckungsquote und berechneten Kosten für Community-Clearing (§ 42b EnWG).
    """
    STATUS_CHOICES = [
        ("active", "Aktiv"),
        ("completed", "Abgeschlossen"),
        ("aborted", "Abgebrochen"),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    station = models.ForeignKey(
        ChargingStation,
        on_delete=models.CASCADE,
        related_name="sessions"
    )
    transaction_id = models.IntegerField(db_index=True)
    
    # Zuordnung des Nutzers (z.B. über RFID oder App)
    id_tag = models.CharField(max_length=64, blank=True, default="", help_text="RFID Tag / Auth ID")
    user = models.ForeignKey(
        User,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="charging_sessions"
    )
    
    start_time = models.DateTimeField(default=timezone.now)
    stop_time = models.DateTimeField(null=True, blank=True)
    
    meter_start_wh = models.FloatField(default=0.0)
    meter_stop_wh = models.FloatField(null=True, blank=True)
    total_energy_kwh = models.FloatField(default=0.0)
    
    # Solare Deckung und Kosten
    solar_energy_kwh = models.FloatField(default=0.0, help_text="Anteil kostenloser Sonnenstrom")
    grid_energy_kwh = models.FloatField(default=0.0, help_text="Anteil zugekaufter Netzstrom")
    solar_coverage_pct = models.FloatField(default=0.0, help_text="Prozentualer PV-Anteil")
    
    cost_eur = models.DecimalField(
        max_digits=8,
        decimal_places=2,
        default=Decimal("0.00"),
        help_text="Gesamtkosten für Community-Abrechnung"
    )
    
    stop_reason = models.CharField(max_length=64, blank=True, default="Local")
    status = models.CharField(max_length=16, choices=STATUS_CHOICES, default="active")

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-start_time"]
        verbose_name = "Ladesitzung"
        verbose_name_plural = "Ladesitzungen"

    def __str__(self):
        return f"Session #{self.transaction_id} an {self.station.name} ({self.total_energy_kwh:.2f} kWh)"


class ChargingRfidTag(models.Model):
    """
    Verknüpft physische RFID-Karten / Chips mit Benutzern für automatische
    Zugriffskontrolle und Mieterstrom-/Nachbarschafts-Abrechnung.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    home = models.ForeignKey(
        "devices.Home",
        on_delete=models.CASCADE,
        related_name="rfid_tags"
    )
    id_tag = models.CharField(max_length=64, unique=True, help_text="Eindeutige UID der RFID-Karte")
    name = models.CharField(max_length=100, default="Mein RFID-Chip")
    user = models.ForeignKey(
        User,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="rfid_tags",
        help_text="Zugeordneter Nutzer für Kostenabrechnung"
    )
    is_active = models.BooleanField(default=True)
    expiry_date = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "RFID-Ladechip"
        verbose_name_plural = "RFID-Ladechips"

    def __str__(self):
        return f"{self.name} ({self.id_tag}) - {'Aktiv' if self.is_active else 'Gesperrt'}"
