###################################
# energy/models_ems_settings.py
###################################

import uuid
from decimal import Decimal
from django.db import models
from django.core.exceptions import ValidationError


class EMSGlobalSettings(models.Model):
    """
    Zentrale, globale EMS-Systemeinstellungen (Singleton).
    Definiert Standard-Preise, Margen, Arbitrage-Schwellen, gesetzliche Abgaben
    sowie Standardtarife für das gesamte EMS und Energy Sharing.
    """

    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
    )

    # =========================================================================
    # ⚡ 1. STROMBEZUG & EINSPEISUNG (STANDARD-PREISE)
    # =========================================================================
    default_grid_price_ct_kwh = models.DecimalField(
        max_digits=6,
        decimal_places=2,
        default=Decimal("32.00"),
        verbose_name="Standard-Arbeitspreis Netzbezug (ct/kWh)",
        help_text="Allgemeiner Standard-Stromarbeitspreis in ct/kWh (brutto) bei Festpreisen",
    )

    default_feed_in_tariff_ct_kwh = models.DecimalField(
        max_digits=6,
        decimal_places=2,
        default=Decimal("8.20"),
        verbose_name="Standard-EEG-Einspeisevergütung (ct/kWh)",
        help_text="Standardmäßige Vergütung für eingespeisten PV-Strom gem. EEG (z. B. 8,20 ct/kWh)",
    )

    # =========================================================================
    # 📈 2. DYNAMISCHE TARIFE, BÖRSENPREISE & ARBITRAGE
    # =========================================================================
    default_spot_markup_ct_kwh = models.DecimalField(
        max_digits=6,
        decimal_places=2,
        default=Decimal("1.50"),
        verbose_name="Spotmarkt-Aufschlag / Marge (ct/kWh)",
        help_text="Anbieter-Aufschlag auf den EPEX Spotpreis in ct/kWh",
    )

    spot_floor_price_ct_kwh = models.DecimalField(
        max_digits=6,
        decimal_places=2,
        null=True,
        blank=True,
        verbose_name="Spotmarkt-Mindestpreis / Floor (ct/kWh)",
        help_text="Optional: Untergrenze für dynamischen Strompreis in ct/kWh",
    )

    spot_cap_price_ct_kwh = models.DecimalField(
        max_digits=6,
        decimal_places=2,
        null=True,
        blank=True,
        verbose_name="Spotmarkt-Maximalpreis / Cap (ct/kWh)",
        help_text="Optional: Preisbremse / Obergrenze in ct/kWh",
    )

    battery_arbitrage_min_spread_ct_kwh = models.DecimalField(
        max_digits=6,
        decimal_places=2,
        default=Decimal("8.00"),
        verbose_name="Batterie-Arbitrage Mindest-Spread (ct/kWh)",
        help_text="Erforderliche Preisdifferenz zwischen Lade- und Entladefenster, ab der Arbitrage wirtschaftlich ist",
    )

    # =========================================================================
    # 🤝 3. ENERGY SHARING & QUARTIERE (SÄULE 2)
    # =========================================================================
    community_sharing_price_ct_kwh = models.DecimalField(
        max_digits=6,
        decimal_places=2,
        default=Decimal("12.00"),
        verbose_name="Community-Sharing Bezugspreis (ct/kWh)",
        help_text="Standard-Bezugspreis für geteilten Solarstrom innerhalb der Gemeinschaft",
    )

    community_producer_payout_ct_kwh = models.DecimalField(
        max_digits=6,
        decimal_places=2,
        default=Decimal("10.00"),
        verbose_name="Community Einspeiser-Vergütung (ct/kWh)",
        help_text="Standard-Auszahlung an Erzeuger für geteilten Solarstrom",
    )

    community_platform_fee_ct_kwh = models.DecimalField(
        max_digits=6,
        decimal_places=2,
        default=Decimal("2.00"),
        verbose_name="Community Plattform- & Betriebsumlage (ct/kWh)",
        help_text="Betriebsgebühr / Plattform-Umlage pro geteilter kWh",
    )

    # =========================================================================
    # 🏛️ 4. GESETZLICHE ABGABEN, NETZENTGELTE & STEUERN (DEUTSCHLAND)
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
    # ⏱️ METADATEN
    # =========================================================================
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Zuletzt aktualisiert")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Erstellt am")

    class Meta:
        db_table = "energy_ems_global_settings"
        verbose_name = "EMS-Globaleinstellung"
        verbose_name_plural = "EMS-Globaleinstellungen (Preise & Tarife)"

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
        return f"Globale EMS-Preiseinstellungen (Stand: {self.updated_at.strftime('%Y-%m-%d %H:%M') if self.updated_at else 'Initial'})"


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
