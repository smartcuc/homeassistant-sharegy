###################################
# energy/models_ems_settings.py
###################################

import uuid
from decimal import Decimal
from django.db import models
from django.utils import timezone
from django.core.exceptions import ValidationError


class EMSGlobalSettings(models.Model):
    """
    Zentrale, globale Plattform- und EMS-Einstellungen (Singleton).
    Definiert:
    1. Sharegy Plattform-Umlage (Transaktions- & Clearing-Gebühr pro geteilter Sharing-kWh)
    2. Gesetzliche Steuern, Netzentgelte & Umlagen (Referenzwerte Deutschland)
    3. SaaS-Lizenzpreise für Software-Abonnements (Sharegy Pro & Vermieter-Quartiere)
    """

    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
    )

    # =========================================================================
    # 💶 1. SHAREGY PLATTFORM-UMLAGE / ABRECHNUNGSGEBÜHR (SÄULE 2)
    # =========================================================================
    sharegy_platform_fee_ct_kwh = models.DecimalField(
        max_digits=6,
        decimal_places=2,
        default=Decimal("2.00"),
        verbose_name="Sharegy Plattform-Umlage (ct/kWh)",
        help_text="Betriebsgebühr / Plattform-Umlage pro geteilter kWh für automatisierte Messdatenerfassung, Clearing und Monatsabrechnungen gem. § 42b EnWG",
    )

    # =========================================================================
    # 🏛️ 2. GESETZLICHE ABGABEN, NETZENTGELTE & STEUERN (DEUTSCHLAND)
    # =========================================================================
    grid_fee_ct_kwh = models.DecimalField(
        max_digits=8,
        decimal_places=4,
        default=Decimal("9.5000"),
        verbose_name="Netzentgelte (ct/kWh)",
        help_text="Standardmäßige Netznutzungsentgelte",
    )

    electricity_tax_ct_kwh = models.DecimalField(
        max_digits=8,
        decimal_places=4,
        default=Decimal("2.0500"),
        verbose_name="Stromsteuer (ct/kWh)",
        help_text="Gesetzliche Stromsteuer (z. B. 2,05 ct/kWh)",
    )

    concession_fee_ct_kwh = models.DecimalField(
        max_digits=8,
        decimal_places=4,
        default=Decimal("1.6600"),
        verbose_name="Konzessionsabgabe (ct/kWh)",
        help_text="Konzessionsabgabe an Kommunen",
    )

    kwk_levy_ct_kwh = models.DecimalField(
        max_digits=8,
        decimal_places=4,
        default=Decimal("0.2750"),
        verbose_name="KWKG-Umlage (ct/kWh)",
        help_text="Kraft-Wärme-Kopplungs-Umlage",
    )

    special_grid_levy_ct_kwh = models.DecimalField(
        max_digits=8,
        decimal_places=4,
        default=Decimal("0.6430"),
        verbose_name="§ 19 StromNEV-Umlage (ct/kWh)",
        help_text="Sonderkunden-Umlage nach § 19 StromNEV",
    )

    offshore_levy_ct_kwh = models.DecimalField(
        max_digits=8,
        decimal_places=4,
        default=Decimal("0.6560"),
        verbose_name="Offshore-Netzumlage (ct/kWh)",
        help_text="Offshore-Netzanbindungs-Umlage",
    )

    vat_percent = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=Decimal("19.00"),
        verbose_name="Mehrwertsteuer (%)",
        help_text="Umsatzsteuer / MwSt in Prozent (z. B. 19.00 %)",
    )

    # =========================================================================
    # 💎 3. SAAS-ABONNEMENTS & PRO-LIZENZPREISE (SÄULE 1)
    # =========================================================================
    saas_pricing_valid_from = models.DateField(
        default=timezone.now,
        verbose_name="SaaS-Preise gültig ab",
        help_text="Datum, ab dem die konfigurierten Software-Lizenzpreise für Neukunden und Verlängerungen gelten",
    )

    trial_days = models.PositiveIntegerField(
        default=14,
        verbose_name="Kostenlose Testphase (Tage)",
        help_text="Dauer der kostenlosen Testphase für Sharegy Pro bei Neuanmeldung",
    )

    pro_monthly_price_eur = models.DecimalField(
        max_digits=6,
        decimal_places=2,
        default=Decimal("4.99"),
        verbose_name="Sharegy Pro (Monatlich - € brutto)",
        help_text="Monatlicher Endkundenpreis für das Sharegy Pro SaaS-Abo inkl. MwSt.",
    )

    pro_yearly_price_eur = models.DecimalField(
        max_digits=6,
        decimal_places=2,
        default=Decimal("49.99"),
        verbose_name="Sharegy Pro (Jährlich - € brutto)",
        help_text="Jährlicher Endkundenpreis für das Sharegy Pro Jahresabonnement inkl. MwSt.",
    )

    landlord_monthly_price_eur = models.DecimalField(
        max_digits=6,
        decimal_places=2,
        default=Decimal("14.99"),
        verbose_name="Vermieter & Quartiere (Monatlich - € brutto)",
        help_text="Monatlicher Preis für Vermieter & Mehrparteien-Gebäude inkl. MwSt.",
    )

    landlord_yearly_price_eur = models.DecimalField(
        max_digits=6,
        decimal_places=2,
        default=Decimal("149.99"),
        verbose_name="Vermieter & Quartiere (Jährlich - € brutto)",
        help_text="Jährlicher Preis für Vermieter & Mehrparteien-Gebäude inkl. MwSt.",
    )

    # =========================================================================
    # ⏱️ METADATEN
    # =========================================================================
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Zuletzt aktualisiert")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Erstellt am")

    class Meta:
        db_table = "energy_ems_global_settings"
        verbose_name = "EMS-Globaleinstellung"
        verbose_name_plural = "EMS-Globaleinstellungen (Plattform-Preise & Abgaben)"

    def clean(self):
        # Singleton-Pattern: Verhindert das Anlegen mehrerer Instanzen
        if not EMSGlobalSettings.objects.filter(pk=self.pk).exists() and EMSGlobalSettings.objects.exists():
            raise ValidationError("Es darf nur genau eine globale EMS-Einstellungsinstanz existieren.")

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)
        # Cache invalidieren
        from django.core.cache import cache
        cache.delete("ems_global_settings_singleton")

    def total_statutory_levies_ct_kwh(self) -> Decimal:
        """Summe aller festen gesetzlichen Nebenkosten/Umlagen (netto)."""
        return (
            self.grid_fee_ct_kwh
            + self.electricity_tax_ct_kwh
            + self.concession_fee_ct_kwh
            + self.kwk_levy_ct_kwh
            + self.special_grid_levy_ct_kwh
            + self.offshore_levy_ct_kwh
        )

    def __str__(self):
        return f"Globale Plattform-Einstellungen (Stand: {self.updated_at.strftime('%Y-%m-%d %H:%M') if self.updated_at else 'Initial'})"


