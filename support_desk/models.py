#############################
# support_desk/models.py
#############################

import uuid
from django.conf import settings
from django.db import models


# =========================================================================
# 1. WISSENSPORTAL & FAQ MODELLE (KNOWLEDGE BASE)
# =========================================================================

class HelpCategory(models.Model):
    """
    Kategorie für Hilfe-Artikel und FAQ-Themenbereiche (z. B. Hardware, Tarife, Prognose).
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    key = models.SlugField(max_length=80, unique=True, help_text="Technischer Key (z. B. inverters, optimizer)")
    icon = models.CharField(max_length=20, default="📖", help_text="Emoji oder Icon-Name")
    title_de = models.CharField(max_length=200)
    title_en = models.CharField(max_length=200)
    description_de = models.TextField(blank=True)
    description_en = models.TextField(blank=True)
    sort_order = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "helpcenter_helpcategory"
        verbose_name = "Hilfe-Kategorie (Wissensportal)"
        verbose_name_plural = "Hilfe-Kategorien (Wissensportal)"
        ordering = ["sort_order", "title_de"]

    def __str__(self):
        return f"{self.icon} {self.title_de} ({self.key})"


class HelpArticle(models.Model):
    """
    Vollwertiger Markdown-Hilfeartikel für Handbuch, FAQ und In-App-Drawer Deflection.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    category = models.ForeignKey(
        HelpCategory,
        related_name="articles",
        on_delete=models.CASCADE,
    )
    slug = models.SlugField(max_length=120, unique=True, help_text="URL-Slug (z. B. solar-prognose-verstaendnis)")
    context_key = models.CharField(
        max_length=50,
        blank=True,
        db_index=True,
        help_text="Kontext-Schlüssel für Drawer-Matching (z. B. 'forecast', 'energy', 'tariffs', 'alerts', 'devices', 'optimizer')",
    )

    title_de = models.CharField(max_length=255)
    title_en = models.CharField(max_length=255)
    summary_de = models.TextField(blank=True, help_text="Kurzbeschreibung für Suchergebnisse und Drawer")
    summary_en = models.TextField(blank=True)

    content_de = models.TextField(help_text="Ausführlicher Artikelinhalt in Markdown (Deutsch)")
    content_en = models.TextField(blank=True, help_text="Ausführlicher Artikelinhalt in Markdown (Englisch)")

    tags = models.JSONField(default=list, blank=True, help_text="Liste von Schlagworten für Volltextsuche")
    is_published = models.BooleanField(default=True, db_index=True)
    is_featured = models.BooleanField(default=False, help_text="Hervorheben auf der Wissensportal-Startseite")
    sort_order = models.IntegerField(default=0)

    views_count = models.PositiveIntegerField(default=0)
    helpful_yes = models.PositiveIntegerField(default=0)
    helpful_no = models.PositiveIntegerField(default=0)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "helpcenter_helparticle"
        verbose_name = "Hilfe-Artikel (Wissensportal)"
        verbose_name_plural = "Hilfe-Artikel (Wissensportal)"
        ordering = ["sort_order", "-is_featured", "-created_at"]

    def __str__(self):
        return f"{self.title_de} [{self.slug}]"


# =========================================================================
# 2. SUPPORT DESK & TICKET SYSTEM MODELLE
# =========================================================================

class SupportProjectConfig(models.Model):
    """
    Configuration and API access keys for connected projects (e.g. sharegy, factofy).
    """
    project_key = models.SlugField(max_length=50, unique=True, help_text="Unique slug: 'sharegy', 'factofy', etc.")
    name = models.CharField(max_length=100, help_text="Display name (e.g. 'Sharegy HEMS', 'Factofy Digital Twin')")
    secret_key = models.CharField(
        max_length=128,
        default=uuid.uuid4,
        help_text="Shared secret key used to sign and verify external JWT tokens / API requests",
    )
    ticket_prefix = models.CharField(max_length=10, default="SUP", help_text="Prefix for ticket numbers, e.g. SHAR, FACT")
    allowed_categories = models.JSONField(
        default=list,
        blank=True,
        help_text="List of allowed categories for this project, e.g. ['hardware', 'telemetry', 'billing']",
    )
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Support-Projektkonfiguration"
        verbose_name_plural = "Support-Projektkonfigurationen"

    def __str__(self):
        return f"{self.name} [{self.project_key}]"


