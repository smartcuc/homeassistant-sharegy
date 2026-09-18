"""
core/services_audit.py

Service für revisionssichere Audit-Log-Aufzeichnungen (ISO 27001, SOC 2, EnWG-Compliance).
"""

import logging
from typing import Optional, Dict, Any
from django.utils import timezone
from core.models import AuditLog

logger = logging.getLogger("django")


def log_audit_event(
    action: str,
    resource_type: str,
    resource_id: str = "",
    resource_name: str = "",
    actor=None,
    tenant=None,
    severity: str = "info",
    changes: Optional[Dict[str, Any]] = None,
    metadata: Optional[Dict[str, Any]] = None,
    request=None,
) -> AuditLog:
    """
    Erstellt einen revisionssicheren AuditLog-Eintrag.
    """
    actor_email = ""
    ip_address = ""
    user_agent = ""

    if request:
        if not actor and hasattr(request, "user") and request.user.is_authenticated:
            actor = request.user
        
        # IP-Adresse ermitteln (inkl. Reverse-Proxy Header)
        x_forwarded_for = request.META.get("HTTP_X_FORWARDED_FOR")
        if x_forwarded_for:
            ip_address = x_forwarded_for.split(",")[0].strip()
        else:
            ip_address = request.META.get("REMOTE_ADDR", "")

        user_agent = request.META.get("HTTP_USER_AGENT", "")[:500]

    if actor and hasattr(actor, "email"):
        actor_email = actor.email

    try:
        entry = AuditLog.objects.create(
            actor=actor if (actor and getattr(actor, "is_authenticated", False)) else None,
            actor_email=actor_email,
            tenant=tenant,
            action=action,
            resource_type=resource_type,
            resource_id=str(resource_id),
            resource_name=resource_name,
            severity=severity,
            ip_address=ip_address,
            user_agent=user_agent,
            changes=changes or {},
            metadata=metadata or {},
        )
        return entry
    except Exception as e:
        logger.error(f"Fehler beim Erstellen des Audit-Logs: {e}", exc_info=True)
        return None
