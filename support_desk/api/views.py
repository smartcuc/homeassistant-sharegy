#############################
# support_desk/api/views.py
#############################

import json
from rest_framework import status, permissions
from rest_framework.decorators import api_view, permission_classes, parser_classes, authentication_classes
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser
from rest_framework.response import Response
from rest_framework.authentication import SessionAuthentication
from rest_framework_simplejwt.authentication import JWTAuthentication
from django.shortcuts import get_object_or_404
from django.db.models import Q
from django.utils import timezone

from accounts.auth import CsrfExemptSessionAuthentication
from support_desk.models import (
    SupportProjectConfig,
    Ticket,
    TicketMessage,
    TicketAttachment,
    CannedResponse,
)
from support_desk.api.serializers import (
    TicketListSerializer,
    TicketDetailSerializer,
    TicketMessageSerializer,
    TicketAttachmentSerializer,
    CannedResponseSerializer,
    SupportProjectConfigSerializer,
)
from support_desk.services.ticket_engine import (
    create_ticket,
    add_message,
    update_ticket_status,
    assign_ticket,
    search_deflection_articles,
)
from support_desk.services.auth_jwt import verify_support_jwt, SupportJWTAuthentication


def _resolve_requester(request):
    """
    Helper to extract user information either from Django Session/Token or external JWT (Factofy).
    Returns (user_or_none, external_user_id, contact_name, contact_email, project_key).
    """
    # 1. Check if Support JWT was already verified by Authentication class
    if hasattr(request.user, "support_jwt_payload") and request.user.support_jwt_payload:
        payload = request.user.support_jwt_payload
        return (
            None,
            str(payload.get("sub", "")),
            str(payload.get("name", "")),
            str(payload.get("email", "")),
            str(payload.get("project", "factofy")),
        )

    # 2. Check Authorization Bearer header directly
    auth_header = request.headers.get("Authorization", "") or request.META.get("HTTP_AUTHORIZATION", "")
    if auth_header.startswith("Bearer "):
        token = auth_header[7:].strip()
        is_valid, payload, err = verify_support_jwt(token)
        if is_valid and payload:
            return (
                None,
                str(payload.get("sub", "")),
                str(payload.get("name", "")),
                str(payload.get("email", "")),
                str(payload.get("project", "factofy")),
            )

    # 3. Check Standard Django Authenticated User (Sharegy)
    if request.user and request.user.is_authenticated:
        name = f"{request.user.first_name} {request.user.last_name}".strip() or request.user.username
        return (
            request.user,
            "",
            name,
            request.user.email or "",
            request.query_params.get("project_key") or "sharegy",
        )


    # 4. Anonymous / Guest
    return (
        None,
        "",
        request.data.get("contact_name", ""),
        request.data.get("contact_email", ""),
        request.query_params.get("project_key") or request.data.get("project_key") or "sharegy",
    )


def _is_staff_or_helpdesk(user) -> bool:
    if not user or not user.is_authenticated:
        return False
    return bool(
        user.is_staff or 
        user.is_superuser or 
        getattr(user, "is_platform_admin", False) or 
        getattr(user, "is_platform_helpdesk", False)
    )


class IsStaffOrPlatformHelpdesk(permissions.BasePermission):
    def has_permission(self, request, view):
        return _is_staff_or_helpdesk(request.user)


def _can_set_custom_priority(user, ext_id=None) -> bool:
    """
    ITIL-Priority Rules:
    - Free-EMS User: Priority is strictly locked to 'low'.
    - EMS Pro User: Allowed to choose custom priority (low, medium, high).
    - Energy Admin / Energy User Admin / Energy Helpdesk: Allowed to choose custom priority (low, medium, high, urgent).
    - Platform Roles (System Admin, Finance, Global User Admin, Platform Helpdesk): Allowed to choose custom priority.
    - External JWT (e.g. Factofy): Allowed to specify priority.
    """
    if ext_id:
        return True

    if not user or not user.is_authenticated:
        return False

    if _is_staff_or_helpdesk(user):
        return True

    # EnergySharing / Tenant Admins, User Admins, Helpdesk
    try:
        if user.memberships.filter(is_active=True, role__in=["admin", "user_admin", "helpdesk"]).exists():
            return True
    except Exception:
        pass

    # EMS Pro / Landlord Active Subscription
    try:
        if hasattr(user, "ems_subscription") and user.ems_subscription.is_pro_active:
            return True
    except Exception:
        pass

    return False



