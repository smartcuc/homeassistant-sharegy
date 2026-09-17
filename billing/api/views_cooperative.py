#####################################
# billing/api/views_cooperative.py
#####################################

from decimal import Decimal
from django.utils import timezone
from django.db import transaction
from django.db.models import Max
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response

from accounts.models import User, TenantMembership
from core.models import Tenant, Meter
from billing.models import CooperativeApplication, CommunityMemberShare


@api_view(["GET"])
@permission_classes([AllowAny])
def cooperative_public_info_view(request, slug):
    """
    Liefert die öffentlichen Stammdaten, Satzungsinformationen und Anteilspreise
    einer Energiegenossenschaft für die digitale Beitritts-Seite (/join/:slug).
    """
    tenant = Tenant.objects.filter(slug=slug).first()
    if not tenant:
        return Response({"error": "Energiegemeinschaft nicht gefunden."}, status=404)

    return Response({
        "id": str(tenant.id),
        "name": tenant.name,
        "slug": tenant.slug,
        "model_type": tenant.model_type,
        "legal_form": tenant.legal_form,
        "company_legal_name": tenant.company_legal_name or tenant.name,
        "support_email": tenant.support_email,
        "primary_color": tenant.primary_color,
        "logo_url": tenant.logo_url,
        "statute_url": tenant.statute_url,
        "statute_version": tenant.statute_version,
        "statute_text": tenant.statute_text,
        "share_nominal_value_eur": float(tenant.share_nominal_value_eur),
        "min_shares_count": tenant.min_shares_count,
        "max_shares_count": tenant.max_shares_count,
        "is_public": tenant.is_public,
    })


