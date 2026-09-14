#######################################
# support_desk/services/ticket_engine.py
#######################################

import datetime
from django.utils import timezone
from django.db import transaction
from django.db.models import Q, Count
from django.core.exceptions import ValidationError

from support_desk.models import (
    SupportProjectConfig,
    Ticket,
    TicketMessage,
    TicketAttachment,
    TicketActivityLog,
    CannedResponse,
)


def generate_ticket_number(project_key: str = "sharegy") -> str:
    """
    Generates a unique, human-readable ticket number (e.g. SHAR-2026-0001, FACT-2026-0042).
    """
    config = SupportProjectConfig.objects.filter(project_key=project_key).first()
    prefix = config.ticket_prefix if config and config.ticket_prefix else project_key[:4].upper()
    year = timezone.now().strftime("%Y")

    with transaction.atomic():
        # Count tickets created this year with this project prefix
        like_pattern = f"{prefix}-{year}-%"
        count_this_year = Ticket.objects.filter(ticket_number__startswith=f"{prefix}-{year}-").count()
        next_seq = count_this_year + 1
        candidate = f"{prefix}-{year}-{next_seq:04d}"

        # Collision avoidance
        while Ticket.objects.filter(ticket_number=candidate).exists():
            next_seq += 1
            candidate = f"{prefix}-{year}-{next_seq:04d}"

        return candidate


def create_ticket(
    project_key: str = "sharegy",
    subject: str = "",
    category: str = "general",
    priority: str = Ticket.PRIORITY_MEDIUM,
    initial_message: str = "",
    user = None,
    tenant = None,
    external_user_id: str = "",
    contact_name: str = "",
    contact_email: str = "",
    context_payload: dict = None,
    attachments_files: list = None,
) -> Ticket:
    """
    Creates a new support ticket and logs the initial customer message and activity.
    """
    if not subject:
        raise ValidationError("Ein Betreff ist erforderlich.")

    ticket_num = generate_ticket_number(project_key)

    if user and user.is_authenticated:
        if not contact_email and user.email:
            contact_email = user.email
        if not contact_name:
            contact_name = f"{user.first_name} {user.last_name}".strip() or user.username
        if not tenant and hasattr(user, "memberships"):
            active_m = user.memberships.filter(is_active=True).select_related("tenant").first()
            if active_m:
                tenant = active_m.tenant

    with transaction.atomic():
        ticket = Ticket.objects.create(
            ticket_number=ticket_num,
            project_key=project_key,
            user=user if user and user.is_authenticated else None,
            tenant=tenant,
            external_user_id=str(external_user_id or ""),
            contact_name=contact_name,
            contact_email=contact_email,
            subject=subject.strip(),
            category=category or "general",
            priority=priority or Ticket.PRIORITY_MEDIUM,
            status=Ticket.STATUS_OPEN,
            context_payload=context_payload or {},
        )

        # Log Ticket Creation Activity
        TicketActivityLog.objects.create(
            ticket=ticket,
            user=user if user and user.is_authenticated else None,
            actor_name=contact_name or "Kunde",
            action="ticket_created",
            details={
                "subject": subject,
                "category": category,
                "priority": priority,
                "project": project_key,
            },
        )

        # Create Initial Message if provided
        msg = None
        if initial_message and initial_message.strip():
            msg = TicketMessage.objects.create(
                ticket=ticket,
                sender=user if user and user.is_authenticated else None,
                external_sender_name=contact_name,
                external_sender_email=contact_email,
                is_staff_reply=False,
                is_internal_note=False,
                body=initial_message.strip(),
            )

        # Process any uploaded file attachments
        if attachments_files:
            for uploaded_f in attachments_files:
                TicketAttachment.objects.create(
                    ticket=ticket,
                    message=msg,
                    file=uploaded_f,
                    filename=getattr(uploaded_f, "name", "attachment"),
                    file_size=getattr(uploaded_f, "size", 0),
                    mime_type=getattr(uploaded_f, "content_type", "application/octet-stream"),
                    uploaded_by=user if user and user.is_authenticated else None,
                )

        return ticket