@api_view(["GET", "POST"])
@authentication_classes([SupportJWTAuthentication, CsrfExemptSessionAuthentication, SessionAuthentication, JWTAuthentication])
@permission_classes([permissions.AllowAny])
@parser_classes([JSONParser, MultiPartParser, FormParser])
def tickets_list_create(request):
    """
    GET: List user's tickets (Sharegy user or Factofy JWT user).
    POST: Create a new support ticket (Authentication required; Free-EMS locked to 'low' priority).
    """
    user, ext_id, name, email, project_key = _resolve_requester(request)

    if request.method == "GET":
        if not user and not ext_id:
            return Response({"detail": "Authentifizierung erforderlich."}, status=status.HTTP_401_UNAUTHORIZED)

        qs = Ticket.objects.all().order_by("-created_at")

        if _is_staff_or_helpdesk(user):
            if request.query_params.get("scope") != "all":
                qs = qs.filter(Q(user=user) | Q(assigned_agent=user))
        elif user:
            qs = qs.filter(user=user)
        elif ext_id:
            qs = qs.filter(project_key=project_key, external_user_id=ext_id)

        req_project = request.query_params.get("project_key")
        if req_project:
            qs = qs.filter(project_key=req_project)

        req_status = request.query_params.get("status")
        if req_status:
            qs = qs.filter(status=req_status)

        serializer = TicketListSerializer(qs, many=True)
        return Response(serializer.data)

    elif request.method == "POST":
        # 1. Anonymous users are NOT allowed to create tickets
        if not user and not ext_id:
            return Response(
                {"error": "Nur angemeldete Benutzer können Support-Tickets erstellen. Bitte logge dich ein."},
                status=status.HTTP_401_UNAUTHORIZED,
            )

        subject = request.data.get("subject", "").strip()
        category = request.data.get("category", "general")
        requested_priority = str(request.data.get("priority", "")).lower().strip()
        initial_message = request.data.get("message", request.data.get("initial_message", "")).strip()
        context_payload = request.data.get("context_payload", {})
        contact_name = request.data.get("contact_name", name)
        contact_email = request.data.get("contact_email", email)

        # 2. Enforce ITIL priority rules based on role / subscription
        if _can_set_custom_priority(user, ext_id=ext_id):
            allowed_priorities = [Ticket.PRIORITY_LOW, Ticket.PRIORITY_MEDIUM, Ticket.PRIORITY_HIGH]
            if user and (user.is_staff or user.is_superuser):
                allowed_priorities.append(Ticket.PRIORITY_URGENT)

            if requested_priority in allowed_priorities:
                priority = requested_priority
            else:
                priority = Ticket.PRIORITY_MEDIUM
        else:
            # Free-EMS user: priority is strictly forced to 'low'
            priority = Ticket.PRIORITY_LOW

        if isinstance(context_payload, str):
            try:
                context_payload = json.loads(context_payload)
            except Exception:
                context_payload = {}

        if not subject:
            return Response({"error": "Bitte gib einen Betreff an."}, status=status.HTTP_400_BAD_REQUEST)

        files = request.FILES.getlist("attachments")

        ticket = create_ticket(
            project_key=project_key,
            subject=subject,
            category=category,
            priority=priority,
            initial_message=initial_message,
            user=user,
            external_user_id=ext_id,
            contact_name=contact_name,
            contact_email=contact_email,
            context_payload=context_payload,
            attachments_files=files,
        )

        serializer = TicketDetailSerializer(ticket, context={"request": request})
        return Response(serializer.data, status=status.HTTP_201_CREATED)



