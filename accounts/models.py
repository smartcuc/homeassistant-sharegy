####################
# accounts/models.py
####################

import uuid
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.conf import settings
from django.utils import timezone
from datetime import timedelta
from zoneinfo import available_timezones

class User(AbstractUser):
    """
    Identity Layer (global).
    Keine Tenant-Abhängigkeiten hier!
    """

    PLATFORM_ROLE_SYSTEM_ADMIN = "system_admin"
    PLATFORM_ROLE_FINANCE = "finance"
    PLATFORM_ROLE_USER_ADMIN = "user_admin"
    PLATFORM_ROLE_HELPDESK = "helpdesk"
    PLATFORM_ROLE_NONE = "none"

    PLATFORM_ROLE_CHOICES = [
        (PLATFORM_ROLE_SYSTEM_ADMIN, "Systemadmin"),
        (PLATFORM_ROLE_FINANCE, "Finanzen & Billing"),
        (PLATFORM_ROLE_USER_ADMIN, "Userverwaltung (Global)"),
        (PLATFORM_ROLE_HELPDESK, "Plattform Helpdesk"),
        (PLATFORM_ROLE_NONE, "Keine Plattform-Rolle"),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    email = models.EmailField(unique=True)
    is_verified = models.BooleanField(default=False)

    # Globale Plattform-Rolle (Ebene 1)
    platform_role = models.CharField(
        max_length=30,
        choices=PLATFORM_ROLE_CHOICES,
        default=PLATFORM_ROLE_NONE,
    )

    # ✅ Tibber Integration
    tibber_token = models.CharField(max_length=255, blank=True, null=True)
    tibber_home_id = models.CharField(max_length=255, blank=True, null=True)

    created_at = models.DateTimeField(auto_now_add=True)

    @property
    def is_platform_admin(self) -> bool:
        return bool(self.is_superuser or self.platform_role == self.PLATFORM_ROLE_SYSTEM_ADMIN)

    @property
    def is_finance_admin(self) -> bool:
        return bool(self.is_superuser or self.platform_role in [self.PLATFORM_ROLE_SYSTEM_ADMIN, self.PLATFORM_ROLE_FINANCE])

    @property
    def is_global_user_admin(self) -> bool:
        return bool(self.is_superuser or self.platform_role in [self.PLATFORM_ROLE_SYSTEM_ADMIN, self.PLATFORM_ROLE_USER_ADMIN])

    @property
    def is_platform_helpdesk(self) -> bool:
        return bool(self.is_staff or self.is_superuser or self.platform_role in [self.PLATFORM_ROLE_SYSTEM_ADMIN, self.PLATFORM_ROLE_HELPDESK])

    def __str__(self):
        return self.email



class UserProfile(models.Model):
    """
    Person-/Kundendaten (tenant-unabhängig).
    """

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="profile")

    # Adresse
    street = models.CharField(max_length=255, blank=True)
    house_number = models.CharField(max_length=20, blank=True)
    postal_code = models.CharField(max_length=20, blank=True)
    city = models.CharField(max_length=100, blank=True)
    country = models.CharField(max_length=50, default="DE")

    # Kontakt
    phone = models.CharField(max_length=30, blank=True)

    # Typ
    customer_type = models.CharField(
        max_length=20,
        choices=[("private", "Private"), ("business", "Business")],
        default="private",
    )

    # Business optional
    billing_name = models.CharField(max_length=255, blank=True)
    billing_email = models.EmailField(blank=True, default="")
    company_name = models.CharField(max_length=255, blank=True)
    vat_id = models.CharField(max_length=50, blank=True)

    # DSGVO / Consent
    consent_given = models.BooleanField(default=False)
    consent_timestamp = models.DateTimeField(null=True, blank=True)

    # Avatar (Preset-Key, Emoji oder Icon-Identifier)
    avatar = models.CharField(max_length=100, blank=True, default="")

    created_at = models.DateTimeField(auto_now_add=True)


class UserSettings(models.Model):
    """
    Standalone Dashboard / Präferenzen (tenant-unabhängig).
    """

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="settings")

    # --- Dashboard ---
    DASHBOARD_MODE = [
        ("simple", "Simple"),
        ("advanced", "Advanced"),
    ]

    dashboard_mode = models.CharField(
        max_length=20,
        choices=DASHBOARD_MODE,
        default="simple",
    )

    USAGE_MODE = [
        ("standalone", "Standalone"),
        ("tenant", "Tenant"),
        ("hybrid", "Hybrid"),
    ]

    usage_mode = models.CharField(
        max_length=20,
        choices=USAGE_MODE,
        default="standalone",
    )

    # --- Benutzer ---
    language = models.CharField(
        max_length=10,
        default="de",
    )

    TIMEZONE_CHOICES = sorted([(tz, tz) for tz in available_timezones()])

    timezone = models.CharField(
        max_length=64,
        choices=TIMEZONE_CHOICES,
        blank=True,
        default="",
    )

    # --- Onboarding ---
    ONBOARDING_STEPS = [
        ("welcome", "Welcome"),
        ("setup", "Setup"),
        ("done", "Done"),
    ]

    onboarding_step = models.CharField(
        max_length=20,
        choices=ONBOARDING_STEPS,
        default="welcome",
    )

    created_at = models.DateTimeField(auto_now_add=True)

    @property
    def is_onboarding_done(self):
        return self.onboarding_step == "done"


