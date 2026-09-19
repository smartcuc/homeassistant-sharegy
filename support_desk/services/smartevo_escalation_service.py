import hashlib
import json
import logging
from typing import Any, Dict, Optional
import requests
from django.conf import settings
from support_desk.models import Ticket

logger = logging.getLogger(__name__)


class SmartEvoEscalationService:
    """
    Eskaliert 1st-Level Support-Tickets aus Sharegy an das zentrale
    smartEvo Platform Operations & Monitoring System (moniy).
    """

    def __init__(self, moniy_base_url: Optional[str] = None, s2s_api_key: Optional[str] = None):
        self.moniy_base_url = (
            moniy_base_url
            or getattr(settings, "MONIY_BASE_URL", "http://127.0.0.1:8001")
        ).rstrip("/")
        self.s2s_api_key = s2s_api_key or getattr(settings, "MONIY_S2S_KEY", "nexus-s2s-master-key-2026")

    def package_telemetry_snapshot(self, ticket: Ticket) -> Dict[str, Any]:
        """
        Sammelt nicht-personenbezogene, rein technische Diagnosedaten für smartEvo Ingenieure.
        """
        snapshot = {
            "platform_version": "v5.4",
            "sharegy_env": "production" if not getattr(settings, "DEBUG", True) else "development",
        }

        # Falls dem Ticket ein Benutzer/Geräte zugeordnet sind
        if ticket.user:
            try:
                devices = ticket.user.devices.all()[:5]
                device_list = []
                for d in devices:
                    dev_info = {
                        "device_id": str(d.id),
                        "device_type": getattr(d, "device_type", "unknown"),
                        "manufacturer": getattr(d, "manufacturer", "unknown"),
                        "model": getattr(d, "model", "unknown"),
                        "is_active": getattr(d, "is_active", True),
                    }
                    device_list.append(dev_info)
                snapshot["devices"] = device_list
                if device_list:
                    snapshot["primary_device_model"] = device_list[0]["model"]
                    snapshot["primary_manufacturer"] = device_list[0]["manufacturer"]
            except Exception as e:
                snapshot["device_query_error"] = str(e)

        # Context-Daten aus Ticket-Metadaten übernehmen
        if ticket.metadata:
            snapshot["ticket_context"] = ticket.metadata

        return snapshot

    def escalate_ticket_to_smartevo(
        self,
        ticket: Ticket,
        reason: str,
        escalating_admin_user: Optional[Any] = None,
    ) -> Dict[str, Any]:
        """
        Sendet das Ticket als 2nd/3rd-Level Eskalation an smartEvo (moniy).
        """
        url = f"{self.moniy_base_url}/api/v1/helpdesk/escalations"
        headers = {
            "Content-Type": "application/json",
            "X-Nexus-S2S-Key": self.s2s_api_key,
        }

        # Anonymisierter User-Hash (DSGVO)
        user_hash = None
        if ticket.contact_email:
            user_hash = hashlib.sha256(ticket.contact_email.strip().lower().encode("utf-8")).hexdigest()[:16]

        payload = {
            "source_platform": "sharegy",
            "external_ticket_id": ticket.ticket_number,
            "customer_tier": "Partner" if (ticket.tenant and getattr(ticket.tenant, "is_partner", False)) else "Prosumer",
            "category": getattr(ticket, "category", "hardware_inverter") or "hardware_inverter",
            "priority": ticket.priority if ticket.priority in ["low", "medium", "high", "critical"] else "high",
            "subject": ticket.subject,
            "description": f"Grund für Eskalation: {reason}\n\nUrsprüngliche Beschreibung:\n{ticket.description}",
            "user_email_hash": user_hash,
            "telemetry_snapshot": self.package_telemetry_snapshot(ticket),
            "callback_url": f"{getattr(settings, 'SHAREGY_PUBLIC_URL', 'https://app.sharegy.de')}/api/v1/support/webhook/smartevo-sync/",
        }

        try:
            resp = requests.post(url, json=payload, headers=headers, timeout=5)
            if resp.status_code in [200, 201]:
                res_data = resp.json()
                smartevo_tkt_id = res_data.get("id")

                # Local ticket status & metadata update
                ticket.status = Ticket.STATUS_WAITING_INTERNAL
                meta = ticket.metadata or {}
                meta["smartevo_escalated"] = True
                meta["smartevo_ticket_id"] = smartevo_tkt_id
                meta["escalation_reason"] = reason
                if escalating_admin_user:
                    meta["escalated_by"] = str(escalating_admin_user)
                ticket.metadata = meta
                ticket.save(update_fields=["status", "metadata", "updated_at"])

                logger.info(f"Successfully escalated ticket {ticket.ticket_number} to smartEvo as {smartevo_tkt_id}")
                return {
                    "success": True,
                    "smartevo_ticket_id": smartevo_tkt_id,
                    "status": "escalated",
                }
            else:
                logger.error(f"Failed to escalate ticket {ticket.ticket_number} to smartEvo: {resp.status_code} - {resp.text}")
                return {
                    "success": False,
                    "error": f"HTTP {resp.status_code}: {resp.text}",
                }
        except Exception as e:
            logger.error(f"Connection error escalating ticket {ticket.ticket_number} to smartEvo ({url}): {e}")
            return {
                "success": False,
                "error": str(e),
            }


smartevo_escalation_service = SmartEvoEscalationService()