@api_view(["POST"])
@permission_classes([AllowAny])
def cooperative_submit_application_view(request, slug):
    """
    Nimmt einen rechtsverbindlichen digitalen Beitrittsantrag mit dokumentierter
    Satzungs-Zustimmung gem. § 15b GenG entgegen.
    """
    tenant = Tenant.objects.filter(slug=slug).first()
    if not tenant:
        return Response({"error": "Energiegemeinschaft nicht gefunden."}, status=404)

    data = request.data
    first_name = (data.get("first_name") or "").strip()
    last_name = (data.get("last_name") or "").strip()
    email = (data.get("email") or "").strip().lower()
    street = (data.get("street") or "").strip()
    postal_code = (data.get("postal_code") or "").strip()
    city = (data.get("city") or "").strip()
    phone = (data.get("phone") or "").strip()
    birth_date = data.get("birth_date") or None
    meter_malo_id = (data.get("meter_malo_id") or "").strip()
    participant_role = data.get("participant_role") or "consumer"

    shares_count = int(data.get("shares_count", tenant.min_shares_count or 1))
    statute_accepted = bool(data.get("statute_accepted"))

    if not first_name or not last_name or not email or not street or not postal_code or not city:
        return Response({"error": "Bitte alle erforderlichen Pflichtfelder ausfüllen."}, status=400)

    if not statute_accepted:
        return Response({"error": "Der Beitritt erfordert die rechtsverbindliche Anerkennung der Genossenschaftssatzung."}, status=400)

    if shares_count < (tenant.min_shares_count or 1):
        return Response({"error": f"Mindestanzahl an Geschäftsanteilen ist {tenant.min_shares_count}."}, status=400)

    # Client IP für rechtssichere Beweiskette (Audit-Log)
    x_forwarded_for = request.META.get("HTTP_X_FORWARDED_FOR")
    if x_forwarded_for:
        ip_address = x_forwarded_for.split(",")[0].strip()
    else:
        ip_address = request.META.get("REMOTE_ADDR")

    share_nominal = tenant.share_nominal_value_eur or Decimal("100.00")
    total_amount = Decimal(shares_count) * share_nominal

    # Verknüpfe ggf. mit bestehendem User-Account
    existing_user = User.objects.filter(email=email).first()
    if not existing_user and request.user.is_authenticated:
        existing_user = request.user

    application = CooperativeApplication.objects.create(
        tenant=tenant,
        user=existing_user,
        first_name=first_name,
        last_name=last_name,
        email=email,
        phone=phone,
        birth_date=birth_date if birth_date else None,
        street=street,
        postal_code=postal_code,
        city=city,
        meter_malo_id=meter_malo_id,
        participant_role=participant_role,
        shares_count=shares_count,
        share_nominal_value_eur=share_nominal,
        total_amount_eur=total_amount,
        statute_accepted=True,
        statute_version_accepted=tenant.statute_version or "1.0",
        statute_accepted_at=timezone.now(),
        statute_ip_address=ip_address,
        status=CooperativeApplication.STATUS_PENDING,
    )

    return Response({
        "message": "Beitrittsantrag erfolgreich eingereicht. Der Vorstand wird diesen prüfen.",
        "application_id": str(application.id),
        "status": application.status,
        "shares_count": application.shares_count,
        "total_amount_eur": float(application.total_amount_eur),
        "statute_version": application.statute_version_accepted,
    }, status=201)


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def cooperative_admin_applications_view(request):
    """
    Liefert alle eingereichten Beitrittsanträge für Administratoren und Vorstandsmitglieder
    zur Prüfung im digitalen Mitgliederverzeichnis (§ 30 GenG).
    """
    user = request.user
    tenant_id = request.headers.get("X-Tenant-ID") or request.GET.get("tenant_id")

    if tenant_id:
        membership = TenantMembership.objects.filter(user=user, tenant_id=tenant_id, is_active=True).first()
        is_admin = user.is_staff or user.is_superuser or (membership and membership.role in ["admin", "owner", "user_admin"])
        if not is_admin:
            return Response({"error": "Forbidden: Keine Vorstands- oder Administrator-Berechtigung."}, status=403)
        tenant = Tenant.objects.filter(id=tenant_id).first()
        qs = CooperativeApplication.objects.filter(tenant=tenant)
    else:
        if user.is_staff or user.is_superuser:
            qs = CooperativeApplication.objects.all()
        else:
            tenant_ids = TenantMembership.objects.filter(
                user=user, role__in=["admin", "owner", "user_admin"], is_active=True
            ).values_list("tenant_id", flat=True)
            qs = CooperativeApplication.objects.filter(tenant_id__in=tenant_ids)

    status_filter = request.GET.get("status")
    if status_filter:
        qs = qs.filter(status=status_filter)

    results = []
    for app in qs.select_related("tenant", "user", "board_approved_by")[:100]:
        results.append({
            "id": str(app.id),
            "tenant_id": str(app.tenant.id),
            "tenant_name": app.tenant.name,
            "first_name": app.first_name,
            "last_name": app.last_name,
            "full_name": f"{app.first_name} {app.last_name}",
            "email": app.email,
            "phone": app.phone,
            "street": app.street,
            "postal_code": app.postal_code,
            "city": app.city,
            "birth_date": app.birth_date.isoformat() if app.birth_date else None,
            "meter_malo_id": app.meter_malo_id,
            "participant_role": app.participant_role,
            "shares_count": app.shares_count,
            "share_nominal_value_eur": float(app.share_nominal_value_eur),
            "total_amount_eur": float(app.total_amount_eur),
            "statute_version_accepted": app.statute_version_accepted,
            "statute_accepted_at": app.statute_accepted_at.isoformat() if app.statute_accepted_at else None,
            "statute_ip_address": app.statute_ip_address,
            "status": app.status,
            "member_number": app.member_number,
            "board_approved_by": app.board_approved_by.email if app.board_approved_by else None,
            "board_approved_at": app.board_approved_at.isoformat() if app.board_approved_at else None,
            "board_notes": app.board_notes,
            "created_at": app.created_at.isoformat(),
        })

    return Response({
        "applications": results,
        "count": len(results),
    })


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def cooperative_admin_approve_application_view(request, application_id):
    """
    Formaler Vorstandsbeschluss gem. § 30 GenG:
    - Genehmigt den Beitrittsantrag
    - Vergibt die nächste fortlaufende Mitgliedsnummer
    - Erzeugt die TenantMembership
    - Erstellt den Zähler (falls MaLo angegeben)
    - Trägt die gezeichneten Geschäftsanteile ein
    """
    user = request.user
    application = CooperativeApplication.objects.filter(id=application_id).select_related("tenant").first()
    if not application:
        return Response({"error": "Beitrittsantrag nicht gefunden."}, status=404)

    tenant = application.tenant
    membership = TenantMembership.objects.filter(user=user, tenant=tenant, is_active=True).first()
    is_admin = user.is_staff or user.is_superuser or (membership and membership.role in ["admin", "owner", "user_admin"])
    if not is_admin:
        return Response({"error": "Forbidden: Nur Vorstände dürfen Beitrittsanträge genehmigen."}, status=403)

    if application.status == CooperativeApplication.STATUS_APPROVED:
        return Response({"error": "Antrag wurde bereits genehmigt."}, status=400)

    with transaction.atomic():
        # 1. Fortlaufende Mitgliedsnummer ermitteln
        current_year = timezone.now().year
        count_approved = CooperativeApplication.objects.filter(
            tenant=tenant, status=CooperativeApplication.STATUS_APPROVED
        ).count()
        next_number = count_approved + 1
        member_number = f"GEN-{current_year}-{next_number:04d}"

        # 2. User-Account sicherstellen
        app_user = application.user
        if not app_user:
            app_user = User.objects.filter(email=application.email).first()
            if not app_user:
                app_user = User.objects.create(
                    email=application.email,
                    username=application.email,
                    is_active=True,
                )
                app_user.set_unusable_password()
                app_user.save()

        # 3. TenantMembership anlegen
        tenant_membership, _ = TenantMembership.objects.get_or_create(
            user=app_user,
            tenant=tenant,
            defaults={"role": TenantMembership.ROLE_MEMBER, "is_active": True},
        )

        # 4. Zähler anlegen, falls MaLo angegeben
        if application.meter_malo_id:
            Meter.objects.get_or_create(
                tenant=tenant,
                serial_number=application.meter_malo_id,
                defaults={
                    "owner_user": app_user,
                    "owner_membership": tenant_membership,
                    "source": "imsys",
                }
            )

        # 5. Geschäftsanteile zuweisen
        CommunityMemberShare.objects.get_or_create(
            tenant=tenant,
            membership=tenant_membership,
            user=app_user,
            defaults={
                "share_percent": Decimal("0.0"),
                "assigned_kwp": Decimal("1.0"),
                "is_active": True,
            }
        )

        # 6. Status aktualisieren
        application.status = CooperativeApplication.STATUS_APPROVED
        application.member_number = member_number
        application.board_approved_by = user
        application.board_approved_at = timezone.now()
        application.board_notes = request.data.get("notes", "Durch Vorstandsbeschluss genehmigt.")
        application.user = app_user
        application.save()

    return Response({
        "message": f"Beitrittsantrag erfolgreich genehmigt. Mitgliedsnummer {member_number} vergeben.",
        "member_number": member_number,
        "status": application.status,
    })


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def cooperative_admin_reject_application_view(request, application_id):
    """
    Ablehnung eines Beitrittsantrags durch den Vorstand.
    """
    user = request.user
    application = CooperativeApplication.objects.filter(id=application_id).select_related("tenant").first()
    if not application:
        return Response({"error": "Beitrittsantrag nicht gefunden."}, status=404)

    tenant = application.tenant
    membership = TenantMembership.objects.filter(user=user, tenant=tenant, is_active=True).first()
    is_admin = user.is_staff or user.is_superuser or (membership and membership.role in ["admin", "owner", "user_admin"])
    if not is_admin:
        return Response({"error": "Forbidden: Nur Vorstände dürfen Anträge bearbeiten."}, status=403)

    application.status = CooperativeApplication.STATUS_REJECTED
    application.board_approved_by = user
    application.board_approved_at = timezone.now()
    application.board_notes = request.data.get("notes", "Antrag vom Vorstand abgelehnt.")
    application.save()

    return Response({
        "message": "Beitrittsantrag abgelehnt.",
        "status": application.status,
    })
