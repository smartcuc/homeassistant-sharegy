#####################
# producer/models.py
#####################

import uuid

from django.db import models

from devices.models import Home, Device


class GeneratorType(models.Model):

    key = models.CharField(
        max_length=50,
        unique=True,
    )

    name = models.CharField(
        max_length=100,
    )

    icon = models.CharField(
        max_length=20,
        blank=True,
        default="⚡",
    )

    active = models.BooleanField(
        default=True,
    )

    sort_order = models.IntegerField(
        default=0,
    )

    class Meta:

        ordering = [
            "sort_order",
            "name",
        ]

        verbose_name = "Generator Typ"
        verbose_name_plural = "Generator Typen"

    def __str__(self):
        return self.name


class Orientation(models.Model):

    key = models.CharField(
        max_length=10,
        unique=True,
    )

    name = models.CharField(
        max_length=50,
    )

    azimuth_deg = models.IntegerField()

    sort_order = models.IntegerField(
        default=0,
    )

    active = models.BooleanField(
        default=True,
    )

    class Meta:

        ordering = [
                "sort_order",
            ]

        verbose_name = "Ausrichtung"
        verbose_name_plural = "Ausrichtungen"

    def __str__(self):
        return self.name


class GeneratorSystem(models.Model):

    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
    )
    home = models.ForeignKey(
        Home,
        on_delete=models.CASCADE,
        related_name="generator_systems",
    )

    device = models.OneToOneField(
        Device,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="generator_system",
    )

    name = models.CharField(
        max_length=100,
    )

    generator_type = models.ForeignKey(
        GeneratorType,
        on_delete=models.PROTECT,
        related_name="generator_systems",
        null=True,
        blank=True,
    )
    peak_power_kw = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="Gesamtleistung des Systems in kW/kWp",
    )

    inverter_power_kw = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="Wechselrichterleistung",
    )

    battery_capacity_kwh = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="Speicherkapazität",
    )

    active = models.BooleanField(
        default=True,
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
    )

    class Meta:

        ordering = [

            "name",
        ]

    @property
    def string_count(self):

        return self.strings.count()

    @property
    def total_string_power_kwp(self):

        return sum(float(s.peak_power_kwp) for s in self.strings.all())

    @property
    def needs_configuration(self):

        if not self.generator_type:
            return True

        if (
            self.generator_type.key == "pv"
            and self.strings.count() == 0
        ):
            return True

        return False

    def __str__(self):

        return f"{self.home.name} | " f"{self.name}"


class GeneratorString(models.Model):

    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
    )

    generator = models.ForeignKey(
        GeneratorSystem,
        on_delete=models.CASCADE,
        related_name="strings",
    )

    name = models.CharField(
        max_length=100,
    )

    module_count = models.PositiveIntegerField(
        default=0,
    )

    peak_power_kwp = models.DecimalField(
        max_digits=10,
        decimal_places=2,
    )

    orientation = models.ForeignKey(
        Orientation,
        on_delete=models.PROTECT,
        related_name="strings",
    )

    tilt_deg = models.IntegerField(
        default=35,
        help_text="Dachneigung",
    )

    shading_percent = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=0,
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
    )

    class Meta:

        ordering = [
            "name",
        ]

    def __str__(self):

        return f"{self.generator.name} | " f"{self.name}"

    @property
    def azimuth_deg(self):

        return self.orientation.azimuth_deg


# ============================================================
# ✅ STORAGE SYSTEM (BATTERIESPEICHER & MESSBÜNDELUNG)
# ============================================================

