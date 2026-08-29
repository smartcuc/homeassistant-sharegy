#######################
# accounts/api/views.py
#######################

import logging
from django.conf import settings
from django.shortcuts import get_object_or_404
from django.contrib.auth import get_user_model, login, logout

logger = logging.getLogger(__name__)

from zoneinfo import available_timezones

from django.utils import timezone
from datetime import timedelta
from django.shortcuts import redirect
from django.http import HttpResponse

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated

from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator

from core.models import Tenant
from accounts.serializers import UserMeSerializer
from accounts.models import (
    UserSettings,
    UserProfile,
    TenantInvite,
    TenantMembership,
    AuditLog,
)


from accounts.services.email_service import send_magic_link_email
from django.db.models import Count, Q

from django.contrib.auth import login
from django.views import View
from accounts.models import User


User = get_user_model()


# ---------------- USER SETTINGS ---------------- #

@method_decorator(csrf_exempt, name='dispatch')
class UserSettingsView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        settings_obj, _ = UserSettings.objects.get_or_create(user=request.user)

        return Response(
            {
                "onboarding_step": settings_obj.onboarding_step,
                "usage_mode": settings_obj.usage_mode,
                "language": settings_obj.language,
                "timezone": settings_obj.timezone,
            }
        )


class UpdateOnboardingStepView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        step = request.data.get("onboarding_step")

        # ✅ Sicherheit: Wert MUSS vorhanden und gültig sein
        if step not in ["welcome", "setup", "done"]:
            return Response(
                {"error": "invalid onboarding_step"},
                status=400,
            )

        # ✅ Settings holen oder erzeugen
        settings_obj, _ = UserSettings.objects.get_or_create(user=request.user)

        # ✅ Step setzen
        settings_obj.onboarding_step = step
        settings_obj.save()

        return Response({"status": "ok"})


class UserProfileView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        user = request.user
        data = request.data

        user.first_name = data.get("first_name", "")
        user.last_name = data.get("last_name", "")
        user.save()

        profile, _ = UserProfile.objects.get_or_create(user=user)

        profile.street = data.get("street", "")
        profile.city = data.get("city", "")
        profile.postal_code = data.get("postal_code", "")
        profile.house_number = data.get("house_number", "")
        profile.country = data.get("country", "DE")
        profile.save()

        return Response({"status": "saved"})


class UserUsageModeView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        mode = request.data.get("usage_mode")

        if mode not in ["standalone", "tenant", "hybrid"]:
            return Response({"error": "invalid usage_mode"}, status=400)

        settings_obj, _ = UserSettings.objects.get_or_create(user=request.user)
        settings_obj.usage_mode = mode
        settings_obj.save()

        return Response({"status": "saved"})


class UserLanguageView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        lang = request.data.get("language")

        if lang not in ["de", "en", "pl"]:
            return Response({"error": "invalid language"}, status=400)

        settings_obj, _ = UserSettings.objects.get_or_create(user=request.user)
        settings_obj.language = lang
        settings_obj.save()

        return Response({"status": "saved", "language": lang})


class UserTimezoneView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):

        timezone_value = request.data.get("timezone")

        if not timezone_value:
            return Response(
                {"error": "timezone required"},
                status=400,
            )

        if timezone_value not in available_timezones():
            return Response(
                {"error": "invalid timezone"},
                status=400,
            )

        settings_obj, _ = UserSettings.objects.get_or_create(user=request.user)

        settings_obj.timezone = timezone_value
        settings_obj.save()

        return Response(
            {
                "status": "saved",
                "timezone": timezone_value,
            }
        )


class TimezoneListView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):

        return Response(sorted(list(available_timezones())))


# ---------------- TENANT / INVITES ---------------- #

class UseInviteView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        token = request.data.get("token")

        invite = get_object_or_404(
            TenantInvite,
            token=token,
            is_active=True
        )

        if invite.used_count >= invite.max_uses:
            return Response({"error": "invite used"}, status=400)

        membership, created = TenantMembership.objects.get_or_create(
            user=request.user,
            tenant=invite.tenant,
            defaults={"role": invite.role}
        )

        invite.used_count += 1
        invite.save()

        return Response({
            "status": "joined",
            "tenant": invite.tenant.name,
            "role": membership.role
        })


from accounts.permissions import can_manage_invites, can_manage_members, ROLE_PERMISSIONS


