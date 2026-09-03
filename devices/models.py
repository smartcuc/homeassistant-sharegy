#####################
# devices/models.py
#####################

import uuid
import secrets
from django.core.cache import cache

from django.db import models
from zoneinfo import available_timezones
from django.contrib.auth import get_user_model

from channels.layers import get_channel_layer

from asgiref.sync import async_to_sync


User = get_user_model()

from zoneinfo import available_timezones

TIMEZONE_CHOICES = sorted([(tz, tz) for tz in available_timezones()])


# ============================================================
# ✅ MQTT PROFILE
# ============================================================

class MQTTProfile(models.Model):

    slug = models.SlugField(
        unique=True
    )

    name = models.CharField(
        max_length=100
    )

    active = models.BooleanField(
        default=True
    )

    def __str__(self):
        return self.name


# ============================================================
# ✅ HOME (MQTT + CORE)
# ============================================================

def generate_mqtt_token():
    return secrets.token_hex(8).upper()

class Home(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="homes"
    )

    name = models.CharField(max_length=100)

    timezone = models.CharField(
        max_length=64,
        default="UTC",
        choices=TIMEZONE_CHOICES,
    )

    postal_code = models.CharField(
        max_length=10,
        blank=True,
        default="",
    )

    city = models.CharField(
        max_length=100,
        blank=True,
        default="",
    )

    latitude = models.FloatField(
        null=True,
        blank=True,
    )

    longitude = models.FloatField(
        null=True,
        blank=True,
    )

    # ✅ MQTT (nur Transport!)
    mqtt_token = models.CharField(
        max_length=16,
        unique=True,
        default=generate_mqtt_token,
        editable=False,
    )

    mqtt_username = models.CharField(max_length=100, blank=True)
    mqtt_password = models.CharField(max_length=100, blank=True)
    mqtt_provisioned = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        if not self.mqtt_username:
            self.mqtt_username = self.mqtt_token

        if not self.mqtt_password:
            self.mqtt_password = secrets.token_hex(16)

        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.name} ({self.user_id})"


# ============================================================
# ✅ STRUCTURE (JETZT WIRKLICH UNABHÄNGIG ✅)
# ============================================================

class Floor(models.Model):
    name = models.CharField(max_length=50)

    def __str__(self):
        return self.name


class Room(models.Model):
    name = models.CharField(max_length=50)

    def __str__(self):
        return self.name


# ============================================================
# ✅ SEMANTIC
# ============================================================

class DeviceRole(models.Model):
    key = models.CharField(max_length=20, unique=True)
    label = models.CharField(max_length=50)

    def __str__(self):
        return self.label

class MetricDefinition(models.Model):
    key = models.CharField(max_length=50, unique=True)
    name = models.CharField(max_length=100)
    unit = models.CharField(max_length=20)

    def __str__(self):
        return self.name


# ============================================================
# ✅ DEVICE (NUR TECHNISCH!)
# ============================================================

class Device(models.Model):

    home = models.ForeignKey(
        Home,
        on_delete=models.CASCADE,
        related_name="devices"
    )

    identifier = models.CharField(max_length=100)

    mqtt_profile = models.ForeignKey(
        MQTTProfile,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="devices",
    )
    
    # ✅ NEU: technischer Status
    configured = models.BooleanField(default=False, db_index=True)
    
    active = models.BooleanField(
        default=True,
        db_index=True,
    )

    pending_delete = models.BooleanField(
        default=False,
        db_index=True,
    )

    delete_after = models.DateTimeField(
        null=True,
        blank=True,
    )

    # 🔥 Lifecycle
    first_seen = models.DateTimeField(auto_now_add=True)
    last_seen = models.DateTimeField(null=True, blank=True)

    # 🔥 Standard
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ("home", "identifier")
        indexes = [
            models.Index(fields=["home", "identifier"]),
        ]

    def __str__(self):
        return self.identifier

    @property
    def name(self):
        cfg = getattr(self, "config", None)
        if cfg and cfg.name:
            return cfg.name
        return self.identifier



# ============================================================
# ✅ DEVICE CONFIG (KERN)
# ============================================================