class TenantMembership(models.Model):

    ROLE_ADMIN = "admin"                    # Energy-Admin (Vollzugriff auf Community & Tarife)
    ROLE_USER_ADMIN = "user_admin"          # Energy-Userverwaltung (Einladungen & Rollenzuweisung)
    ROLE_HELPDESK = "helpdesk"              # Energy-Helpdesk (1st-Level Quartierssupport)
    ROLE_AUDITOR = "auditor"                # Kassenprüfer / Beirat (Read-only Bilanzen & Berichte)
    ROLE_MEMBER = "member"                  # Standard Community-Mitglied (Consumer/Producer/Prosumer)
    ROLE_EDITOR = "editor"                  # Legacy Alias -> user_admin / admin
    ROLE_VIEWER = "viewer"                  # Legacy Alias -> member / auditor

    ROLE_CHOICES = [
        (ROLE_ADMIN, "Energy Admin"),
        (ROLE_USER_ADMIN, "Energy Userverwaltung"),
        (ROLE_HELPDESK, "Energy Helpdesk"),
        (ROLE_AUDITOR, "Kassenprüfer / Auditor"),
        (ROLE_MEMBER, "Mitglied"),
        (ROLE_EDITOR, "Editor (Legacy)"),
        (ROLE_VIEWER, "Viewer (Legacy)"),
    ]

    # ✅ FIX: related_name statt source
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="memberships"
    )

    tenant = models.ForeignKey(
        "core.Tenant",
        on_delete=models.CASCADE,
        related_name="memberships"
    )

    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default=ROLE_MEMBER)

    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("user", "tenant")

    def __str__(self):
        return f"{self.user.email} → {self.tenant} ({self.role})"


class TenantInvite(models.Model):
    token = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)

    tenant = models.ForeignKey("core.Tenant", on_delete=models.CASCADE)
    
    role = models.CharField(
        max_length=20,
        choices=TenantMembership.ROLE_CHOICES,
        default=TenantMembership.ROLE_MEMBER
    )


    max_uses = models.IntegerField(default=1)
    used_count = models.IntegerField(default=0)

    is_active = models.BooleanField(default=True)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.tenant} invite ({self.role})"

class AuditLog(models.Model):

    ACTION_CHOICES = [
        ("invite_created", "Invite Created"),
        ("member_removed", "Member Removed"),
        ("role_updated", "Role Updated"),
        ("invite_deactivated", "Invite Deactivated"),
    ]

    user = models.ForeignKey(
        "accounts.User",
        on_delete=models.SET_NULL,
        null=True
    )

    tenant = models.ForeignKey(
        "core.Tenant",
        on_delete=models.CASCADE
    )

    action = models.CharField(max_length=50, choices=ACTION_CHOICES)

    target_user = models.ForeignKey(
        "accounts.User",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="target_logs"
    )

    metadata = models.JSONField(blank=True, default=dict)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.action} by {self.user} in {self.tenant}"


class MagicLoginToken(models.Model):
    token = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)

    created_at = models.DateTimeField(auto_now_add=True)
    used_at = models.DateTimeField(null=True, blank=True)
    is_used = models.BooleanField(default=False)

    # ✅ NEU (TRACKING)
    opened_at = models.DateTimeField(null=True, blank=True)
    last_login_ip = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.TextField(blank=True)

    # Tracking
    clicked_at = models.DateTimeField(null=True, blank=True)

    def is_expired(self):
        return self.created_at < timezone.now() - timedelta(minutes=15)

    def __str__(self):
        return f"{self.user} - {self.token}"


class UserTermsConsent(models.Model):
    """
    Dokumentierte, revisionssichere Zustimmung zu AGB & Datenschutz (DSGVO-Nachweispflicht).
    """
    CONSENT_REGISTRATION = "registration"
    CONSENT_UPGRADE_PRO = "upgrade_pro"
    CONSENT_TERMS_UPDATE = "terms_update"

    CONSENT_CHOICES = [
        (CONSENT_REGISTRATION, "Registrierung"),
        (CONSENT_UPGRADE_PRO, "Pro/Landlord Upgrade"),
        (CONSENT_TERMS_UPDATE, "AGB-Aktualisierung"),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="terms_consents")
    terms_version = models.CharField(max_length=32, default="2026-08")
    privacy_version = models.CharField(max_length=32, default="2026-08")
    consent_type = models.CharField(max_length=32, choices=CONSENT_CHOICES, default=CONSENT_REGISTRATION)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "accounts_user_terms_consent"
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["user", "-created_at"]),
        ]

    def __str__(self):
        return f"{self.user.email} - {self.consent_type} ({self.terms_version}) am {self.created_at}"