class CreateInviteView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        tenant_id = request.data.get("tenant_id")
        role = request.data.get("role", TenantMembership.ROLE_MEMBER)

        tenant = get_object_or_404(Tenant, id=tenant_id)

        valid_roles = [c[0] for c in TenantMembership.ROLE_CHOICES]
        if role not in valid_roles:
            return Response({"error": "invalid role"}, status=400)

        # Check permission (Admin or User Admin)
        if not can_manage_invites(request.user, tenant):
            return Response({"error": "not allowed"}, status=403)

        # User-Admin cannot invite new Admins
        user_membership = TenantMembership.objects.filter(
            user=request.user,
            tenant=tenant,
            is_active=True
        ).first()

        is_tenant_admin = user_membership and user_membership.role == TenantMembership.ROLE_ADMIN
        is_global_admin = getattr(request.user, "is_platform_admin", False) or request.user.is_superuser

        if role in [TenantMembership.ROLE_ADMIN, TenantMembership.ROLE_USER_ADMIN] and not (is_tenant_admin or is_global_admin):
            return Response({"error": "Only Energy Admins can invite administrative roles."}, status=403)

        invite = TenantInvite.objects.create(
            tenant=tenant,
            role=role,
            max_uses=10
        )

        AuditLog.objects.create(
            user=request.user,
            tenant=tenant,
            action="invite_created",
            metadata={"role": invite.role, "token": str(invite.token)},
        )

        return Response({
            "link": f"{settings.FRONTEND_URL}/join?token={invite.token}",
            "token": str(invite.token),
            "role": invite.role,
            "role_display": invite.get_role_display(),
        })


class MyTenantView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        membership = request.user.memberships.filter(is_active=True).first()

        if not membership:
            return Response({"tenant": None})

        tenant = membership.tenant

        members = TenantMembership.objects.filter(
            tenant=tenant,
            is_active=True
        ).select_related("user")

        invites = TenantInvite.objects.filter(tenant=tenant)

        return Response({
            "tenant": {
                "id": str(tenant.id),
                "name": tenant.name
            },
            "members": [
                {
                    "id": str(m.user.id),
                    "email": m.user.email,
                    "role": m.role,
                    "role_display": m.get_role_display(),
                    "permissions": ROLE_PERMISSIONS.get(m.role, []),
                }
                for m in members
            ],
            "invites": [
                {
                    "token": str(i.token),
                    "role": i.role,
                    "role_display": i.get_role_display(),
                    "used": i.used_count
                }
                for i in invites
            ]
        })


class UpdateMemberRoleView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        tenant_id = request.data.get("tenant_id")
        user_id = request.data.get("user_id")
        new_role = request.data.get("role")

        valid_roles = [c[0] for c in TenantMembership.ROLE_CHOICES]
        if new_role not in valid_roles:
            return Response({"error": "invalid role"}, status=400)

        tenant = get_object_or_404(Tenant, id=tenant_id)

        if not can_manage_members(request.user, tenant):
            return Response({"error": "not allowed"}, status=403)

        user_membership = TenantMembership.objects.filter(
            user=request.user,
            tenant=tenant,
            is_active=True
        ).first()

        is_tenant_admin = user_membership and user_membership.role == TenantMembership.ROLE_ADMIN
        is_global_admin = getattr(request.user, "is_platform_admin", False) or request.user.is_superuser

        # User-Admin cannot promote/demote to/from Admin
        if new_role in [TenantMembership.ROLE_ADMIN, TenantMembership.ROLE_USER_ADMIN] and not (is_tenant_admin or is_global_admin):
            return Response({"error": "Only Energy Admins can assign administrative roles."}, status=403)

        membership = get_object_or_404(
            TenantMembership,
            tenant_id=tenant_id,
            user_id=user_id
        )

        if membership.role == TenantMembership.ROLE_ADMIN and not (is_tenant_admin or is_global_admin):
            return Response({"error": "Cannot modify Energy Admin role."}, status=403)

        old_role = membership.role
        membership.role = new_role
        membership.save()

        AuditLog.objects.create(
            user=request.user,
            tenant=tenant,
            action="role_updated",
            target_user=membership.user,
            metadata={"old_role": old_role, "new_role": new_role},
        )

        return Response({
            "status": "updated",
            "role": membership.role,
            "role_display": membership.get_role_display(),
        })


