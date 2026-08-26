####################
# tracking/models.py
####################

import uuid
from django.db import models
from django.conf import settings


class EventLog(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    # WHAT
    name = models.CharField(max_length=255, db_index=True)

    # WHO
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="events",
        db_index=True,
    )

    anonymous_id = models.CharField(max_length=255, null=True, blank=True, db_index=True)

    # CONTEXT (CRITICAL)
    tenant = models.ForeignKey(
        "core.Tenant",
        null=True,
        blank=True,
        on_delete=models.CASCADE,
        db_index=True,
    )

    context = models.CharField(
        max_length=50,
        choices=[
            ("global", "Global"),
            ("tenant", "Tenant"),
        ],
        db_index=True,
    )

    # SESSION
    session_id = models.CharField(max_length=255, null=True, blank=True, db_index=True)

    # ATTRIBUTION
    source = models.CharField(max_length=100, null=True, blank=True)
    campaign = models.CharField(max_length=100, null=True, blank=True)

    # EXTRA
    metadata = models.JSONField(default=dict, blank=True)

    ip = models.GenericIPAddressField(null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True, db_index=True)

    class Meta:
        indexes = [
            models.Index(fields=["context", "tenant", "name", "created_at"]),
            models.Index(fields=["user", "created_at"]),
        ]

    def __str__(self):
        return f"{self.name} ({self.context})"
    