@api_view(["GET", "PATCH"])
@authentication_classes([SupportJWTAuthentication, CsrfExemptSessionAuthentication, SessionAuthentication, JWTAuthentication])
@permission_classes([permissions.AllowAny])
def ticket_detail(request, ticket_id):
    """
    GET: Get full ticket details with messages and timeline.
    PATCH: Update ticket (e.g. resolve or reopen).
    """
    user, ext_id, name, email, project_key = _resolve_requester(request)
    ticket = get_object_or_404(Ticket, id=ticket_id)

    is_authorized = (
        _is_staff_or_helpdesk(user)
        or (user and ticket.user_id == user.id)
        or (ext_id and ticket.external_user_id == ext_id and ticket.project_key == project_key)
    )
    if not is_authorized:
        return Response({"detail": "Kein Zugriff auf dieses Ticket."}, status=status.HTTP_403_FORBIDDEN)

    if request.method == "GET":
        serializer = TicketDetailSerializer(ticket, context={"request": request})
        return Response(serializer.data)

    elif request.method == "PATCH":
        new_status = request.data.get("status")
        if new_status:
            ticket = update_ticket_status(
                ticket,
                new_status,
                actor_user=user,
                actor_name=name or "Kunde",
            )
        serializer = TicketDetailSerializer(ticket, context={"request": request})
        return Response(serializer.data)


@api_view(["POST"])
@authentication_classes([SupportJWTAuthentication, CsrfExemptSessionAuthentication, SessionAuthentication, JWTAuthentication])
@permission_classes([permissions.AllowAny])
@parser_classes([JSONParser, MultiPartParser, FormParser])
def ticket_add_message(request, ticket_id):
    """
    POST: Post a customer reply or agent message to an existing ticket.
    """
    user, ext_id, name, email, project_key = _resolve_requester(request)
    ticket = get_object_or_404(Ticket, id=ticket_id)

    is_staff = _is_staff_or_helpdesk(user)
    is_authorized = (
        is_staff
        or (user and ticket.user_id == user.id)
        or (ext_id and ticket.external_user_id == ext_id and ticket.project_key == project_key)
    )
    if not is_authorized:
        return Response({"detail": "Kein Zugriff auf dieses Ticket."}, status=status.HTTP_403_FORBIDDEN)

    body = request.data.get("body", request.data.get("message", "")).strip()
    is_internal_note = bool(request.data.get("is_internal_note", False) and is_staff)
    files = request.FILES.getlist("attachments")

    if not body and not files:
        return Response({"error": "Nachrichtentext oder Anhang erforderlich."}, status=status.HTTP_400_BAD_REQUEST)

    msg = add_message(
        ticket=ticket,
        body=body or "(Anhang gesendet)",
        sender=user,
        external_sender_name=name or "Kunde",
        external_sender_email=email,
        is_staff_reply=is_staff and not is_internal_note,
        is_internal_note=is_internal_note,
        attachments_files=files,
    )

    serializer = TicketMessageSerializer(msg)
    return Response(serializer.data, status=status.HTTP_201_CREATED)


@api_view(["GET"])
@permission_classes([permissions.AllowAny])
def deflection_suggest(request):
    """
    Live search suggestions from HelpCenter knowledge base before ticket creation.
    """
    query = request.query_params.get("q", "").strip()
    suggestions = search_deflection_articles(query, limit=4)
    return Response({"query": query, "suggestions": suggestions})