class RemoveMemberView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        tenant_id = request.data.get("tenant_id")
        user_id = request.data.get("user_id")

        tenant = get_object_or_404(Tenant, id=tenant_id)

        if not can_manage_members(request.user, tenant):
            return Response({"error": "not allowed"}, status=403)

        membership = get_object_or_404(
            TenantMembership,
            tenant_id=tenant_id,
            user_id=user_id
        )

        user_membership = TenantMembership.objects.filter(
            user=request.user,
            tenant=tenant,
            is_active=True
        ).first()

        is_tenant_admin = user_membership and user_membership.role == TenantMembership.ROLE_ADMIN
        is_global_admin = getattr(request.user, "is_platform_admin", False) or request.user.is_superuser

        # User Admin cannot remove Energy Admin
        if membership.role == TenantMembership.ROLE_ADMIN and not (is_tenant_admin or is_global_admin):
            return Response({"error": "Cannot remove Energy Admin."}, status=403)

        membership.is_active = False
        membership.save()

        AuditLog.objects.create(
            user=request.user,
            tenant=tenant,
            action="member_removed",
            target_user=membership.user,
        )

        return Response({"status": "removed"})


class DeactivateInviteView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        token = request.data.get("token")

        invite = get_object_or_404(TenantInvite, token=token)

        is_admin = TenantMembership.objects.filter(
            user=request.user,
            tenant=invite.tenant,
            role="admin",
            is_active=True
        ).exists()

        if not is_admin:
            return Response({"error": "not allowed"}, status=403)

        invite.is_active = False
        invite.save()

        AuditLog.objects.create(
            user=request.user,
            tenant=invite.tenant,
            action="invite_deactivated",
            metadata={"token": str(invite.token)},
        )

        return Response({"status": "deactivated"})


class AuditLogView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        membership = request.user.memberships.filter(is_active=True).first()
        if not membership:
            return Response([])

        logs = (
            AuditLog.objects.filter(tenant=membership.tenant)
            .select_related("user", "target_user")
            .order_by("-created_at")[:50]
        )
        return Response([
            {
                "id": l.id,
                "action": l.action,
                "user": l.user.email if l.user else "System",
                "target_user": l.target_user.email if l.target_user else "",
                "created_at": l.created_at.isoformat(),
                "metadata": l.metadata,
            }
            for l in logs
        ])



# ---------------- MAGIC LINK LOGIN ---------------- #

class RequestMagicLinkView(APIView):
    authentication_classes = []
    permission_classes = [AllowAny]

    def post(self, request):
        email = request.data.get("email", "")
        if isinstance(email, str):
            email = email.strip().lower()

        if not email or "@" not in email:
            return Response({"error": "Bitte eine gültige E-Mail-Adresse eingeben."}, status=400)

        user, _ = User.objects.get_or_create(
            email=email,
            defaults={"username": email}
        )

        # Rate limit
        last_token = MagicLoginToken.objects.filter(user=user).order_by("-created_at").first()

        if last_token and last_token.created_at > timezone.now() - timedelta(seconds=30):
            return Response({"error": "Bitte warte kurz vor einer erneuten Anfrage."}, status=400)

        MagicLoginToken.objects.filter(user=user, is_used=False).delete()

        token = MagicLoginToken.objects.create(
            user=user,
        )

        # ✅ BEST PRACTICE: LINK IMMER FRONTEND / TRACKING
        frontend_url = getattr(settings, "FRONTEND_URL", "https://sharegy.de").rstrip("/")
        link = f"{frontend_url}/t/{token.token}"

        try:
            send_magic_link_email(user, link, token.token)
        except Exception as exc:
            logger.exception("Failed to send magic link email to %s: %s", user.email, exc)
            return Response({"error": f"Mailversand fehlgeschlagen: {str(exc)}"}, status=400)

        return Response({"status": "sent"})


class MagicLoginView(APIView):
    authentication_classes = []
    permission_classes = [AllowAny]

    def get(self, request):
        token = request.GET.get("token")

        if not token:
            return Response({"error": "missing token"}, status=400)

        magic = get_object_or_404(MagicLoginToken, token=token)

        if magic.is_expired():
            return Response({"error": "expired"}, status=400)

        # ✅ WICHTIG: idempotent (mehrfach erlaubt!)
        user = magic.user
        login(request, user)

        # ✅ Sicherstellen, dass ein Standard-Zuhause existiert
        from devices.models import Home
        if not user.homes.exists():
            Home.objects.create(
                user=user,
                name="Mein Zuhause",
                timezone="Europe/Berlin"
            )

        # ✅ LOGIN TRACKING (NEU)
        magic.last_login_at = timezone.now()
        
        magic.last_login_ip = request.META.get("REMOTE_ADDR")
        magic.user_agent = request.headers.get("User-Agent", "")

        # nur speichern wenn neu oder leer (optional)
        magic.save()

        # ✅ Token nur einmal markieren
        if not magic.is_used:
            magic.is_used = True
            magic.used_at = timezone.now()
            magic.save()

        # ✅ Session Dauer zentral aus Settings
        request.session.set_expiry(
            settings.SESSION_COOKIE_AGE
        )

        return Response({"status": "ok"})


