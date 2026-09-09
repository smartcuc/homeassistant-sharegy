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

    OCPP_VERSION_CHOICES = [
        ("ocpp1.6", "OCPP 1.6-J"),
        ("ocpp2.0.1", "OCPP 2.0.1"),
        ("ocpp2.1", "OCPP 2.1"),
    ]

    V2G_MODES = [
        ("off", "Aus / Nur Laden"),
        ("v2h_home", "V2H Heimspeicher-Puffer"),
        ("v2g_grid", "V2G Börsenstrom-Arbitrage"),
        ("v2x_auto", "V2X Smart Auto"),
        ("peak_shaving", "⚡ Peak Shaving (Lastspitzenkappung)"),
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
    
    ocpp_version = models.CharField(
        max_length=16,
        choices=OCPP_VERSION_CHOICES,
        default="ocpp1.6",
        help_text="Aktive oder ausgehandelte OCPP Protokollversion"
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

    # 🚗 V2G & V2H Bidirektionales Laden (ISO 15118-20 / OCPP 2.0.1 / OCPP 2.1)
    supports_bidirectional = models.BooleanField(default=False, help_text="Wallbox und Fahrzeug unterstützen bidirektionales Laden (V2G/V2H)")
    v2g_mode = models.CharField(max_length=32, choices=V2G_MODES, default="off", help_text="Aktiver V2G/V2H Betriebsmodus")
    v2g_min_soc_pct = models.PositiveIntegerField(default=50, help_text="Sicherheits-Mindestladestand des Fahrzeugakkus in %")
    v2g_max_discharge_power_kw = models.FloatField(default=11.0, help_text="Max. Entladeleistung in kW für Haus- oder Netzeinspeisung")
    v2g_discharge_power_w = models.FloatField(default=0.0, help_text="Aktuelle Live-Entladeleistung in Watt")
    
    # ⏱️ Smart Departure Guarantee (ISO 15118-20)
    departure_time = models.TimeField(null=True, blank=True, help_text="Tägliche Abfahrtszeit für garantierte Mindestladung (z.B. 07:30)")
    target_departure_soc_pct = models.PositiveIntegerField(default=80, help_text="Ziel-SoC zur Abfahrtszeit in %")
    
    # ⚡ Grid Peak Shaving (§ 14a EnWG / Lastspitzenkappung)
    peak_shaving_threshold_w = models.FloatField(default=4200.0, help_text="Netzbezugsschwelle in Watt für Peak Shaving Entladung")
    
    # 🛡️ Battery Health Care & Degradation Protection
    battery_care_mode = models.BooleanField(default=True, help_text="Schonendes Laden/Entladen zur Verlängerung der Batterielebensdauer")
    max_c_rate = models.FloatField(default=0.5, help_text="Maximale Dauerentladerate bezogen auf die Akkukapazität (C-Rate)")
    
    # Fahrzeug-Batterie- und ISO 15118-20 Telemetrie
    ev_battery_capacity_kwh = models.FloatField(default=77.0, help_text="Brutto-Kapazität der Fahrzeugbatterie in kWh")
    ev_soc_pct = models.FloatField(null=True, blank=True, help_text="Aktueller State of Charge (SoC) des Elektroautos in %")
    iso15118_evccid = models.CharField(max_length=128, blank=True, default="", help_text="ISO 15118 EVCCID des Fahrzeugs")
    iso15118_emaid = models.CharField(max_length=128, blank=True, default="", help_text="ISO 15118 Contract eMAID (Plug & Charge)")
    
    # OCPP 2.0.1 / 2.1 Device Model & Variable Monitoring Storage
    device_variables = models.JSONField(default=dict, blank=True, help_text="Gespeicherte Device-Model-Variablen (OCPP 2.0.1/2.1)")

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
    
    # Reservierungs-Status (OCPP 1.6 Reservation Profile)
    reservation_id = models.IntegerField(null=True, blank=True, help_text="Aktive Reservierungs-ID")
    reserved_id_tag = models.CharField(max_length=64, blank=True, default="", help_text="RFID Tag / Auth ID der Reservierung")
    reservation_expiry = models.DateTimeField(null=True, blank=True, help_text="Ablaufzeitpunkt der Reservierung")

    # Local Auth List Management (OCPP 1.6 Local Auth List Profile)
    local_auth_list_version = models.IntegerField(default=0, help_text="Version der lokalen Offline-Auth-Liste auf der Box")

    # Diagnostics & Firmware Management (OCPP 1.6 Firmware Management Profile)
    diagnostics_status = models.CharField(max_length=32, blank=True, default="Idle", help_text="Status des Diagnostics-Uploads")
    last_diagnostics_file = models.CharField(max_length=255, blank=True, default="", help_text="Name der letzten Diagnosedatei")

    # Smart Charging Schedule Snapshot (OCPP 1.6 GetCompositeSchedule)
    composite_schedule_data = models.JSONField(null=True, blank=True, help_text="Letzter empfangener zusammengesetzter Ladefahrplan")

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
        return (self.status == "Charging") or (self.active_transaction_id is not None and self.active_power_w > 50.0)

    @property
    def is_discharging_v2g(self):
        return self.v2g_discharge_power_w > 50.0

    @property
    def current_power_kw(self):
        if self.is_discharging_v2g:
            return -round(self.v2g_discharge_power_w / 1000.0, 2)
        return round(self.active_power_w / 1000.0, 2)

    @property
    def charging_mode(self):
        return self.smart_charging_mode

    @property
    def max_charge_power_kw(self):
        return round((float(self.max_current_a or 16.0) * 230.0 * int(self.phases or 3)) / 1000.0, 1)

    @property
    def min_charge_current(self):
        return float(self.min_current_a or 6.0)


class ChargingSession(models.Model):
    """
    Dokumentiert einen vollständigen Ladevorgang mit Beginn, Ende, Zählerständen,
    Solarer Deckungsquote, V2G-Entladung und berechneten Kosten für Community-Clearing (§ 42b EnWG).
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
    
    # 🚗 V2G / V2H Entladerückspeisung & Erträge
    v2g_discharged_kwh = models.FloatField(default=0.0, help_text="Ins Haus / Netz entladene Energie in kWh")
    v2g_earnings_eur = models.DecimalField(
        max_digits=8,
        decimal_places=2,
        default=Decimal("0.00"),
        help_text="Erwirtschafteter Ertrag aus V2G-Börsenarbitrage / V2H-Einsparung"
    )
    
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