class DeviceConfig(models.Model):

    device = models.OneToOneField(
        Device,
        on_delete=models.CASCADE,
        related_name="config"
    )

    # ✅ Anzeige
    name = models.CharField(max_length=255, blank=True)

    # ✅ Semantik
    role = models.ForeignKey(
        DeviceRole,
        null=True,
        blank=True,
        on_delete=models.SET_NULL
    )

    generator_type = models.ForeignKey(
        "producer.GeneratorType",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
    )

    metric_definition = models.ForeignKey(
        MetricDefinition,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
    )

    energy_signal_type = models.ForeignKey(
        "energy.EMSSignalType",
        null=True,
        blank=True,
        on_delete=models.PROTECT,
    )

    # ✅ Location (frei!)
    home = models.ForeignKey(
        Home,
        on_delete=models.CASCADE
    )

    floor = models.ForeignKey(
        Floor,
        null=True,
        blank=True,
        on_delete=models.SET_NULL
    )

    room = models.ForeignKey(
        Room,
        null=True,
        blank=True,
        on_delete=models.SET_NULL
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    # ✅ derived
    def display_name(self):
        return self.name or self.device.identifier

    def is_classified(self):

        if self.role is None:
            return False

        if self.metric_definition is None:
            return False

        if self.energy_signal_type is None:
            return False

        if self.role.key == "producer":

            return self.generator_type is not None and (
                self.room is not None or self.floor is not None
            )

        return self.room is not None or self.floor is not None

    def __str__(self):
        return self.display_name()


# ============================================================
# ✅ DEVICE METRIC (UNVERÄNDERT)
# ============================================================

class DeviceMetric(models.Model):
    device = models.ForeignKey(
        Device,
        on_delete=models.CASCADE,
        related_name="metrics"
    )

    metric_key = models.CharField(max_length=64)
    unit = models.CharField(max_length=16)

    value = models.FloatField(null=True, blank=True)
    data = models.JSONField(null=True, blank=True)

    timestamp = models.DateTimeField()
    created_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        is_new = self.pk is None

        old_value = None

        if not is_new:
            old_value = (
                DeviceMetric.objects.filter(pk=self.pk)
                .values_list("value", flat=True)
                .first()
            )

        super().save(*args, **kwargs)

        if not is_new:
            if (old_value is None and self.value is None):
                return
            if old_value == self.value:
                return

        if self.metric_key != "power":
            return

        user_id = self.device.home.user_id

        cache_key = f"ws_update_{user_id}"
        if cache.get(cache_key):
            return
        cache.set(cache_key, True, timeout=1)

        channel_layer = get_channel_layer()
        if not channel_layer:
            return

        async_to_sync(channel_layer.group_send)(
            f"energy_{user_id}",
            {
                "type": "send_energy_update",
                "data": {
                    "type": "metric_update",
                    "device_id": self.device_id,
                    "metric": self.metric_key,
                    "value": self.value,
                    "unit": self.unit,
                    "timestamp": self.timestamp.isoformat(),
                },
            },
        )

    class Meta:
        indexes = [
            models.Index(
                fields=[
                    "timestamp",
                    "device",
                    "metric_key",
                ],
                name="dm_ts_dev_key_idx",
            ),
            models.Index(
                fields=[
                    "device",
                    "metric_key",
                    "-timestamp",
                ],
                name="metric_latest_idx",
            ),
            models.Index(
                fields=[
                    "device",
                    "-timestamp",
                ],
                name="dm_device_timestamp_idx",
            ),
        ]


class DeviceLatestMetric(models.Model):
    """
    High-Performance Snapshot Table für den jeweils aktuellsten Messwert pro Gerät & Metrik.
    Eliminiert teure subqueries/order_by("-timestamp") Scans auf Millionen Zeilen.
    """
    device = models.ForeignKey(
        Device,
        on_delete=models.CASCADE,
        related_name="latest_metrics",
    )
    metric_key = models.CharField(max_length=64, db_index=True)
    value = models.FloatField(null=True, blank=True)
    unit = models.CharField(max_length=16, blank=True, default="")
    data = models.JSONField(null=True, blank=True)
    timestamp = models.DateTimeField()
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["device", "metric_key"],
                name="unique_device_latest_metric",
            )
        ]
        indexes = [
            models.Index(fields=["device", "metric_key"], name="dev_latest_metric_idx"),
        ]

    def __str__(self):
        return f"{self.device_id} - {self.metric_key}: {self.value}"


class DeviceResource(models.Model):
    device = models.OneToOneField(
        Device,
        on_delete=models.CASCADE,
        related_name="resource",
    )

    attributes = models.JSONField(
        default=dict,
        blank=True,
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
    )

    updated_at = models.DateTimeField(
        auto_now=True,
    )

    def __str__(self):
        return self.device.identifier


# ============================================================
# ✅ METRIC AGGREGATIONS
# ============================================================

