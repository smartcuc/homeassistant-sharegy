import uuid
from decimal import Decimal
from django.db import models
from django.utils import timezone


class VPPFlexibilityPool(models.Model):
    """
    Aggregations-Pool für dezentrale Flexibilitäten zur Teilnahme an Regelenergiemärkten
    (aFRR / Sekundärregelleistung, FCR / Primärregelleistung) und Redispatch 2.0.
    """
    TSO_CHOICES = [
        ("tennet", "TenneT TSO"),
        ("50hertz", "50Hertz Transmission"),
        ("amprion", "Amprion"),
        ("transnetbw", "TransnetBW"),
        ("local_dso", "Lokaler Verteilnetzbetreiber (VNB)"),
    ]

    PRODUCT_CHOICES = [
        ("afrr_positive", "aFRR Positive Sekundärregelleistung (+kW)"),
        ("afrr_negative", "aFRR Negative Sekundärregelleistung (-kW)"),
        ("fcr", "FCR Primärregelleistung (Frequenzhaltung +/-)"),
        ("redispatch_2_0", "Redispatch 2.0 (Einspeisemanagement & Engpassbeseitigung)"),
        ("peak_shaving", "Netzentgelt-Optimierung / Peak Shaving (§ 19 StromNEV)"),
        ("spot_arbitrage", "Dynamische Intraday/Day-Ahead Arbitrage"),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=200, help_text="z. B. 50Hertz Heimspeicher-Pool Berlin")
    tso_operator = models.CharField(max_length=50, choices=TSO_CHOICES, default="50hertz")
    market_product = models.CharField(max_length=50, choices=PRODUCT_CHOICES, default="afrr_positive")
    grid_region = models.CharField(max_length=100, blank=True, default="Regelzone Deutschland")
    postal_code_prefix = models.CharField(max_length=100, default="*", help_text="Komma-separierte PLZ-Bereiche oder '*' für alle")
    min_activation_power_kw = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal("1.00"))
    max_activation_power_kw = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal("500.00"))
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "VPP Flexibilitäts-Pool"
        verbose_name_plural = "VPP Flexibilitäts-Pools"
        ordering = ["name"]

    def __str__(self):
        return f"{self.name} ({self.get_tso_operator_display()} | {self.get_market_product_display()})"


class VPPDispatchOrder(models.Model):
    """
    Abruf-Auftrag von Übertragungsnetzbetreiber (ÜNB) oder Aggregator
    zur Aktivierung von Regelleistung oder Redispatch.
    """
    DISPATCH_TYPES = [
        ("positive_flex", "Positive Flexibilität (Einspeisung ↑ / Last ↓)"),
        ("negative_flex", "Negative Flexibilität (Einspeisung ↓ / Last ↑ / Speicher laden)"),
    ]

    STATUS_CHOICES = [
        ("pending", "Ausstehend"),
        ("active", "Aktiv / Erbringung läuft"),
        ("completed", "Erfolgreich abgeschlossen"),
        ("failed", "Fehlgeschlagen / Abweichung"),
        ("cancelled", "Storniert"),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    pool = models.ForeignKey(VPPFlexibilityPool, on_delete=models.SET_NULL, null=True, blank=True, related_name="dispatch_orders")
    dispatch_type = models.CharField(max_length=30, choices=DISPATCH_TYPES, default="positive_flex")
    target_power_kw = models.DecimalField(max_digits=10, decimal_places=2, help_text="Soll-Leistungsänderung in kW")
    duration_minutes = models.IntegerField(default=15, help_text="Dauer des Abrufs in Minuten")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="pending")
    
    requested_by = models.CharField(max_length=150, default="Übertragungsnetzbetreiber (ÜNB)")
    connect_plus_order_id = models.CharField(max_length=100, blank=True, default="", help_text="Connect+ / Redispatch 2.0 Auftragsnummer")
    
    start_time = models.DateTimeField(default=timezone.now)
    end_time = models.DateTimeField(null=True, blank=True)
    
    baseline_power_kw = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal("0.00"), help_text="Referenzleistung vor Aktivierung")
    delivered_power_kw = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal("0.00"), help_text="Tatsächlich erbrachte mittlere Leistung")
    energy_delivered_kwh = models.DecimalField(max_digits=10, decimal_places=3, default=Decimal("0.000"), help_text="Erbringungsarbeit in kWh")
    remuneration_eur = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal("0.00"), help_text="Erlös / Vergütung in EUR")
    
    activated_devices_count = models.IntegerField(default=0)
    meta_info = models.JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "VPP Dispatch-Auftrag"
        verbose_name_plural = "VPP Dispatch-Aufträge"
        ordering = ["-created_at"]

    def __str__(self):
        return f"Dispatch {str(self.id)[:8]} ({self.target_power_kw} kW {self.get_dispatch_type_display()} - {self.get_status_display()})"


class VPPDispatchTelemetry(models.Model):
    """
    Feingranulare Telemetrie-Aufzeichnung zur revisionssicheren Nachweiserbringung
    und Abrechnung gegenüber dem Übertragungsnetzbetreiber.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    dispatch_order = models.ForeignKey(VPPDispatchOrder, on_delete=models.CASCADE, related_name="telemetry_points")
    timestamp = models.DateTimeField(default=timezone.now, db_index=True)
    target_power_kw = models.DecimalField(max_digits=10, decimal_places=2)
    measured_power_kw = models.DecimalField(max_digits=10, decimal_places=2)
    frequency_hz = models.DecimalField(max_digits=6, decimal_places=3, default=Decimal("50.000"))
    battery_soc_avg = models.DecimalField(max_digits=5, decimal_places=2, default=Decimal("0.00"))

    class Meta:
        verbose_name = "VPP Dispatch Telemetrie"
        verbose_name_plural = "VPP Dispatch Telemetrien"
        ordering = ["timestamp"]
