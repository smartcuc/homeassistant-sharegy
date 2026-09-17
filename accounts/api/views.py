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
    MagicLoginToken,
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
                "notify_weekly_report": settings_obj.notify_weekly_report,
                "notify_critical_alerts": settings_obj.notify_critical_alerts,
            }
        )

    def post(self, request):
        settings_obj, _ = UserSettings.objects.get_or_create(user=request.user)
        data = request.data

        if "notify_weekly_report" in data:
            settings_obj.notify_weekly_report = bool(data.get("notify_weekly_report"))
        if "notify_critical_alerts" in data:
            settings_obj.notify_critical_alerts = bool(data.get("notify_critical_alerts"))
        if "language" in data:
            lang = str(data.get("language", "")).strip().lower()
            if lang in ["de", "en", "pl"]:
                settings_obj.language = lang
        if "timezone" in data:
            settings_obj.timezone = str(data.get("timezone", "")).strip()

        settings_obj.save()

        return Response(
            {
                "status": "saved",
                "onboarding_step": settings_obj.onboarding_step,
                "usage_mode": settings_obj.usage_mode,
                "language": settings_obj.language,
                "timezone": settings_obj.timezone,
                "notify_weekly_report": settings_obj.notify_weekly_report,
                "notify_critical_alerts": settings_obj.notify_critical_alerts,
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

    def get(self, request):
        user = request.user
        profile, _ = UserProfile.objects.get_or_create(user=user)
        return Response(
            {
                "first_name": user.first_name or "",
                "last_name": user.last_name or "",
                "email": user.email or "",
                "phone": profile.phone or "",
                "avatar": profile.avatar or "",
                "customer_type": profile.customer_type or "private",
                "company_name": profile.company_name or "",
                "billing_name": profile.billing_name or "",
                "billing_email": profile.billing_email or "",
                "vat_id": profile.vat_id or "",
                "street": profile.street or "",
                "house_number": profile.house_number or "",
                "postal_code": profile.postal_code or "",
                "city": profile.city or "",
                "country": profile.country or "DE",
            }
        )

    def post(self, request):
        user = request.user
        data = request.data

        user.first_name = data.get("first_name", user.first_name)
        user.last_name = data.get("last_name", user.last_name)
        user.save()

        profile, _ = UserProfile.objects.get_or_create(user=user)

        if "avatar" in data:
            profile.avatar = str(data.get("avatar", "")).strip()

        profile.phone = data.get("phone", profile.phone)
        profile.customer_type = data.get("customer_type", profile.customer_type)
        profile.company_name = data.get("company_name", profile.company_name)
        profile.billing_name = data.get("billing_name", profile.billing_name)
        profile.billing_email = str(data.get("billing_email", profile.billing_email or "")).strip().lower()
        profile.vat_id = data.get("vat_id", profile.vat_id)

        profile.street = data.get("street", profile.street)
        profile.house_number = data.get("house_number", profile.house_number)
        profile.postal_code = data.get("postal_code", profile.postal_code)
        profile.city = data.get("city", profile.city)
        profile.country = data.get("country", profile.country or "DE")
        profile.save()

        return Response({"status": "saved", "avatar": profile.avatar})


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
        is_admin = bool(request.user.is_staff or (membership and membership.role in ["admin", "owner", "auditor"]))
        is_manager = bool(is_admin or (membership and membership.role in ["manager", "support"]))

        members_data = []
        invites_data = []

        if is_manager:
            members = TenantMembership.objects.filter(
                tenant=tenant,
                is_active=True
            ).select_related("user")
            invites = TenantInvite.objects.filter(tenant=tenant, is_active=True)

            members_data = [
                {
                    "id": str(m.user.id),
                    "email": m.user.email,
                    "role": m.role,
                    "role_display": m.get_role_display(),
                    "permissions": ROLE_PERMISSIONS.get(m.role, []),
                }
                for m in members
            ]
            invites_data = [
                {
                    "token": str(i.token),
                    "role": i.role,
                    "role_display": i.get_role_display(),
                    "used": i.used_count
                }
                for i in invites
            ]

        return Response({
            "tenant": {
                "id": str(tenant.id),
                "name": tenant.name,
                "user_role": membership.role,
                "is_admin": is_admin,
                "is_manager": is_manager,
            },
            "members": members_data,
            "invites": invites_data,
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

        if not can_manage_invites(request.user, invite.tenant):
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
        import secrets
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

        # 6-stelligen numerischen Code erzeugen
        code = f"{secrets.randbelow(900000) + 100000}"

        token = MagicLoginToken.objects.create(
            user=user,
            code=code,
        )

        # ✅ BEST PRACTICE: LINK IMMER FRONTEND / TRACKING
        frontend_url = getattr(settings, "FRONTEND_URL", "https://sharegy.de").rstrip("/")
        link = f"{frontend_url}/t/{token.token}"
        req_lang = request.data.get("language") or request.data.get("lang") or request.GET.get("lang")

        # 📱 App vs. Browser Erkennung
        client = str(request.data.get("client") or request.headers.get("X-Client-Type") or "").strip().lower()
        platform = str(request.data.get("platform") or "").strip().lower()
        user_agent = (request.META.get("HTTP_USER_AGENT") or "").lower()

        if not client:
            if "capacitor" in user_agent or "sharegy-app" in user_agent or "android" in user_agent and "wv" in user_agent:
                client = "app"
            else:
                client = "web"

        is_app = (client == "app" or platform in ["android", "ios", "capacitor"])

        try:
            send_magic_link_email(user, link, token.token, code=code, language=req_lang, is_app=is_app)
        except Exception as exc:
            logger.exception("Failed to send magic link email to %s: %s", user.email, exc)
            return Response({"error": f"Mailversand fehlgeschlagen: {str(exc)}"}, status=400)

        return Response({"status": "sent", "client": "app" if is_app else "web"})


class MagicLoginView(APIView):
    authentication_classes = []
    permission_classes = [AllowAny]

    def _login_with_token_or_code(self, request, token_or_code):
        import uuid
        token_str = str(token_or_code or "").strip()

        if not token_str:
            return Response({"error": "Bitte einen gültigen Login-Code oder Link angeben."}, status=400)

        # Falls ein vollständiger Link (https://.../t/UUID oder sharegy://magic?token=UUID) eingefügt wurde:
        if "/t/" in token_str:
            token_str = token_str.split("/t/")[-1].split("?")[0].split("/")[0].strip()
        elif "token=" in token_str:
            token_str = token_str.split("token=")[-1].split("&")[0].strip()

        cleaned_digits = token_str.replace(" ", "").replace("-", "")

        magic = None

        # 1. Versuch: UUID Token Lookup
        try:
            val_uuid = uuid.UUID(token_str)
            magic = MagicLoginToken.objects.filter(token=val_uuid).first()
        except (ValueError, TypeError):
            pass

        # 2. Versuch: 6-Stelliger Code Lookup
        if not magic and cleaned_digits:
            magic = MagicLoginToken.objects.filter(code=cleaned_digits).order_by("-created_at").first()

        # 3. Fallback: Lookup als String
        if not magic:
            magic = MagicLoginToken.objects.filter(code=token_str).order_by("-created_at").first()

        if not magic:
            return Response({"error": "Ungültiger oder abgelaufener Login-Code."}, status=400)

        if magic.is_expired():
            return Response({"error": "Dieser Login-Code ist abgelaufen (Gültigkeit: 15 Minuten). Bitte fordere einen neuen an."}, status=400)

        # ✅ Idempotent (mehrfach erlaubt solange nicht abgelaufen)
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

        # ✅ LOGIN TRACKING
        magic.last_login_at = timezone.now() if hasattr(magic, "last_login_at") else None
        magic.last_login_ip = request.META.get("REMOTE_ADDR")
        magic.user_agent = request.headers.get("User-Agent", "")

        if not magic.is_used:
            magic.is_used = True
            magic.used_at = timezone.now()
        magic.save()

        # ✅ Session Dauer zentral aus Settings
        request.session.set_expiry(
            settings.SESSION_COOKIE_AGE
        )

        return Response({"status": "ok"})

    def get(self, request):
        token = request.GET.get("token") or request.GET.get("code")
        return self._login_with_token_or_code(request, token)

    def post(self, request):
        token = request.data.get("token") or request.data.get("code") or request.GET.get("token")
        return self._login_with_token_or_code(request, token)


# ---------------- EMAIL CHANGE (ENTERPRISE VERIFICATION) ---------------- #

class ChangeEmailRequestView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        from django.core import signing
        from django.core.mail import EmailMultiAlternatives

        new_email = request.data.get("new_email", "")
        if isinstance(new_email, str):
            new_email = new_email.strip().lower()

        if not new_email or "@" not in new_email or "." not in new_email:
            return Response({"error": "Bitte eine gültige E-Mail-Adresse eingeben."}, status=400)

        if new_email == request.user.email.lower():
            return Response({"error": "Die neue E-Mail-Adresse entspricht bereits der aktuellen Adresse."}, status=400)

        if User.objects.filter(email__iexact=new_email).exclude(id=request.user.id).exists():
            return Response({"error": "Diese E-Mail-Adresse wird bereits von einem anderen Konto verwendet."}, status=400)

        # Token erzeugen mit 30 Minuten Gültigkeit
        token = signing.dumps(
            {"user_id": str(request.user.id), "new_email": new_email},
            salt="sharegy-change-email-v1",
        )

        frontend_url = getattr(settings, "FRONTEND_URL", "https://sharegy.de").rstrip("/")
        confirm_link = f"{frontend_url}/confirm-email-change?token={token}"
        from accounts.services.email_service import send_email_change_request_email, send_email_change_alert_email

        # 1. Bestätigungs-Mail an NEUE Adresse (in gewählter Nutzersprache)
        try:
            send_email_change_request_email(request.user, new_email, confirm_link)
        except Exception as exc:
            logger.exception("Failed to send email change verification to %s: %s", new_email, exc)
            return Response({"error": f"Mailversand an die neue Adresse fehlgeschlagen: {str(exc)}"}, status=400)

        # 2. Sicherheits-Benachrichtigung an ALTE Adresse
        try:
            send_email_change_alert_email(request.user, new_email)
        except Exception:
            pass

        return Response({"status": "sent", "new_email": new_email})


class ConfirmEmailChangeView(APIView):
    authentication_classes = []
    permission_classes = [AllowAny]

    def post(self, request):
        from django.core import signing

        token = request.data.get("token") or request.GET.get("token")
        if not token:
            return Response({"error": "Token fehlt."}, status=400)

        try:
            data = signing.loads(token, salt="sharegy-change-email-v1", max_age=1800)
            user_id = data.get("user_id")
            new_email = data.get("new_email")
        except signing.SignatureExpired:
            return Response({"error": "Der Bestätigungslink ist abgelaufen (Gültigkeit: 30 Minuten). Bitte fordere einen neuen an."}, status=400)
        except Exception:
            return Response({"error": "Ungültiger oder beschädigter Bestätigungslink."}, status=400)

        user = User.objects.filter(id=user_id).first()
        if not user:
            return Response({"error": "Benutzerkonto nicht gefunden."}, status=404)

        if User.objects.filter(email__iexact=new_email).exclude(id=user.id).exists():
            return Response({"error": "Diese E-Mail-Adresse ist inzwischen bereits vergeben."}, status=400)

        old_email = user.email
        user.email = new_email
        user.username = new_email
        user.save()

        # Invalidate existing unconsumed magic tokens for security
        MagicLoginToken.objects.filter(user=user, is_used=False).delete()

        return Response({
            "status": "confirmed",
            "message": f"E-Mail-Adresse erfolgreich von {old_email} auf {new_email} geändert.",
            "email": new_email,
        })


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


@method_decorator(csrf_exempt, name='dispatch')
class RevokeMagicLinksView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        from django.contrib.auth import logout

        user = request.user
        deleted_count, _ = MagicLoginToken.objects.filter(user=user).delete()
        logger.info("Revoked %d magic login tokens for user %s (ID: %s)", deleted_count, user.email, user.id)

        # Invalidate current session & logout
        logout(request)
        request.session.flush()

        return Response({
            "status": "revoked",
            "deleted_count": deleted_count,
            "message": "Alle Magic-Links wurden erfolgreich gelöscht und du wurdest abgemeldet."
        })



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

        from devices.services.interface_tracker import get_aggregated_interface_stats
        interface_stats = get_aggregated_interface_stats()

        return Response({
            "funnel": {
                "total": total,
                "opened": opened,
                "clicked": clicked,
                "used": used,
            },
            "live_logins": live_logins,
            "interface_stats": interface_stats,
        })


# ---------------- DEMO SYSTEM ---------------- #
class DemoLoginView(View):
    def get(self, request):
        role = request.GET.get("role", "").lower().strip()
        if role in ("sharing-admin", "sharing_admin", "admin-sharing"):
            return DemoSharingAdminLoginView().get(request)
        elif role in ("sharing-user", "sharing_user", "community", "sharing"):
            return DemoSharingUserLoginView().get(request)
        elif role in ("mieterstrom-admin", "mieterstrom_admin", "admin-mieterstrom"):
            return DemoMieterstromAdminLoginView().get(request)
        elif role in ("mieterstrom-user", "mieterstrom_user", "mieterstrom", "mieter"):
            return DemoMieterstromUserLoginView().get(request)
        elif role in ("ggv-admin", "ggv_admin", "admin-ggv"):
            return DemoGGVAdminLoginView().get(request)
        elif role in ("ggv-user", "ggv_user", "ggv"):
            return DemoGGVUserLoginView().get(request)
        elif role in ("admin", "superadmin"):
            return DemoSharingAdminLoginView().get(request)
        elif role in ("user", "household"):
            pass

        # Standard Dashboard Demo
        demo_user, created = User.objects.get_or_create(
            email="demo@sharegy.de",
            defaults={"username": "demo@sharegy.de", "first_name": "Demo", "last_name": "User", "is_active": True}
        )
        if not demo_user.is_active:
            demo_user.is_active = True
            demo_user.save(update_fields=["is_active"])

        # Sicherstellen, dass das Demo-Zuhause mit allen Geräten, Prognosen und Rechnungen existiert
        if created or not demo_user.homes.exists() or demo_user.homes.first().devices.count() == 0:
            try:
                from demo.services.data_generator import setup_demo_household, generate_demo_telemetry
                setup_demo_household(demo_user)
                generate_demo_telemetry()
            except Exception as e:
                import logging
                logging.getLogger(__name__).warning("Demo household initial setup warning: %s", e)

        login(
            request,
            demo_user,
            backend="django.contrib.auth.backends.ModelBackend",
        )

        return redirect("/app/dashboard")


class DemoSharingAdminLoginView(View):
    """
    Loggt den Sharing-Admin ein und leitet direkt auf den Multi-Community Hub weiter.
    """
    def get(self, request):
        import logging
        from accounts.services_demo_sharing import seed_sharing_demo_environment

        logger = logging.getLogger(__name__)
        try:
            data = seed_sharing_demo_environment()
            admin_user = data.get("admin_user")
        except Exception as e:
            logger.exception("Demo seeding error in DemoSharingAdminLoginView: %s", e)
            admin_user = None

        if not admin_user or not isinstance(admin_user, User):
            admin_user, _ = User.objects.get_or_create(
                email="sharing-admin@sharegy.de",
                defaults={"username": "sharing-admin@sharegy.de", "first_name": "Alexander", "last_name": "Quartiermanager", "is_staff": True, "is_active": True}
            )

        login(
            request,
            admin_user,
            backend="django.contrib.auth.backends.ModelBackend",
        )

        return redirect("/app/admin/communities")


class DemoSharingUserLoginView(View):
    """
    Loggt den Sharing-User / Community-Teilnehmer ein und leitet auf das Energy Sharing Cockpit weiter.
    """
    def get(self, request):
        import logging
        from accounts.services_demo_sharing import seed_sharing_demo_environment

        logger = logging.getLogger(__name__)
        try:
            data = seed_sharing_demo_environment()
            member_user = data.get("member_user")
        except Exception as e:
            logger.exception("Demo seeding error in DemoSharingUserLoginView: %s", e)
            member_user = None

        if not member_user or not isinstance(member_user, User):
            member_user, _ = User.objects.get_or_create(
                email="sharing-user@sharegy.de",
                defaults={"username": "sharing-user@sharegy.de", "first_name": "Julia", "last_name": "Sonnenschein", "is_active": True}
            )

        login(
            request,
            member_user,
            backend="django.contrib.auth.backends.ModelBackend",
        )

        return redirect("/app/community")


class DemoMieterstromAdminLoginView(View):
    """
    Loggt den Mieterstrom-Admin (Vermieter/Contractor) ein.
    """
    def get(self, request):
        import logging
        from accounts.services_demo_sharing import seed_sharing_demo_environment

        logger = logging.getLogger(__name__)
        try:
            data = seed_sharing_demo_environment()
            admin_user = data.get("mieterstrom_admin")
        except Exception as e:
            logger.exception("Demo seeding error in DemoMieterstromAdminLoginView: %s", e)
            admin_user = None

        if not admin_user or not isinstance(admin_user, User):
            admin_user, _ = User.objects.get_or_create(
                email="mieterstrom-admin@sharegy.de",
                defaults={"username": "mieterstrom-admin@sharegy.de", "first_name": "Maximilian", "last_name": "Contractor", "is_staff": True, "is_active": True}
            )

        login(
            request,
            admin_user,
            backend="django.contrib.auth.backends.ModelBackend",
        )

        return redirect("/app/admin/communities")


class DemoMieterstromUserLoginView(View):
    """
    Loggt den Mieterstrom-User / Mieter ein und leitet auf das Mieterstrom-Cockpit weiter.
    """
    def get(self, request):
        import logging
        from accounts.services_demo_sharing import seed_sharing_demo_environment

        logger = logging.getLogger(__name__)
        try:
            data = seed_sharing_demo_environment()
            user = data.get("mieterstrom_user")
        except Exception as e:
            logger.exception("Demo seeding error in DemoMieterstromUserLoginView: %s", e)
            user = None

        if not user or not isinstance(user, User):
            user, _ = User.objects.get_or_create(
                email="mieterstrom-user@sharegy.de",
                defaults={"username": "mieterstrom-user@sharegy.de", "first_name": "Tim", "last_name": "Mieter", "is_active": True}
            )

        login(
            request,
            user,
            backend="django.contrib.auth.backends.ModelBackend",
        )

        return redirect("/app/community")


class DemoGGVAdminLoginView(View):
    """
    Loggt den GGV-Admin (WEG-Verwalter) ein.
    """
    def get(self, request):
        import logging
        from accounts.services_demo_sharing import seed_sharing_demo_environment

        logger = logging.getLogger(__name__)
        try:
            data = seed_sharing_demo_environment()
            admin_user = data.get("ggv_admin")
        except Exception as e:
            logger.exception("Demo seeding error in DemoGGVAdminLoginView: %s", e)
            admin_user = None

        if not admin_user or not isinstance(admin_user, User):
            admin_user, _ = User.objects.get_or_create(
                email="ggv-admin@sharegy.de",
                defaults={"username": "ggv-admin@sharegy.de", "first_name": "Susanne", "last_name": "WEG-Verwaltung", "is_staff": True, "is_active": True}
            )

        login(
            request,
            admin_user,
            backend="django.contrib.auth.backends.ModelBackend",
        )

        return redirect("/app/admin/communities")


class DemoGGVUserLoginView(View):
    """
    Loggt den GGV-User / Wohnungseigentümer ein und leitet auf das GGV-Cockpit weiter.
    """
    def get(self, request):
        import logging
        from accounts.services_demo_sharing import seed_sharing_demo_environment

        logger = logging.getLogger(__name__)
        try:
            data = seed_sharing_demo_environment()
            user = data.get("ggv_user")
        except Exception as e:
            logger.exception("Demo seeding error in DemoGGVUserLoginView: %s", e)
            user = None

        if not user or not isinstance(user, User):
            user, _ = User.objects.get_or_create(
                email="ggv-user@sharegy.de",
                defaults={"username": "ggv-user@sharegy.de", "first_name": "Sabine", "last_name": "Eigentümerin", "is_active": True}
            )

        login(
            request,
            user,
            backend="django.contrib.auth.backends.ModelBackend",
        )

        return redirect("/app/community")


# ---------------- GDPR / DSGVO COMPLIANCE ---------------- #

class GDPRExportView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user

        # 1. Base User info
        user_data = {
            "id": str(user.id),
            "username": getattr(user, "username", ""),
            "first_name": getattr(user, "first_name", ""),
            "last_name": getattr(user, "last_name", ""),
            "email": user.email,
            "avatar": getattr(getattr(user, "profile", None), "avatar", ""),
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
                    "avatar": getattr(profile_obj, "avatar", ""),
                    "first_name": getattr(user, "first_name", ""),
                    "last_name": getattr(user, "last_name", ""),
                    "street": getattr(profile_obj, "street", ""),
                    "postal_code": getattr(profile_obj, "postal_code", ""),
                    "city": getattr(profile_obj, "city", ""),
                    "country": getattr(profile_obj, "country", "DE"),
                    "phone": getattr(profile_obj, "phone", ""),
                    "customer_type": getattr(profile_obj, "customer_type", "private"),
                    "company_name": getattr(profile_obj, "company_name", ""),
                    "billing_name": getattr(profile_obj, "billing_name", ""),
                    "billing_email": getattr(profile_obj, "billing_email", ""),
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
                "service": "Sharegy EMS (smartEvo GmbH)",
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

            # Stripe cleanup: cancel subscription and delete customer object
            try:
                from billing.services_stripe import delete_stripe_customer_for_user
                delete_stripe_customer_for_user(user)
            except Exception as e:
                logger.warning("Stripe customer deletion during GDPR cleanup failed: %s", e)

            # Flush user session & logout
            logout(request)
            request.session.flush()

            # Delete user (cascades to Profile, Settings, Devices, Homes, Memberships, MagicLoginTokens)
            user.delete()

        return Response({"status": "deleted", "message": "Dein Benutzerkonto und alle personenbezogenen Daten wurden unwiderruflich gelöscht."})