def add_message(
    ticket: Ticket,
    body: str,
    sender = None,
    external_sender_name: str = "",
    external_sender_email: str = "",
    is_staff_reply: bool = False,
    is_internal_note: bool = False,
    attachments_files: list = None,
) -> TicketMessage:
    """
    Adds a new message or staff internal note to an existing ticket.
    Automatically advances status (e.g. from open to waiting_customer if staff replies).
    """
    if not body or not body.strip():
        raise ValidationError("Nachricht darf nicht leer sein.")

    with transaction.atomic():
        msg = TicketMessage.objects.create(
            ticket=ticket,
            sender=sender if sender and sender.is_authenticated else None,
            external_sender_name=external_sender_name,
            external_sender_email=external_sender_email,
            is_staff_reply=is_staff_reply,
            is_internal_note=is_internal_note,
            body=body.strip(),
        )

        # Attachments
        if attachments_files:
            for uploaded_f in attachments_files:
                TicketAttachment.objects.create(
                    ticket=ticket,
                    message=msg,
                    file=uploaded_f,
                    filename=getattr(uploaded_f, "name", "attachment"),
                    file_size=getattr(uploaded_f, "size", 0),
                    mime_type=getattr(uploaded_f, "content_type", "application/octet-stream"),
                    uploaded_by=sender if sender and sender.is_authenticated else None,
                )

        # Update Ticket State
        if is_staff_reply and not is_internal_note:
            if not ticket.first_responded_at:
                ticket.first_responded_at = timezone.now()
            if ticket.status in [Ticket.STATUS_OPEN, Ticket.STATUS_IN_PROGRESS]:
                ticket.status = Ticket.STATUS_WAITING_CUSTOMER
            ticket.save(update_fields=["first_responded_at", "status", "updated_at"])
        elif not is_staff_reply and not is_internal_note:
            if ticket.status in [Ticket.STATUS_WAITING_CUSTOMER, Ticket.STATUS_RESOLVED]:
                ticket.status = Ticket.STATUS_IN_PROGRESS
            ticket.save(update_fields=["status", "updated_at"])
        else:
            ticket.save(update_fields=["updated_at"])

        actor = (
            f"{sender.first_name} {sender.last_name}".strip() or sender.username
            if sender and sender.is_authenticated
            else (external_sender_name or "System")
        )

        TicketActivityLog.objects.create(
            ticket=ticket,
            user=sender if sender and sender.is_authenticated else None,
            actor_name=actor,
            action="note_added" if is_internal_note else "message_sent",
            details={
                "message_id": str(msg.id),
                "is_staff": is_staff_reply,
                "is_internal": is_internal_note,
            },
        )

        return msg


def update_ticket_status(ticket: Ticket, new_status: str, actor_user = None, actor_name: str = "Agent") -> Ticket:
    """
    Transitions the ticket to a new status.
    """
    valid_statuses = [choice[0] for choice in Ticket.STATUS_CHOICES]
    if new_status not in valid_statuses:
        raise ValidationError(f"Ungültiger Status '{new_status}'.")

    old_status = ticket.status
    if old_status == new_status:
        return ticket

    ticket.status = new_status
    now = timezone.now()

    if new_status == Ticket.STATUS_RESOLVED and not ticket.resolved_at:
        ticket.resolved_at = now
    elif new_status == Ticket.STATUS_CLOSED:
        if not ticket.resolved_at:
            ticket.resolved_at = now
        ticket.closed_at = now
    elif new_status in [Ticket.STATUS_OPEN, Ticket.STATUS_IN_PROGRESS]:
        ticket.resolved_at = None
        ticket.closed_at = None

    ticket.save()

    TicketActivityLog.objects.create(
        ticket=ticket,
        user=actor_user if actor_user and actor_user.is_authenticated else None,
        actor_name=actor_name,
        action="status_changed",
        details={"old_status": old_status, "new_status": new_status},
    )
    return ticket


def assign_ticket(ticket: Ticket, agent_user, actor_user = None) -> Ticket:
    """
    Assigns a support agent to the ticket.
    """
    old_agent = ticket.assigned_agent
    ticket.assigned_agent = agent_user
    if ticket.status == Ticket.STATUS_OPEN:
        ticket.status = Ticket.STATUS_IN_PROGRESS
    ticket.save()

    TicketActivityLog.objects.create(
        ticket=ticket,
        user=actor_user if actor_user and actor_user.is_authenticated else None,
        actor_name=actor_user.username if actor_user else "System",
        action="agent_assigned",
        details={
            "old_agent": old_agent.username if old_agent else None,
            "new_agent": agent_user.username if agent_user else None,
        },
    )
    return ticket


from support_desk.services.knowledge_engine import search_deflection_articles