class InverterManufacturerPollingConfig(models.Model):
    """
    Konfiguration der API-Abfragezyklen (Polling-Intervall in Sekunden)
    je Wechselrichter- und Cloud-Hersteller.
    Ermöglicht dem Betreiber die feingranulare Steuerung der Abfragefrequenzen.
    """

    MANUFACTURER_CHOICES = [
        ("sungrow", "Sungrow (iSolarCloud)"),
        ("huawei", "Huawei (FusionSolar)"),
        ("solaredge", "SolarEdge (Monitoring API)"),
        ("fronius", "Fronius (Solarweb API)"),
        ("sma", "SMA (Sunny Portal / WebConnect)"),
        ("kostal", "Kostal (Solar Portal)"),
        ("deye", "Deye / Solarman"),
        ("goodwe", "GoodWe (SEMS Portal)"),
        ("growatt", "Growatt (ShineServer)"),
        ("victron", "Victron Energy (VRM API)"),
        ("solis", "Solis / Ginlong Cloud"),
        ("shelly", "Shelly (Cloud API / Pro EM)"),
        ("enphase", "Enphase (Enlighten API)"),
        ("foxess", "FoxESS Cloud"),
        ("alphaess", "AlphaESS Cloud"),
        ("generic", "Allgemeiner Standard / Fallback"),
    ]

    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
    )

    manufacturer_key = models.CharField(
        max_length=64,
        unique=True,
        choices=MANUFACTURER_CHOICES,
        verbose_name="Hersteller / System-Schlüssel",
        help_text="Eindeutiger Schlüssel des Wechselrichter-Herstellers",
    )

    manufacturer_name = models.CharField(
        max_length=150,
        verbose_name="Herstellername (Anzeige)",
        help_text="Vollständiger Name des Herstellers / Portals",
    )

    polling_interval_seconds = models.PositiveIntegerField(
        default=60,
        verbose_name="Lesezyklus (Sekunden)",
        help_text="Abfrageintervall der Hersteller-API in Sekunden (z. B. 15s bei Sungrow, 60s bei Huawei)",
    )

    min_allowed_interval_seconds = models.PositiveIntegerField(
        default=10,
        verbose_name="Min. zulässiges Intervall (Sekunden)",
        help_text="Sicherheits-Untergrenze, um API-Sperren / Rate-Limits zu verhindern",
    )

    rate_limit_notes = models.CharField(
        max_length=255,
        blank=True,
        default="",
        verbose_name="Rate-Limit Hinweise & API-Limits",
        help_text="z. B. 'Max. 100 Anfragen / Std.' oder 'OpenAPI Token erforderlich'",
    )

    is_active = models.BooleanField(
        default=True,
        verbose_name="Aktiv",
        help_text="Steuert, ob Integrationen dieses Herstellers periodisch gepollt werden",
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "energy_inverter_manufacturer_polling_config"
        verbose_name = "WR-Hersteller Lesezyklus"
        verbose_name_plural = "WR-Hersteller Lesezyklen (API-Polling)"
        ordering = ["manufacturer_name"]

    def clean(self):
        if self.polling_interval_seconds < self.min_allowed_interval_seconds:
            raise ValidationError(
                {
                    "polling_interval_seconds": (
                        f"Das Abfrageintervall ({self.polling_interval_seconds}s) darf die herstellerspezifische "
                        f"Mindestgrenze von {self.min_allowed_interval_seconds}s nicht unterschreiten."
                    )
                }
            )

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)
        # Cache invalidieren
        from django.core.cache import cache
        cache.delete(f"mfg_polling_interval_{self.manufacturer_key}")
        cache.delete("all_mfg_polling_intervals")

    def __str__(self):
        return f"{self.manufacturer_name}: {self.polling_interval_seconds}s {'(Aktiv)' if self.is_active else '(Pausiert)'}"
