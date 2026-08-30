#####################
# producer/models.py
#####################

import uuid

from django.db import models
from django.core.cache import cache
from devices.models import Home, Device, DeviceLatestMetric


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
        if self.generator_type.key == "pv" and self.strings.count() == 0:
            return True
        return False

    def __str__(self):
        return f"{self.home.name} | {self.name}"


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
        return f"{self.generator.name} | {self.name}"

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
        help_text="Gerät, das die Lade-/Entladeleistung liefert (in W)",
    )
    power_metric_key = models.CharField(
        max_length=100,
        default="power",
        blank=True,
        help_text="Datenpunkt für Lade-/Entladeleistung (z. B. power, battery_power, battery_w)",
    )
    current_device = models.ForeignKey(
        Device,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="storage_current_systems",
        help_text="Optionales Gerät für Batteriestrom (in A) zur Vorzeichen-/Flussrichtungsbestimmung",
    )
    current_metric_key = models.CharField(
        max_length=100,
        default="battery_current",
        blank=True,
        help_text="Datenpunkt für Batteriestrom in Ampere (z. B. battery_current, current)",
    )
    voltage_device = models.ForeignKey(
        Device,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="storage_voltage_systems",
        help_text="Optionales Gerät für Batteriespannung (in V)",
    )
    voltage_metric_key = models.CharField(
        max_length=100,
        default="battery_voltage",
        blank=True,
        help_text="Datenpunkt für Batteriespannung in Volt (z. B. battery_voltage, voltage)",
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
        from devices.models import DeviceMetric
        target_device = self.soc_device or self.primary_device
        keys = [
            "soc", "battery_soc", "battery_soc_pct", "state_of_charge",
            "battery_percent", "soc_pct", "battery_level", "value", "state"
        ]
        if self.soc_metric_key and self.soc_metric_key not in keys:
            keys.insert(0, self.soc_metric_key)

        def _extract_soc(queryset):
            for m in queryset:
                if m.value is not None:
                    try:
                        val = float(m.value)
                        if 0.0 <= val <= 100.0:
                            return round(val, 1)
                    except (ValueError, TypeError):
                        pass
            return None

        if target_device:
            # 1. Redis Cache prüfen
            c_soc = cache.get(f"device:{target_device.id}:latest_soc")
            if c_soc is not None:
                try:
                    return round(float(c_soc), 1)
                except (ValueError, TypeError):
                    pass

            # 2. DeviceLatestMetric prüfen
            val = _extract_soc(DeviceLatestMetric.objects.filter(device=target_device, metric_key__in=keys).order_by("-timestamp"))
            if val is not None:
                return val

            # 3. Beliebige Metrik des SoC-Geräts prüfen
            val = _extract_soc(DeviceLatestMetric.objects.filter(device=target_device).order_by("-timestamp"))
            if val is not None:
                return val

            # 4. DeviceMetric Zeitreihe prüfen
            val = _extract_soc(DeviceMetric.objects.filter(device=target_device, metric_key__in=keys).order_by("-timestamp")[:5])
            if val is not None:
                return val

        # Fallback: Suche in allen Geräten des Haushalts
        val = _extract_soc(DeviceLatestMetric.objects.filter(
            device__home=self.home,
            metric_key__in=keys,
        ).order_by("-timestamp")[:10])
        if val is not None:
            return val

        # Fallback auf Geräte mit Rolle 'battery' / 'storage'
        val = _extract_soc(DeviceLatestMetric.objects.filter(
            device__home=self.home,
            device__config__role__key__in=["battery", "storage", "akku"],
        ).order_by("-timestamp")[:10])
        if val is not None:
            return val

        # Fallback auf DeviceMetric Zeitreihe
        val = _extract_soc(DeviceMetric.objects.filter(
            device__home=self.home,
            metric_key__in=["soc", "battery_soc", "battery_soc_pct", "battery_level"],
        ).order_by("-timestamp")[:10])
        return val

    def get_live_power(self):
        """
        Ermittelt die aktuelle Lade-/Entladeleistung in Watt mit exaktem Vorzeichen.
        Ampere (A) werden niemals direkt als Watt interpretiert!
        """
        from devices.models import DeviceMetric

        # 1. Reine Wirkleistung suchen (W)
        power_val = None
        target_device = self.power_device or self.primary_device
        keys = [
            "power", "battery_power", "battery_power_w", "battery_w",
            "active_power", "p_total", "value", "state", "p", "w"
        ]
        if self.power_metric_key and self.power_metric_key not in ["current", "battery_current", "voltage", "battery_voltage"]:
            keys.insert(0, self.power_metric_key)

        def _is_curr_dev(dev):
            if not dev:
                return False
            try:
                cfg = dev.config
                mdef = cfg.metric_definition if cfg else None
                if mdef and (mdef.unit in ["A", "a"] or mdef.key in ["current", "battery_current"]):
                    return True
            except Exception:
                pass
            d_name = (dev.identifier or "").lower()
            return any(w in d_name for w in ["_current", "stromstärke", "battery_current"]) and not any(w in d_name for w in ["power", "leistung", "watt"])

        if target_device and not _is_curr_dev(target_device):
            # 1a. Redis Cache prüfen
            c_pwr = cache.get(f"device:{target_device.id}:latest_power")
            if c_pwr is not None:
                try:
                    power_val = float(c_pwr)
                except (ValueError, TypeError):
                    pass

            # 1b. DeviceLatestMetric prüfen
            if power_val is None:
                m = DeviceLatestMetric.objects.filter(device=target_device, metric_key__in=keys).order_by("-timestamp").first()
                if m and m.value is not None:
                    try:
                        power_val = float(m.value)
                    except (ValueError, TypeError):
                        pass

            # 1c. DeviceMetric Zeitreihe prüfen
            if power_val is None:
                m = DeviceMetric.objects.filter(device=target_device, metric_key__in=keys).order_by("-timestamp").first()
                if m and m.value is not None:
                    try:
                        power_val = float(m.value)
                    except (ValueError, TypeError):
                        pass

        # Fallback auf Haushalts-Geräte
        if power_val is None:
            m = DeviceLatestMetric.objects.filter(
                device__home=self.home,
                metric_key__in=["battery_power", "battery_power_w", "battery_w"],
            ).order_by("-timestamp").first()
            if m and m.value is not None:
                try:
                    power_val = float(m.value)
                except (ValueError, TypeError):
                    pass

        # Fallback auf Geräte mit Batterie-Rolle (ohne Stromsensoren)
        if power_val is None:
            for d in self.home.devices.all():
                if not _is_curr_dev(d):
                    m = DeviceLatestMetric.objects.filter(device=d, metric_key__in=keys).order_by("-timestamp").first()
                    if m and m.value is not None:
                        try:
                            power_val = float(m.value)
                            break
                        except (ValueError, TypeError):
                            pass

        # 2. Stromstärke ermitteln (A)
        curr_val = None
        curr_device = self.current_device or self.primary_device
        curr_keys = ["battery_current", "current", "battery_current_a", "current_a", "value"]
        if self.current_metric_key:
            curr_keys.insert(0, self.current_metric_key)

        if curr_device:
            c_metric = DeviceLatestMetric.objects.filter(device=curr_device, metric_key__in=curr_keys).order_by("-timestamp").first()
            if c_metric and c_metric.value is not None:
                try:
                    curr_val = float(c_metric.value)
                except (ValueError, TypeError):
                    pass

        if curr_val is None:
            c_metric = DeviceLatestMetric.objects.filter(
                device__home=self.home,
                metric_key__in=["battery_current", "current"],
            ).order_by("-timestamp").first()
            if c_metric and c_metric.value is not None:
                try:
                    curr_val = float(c_metric.value)
                except (ValueError, TypeError):
                    pass

        # 3. Falls keine direkte Leistung vorliegt, aber Spannung und Strom: P = U * I
        if power_val is None and curr_val is not None:
            volt_device = self.voltage_device or self.primary_device
            v_keys = ["battery_voltage", "voltage", "battery_voltage_v", "value"]
            if self.voltage_metric_key:
                v_keys.insert(0, self.voltage_metric_key)
            v_metric = None
            if volt_device:
                v_metric = DeviceLatestMetric.objects.filter(device=volt_device, metric_key__in=v_keys).order_by("-timestamp").first()
            if not v_metric:
                v_metric = DeviceLatestMetric.objects.filter(
                    device__home=self.home,
                    metric_key__in=["battery_voltage", "voltage"],
                ).order_by("-timestamp").first()
            if v_metric and v_metric.value is not None:
                try:
                    volt_val = float(v_metric.value)
                    if volt_val > 0:
                        return round(volt_val * curr_val, 1)
                except (ValueError, TypeError):
                    pass

        if power_val is None:
            return None

        # 4. Vorzeichen über Batteriestrom absichern (falls Leistung positiv übergeben wurde)
        if curr_val is not None:
            if curr_val < 0:
                return -round(abs(power_val), 1)
            elif curr_val > 0:
                return round(abs(power_val), 1)
            else:
                return 0.0

        return round(power_val, 1)
