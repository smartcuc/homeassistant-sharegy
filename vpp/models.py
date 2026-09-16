import uuid
from decimal import Decimal
from django.conf import settings
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


class VPPAssetEnrollment(models.Model):
    """
    Kunden-Einschreibung eines Assets (Heimspeicher, Wallbox, § 14a SteuVE) in das Virtuelle Kraftwerk.
    Verwaltet Opt-In, Mindest-SoC Reserve und Abrechnungs-Konditionen.
    """
    STATUS_CHOICES = [
        ("active", "Aktiv / Bereit für Abrufe"),
        ("paused", "Pausiert durch Nutzer"),
        ("opted_out", "Abgemeldet"),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="vpp_enrollments")
    device = models.ForeignKey("devices.Device", on_delete=models.CASCADE, related_name="vpp_enrollments")
    pool = models.ForeignKey(VPPFlexibilityPool, on_delete=models.SET_NULL, null=True, blank=True, related_name="enrolled_assets")
    
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="active")
    min_soc_reserve_pct = models.DecimalField(
        max_digits=5, decimal_places=2, default=Decimal("20.00"),
        help_text="Mindest-Ladestand, der für den Eigenbedarf im Haushalt reserviert bleibt (%)"
    )
    payout_share_pct = models.DecimalField(
        max_digits=5, decimal_places=2, default=Decimal("80.00"),
        help_text="Kunden-Anteil an der erlösten Flexibilitätsprämie (Standard: 80%)"
    )
    total_earned_eur = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal("0.00"))
    total_dispatches_count = models.IntegerField(default=0)
    
    auto_spot_arbitrage = models.BooleanField(default=True, help_text="Erlaubt automatische Börsentarif-Arbitrage (Preistiefststände laden)")
    auto_afrr_frequency = models.BooleanField(default=True, help_text="Erlaubt Teilnahme an Sekundärregelleistung (aFRR)")
    
    joined_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "VPP Asset Einschreibung"
        verbose_name_plural = "VPP Asset Einschreibungen"
        unique_together = ("user", "device")
        ordering = ["-joined_at"]

    def __str__(self):
        return f"{self.device.name} ({self.user.email} - {self.get_status_display()})"


class VPPAssetDispatch(models.Model):
    """
    Granulare Zuordnung und Abrechnung eines VPP-Abrufs für ein einzelnes Kunden-Gerät.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    dispatch_order = models.ForeignKey(VPPDispatchOrder, on_delete=models.CASCADE, related_name="asset_dispatches")
    enrollment = models.ForeignKey(VPPAssetEnrollment, on_delete=models.CASCADE, related_name="dispatch_events")
    device = models.ForeignKey("devices.Device", on_delete=models.CASCADE, related_name="vpp_dispatches")
    
    allocated_power_kw = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal("0.00"))
    delivered_power_kw = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal("0.00"))
    energy_kwh = models.DecimalField(max_digits=10, decimal_places=3, default=Decimal("0.000"))
    
    gross_revenue_eur = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal("0.00"))
    customer_payout_eur = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal("0.00"))
    sharegy_fee_eur = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal("0.00"))
    
    soc_before_pct = models.DecimalField(max_digits=5, decimal_places=2, default=Decimal("0.00"))
    soc_after_pct = models.DecimalField(max_digits=5, decimal_places=2, default=Decimal("0.00"))
    
    is_cleared = models.BooleanField(default=False, help_text="Wurde bereits im monatlichen Clearing-Lauf abgerechnet")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "VPP Asset Dispatch Allokation"
        verbose_name_plural = "VPP Asset Dispatch Allokationen"
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.device.name}: {self.delivered_power_kw} kW ({self.customer_payout_eur} € Payout)"


class VPPClearingStatement(models.Model):
    """
    Monatliche oder periodische Abrechnung & Gutschrift der Flexibilitätserlöse an den Endkunden.
    """
    STATUS_CHOICES = [
        ("pending", "Ausstehend"),
        ("credited", "Als Guthaben auf Kundenkonto verbucht"),
        ("paid_out", "Ausgezahlt (Stripe / Bank)"),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="vpp_clearing_statements")
    period_start = models.DateField()
    period_end = models.DateField()
    
    dispatches_count = models.IntegerField(default=0)
    total_energy_kwh = models.DecimalField(max_digits=10, decimal_places=3, default=Decimal("0.000"))
    
    gross_revenue_eur = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal("0.00"))
    customer_payout_eur = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal("0.00"))
    sharegy_fee_eur = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal("0.00"))
    
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="pending")
    payment_reference = models.CharField(max_length=100, blank=True, default="")
    credited_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "VPP Clearing Abrechnung"
        verbose_name_plural = "VPP Clearing Abrechnungen"
        unique_together = ("user", "period_start", "period_end")
        ordering = ["-period_end"]

    def __str__(self):
        return f"VPP Clearing {self.user.email} [{self.period_start} bis {self.period_end}]: {self.customer_payout_eur} € ({self.get_status_display()})"
