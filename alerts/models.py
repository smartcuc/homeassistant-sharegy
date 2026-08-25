###################
# alerts/models.py
###################

import uuid
from django.db import models


class AlertEvent(models.Model):
    SEVERITY_CRITICAL = "critical"
    SEVERITY_WARNING = "warning"
    SEVERITY_INFO = "info"

    SEVERITY_CHOICES = [
        (SEVERITY_CRITICAL, "Kritisch"),
        (SEVERITY_WARNING, "Warnung"),
        (SEVERITY_INFO, "Information / Spar-Tipp"),
    ]

    STATUS_ACTIVE = "active"
    STATUS_ACKNOWLEDGED = "acknowledged"
    STATUS_RESOLVED = "resolved"

    STATUS_CHOICES = [
        (STATUS_ACTIVE, "Aktiv"),
        (STATUS_ACKNOWLEDGED, "Gesehen / Quittiert"),
        (STATUS_RESOLVED, "Behoben / Gelöst"),
    ]

    ALERT_TYPES = [
        ("no_pv", "Keine PV-Erzeugung (Ertragsausfall)"),
        ("battery_empty", "Batterie leer / Ungewöhnliche Entladung"),
        ("night_leakage", "Unerwarteter Nachtverbrauch / Dauerlast"),
        ("device_offline", "Gerät offline / Signal-Verlust"),
        ("negative_price", "Negativer Strompreis / Börsentief-Chance"),
        ("price_peak", "Extremer Preis-Peak (Dunkelflaute)"),
        ("grid_import_surplus", "Netzbezug trotz Solarüberschuss"),
        ("freeze_guard", "Frostschutz & Wärmepumpen-Vorlauf"),
        ("custom", "Benutzerdefiniert"),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    home = models.ForeignKey(
        "devices.Home",
        on_delete=models.CASCADE,
        related_name="alert_events",
    )

    device = models.ForeignKey(
        "devices.Device",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="alert_events",
    )

    alert_type = models.CharField(max_length=64, choices=ALERT_TYPES)
    severity = models.CharField(max_length=32, choices=SEVERITY_CHOICES, default=SEVERITY_INFO)

    title = models.CharField(max_length=255)
    message = models.TextField()
    action_hint = models.CharField(max_length=255, blank=True, default="")
    action_type = models.CharField(max_length=64, blank=True, default="")

    details = models.JSONField(default=dict, blank=True)
    status = models.CharField(max_length=32, choices=STATUS_CHOICES, default=STATUS_ACTIVE, db_index=True)

    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    acknowledged_at = models.DateTimeField(null=True, blank=True)
    resolved_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["home", "status", "created_at"]),
            models.Index(fields=["home", "alert_type", "status"]),
        ]

    def __str__(self):
        return f"[{self.severity.upper()}] {self.title} ({self.status})"