class DeviceMetric1m(models.Model):

    device = models.ForeignKey(
        "Device",
        on_delete=models.CASCADE
    )

    metric_key = models.CharField(
        max_length=64,
        db_index=True,
        null=True,
        blank=True,
    )

    bucket = models.DateTimeField(
        db_index=True
    )

    avg = models.FloatField()
    min = models.FloatField()
    max = models.FloatField()
    count = models.IntegerField()

    energy_wh = models.FloatField(
        null=True,
        blank=True,
    )

    class Meta:

        unique_together = (
            "device",
            "metric_key",
            "bucket",
        )

        indexes = [

            models.Index(
                fields=[
                    "device",
                    "metric_key",
                    "bucket",
                ]
            ),

            models.Index(
                fields=[
                    "bucket",
                    "metric_key",
                ]
            ),

        ]


class DeviceMetric5m(models.Model):

    device = models.ForeignKey(
        "Device",
        on_delete=models.CASCADE
    )

    metric_key = models.CharField(
        max_length=64,
        db_index=True,
        null=True,
        blank=True,
    )

    bucket = models.DateTimeField(
        db_index=True
    )

    avg = models.FloatField()
    min = models.FloatField()
    max = models.FloatField()
    count = models.IntegerField()

    energy_wh = models.FloatField(
        null=True,
        blank=True,
    )

    class Meta:

        unique_together = (
            "device",
            "metric_key",
            "bucket",
        )

        indexes = [

            models.Index(
                fields=[
                    "device",
                    "metric_key",
                    "bucket",
                ]
            ),

            models.Index(
                fields=[
                    "bucket",
                    "metric_key",
                ]
            ),

        ]


class DeviceMetric15m(models.Model):

    device = models.ForeignKey(
        "Device",
        on_delete=models.CASCADE
    )

    metric_key = models.CharField(
        max_length=64,
        db_index=True,
        null=True,
        blank=True,
    )

    bucket = models.DateTimeField(
        db_index=True
    )

    avg = models.FloatField()
    min = models.FloatField()
    max = models.FloatField()
    count = models.IntegerField()

    energy_wh = models.FloatField(
        null=True,
        blank=True,
    )
    
    class Meta:

        unique_together = (
            "device",
            "metric_key",
            "bucket",
        )

        indexes = [

            models.Index(
                fields=[
                    "device",
                    "metric_key",
                    "bucket",
                ]
            ),

            models.Index(
                fields=[
                    "bucket",
                    "metric_key",
                ]
            ),

        ]


class DeviceMetric1h(models.Model):

    device = models.ForeignKey(
        "Device",
        on_delete=models.CASCADE
    )

    metric_key = models.CharField(
        max_length=64,
        db_index=True,
        null=True,
        blank=True,
    )

    bucket = models.DateTimeField(
        db_index=True
    )

    avg = models.FloatField()
    min = models.FloatField()
    max = models.FloatField()
    count = models.IntegerField()

    energy_wh = models.FloatField(
        null=True,
        blank=True,
    )
    
    class Meta:

        unique_together = (
            "device",
            "metric_key",
            "bucket",
        )

        indexes = [

            models.Index(
                fields=[
                    "device",
                    "metric_key",
                    "bucket",
                ]
            ),

            models.Index(
                fields=[
                    "bucket",
                    "metric_key",
                ]
            ),

        ]


# ============================================================
# 🧠 GERÄTEPROFILING & BASELINE-ÜBERWACHUNG
# ============================================================

