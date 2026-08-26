########################
# core/models.py
########################

import uuid
from django.db import models
from django.utils import timezone
from django.utils.text import slugify

from core.ownership import owner_xor_constraints


# -----------------------------------------------------
# TENANT
# -----------------------------------------------------
class Tenant(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    name = models.CharField(max_length=255)
    slug = models.SlugField(unique=True)

    latitude = models.FloatField(null=True, blank=True)
    longitude = models.FloatField(null=True, blank=True)

    is_public = models.BooleanField(default=False)

    # Theme & Branding Felder (aus tenants.models konsolidiert)
    primary_color = models.CharField(max_length=50, default="from-orange-400")
    secondary_color = models.CharField(max_length=50, default="to-orange-600")
    button_color = models.CharField(max_length=50, default="bg-orange-500")

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name


# -----------------------------------------------------
# METER
# -----------------------------------------------------
class Meter(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    SOURCE_CHOICES = [
        ("imsys", "iMSys"),
        ("mqtt", "MQTT"),
        ("tibber", "Tibber"),
        ("sungrow", "Sungrow"),
        ("manual", "Manual"),
    ]

    tenant = models.ForeignKey(
        "core.Tenant",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="meters"
    )

    owner_user = models.ForeignKey(
        "accounts.User",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="owned_meters"
    )

    owner_membership = models.ForeignKey(
        "accounts.TenantMembership",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="meters"
    )

    serial_number = models.CharField(max_length=100, unique=True, null=True, blank=True)

    METER_TYPES = [
        ("electricity", "Electricity"),
        ("pv", "PV"),
        ("battery", "Battery"),
    ]

    # ✅ NEU: technisch (woher kommt die Daten)
    source = models.CharField(
        max_length=32,
        choices=SOURCE_CHOICES,
        default="manual",
    )

    # ✅ BLEIBT: fachlich (welche Integration / Anbieter)
    integration_type = models.CharField(
        max_length=32,
        choices=[
            ("tibber", "Tibber"),
            ("manual", "Manual"),
            ("none", "None"),
        ],
        default="none",
    )

    meter_type = models.CharField(max_length=20, choices=METER_TYPES, default="electricity")

    manufacturer = models.CharField(max_length=100, blank=True)

    installed_at = models.DateTimeField(null=True, blank=True)
    removed_at = models.DateTimeField(null=True, blank=True)

    tibber_home_id = models.CharField(max_length=64, null=True, blank=True)
    last_tibber_sync = models.DateTimeField(null=True, blank=True)

    class Meta:
        indexes = [
            models.Index(fields=["tenant", "serial_number"]),
            models.Index(fields=["tenant"]),
            models.Index(fields=["integration_type"]),  # ✅ wichtig wieder drin
        ]
        constraints = owner_xor_constraints("meter")

    def __str__(self):
        return self.serial_number or str(self.id)


# -----------------------------------------------------
# METER REGISTER
# -----------------------------------------------------
class MeterRegister(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4)

    meter = models.ForeignKey("core.Meter", on_delete=models.CASCADE, related_name="registers")
    obis_code = models.CharField(max_length=20)
    description = models.CharField(max_length=255, blank=True)

    class Meta:
        db_table = "core_meterregister"
        unique_together = ("meter", "obis_code")


# -----------------------------------------------------
# INTERVAL READING (RAW DATA)
# -----------------------------------------------------
class IntervalReading(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    tenant = models.ForeignKey(
        "core.Tenant", on_delete=models.CASCADE, null=True, blank=True
    )

    meter = models.ForeignKey("core.Meter", on_delete=models.CASCADE)

    ts_start = models.DateTimeField()
    ts_end = models.DateTimeField(null=True, blank=True)

    received_at = models.DateTimeField(default=timezone.now)

    obis_code = models.CharField(max_length=20)
    value = models.DecimalField(max_digits=12, decimal_places=3)
    unit = models.CharField(max_length=20, default="kWh")

    source = models.CharField(max_length=20, default="system")

    is_late = models.BooleanField(default=False)
    is_duplicate = models.BooleanField(default=False)
    ingestion_delay_seconds = models.IntegerField(null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "core_intervalreading"
        unique_together = ("meter", "ts_start", "obis_code")
        indexes = [
            models.Index(fields=["tenant", "ts_start"]),
            models.Index(fields=["meter", "ts_start"]),
            models.Index(fields=["tenant", "obis_code", "ts_start"]),
        ]


# -----------------------------------------------------
# AGGREGATED READING
# -----------------------------------------------------
class AggregatedReading(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    tenant = models.ForeignKey(
        "core.Tenant", on_delete=models.CASCADE, null=True, blank=True
    )

    meter = models.ForeignKey("core.Meter", on_delete=models.CASCADE)

    obis_code = models.CharField(max_length=20)

    unit = models.CharField(max_length=16, default="kWh")

    period_start = models.DateTimeField()
    period_end = models.DateTimeField(null=True, blank=True)

    value = models.DecimalField(max_digits=14, decimal_places=3)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "core_aggregatedreading"
        unique_together = ("meter", "period_start")
        indexes = [
            models.Index(fields=["meter", "period_start"]),
        ]


# -----------------------------------------------------
# BALANCE SLOT
# -----------------------------------------------------
class BalanceSlot(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    tenant = models.ForeignKey(
        "core.Tenant", on_delete=models.CASCADE, null=True, blank=True
    )

    meter = models.ForeignKey("core.Meter", on_delete=models.CASCADE)

    period_start = models.DateTimeField()

    consumption_kwh = models.DecimalField(max_digits=14, decimal_places=3)
    generation_kwh = models.DecimalField(max_digits=14, decimal_places=3)
    self_consumption_kwh = models.DecimalField(max_digits=14, decimal_places=3)
    grid_import_kwh = models.DecimalField(max_digits=14, decimal_places=3)
    grid_export_kwh = models.DecimalField(max_digits=14, decimal_places=3)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "core_balanceslot"
        unique_together = ("meter", "period_start")


class MemberEnergyProfile(models.Model):
    member = models.OneToOneField(
        "accounts.TenantMembership",
        on_delete=models.CASCADE,
        related_name="energy_profile",
    )

    ENERGY_ROLE = [
        ("consumer", "Consumer"),
        ("producer", "Producer"),
        ("prosumer", "Prosumer"),
    ]

    energy_role = models.CharField(
        max_length=20,
        choices=ENERGY_ROLE,
        default="consumer",
    )

    grid_connection_id = models.CharField(
        max_length=100,
        blank=True,
    )

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "core_memberenergyprofile"

    def __str__(self):
        return f"{self.member} ({self.energy_role})"
    