class Ticket(models.Model):
    """
    Universal Support Ticket entity for Sharegy and external platforms (Factofy).
    """
    STATUS_OPEN = "open"
    STATUS_IN_PROGRESS = "in_progress"
    STATUS_WAITING_CUSTOMER = "waiting_customer"
    STATUS_WAITING_INTERNAL = "waiting_internal"
    STATUS_RESOLVED = "resolved"
    STATUS_CLOSED = "closed"

    STATUS_CHOICES = [
        (STATUS_OPEN, "Neu / Offen"),
        (STATUS_IN_PROGRESS, "In Bearbeitung"),
        (STATUS_WAITING_CUSTOMER, "Wartet auf Rückmeldung"),
        (STATUS_WAITING_INTERNAL, "Wartet intern / Entwicklung"),
        (STATUS_RESOLVED, "Gelöst"),
        (STATUS_CLOSED, "Geschlossen"),
    ]

    PRIORITY_LOW = "low"
    PRIORITY_MEDIUM = "medium"
    PRIORITY_HIGH = "high"
    PRIORITY_URGENT = "urgent"

    PRIORITY_CHOICES = [
        (PRIORITY_LOW, "Niedrig"),
        (PRIORITY_MEDIUM, "Normal"),
        (PRIORITY_HIGH, "Hoch"),
        (PRIORITY_URGENT, "Dringend / Kritisch"),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    ticket_number = models.CharField(max_length=30, unique=True, db_index=True)
    project_key = models.CharField(max_length=50, default="sharegy", db_index=True)

    # User relations: local Django User OR external guest/JWT user (from Factofy)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="support_tickets",
    )
    external_user_id = models.CharField(
        max_length=100,
        blank=True,
        db_index=True,
        help_text="External user ID from connected platform (e.g. Factofy usr_123)",
    )
    contact_name = models.CharField(max_length=150, blank=True)
    contact_email = models.EmailField(blank=True, db_index=True)

    # Assignment & Triage
    assigned_agent = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="assigned_support_tickets",
    )

    # Core Ticket Details
    subject = models.CharField(max_length=255)
    category = models.CharField(max_length=60, default="general", db_index=True)
    priority = models.CharField(max_length=20, choices=PRIORITY_CHOICES, default=PRIORITY_MEDIUM, db_index=True)
    status = models.CharField(max_length=30, choices=STATUS_CHOICES, default=STATUS_OPEN, db_index=True)

    # Dynamic free-form Context Payload (Devices, Inverters, Invoices, 3D Assets, Geolocation)
    context_payload = models.JSONField(
        default=dict,
        blank=True,
        help_text="Arbitrary telemetry/asset metadata (e.g. device_id, building_id, sensor_eui, coordinates, url, browser)",
    )

    # Timestamps & SLAs
    first_response_due = models.DateTimeField(null=True, blank=True)
    first_responded_at = models.DateTimeField(null=True, blank=True)
    resolved_at = models.DateTimeField(null=True, blank=True)
    closed_at = models.DateTimeField(null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Support-Ticket"
        verbose_name_plural = "Support-Tickets"
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["project_key", "status"]),
            models.Index(fields=["project_key", "created_at"]),
        ]

    def __str__(self):
        return f"[{self.project_key.upper()}] #{self.ticket_number} - {self.subject} ({self.get_status_display()})"


class TicketMessage(models.Model):
    """
    Message or timeline update within a support ticket thread.
    Can be public (customer-facing) or an internal staff note (yellow note).
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    ticket = models.ForeignKey(Ticket, on_delete=models.CASCADE, related_name="messages")

    sender = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="sent_support_messages",
    )
    external_sender_name = models.CharField(max_length=150, blank=True)
    external_sender_email = models.EmailField(blank=True)

    is_staff_reply = models.BooleanField(default=False)
    is_internal_note = models.BooleanField(
        default=False,
        help_text="Internal note only visible to support team / staff agents.",
    )

    body = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)

    class Meta:
        verbose_name = "Ticket-Nachricht"
        verbose_name_plural = "Ticket-Nachrichten"
        ordering = ["created_at"]

    def __str__(self):
        note_badge = " [INTERN]" if self.is_internal_note else ""
        return f"Msg on #{self.ticket.ticket_number} by {self.sender or self.external_sender_name}{note_badge}"


class TicketAttachment(models.Model):
    """
    File attachments (screenshots, log dumps, diagnostics) linked to a ticket or message.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    ticket = models.ForeignKey(Ticket, on_delete=models.CASCADE, related_name="attachments")
    message = models.ForeignKey(
        TicketMessage,
        null=True,
        blank=True,
        on_delete=models.CASCADE,
        related_name="attachments",
    )

    file = models.FileField(upload_to="support_attachments/%Y/%m/")
    filename = models.CharField(max_length=255)
    file_size = models.PositiveIntegerField(default=0)
    mime_type = models.CharField(max_length=120, default="application/octet-stream")

    uploaded_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Ticket-Anhang"
        verbose_name_plural = "Ticket-Anhänge"

    def __str__(self):
        return f"{self.filename} ({self.file_size} bytes)"


class CannedResponse(models.Model):
    """
    Pre-defined canned responses and snippets for support agents.
    """
    project_key = models.CharField(max_length=50, default="global", db_index=True)
    shortcut = models.SlugField(max_length=50, help_text="e.g. 'reboot-inverter', 'gateway-sync'")
    title = models.CharField(max_length=150)
    category = models.CharField(max_length=60, blank=True)
    body_de = models.TextField()
    body_en = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Textbaustein (Canned Response)"
        verbose_name_plural = "Textbausteine (Canned Responses)"
        ordering = ["category", "title"]

    def __str__(self):
        return f"!{self.shortcut} - {self.title}"


class TicketActivityLog(models.Model):
    """
    Audit log of actions performed on a ticket (status change, reassignment, note added).
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    ticket = models.ForeignKey(Ticket, on_delete=models.CASCADE, related_name="activity_logs")
    user = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL)
    actor_name = models.CharField(max_length=150, default="System")
    action = models.CharField(max_length=100) # 'status_changed', 'priority_changed', 'agent_assigned', 'message_sent'
    details = models.JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Ticket-Aktivitätsprotokoll"
        verbose_name_plural = "Ticket-Aktivitätsprotokolle"
        ordering = ["-created_at"]