class DeviceBaselineProfile(models.Model):
    """
    Intelligentes Geräteprofil zur Überwachung der Baseline (z. B. Standby-Verbrauch,
    Betriebsleistung, Zyklus- und Dauerlaufzeiten für BWWP, Wärmepumpen, Kühlschränke, Pumpen).
    Erkennt frühzeitig Fehlverhalten, Verschleiß, Defekte oder Kriechströme.
    """
    APPLIANCE_CHOICES = [
        ("bwwp", "Brauchwasserwärmepumpe (BWWP)"),
        ("heatpump", "Heizungs-Wärmepumpe"),
        ("fridge", "Kühlschrank / Gefriergerät"),
        ("circulation_pump", "Zirkulationspumpe"),
        ("heating_pump", "Umwälz- / Heizungspumpe"),
        ("washing_machine", "Waschmaschine / Trockner"),
        ("dishwasher", "Geschirrspüler"),
        ("ev_charger", "Wallbox / E-Auto"),
        ("ac_inverter", "Klimaanlage / Inverter"),
        ("generic", "Individuelles Gerät"),
    ]

    HEALTH_HEALTHY = "healthy"
    HEALTH_WARNING = "warning"
    HEALTH_ANOMALY = "anomaly"

    HEALTH_CHOICES = [
        (HEALTH_HEALTHY, "Normal / Baseline eingehalten"),
        (HEALTH_WARNING, "Auffällig / Leichte Abweichung"),
        (HEALTH_ANOMALY, "Kritische Anomalie / Alarm"),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    device = models.OneToOneField(
        "Device",
        on_delete=models.CASCADE,
        related_name="baseline_profile",
    )
    appliance_type = models.CharField(
        max_length=40,
        choices=APPLIANCE_CHOICES,
        default="generic",
    )
    is_active = models.BooleanField(
        default=True,
        help_text="Überwachung der Baseline aktiv",
    )

    # 1. Standby / Ruhe-Baseline
    standby_power_w = models.FloatField(
        default=30.0,
        help_text="Erwarteter Standby-/Ruheverbrauch in Watt (z. B. 30W bei BWWP)",
    )
    standby_tolerance_pct = models.FloatField(
        default=30.0,
        help_text="Zulässige Abweichung vom Standby in % (z. B. 30%)",
    )
    standby_max_w = models.FloatField(
        default=45.0,
        help_text="Absolute Obergrenze für den Standby-Zustand (z. B. 45W)",
    )

    # 2. Betriebs-Leistung (z. B. Kompressor / Pumpe aktiv)
    operating_power_min_w = models.FloatField(
        default=350.0,
        help_text="Minimale Leistung im aktiven Betriebsmodus (z. B. 350W)",
    )
    operating_power_max_w = models.FloatField(
        default=750.0,
        help_text="Maximale Leistung im regulären Betriebsmodus (z. B. 750W)",
    )

    # 3. Laufzeit-Überwachung
    max_continuous_run_hours = models.FloatField(
        default=6.0,
        help_text="Maximal zulässige ununterbrochene Laufzeit vor Alarm (z. B. 6.0h)",
    )

    # 4. Status & Auto-Learning
    learning_mode = models.BooleanField(
        default=False,
        help_text="Lernt automatisch die Baseline aus den realen Messwerten",
    )
    last_evaluated_at = models.DateTimeField(null=True, blank=True)
    current_health_status = models.CharField(
        max_length=20,
        choices=HEALTH_CHOICES,
        default=HEALTH_HEALTHY,
    )
    last_measured_standby_w = models.FloatField(null=True, blank=True)
    last_measured_operating_w = models.FloatField(null=True, blank=True)
    anomaly_reason = models.TextField(blank=True, default="")
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Baseline-Profil ({self.get_appliance_type_display()}) für Device #{self.device_id}"


# ============================================================
# ☁️ CLOUD-INTEGRATION & 3RD-PARTY WECHSELRICHTER-PROFILE
# ============================================================

class CloudDeviceIntegration(models.Model):
    """
    Kopplung eines Geräts an eine Hersteller-Cloud (z. B. Sungrow iSolarCloud, SolarEdge, Fronius).
    Verwendet deklarative YAML-Profile unter devices/profiles/*.yaml für Abfragen, Auth & Mappings.
    """
    STATUS_OK = "ok"
    STATUS_ERROR = "error"
    STATUS_PENDING = "pending"

    STATUS_CHOICES = [
        (STATUS_OK, "Aktiv / Verbunden"),
        (STATUS_ERROR, "Fehler bei Abfrage"),
        (STATUS_PENDING, "Ausstehend"),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    device = models.OneToOneField(
        "Device",
        on_delete=models.CASCADE,
        related_name="cloud_integration",
    )
    profile_id = models.CharField(
        max_length=64,
        help_text="ID des YAML-Profils (z. B. sungrow_isolarcloud, solaredge_cloud)",
    )
    credentials = models.JSONField(
        default=dict,
        blank=True,
        help_text="Konfigurations- und Zugangsdaten (z. B. appkey, user_account, password, site_id)",
    )
    polling_interval_seconds = models.IntegerField(
        default=60,
        help_text="Abfrageintervall in Sekunden (Standard: 60s)",
    )
    is_active = models.BooleanField(
        default=True,
        help_text="Aktiviert das periodische Polling über Celery",
    )
    last_polled_at = models.DateTimeField(
        null=True,
        blank=True,
    )
    last_status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default=STATUS_PENDING,
    )
    last_error_message = models.TextField(
        blank=True,
        default="",
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Cloud-Integration ({self.profile_id}) für Device #{self.device_id}"


# ============================================================
# ✅ OCPP 1.6-J SMART CHARGING & WALLBOX MODELS
# ============================================================
from .models_ocpp import ChargingStation, ChargingSession, ChargingRfidTag