# ---------------- AUTH ---------------- #

@method_decorator(csrf_exempt, name='dispatch')
class MeView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        
        print("AUTH CLASS:", type(request._authenticator))
        print("USER:", request.user)

        serializer = UserMeSerializer(request.user)
        return Response(serializer.data)


@method_decorator(csrf_exempt, name='dispatch')
class LogoutView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        from django.contrib.auth import logout

        logout(request)
        request.session.flush()   # 💥 extra safe
        return Response({"status": "logged_out"})


def track_magic_click(request, token):
    obj = MagicLoginToken.objects.filter(token=token).first()

    if obj and not obj.clicked_at:
        obj.clicked_at = timezone.now()
        obj.save()

    frontend_url = getattr(settings, "FRONTEND_BASE_URL", getattr(settings, "FRONTEND_URL", "https://sharegy.de")).rstrip("/")
    return redirect(f"{frontend_url}/t/{token}")


def track_open(request, token):
    token_obj = MagicLoginToken.objects.filter(token=token).first()

    if token_obj:
        token_obj.opened_at = timezone.now()
        token_obj.save()

    return HttpResponse("", content_type="image/png")


def track_email_open(request, token):
    obj = MagicLoginToken.objects.filter(token=token).first()

    if obj and not obj.opened_at:
        obj.opened_at = timezone.now()
        obj.save()

    # ✅ UNSICHTBARER PIXEL
    return HttpResponse(
        b"",
        content_type="image/png"
    )

class MagicLinkStatsView(APIView):
    def get(self, request):
        total = MagicLoginToken.objects.count()
        opened = MagicLoginToken.objects.filter(opened_at__isnull=False).count()
        clicked = MagicLoginToken.objects.filter(clicked_at__isnull=False).count()
        used = MagicLoginToken.objects.filter(used_at__isnull=False).count()

        return Response({
            "total": total,
            "opened": opened,
            "clicked": clicked,
            "used": used,
            "open_rate": opened / total if total else 0,
            "click_rate": clicked / total if total else 0,
            "conversion_rate": used / total if total else 0,
        })


class LiveLoginsView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        recent = MagicLoginToken.objects.filter(
            used_at__isnull=False
        ).order_by("-used_at")[:10]

        data = [
            {
                "email": token.user.email,
                "login_time": token.used_at,
            }
            for token in recent
        ]

        return Response(data)


class TenantStatsView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        stats = MagicLoginToken.objects.values(
            "user__memberships__tenant__name"
        ).annotate(
            total=Count("id"),
            used=Count("id", filter=Q(used_at__isnull=False))
        )

        return Response(list(stats))


class DashboardStatsView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        tokens = MagicLoginToken.objects.all()

        total = tokens.count()
        opened = tokens.exclude(clicked_at=None).count()
        clicked = opened
        used = tokens.filter(is_used=True).count()

        # letzte Logins (einfach)
        recent = tokens.filter(is_used=True).order_by("-used_at")[:10]

        live_logins = [
            {
                "user": t.user.email,
                "timestamp": t.used_at.strftime("%Y-%m-%d %H:%M"),
            }
            for t in recent
        ]

        return Response({
            "funnel": {
                "total": total,
                "opened": opened,
                "clicked": clicked,
                "used": used,
            },
            "live_logins": live_logins
        })


# ---------------- DEMO SYSTEM ---------------- #
class DemoLoginView(View):

    def get(self, request):

        demo_user = User.objects.get(email="demo@sharegy.de")

        login(
            request,
            demo_user,
            backend="django.contrib.auth.backends.ModelBackend",
        )

        return redirect("/app/dashboard")


# ---------------- GDPR / DSGVO COMPLIANCE ---------------- #