class StorageSystem(models.Model):
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
    )
    home = models.ForeignKey(
        Home,
        on_delete=models.CASCADE,
        related_name="storage_systems",
    )
    name = models.CharField(
        max_length=100,
        default="Hausspeicher",
    )

    # Physikalische Parameter
    capacity_kwh = models.DecimalField(
        max_digits=8,
        decimal_places=2,
        default=10.0,
        help_text="Nennkapazität des Batteriespeichers in kWh",
    )
    max_charge_power_kw = models.DecimalField(
        max_digits=8,
        decimal_places=2,
        default=5.0,
        help_text="Max. Ladeleistung in kW",
    )
    max_discharge_power_kw = models.DecimalField(
        max_digits=8,
        decimal_places=2,
        default=5.0,
        help_text="Max. Entladeleistung in kW",
    )
    min_soc_reserve_pct = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=10.0,
        help_text="Notstromreserve / Tiefentladeschutz in %",
    )
    max_soc_pct = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=100.0,
        help_text="Maximales Ladelimit in %",
    )
    charge_efficiency_pct = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=95.0,
        help_text="Ladewirkungsgrad in %",
    )
    discharge_efficiency_pct = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=95.0,
        help_text="Entladewirkungsgrad in %",
    )

    # Signal- & Messpunkt-Zuordnung
    primary_device = models.ForeignKey(
        Device,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="primary_storage_systems",
        help_text="Optionales Hauptgerät (z. B. Hybrid-Wechselrichter)",
    )
    soc_device = models.ForeignKey(
        Device,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="storage_soc_systems",
        help_text="Gerät, das den Ladestand (SoC %) liefert",
    )
    soc_metric_key = models.CharField(
        max_length=100,
        default="soc",
        blank=True,
        help_text="Datenpunkt für Ladestand (z. B. soc, battery_soc)",
    )
    power_device = models.ForeignKey(
        Device,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="storage_power_systems",
        help_text="Gerät, das die Lade-/Entladeleistung liefert",
    )
    power_metric_key = models.CharField(
        max_length=100,
        default="power",
        blank=True,
        help_text="Datenpunkt für Lade-/Entladeleistung (z. B. power, battery_power, battery_w)",
    )
    charge_energy_device = models.ForeignKey(
        Device,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="storage_charge_energy_systems",
        help_text="Gerät für kumulierten Ladezähler in kWh",
    )
    charge_energy_metric_key = models.CharField(
        max_length=100,
        default="energy_in",
        blank=True,
    )
    discharge_energy_device = models.ForeignKey(
        Device,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="storage_discharge_energy_systems",
        help_text="Gerät für kumulierten Entladezähler in kWh",
    )
    discharge_energy_metric_key = models.CharField(
        max_length=100,
        default="energy_out",
        blank=True,
    )

    active = models.BooleanField(
        default=True,
    )
    is_auto_detected = models.BooleanField(
        default=False,
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
    )
    updated_at = models.DateTimeField(
        auto_now=True,
    )

    class Meta:
        ordering = ["name"]
        verbose_name = "Speichersystem"
        verbose_name_plural = "Speichersysteme"

    def __str__(self):
        return f"{self.home.name} | {self.name} ({self.capacity_kwh} kWh)"

    def get_live_soc(self):
        """Ermittelt den aktuellen Live-Ladestand in %."""
        from devices.models import DeviceLatestMetric
        target_device = self.soc_device or self.primary_device
        if not target_device:
            return None
        keys = [self.soc_metric_key] if self.soc_metric_key else []
        keys += ["soc", "battery_soc", "state_of_charge", "value"]
        metric = DeviceLatestMetric.objects.filter(
            device=target_device,
            metric_key__in=keys,
        ).first()
        if metric and metric.value is not None:
            return round(float(metric.value), 1)
        return None

    def get_live_power(self):
        """Ermittelt die aktuelle Lade-/Entladeleistung in Watt."""
        from devices.models import DeviceLatestMetric
        target_device = self.power_device or self.primary_device
        if not target_device:
            return None
        keys = [self.power_metric_key] if self.power_metric_key else []
        keys += ["power", "battery_power", "battery_w", "value"]
        metric = DeviceLatestMetric.objects.filter(
            device=target_device,
            metric_key__in=keys,
        ).first()
        if metric and metric.value is not None:
            return round(float(metric.value), 1)
        return None