@api_view(["GET", "PATCH", "POST"])
@authentication_classes([SupportJWTAuthentication, CsrfExemptSessionAuthentication, SessionAuthentication, JWTAuthentication])
@permission_classes([IsStaffOrPlatformHelpdesk])
def agent_ticket_management(request, ticket_id=None):
    """
    Agent Support Hub management endpoints (staff & platform helpdesk):
    GET: List / filter all tickets across projects (sharegy & factofy) with KPI summary.
    PATCH <id>: Reassign agent or change status / priority.
    POST <id>/note: Add internal note.
    """
    if ticket_id:
        ticket = get_object_or_404(Ticket, id=ticket_id)
        if request.method == "PATCH":
            new_status = request.data.get("status")
            new_priority = request.data.get("priority")
            assigned_agent_id = request.data.get("assigned_agent_id")

            if new_status:
                update_ticket_status(ticket, new_status, actor_user=request.user, actor_name=request.user.username)
            if new_priority:
                ticket.priority = new_priority
                ticket.save(update_fields=["priority", "updated_at"])
            if assigned_agent_id is not None:
                from django.contrib.auth import get_user_model
                agent = get_user_model().objects.filter(id=assigned_agent_id).first() if assigned_agent_id else None
                assign_ticket(ticket, agent, actor_user=request.user)

            serializer = TicketDetailSerializer(ticket, context={"request": request})
            return Response(serializer.data)

        elif request.method == "POST":
            # Add Internal Note
            body = request.data.get("body", "").strip()
            if not body:
                return Response({"error": "Notiztext erforderlich."}, status=status.HTTP_400_BAD_REQUEST)
            msg = add_message(
                ticket=ticket,
                body=body,
                sender=request.user,
                is_staff_reply=False,
                is_internal_note=True,
            )
            return Response(TicketMessageSerializer(msg).data, status=status.HTTP_201_CREATED)

    # List all tickets for Support Hub
    qs = Ticket.objects.all().order_by("-created_at")

    project_key = request.query_params.get("project_key")
    if project_key and project_key != "all":
        qs = qs.filter(project_key=project_key)

    req_status = request.query_params.get("status")
    if req_status and req_status != "all":
        qs = qs.filter(status=req_status)

    req_priority = request.query_params.get("priority")
    if req_priority and req_priority != "all":
        qs = qs.filter(priority=req_priority)

    search_q = request.query_params.get("search", "").strip()
    if search_q:
        qs = qs.filter(
            Q(ticket_number__icontains=search_q)
            | Q(subject__icontains=search_q)
            | Q(contact_name__icontains=search_q)
            | Q(contact_email__icontains=search_q)
            | Q(messages__body__icontains=search_q)
        ).distinct()

    # KPI Summary
    kpis = {
        "total": Ticket.objects.count(),
        "open": Ticket.objects.filter(status=Ticket.STATUS_OPEN).count(),
        "in_progress": Ticket.objects.filter(status=Ticket.STATUS_IN_PROGRESS).count(),
        "waiting_customer": Ticket.objects.filter(status=Ticket.STATUS_WAITING_CUSTOMER).count(),
        "resolved": Ticket.objects.filter(status=Ticket.STATUS_RESOLVED).count(),
        "sharegy_count": Ticket.objects.filter(project_key="sharegy").count(),
        "factofy_count": Ticket.objects.filter(project_key="factofy").count(),
    }

    serializer = TicketListSerializer(qs, many=True)
    return Response({"kpis": kpis, "tickets": serializer.data})


@api_view(["GET", "POST"])
@authentication_classes([SupportJWTAuthentication, CsrfExemptSessionAuthentication, SessionAuthentication, JWTAuthentication])
@permission_classes([IsStaffOrPlatformHelpdesk])
def canned_responses_list(request):
    """
    List or create quick response templates for agents.
    """
    if request.method == "GET":
        project_key = request.query_params.get("project_key")
        qs = CannedResponse.objects.all()
        if project_key:
            qs = qs.filter(Q(project_key=project_key) | Q(project_key="global"))
        serializer = CannedResponseSerializer(qs, many=True)
        return Response(serializer.data)

    elif request.method == "POST":
        serializer = CannedResponseSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

