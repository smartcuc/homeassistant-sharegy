###################
# billing/models.py
###################

import uuid
from django.db import models
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
