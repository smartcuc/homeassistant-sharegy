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
from accounts.models import MagicLoginToken
from accounts.models import (
    UserSettings,
    UserProfile,
    TenantInvite,
    TenantMembership,
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


class CreateInviteView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        tenant_id = request.data.get("tenant_id")
        role = request.data.get("role", "viewer")

        tenant = get_object_or_404(Tenant, id=tenant_id)

        is_admin = TenantMembership.objects.filter(
            user=request.user,
            tenant=tenant,
            role="admin",
            is_active=True
        ).exists()

        if not is_admin:
            return Response({"error": "not allowed"}, status=403)

        invite = TenantInvite.objects.create(
            tenant=tenant,
            role=role,
            max_uses=10
        )

        return Response({
            "link": f"{settings.FRONTEND_URL}/join?token={invite.token}",
            "token": str(invite.token)
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
                    "role": m.role
                }
                for m in members
            ],
            "invites": [
                {
                    "token": str(i.token),
                    "role": i.role,
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

        if new_role not in ["admin", "editor", "viewer"]:
            return Response({"error": "invalid role"}, status=400)

        is_admin = TenantMembership.objects.filter(
            user=request.user,
            tenant_id=tenant_id,
            role="admin",
            is_active=True
        ).exists()

        if not is_admin:
            return Response({"error": "not allowed"}, status=403)

        membership = get_object_or_404(
            TenantMembership,
            tenant_id=tenant_id,
            user_id=user_id
        )

        membership.role = new_role
        membership.save()

        return Response({"status": "updated"})


class RemoveMemberView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        tenant_id = request.data.get("tenant_id")
        user_id = request.data.get("user_id")

        is_admin = TenantMembership.objects.filter(
            user=request.user,
            tenant_id=tenant_id,
            role="admin",
            is_active=True
        ).exists()

        if not is_admin:
            return Response({"error": "not allowed"}, status=403)

        membership = get_object_or_404(
            TenantMembership,
            tenant_id=tenant_id,
            user_id=user_id
        )

        membership.is_active = False
        membership.save()

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

        return Response({"status": "deactivated"})


# ---------------- MAGIC LINK LOGIN ---------------- #

class RequestMagicLinkView(APIView):
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