class GDPRExportView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user

        # 1. Base User info
        user_data = {
            "id": str(user.id),
            "username": getattr(user, "username", ""),
            "email": user.email,
            "date_joined": user.date_joined.isoformat() if hasattr(user, "date_joined") and user.date_joined else None,
            "last_login": user.last_login.isoformat() if user.last_login else None,
            "is_active": user.is_active,
        }

        # 2. User Settings & Profile
        settings_data = {}
        try:
            settings_obj = getattr(user, "settings", None)
            if settings_obj:
                settings_data = {
                    "language": getattr(settings_obj, "language", "de"),
                    "timezone": getattr(settings_obj, "timezone", "Europe/Berlin"),
                    "dashboard_mode": getattr(settings_obj, "dashboard_mode", "user"),
                    "usage_mode": getattr(settings_obj, "usage_mode", "standard"),
                    "onboarding_step": getattr(settings_obj, "onboarding_step", None),
                }
        except Exception:
            pass

        profile_data = {}
        try:
            profile_obj = getattr(user, "profile", None)
            if profile_obj:
                profile_data = {
                    "street": getattr(profile_obj, "street", ""),
                    "postal_code": getattr(profile_obj, "postal_code", ""),
                    "city": getattr(profile_obj, "city", ""),
                    "country": getattr(profile_obj, "country", "DE"),
                    "phone": getattr(profile_obj, "phone", ""),
                    "company_name": getattr(profile_obj, "company_name", ""),
                    "vat_id": getattr(profile_obj, "vat_id", ""),
                    "consent_given": getattr(profile_obj, "consent_given", True),
                    "consent_timestamp": getattr(profile_obj, "consent_timestamp", None).isoformat() if getattr(profile_obj, "consent_timestamp", None) else None,
                }
        except Exception:
            pass

        # 3. Memberships / Tenants
        memberships_data = []
        if hasattr(user, "memberships"):
            for m in user.memberships.select_related("tenant").all():
                memberships_data.append({
                    "tenant_name": m.tenant.name if m.tenant else None,
                    "tenant_slug": m.tenant.slug if m.tenant else None,
                    "role": getattr(m, "role", "member"),
                    "is_active": getattr(m, "is_active", True),
                    "joined_at": m.created_at.isoformat() if hasattr(m, "created_at") else None,
                })

        # 4. Homes & Devices
        homes_data = []
        if hasattr(user, "homes"):
            for home in user.homes.prefetch_related("devices").all():
                devices_list = []
                for dev in home.devices.all():
                    devices_list.append({
                        "id": str(dev.id),
                        "name": getattr(dev, "name", ""),
                        "device_type": getattr(dev, "device_type", ""),
                        "category": getattr(dev, "category", ""),
                        "is_active": getattr(dev, "is_active", True),
                        "mqtt_topic": getattr(dev, "mqtt_topic", ""),
                    })
                homes_data.append({
                    "id": str(home.id),
                    "name": getattr(home, "name", ""),
                    "address": getattr(home, "address", ""),
                    "devices": devices_list,
                })

        # 5. Billing / Subscription
        billing_data = {}
        if hasattr(user, "ems_subscription"):
            sub = user.ems_subscription
            billing_data["subscription"] = {
                "plan": getattr(sub, "plan", "free"),
                "status": getattr(sub, "status", "active"),
                "current_period_end": sub.current_period_end.isoformat() if getattr(sub, "current_period_end", None) else None,
            }

        # 6. Assemble Full Export
        export_payload = {
            "export_metadata": {
                "title": "Sharegy GDPR Personal Data Export",
                "export_date": timezone.now().isoformat(),
                "service": "Sharegy HEMS/EMS (smartEvo GmbH)",
                "gdpr_reference": "Article 15 & Article 20 GDPR",
            },
            "user": user_data,
            "settings": settings_data,
            "profile": profile_data,
            "memberships": memberships_data,
            "homes_and_devices": homes_data,
            "billing": billing_data,
        }

        response = Response(export_payload)
        safe_email = user.email.replace("@", "_at_")
        filename = f"sharegy_datenexport_{safe_email}_{timezone.now().strftime('%Y%m%d')}.json"
        response["Content-Disposition"] = f'attachment; filename="{filename}"'
        return response


class GDPRDeleteAccountView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        user = request.user
        confirmation = request.data.get("confirmation", "").strip()

        # Confirmation check: must match user email or "DELETE" / "LÖSCHEN"
        valid_confirmations = [user.email.lower(), "delete", "löschen", "loeschen"]
        if confirmation.lower() not in valid_confirmations:
            return Response(
                {"error": "Bitte bestätige die Löschung durch Eingabe deiner E-Mail-Adresse oder 'LÖSCHEN'."},
                status=400
            )

        from django.db import transaction
        with transaction.atomic():
            logger.info("GDPR Account deletion executed for user %s (ID: %s)", user.email, user.id)

            # Flush user session & logout
            logout(request)
            request.session.flush()

            # Delete user (cascades to Profile, Settings, Devices, Homes, Memberships, MagicLoginTokens)
            user.delete()

        return Response({"status": "deleted", "message": "Dein Benutzerkonto und alle personenbezogenen Daten wurden unwiderruflich gelöscht."})

