###################
# billing/models.py
###################

import uuid
from decimal import Decimal
from django.db import models
from django.utils import timezone
from core.ownership import owner_xor_constraints


class BankAccount(models.Model):
    """
    Bankdaten: Standalone oder Tenant-Kontext.
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    tenant = models.ForeignKey(
        "core.Tenant", on_delete=models.CASCADE, null=True, blank=True
    )
    owner_user = models.ForeignKey(
        "accounts.User", on_delete=models.CASCADE, null=True, blank=True
    )
    owner_membership = models.ForeignKey(
        "accounts.TenantMembership",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
    )

    iban = models.CharField(max_length=34)
    bic = models.CharField(max_length=20, blank=True)
    account_holder = models.CharField(max_length=255)

    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        indexes = [models.Index(fields=["tenant", "is_active"])]
        constraints = owner_xor_constraints("bankaccount")

    def __str__(self):
        return f"{self.account_holder} ({'tenant' if self.owner_member_id else 'standalone'})"


class Contract(models.Model):
    """
    Minimaler Vertrag (später erweiterbar).
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    tenant = models.ForeignKey(
        "core.Tenant", on_delete=models.CASCADE, null=True, blank=True
    )
    owner_user = models.ForeignKey(
        "accounts.User", on_delete=models.CASCADE, null=True, blank=True
    )
    owner_membership = models.ForeignKey(
        "accounts.TenantMembership",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
    )

    CONTRACT_TYPE = [
        ("supply", "Supply"),
        ("sharing", "Sharing"),
        ("dynamic", "Dynamic pricing supply"),
    ]
    contract_type = models.CharField(
        max_length=20, choices=CONTRACT_TYPE, default="supply"
    )

    supplier_name = models.CharField(max_length=255, blank=True)

    start_date = models.DateField()
    end_date = models.DateField(null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = owner_xor_constraints("contract")

    def __str__(self):
        return f"{self.contract_type} ({self.supplier_name})"


class UserMeterAssignment(models.Model):
    """
    Genau ein aktiver Billing-User pro Meter.
    Ein User kann mehrere Meter haben.
    Ein Meter gehört nicht mehreren Billing-Usern gleichzeitig.
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    user = models.ForeignKey(
        "accounts.User",
        on_delete=models.CASCADE,
        related_name="meter_assignments",
    )
    meter = models.ForeignKey(
        "core.Meter",
        on_delete=models.CASCADE,
        related_name="billing_assignments",
    )

    valid_from = models.DateTimeField()
    valid_to = models.DateTimeField(null=True, blank=True)

    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        indexes = [
            models.Index(fields=["user", "is_active"]),
            models.Index(fields=["meter", "is_active"]),
        ]
        constraints = [
            models.UniqueConstraint(
                fields=["meter"],
                condition=models.Q(is_active=True),
                name="uniq_active_assignment_per_meter",
            )
        ]

    def __str__(self):
        return f"{self.user} ← {self.meter}"


class UserBalanceSlot(models.Model):
    """
    Billing-/Abrechnungs-Sicht pro User und Meter und Slot.
    Grundlage: BalanceSlot (pro Meter).
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    tenant = models.ForeignKey(
        "core.Tenant",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
    )
    user = models.ForeignKey(
        "accounts.User",
        on_delete=models.CASCADE,
        related_name="balance_slots",
    )
    meter = models.ForeignKey(
        "core.Meter",
        on_delete=models.CASCADE,
        related_name="user_balance_slots",
    )

    period_start = models.DateTimeField()

    consumption_kwh = models.DecimalField(max_digits=12, decimal_places=6, default=0)
    generation_kwh = models.DecimalField(max_digits=12, decimal_places=6, default=0)
    self_consumption_kwh = models.DecimalField(
        max_digits=12, decimal_places=6, default=0
    )
    grid_import_kwh = models.DecimalField(max_digits=12, decimal_places=6, default=0)
    grid_export_kwh = models.DecimalField(max_digits=12, decimal_places=6, default=0)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        indexes = [
            models.Index(fields=["user", "period_start"]),
            models.Index(fields=["meter", "period_start"]),
            models.Index(fields=["tenant", "period_start"]),
        ]
        constraints = [
            models.UniqueConstraint(
                fields=["user", "meter", "period_start"],
                name="uniq_user_meter_period",
            )
        ]

    def __str__(self):
        return f"{self.user} / {self.meter} @ {self.period_start}"


class EMSSubscription(models.Model):
    """
    SaaS-Abonnement & Lizenzstatus für EMS Endnutzer (Säule 1).
    """

    PLAN_FREE = "free"
    PLAN_PRO_MONTHLY = "pro_monthly"
    PLAN_PRO_YEARLY = "pro_yearly"
    PLAN_LANDLORD_MONTHLY = "landlord_monthly"
    PLAN_LANDLORD_YEARLY = "landlord_yearly"

    PLAN_CHOICES = [
        (PLAN_FREE, "Free (Kostenlos)"),
        (PLAN_PRO_MONTHLY, "Sharegy Pro (Monatlich - 4,99 €)"),
        (PLAN_PRO_YEARLY, "Sharegy Pro (Jährlich - 49,99 €)"),
        (PLAN_LANDLORD_MONTHLY, "Vermieter & Quartiere (Monatlich - 14,99 €)"),
        (PLAN_LANDLORD_YEARLY, "Vermieter & Quartiere (Jährlich - 149,99 €)"),
    ]

    STATUS_ACTIVE = "active"
    STATUS_TRIALING = "trialing"
    STATUS_PAST_DUE = "past_due"
    STATUS_CANCELED = "canceled"
    STATUS_UNPAID = "unpaid"

    STATUS_CHOICES = [
        (STATUS_ACTIVE, "Aktiv"),
        (STATUS_TRIALING, "Testphase"),
        (STATUS_PAST_DUE, "Zahlung ausstehend"),
        (STATUS_CANCELED, "Gekündigt"),
        (STATUS_UNPAID, "Unbezahlt"),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.OneToOneField(
        "accounts.User",
        on_delete=models.CASCADE,
        related_name="ems_subscription",
    )

    plan = models.CharField(max_length=32, choices=PLAN_CHOICES, default=PLAN_FREE)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=STATUS_ACTIVE)

    current_period_start = models.DateTimeField(null=True, blank=True)
    current_period_end = models.DateTimeField(null=True, blank=True)
    trial_ends_at = models.DateTimeField(null=True, blank=True)
    cancel_at_period_end = models.BooleanField(default=False)

    # Stripe / Payment Provider References
    stripe_customer_id = models.CharField(max_length=100, blank=True, null=True)
    stripe_subscription_id = models.CharField(max_length=100, blank=True, null=True)
    payment_method = models.CharField(max_length=30, default="stripe")  # stripe, sepa, invoice
    payment_method_brand = models.CharField(max_length=30, blank=True)  # visa, mastercard, sepa_debit
    payment_method_last4 = models.CharField(max_length=10, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "billing_ems_subscription"
        indexes = [
            models.Index(fields=["user", "status"]),
            models.Index(fields=["plan", "status"]),
        ]

    def __str__(self):
        return f"{self.user.email} → {self.plan} ({self.status})"

    @property
    def is_pro_active(self):
        if self.status in [self.STATUS_ACTIVE, self.STATUS_TRIALING]:
            return self.plan in [
                self.PLAN_PRO_MONTHLY,
                self.PLAN_PRO_YEARLY,
                self.PLAN_LANDLORD_MONTHLY,
                self.PLAN_LANDLORD_YEARLY,
            ]
        return False

    @property
    def is_landlord_active(self):
        if self.status in [self.STATUS_ACTIVE, self.STATUS_TRIALING]:
            return self.plan in [
                self.PLAN_LANDLORD_MONTHLY,
                self.PLAN_LANDLORD_YEARLY,
            ]
        return False

    @property
    def entitlements(self):
        is_pro = self.is_pro_active
        is_landlord = self.is_landlord_active
        return {
            "unlimited_history": is_pro,
            "forecast_trio": is_pro,
            "spot_optimizer": is_pro,
            "battery_arbitrage": is_pro,
            "live_co2_signal": is_pro,
            "proactive_alerts": is_pro,
            "multi_format_exports": is_pro,
            "multi_home_landlord": is_landlord,
            "tenant_sub_billing": is_landlord,
        }


class EMSInvoice(models.Model):
    """
    SaaS-Rechnung für Endnutzer-Abonnements (Säule 1).
    """

    STATUS_PAID = "paid"
    STATUS_OPEN = "open"
    STATUS_REFUNDED = "refunded"

    STATUS_CHOICES = [
        (STATUS_PAID, "Bezahlt"),
        (STATUS_OPEN, "Offen"),
        (STATUS_REFUNDED, "Erstattet"),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    invoice_number = models.CharField(max_length=64, unique=True)
    user = models.ForeignKey(
        "accounts.User",
        on_delete=models.CASCADE,
        related_name="ems_invoices",
    )
    subscription = models.ForeignKey(
        EMSSubscription,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="invoices",
    )

    plan_name = models.CharField(max_length=100)
    amount_net_eur = models.DecimalField(max_digits=10, decimal_places=2)
    tax_eur = models.DecimalField(max_digits=10, decimal_places=2)
    amount_gross_eur = models.DecimalField(max_digits=10, decimal_places=2)
    tax_rate_pct = models.DecimalField(max_digits=5, decimal_places=2, default=19.0)

    period_start = models.DateField()
    period_end = models.DateField()

    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=STATUS_PAID)
    payment_method = models.CharField(max_length=50, default="Kreditkarte (via Stripe)")
    paid_at = models.DateTimeField(null=True, blank=True)

    # Rechnungsadresse Snapshot
    recipient_name = models.CharField(max_length=255, blank=True)
    company_name = models.CharField(max_length=255, blank=True)
    street_and_number = models.CharField(max_length=255, blank=True)
    postal_code = models.CharField(max_length=20, blank=True)
    city = models.CharField(max_length=100, blank=True)
    country = models.CharField(max_length=50, default="DE")
    vat_id = models.CharField(max_length=50, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "billing_ems_invoice"
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["user", "-created_at"]),
            models.Index(fields=["invoice_number"]),
        ]

    def __str__(self):
        return f"{self.invoice_number} - {self.user.email} ({self.amount_gross_eur} €)"


class Coupon(models.Model):
    """
    Gutschein- und Promo-Codes für Abonnements und Rabatte.
    """
    TYPE_PERCENT = "percent"            # z. B. 100% oder 20%
    TYPE_FIXED_AMOUNT = "fixed_amount"  # z. B. 10.00 EUR
    TYPE_FREE_MONTHS = "free_months"    # z. B. 3 Monate Pro kostenlos

    TYPE_CHOICES = [
        (TYPE_PERCENT, "Prozentualer Rabatt (%)"),
        (TYPE_FIXED_AMOUNT, "Fester Rabattbetrag (€)"),
        (TYPE_FREE_MONTHS, "Gratismonate"),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    code = models.CharField(max_length=64, unique=True)
    description = models.CharField(max_length=255, blank=True)
    discount_type = models.CharField(max_length=20, choices=TYPE_CHOICES, default=TYPE_FREE_MONTHS)
    discount_value = models.DecimalField(max_digits=10, decimal_places=2, default=100.00)
    free_plan = models.CharField(max_length=32, default=EMSSubscription.PLAN_PRO_MONTHLY)
    duration_months = models.PositiveIntegerField(default=3)

    valid_from = models.DateTimeField(null=True, blank=True)
    valid_until = models.DateTimeField(null=True, blank=True)

    max_redemptions = models.PositiveIntegerField(default=100)
    redemptions_count = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "billing_coupon"
        indexes = [
            models.Index(fields=["code", "is_active"]),
        ]

    def __str__(self):
        return f"{self.code} ({self.discount_type}: {self.discount_value})"

    @property
    def is_valid(self):
        from django.utils import timezone
        now = timezone.now()
        if not self.is_active:
            return False
        if self.valid_from and now < self.valid_from:
            return False
        if self.valid_until and now > self.valid_until:
            return False
        if self.max_redemptions > 0 and self.redemptions_count >= self.max_redemptions:
            return False
        return True


class CouponRedemption(models.Model):
    """
    Dokumentiert die Einlösung eines Gutscheins durch einen Benutzer.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    coupon = models.ForeignKey(Coupon, on_delete=models.CASCADE, related_name="redemptions")
    user = models.ForeignKey("accounts.User", on_delete=models.CASCADE, related_name="coupon_redemptions")
    subscription = models.ForeignKey(EMSSubscription, on_delete=models.SET_NULL, null=True, blank=True)
    applied_discount = models.CharField(max_length=255, blank=True)
    redeemed_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "billing_coupon_redemption"
        unique_together = ("coupon", "user")
        ordering = ["-redeemed_at"]

    def __str__(self):
        return f"{self.user.email} löste {self.coupon.code} ein ({self.redeemed_at})"


# =========================================================
# ⚡ ENERGY SHARING: TARIFE & MONATSABRECHNUNGEN (SÄULE 2)
# =========================================================

class CommunityTariff(models.Model):
    """
    Tarifstruktur für eine Energy Sharing Community.
    Definiert Bezugs- und Einspeisevergütung sowie Community-Umlagen pro kWh
    und das vertragliche Allokationsmodell.
    """
    ALLOCATION_DYNAMIC = "dynamic"
    ALLOCATION_STATIC = "static"
    ALLOCATION_HYBRID = "hybrid"

    ALLOCATION_CHOICES = [
        (ALLOCATION_DYNAMIC, "Dynamisch nach Verbrauch (Standard)"),
        (ALLOCATION_STATIC, "Statische Beteiligungsquoten (MEA)"),
        (ALLOCATION_HYBRID, "Hybrid (Vorrang-Quote + dynamischer Überlauf)"),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    tenant = models.ForeignKey(
        "core.Tenant",
        on_delete=models.CASCADE,
        related_name="community_tariffs",
    )
    name = models.CharField(max_length=150, default="Standard Sharing Tarif")
    allocation_model = models.CharField(
        max_length=20,
        choices=ALLOCATION_CHOICES,
        default=ALLOCATION_DYNAMIC,
        help_text="Verfahren zur Verteilung von Solarstrom innerhalb der Gemeinschaft",
    )

    PRICING_MODEL_STATIC = "static"
    PRICING_MODEL_SPOT_INDEXED = "spot_indexed"
    PRICING_MODEL_TIME_OF_USE = "time_of_use"

    PRICING_MODEL_CHOICES = [
        (PRICING_MODEL_STATIC, "Statischer Festpreis"),
        (PRICING_MODEL_SPOT_INDEXED, "Börsenpreis-indexiert (EPEX Spot Day-Ahead)"),
        (PRICING_MODEL_TIME_OF_USE, "Dynamischer Zeittarif (HT/NT)"),
    ]

    pricing_model = models.CharField(
        max_length=30,
        choices=PRICING_MODEL_CHOICES,
        default=PRICING_MODEL_STATIC,
        help_text="Preismechanismus: Festpreis, EPEX Spotmarkt-Indexierung oder Zeittarif",
    )

    # Preise in Cent pro kWh
    sharing_price_ct_kwh = models.DecimalField(
        max_digits=6,
        decimal_places=2,
        default=12.00,
        help_text="Bezugspreis für geteilten Solarstrom (Cent/kWh) im statischen Modell",
    )
    producer_payout_ct_kwh = models.DecimalField(
        max_digits=6,
        decimal_places=2,
        default=10.00,
        help_text="Vergütung für geteilten Solarstrom an Einspeiser (Cent/kWh)",
    )
    community_fee_ct_kwh = models.DecimalField(
        max_digits=6,
        decimal_places=2,
        default=2.00,
        help_text="Betriebsumlage der Energy Community (Cent/kWh)",
    )
    grid_fee_saved_ct_kwh = models.DecimalField(
        max_digits=6,
        decimal_places=2,
        default=0.00,
        help_text="Ermäßigte Netzentgelte gem. § 42b EnWG (Cent/kWh)",
    )

    # Parameter für Börsenpreis-indexierte Tarife
    spot_markup_ct_kwh = models.DecimalField(
        max_digits=6,
        decimal_places=2,
        default=3.50,
        help_text="Aufschlag auf den EPEX Spotpreis in Cent/kWh (z. B. +3,50 Ct)",
    )
    spot_floor_price_ct_kwh = models.DecimalField(
        max_digits=6,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="Mindestpreisuntergrenze in Cent/kWh (Floor)",
    )
    spot_cap_price_ct_kwh = models.DecimalField(
        max_digits=6,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="Maximalpreisobergrenze / Preisbremse in Cent/kWh (Cap)",
    )
    feed_in_spot_share_pct = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=80.00,
        help_text="Prozentuale Beteiligung des Einspeisers am Börsenpreis (%)",
    )

    valid_from = models.DateTimeField(default=timezone.now)
    valid_to = models.DateTimeField(null=True, blank=True)
    is_active = models.BooleanField(default=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "billing_community_tariff"
        ordering = ["-valid_from"]
        indexes = [
            models.Index(fields=["tenant", "is_active"]),
            models.Index(fields=["tenant", "valid_from"]),
        ]

    def __str__(self):
        return f"{self.tenant.name} - {self.name} ({self.sharing_price_ct_kwh} Ct/kWh, {self.allocation_model})"


class CommunityMemberShare(models.Model):
    """
    Beteiligungsquote eines Mitglieds an den Gemeinschaftserzeugungsanlagen (z. B. PV, Speicher).
    Unterstützt Prozentangaben, Miteigentumsanteile (MEA) sowie kWp-Zuweisungen.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    tenant = models.ForeignKey(
        "core.Tenant",
        on_delete=models.CASCADE,
        related_name="member_shares",
    )
    membership = models.ForeignKey(
        "accounts.TenantMembership",
        on_delete=models.CASCADE,
        related_name="shares",
    )
    user = models.ForeignKey(
        "accounts.User",
        on_delete=models.CASCADE,
        related_name="community_shares",
    )

    # Beteiligungsquote in Prozent (z. B. 25.5000 %)
    share_percent = models.DecimalField(
        max_digits=7,
        decimal_places=4,
        default=0.0000,
        help_text="Beteiligungsquote an der Gemeinschafts-PV in Prozent (%)",
    )

    # Miteigentumsanteile (MEA - z. B. 250 / 1000)
    mea_numerator = models.PositiveIntegerField(
        null=True,
        blank=True,
        help_text="Miteigentumsanteile Zähler (z. B. 250)",
    )
    mea_denominator = models.PositiveIntegerField(
        default=1000,
        help_text="Miteigentumsanteile Nenner (Standard 1000 oder 10.000)",
    )

    # Zugewiesene kWp-Leistung (optional)
    assigned_kwp = models.DecimalField(
        max_digits=8,
        decimal_places=3,
        null=True,
        blank=True,
        help_text="Zugewiesener kWp-Anteil an der Gemeinschaftsanlage",
    )

    valid_from = models.DateTimeField(default=timezone.now)
    valid_to = models.DateTimeField(null=True, blank=True)
    is_active = models.BooleanField(default=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "billing_community_member_share"
        ordering = ["-valid_from"]
        indexes = [
            models.Index(fields=["tenant", "is_active"]),
            models.Index(fields=["membership", "is_active"]),
            models.Index(fields=["user", "is_active"]),
        ]

    def __str__(self):
        return f"{self.tenant.name} - {self.user.email}: {self.share_percent}% ({self.mea_numerator}/{self.mea_denominator} MEA)"

    def save(self, *args, **kwargs):
        # Automatische Berechnung des Prozentsatzes aus MEA, falls Zähler angegeben
        if self.mea_numerator is not None and self.mea_denominator and self.mea_denominator > 0:
            calculated_pct = (Decimal(self.mea_numerator) / Decimal(self.mea_denominator)) * Decimal("100.0")
            if not self.share_percent or self.share_percent == Decimal("0.0"):
                self.share_percent = round(calculated_pct, 4)
        super().save(*args, **kwargs)



class CommunityMonthlyStatement(models.Model):
    """
    Monatlicher Abrechnungsnachweis pro Mitglied einer Energy Sharing Community.
    Weist geteilte Erzeugung vs. Verbrauch sowie Netto-Gutschrift/Forderung aus.
    """
    STATUS_DRAFT = "draft"
    STATUS_FINALIZED = "finalized"
    STATUS_SETTLED = "settled"

    STATUS_CHOICES = [
        (STATUS_DRAFT, "Entwurf"),
        (STATUS_FINALIZED, "Abgerechnet"),
        (STATUS_SETTLED, "Ausgeglichen"),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    statement_number = models.CharField(max_length=64, unique=True)

    tenant = models.ForeignKey(
        "core.Tenant",
        on_delete=models.CASCADE,
        related_name="monthly_statements",
    )
    membership = models.ForeignKey(
        "accounts.TenantMembership",
        on_delete=models.CASCADE,
        related_name="sharing_statements",
    )
    user = models.ForeignKey(
        "accounts.User",
        on_delete=models.CASCADE,
        related_name="sharing_statements",
    )
    tariff = models.ForeignKey(
        CommunityTariff,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="statements",
    )

    period_start = models.DateField()
    period_end = models.DateField()

    # Mengenbilanz (kWh)
    produced_total_kwh = models.DecimalField(max_digits=12, decimal_places=3, default=0.0)
    consumed_total_kwh = models.DecimalField(max_digits=12, decimal_places=3, default=0.0)
    shared_imported_kwh = models.DecimalField(max_digits=12, decimal_places=3, default=0.0)
    shared_exported_kwh = models.DecimalField(max_digits=12, decimal_places=3, default=0.0)
    grid_residual_import_kwh = models.DecimalField(max_digits=12, decimal_places=3, default=0.0)
    grid_residual_export_kwh = models.DecimalField(max_digits=12, decimal_places=3, default=0.0)

    # Finanzielle Verrechnung (€)
    charge_shared_import_eur = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    credit_shared_export_eur = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    community_fee_eur = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    net_balance_eur = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0.00,
        help_text="Netto-Saldo: Positiv = Gutschrift/Auszahlung, Negativ = Nachzahlung",
    )

    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=STATUS_DRAFT)
    finalized_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "billing_community_monthly_statement"
        ordering = ["-period_start", "-created_at"]
        unique_together = ("membership", "period_start", "period_end")
        indexes = [
            models.Index(fields=["tenant", "period_start"]),
            models.Index(fields=["user", "period_start"]),
            models.Index(fields=["statement_number"]),
        ]

    def __str__(self):
        return f"{self.statement_number} - {self.user.email} ({self.period_start} bis {self.period_end}): {self.net_balance_eur} €"


class CommunityAnnouncement(models.Model):
    """
    Zentrale Rundschreiben / Mitteilungen für eine Energiegemeinschaft.
    Ermöglicht Betreibern & Admins, alle Teilnehmer über Tarife, Zählerwechsel
    oder Wartungsarbeiten zentral zu informieren.
    """
    CATEGORY_INFO = "info"
    CATEGORY_TARIFF = "tariff"
    CATEGORY_MAINTENANCE = "maintenance"
    CATEGORY_IMPORTANT = "important"

    CATEGORY_CHOICES = [
        (CATEGORY_INFO, "Information"),
        (CATEGORY_TARIFF, "Tarif & Abrechnung"),
        (CATEGORY_MAINTENANCE, "Wartung & Zähler"),
        (CATEGORY_IMPORTANT, "Wichtig / Dringend"),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    tenant = models.ForeignKey(
        "core.Tenant",
        on_delete=models.CASCADE,
        related_name="announcements",
    )
    author = models.ForeignKey(
        "accounts.User",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="community_announcements",
    )
    title = models.CharField(max_length=200)
    message = models.TextField()
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES, default=CATEGORY_INFO)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "billing_community_announcement"
        ordering = ["-created_at"]

    def __str__(self):
        return f"[{self.tenant.name}] {self.title}"


# =========================================================
# 🔄 SIGNALS: AUTOMATISCHE FREE-PLAN ZUWEISUNG BEI REGISTRIERUNG
# =========================================================
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.conf import settings
from django.utils import timezone

@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def auto_create_free_ems_subscription(sender, instance, created, **kwargs):
    """
    Stellt sicher, dass jede Neuregistrierung sofort den kostenlosen Free-Plan erhält.
    """
    if created:
        EMSSubscription.objects.get_or_create(
            user=instance,
            defaults={
                "plan": EMSSubscription.PLAN_FREE,
                "status": EMSSubscription.STATUS_ACTIVE,
                "current_period_start": timezone.now(),
                "payment_method": "stripe",
            },
        )



