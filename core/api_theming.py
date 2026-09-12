import logging
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated, AllowAny
from django.shortcuts import get_object_or_404

from core.models import Tenant
from accounts.models import TenantMembership

logger = logging.getLogger("django")


class TenantThemingView(APIView):
    """
    GET /api/core/tenant/theming/
    PATCH /api/core/tenant/theming/
    Liest und aktualisiert die Whitelabel- und Theming-Einstellungen eines Mandanten / Stadtwerks.
    """
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        tenant_id = request.query_params.get("tenant_id")
        if tenant_id:
            tenant = get_object_or_404(Tenant, id=tenant_id)
        else:
            membership = TenantMembership.objects.filter(user=user, role__in=["admin", "user_admin"]).first()
            if not membership:
                membership = TenantMembership.objects.filter(user=user).first()
            tenant = membership.tenant if membership else Tenant.objects.first()

        if not tenant:
            return Response({"error": "Kein Tenant gefunden."}, status=status.HTTP_404_NOT_FOUND)

        return Response({
            "tenant_id": str(tenant.id),
            "name": tenant.name,
            "slug": tenant.slug,
            "is_whitelabel_active": tenant.is_whitelabel_active,
            "primary_color": tenant.primary_color,
            "secondary_color": tenant.secondary_color,
            "accent_color": tenant.accent_color,
            "button_color": tenant.button_color,
            "logo_url": tenant.logo_url,
            "favicon_url": tenant.favicon_url,
            "company_legal_name": tenant.company_legal_name or tenant.name,
            "support_email": tenant.support_email,
            "custom_domain": tenant.custom_domain,
        })

    def patch(self, request):
        user = request.user
        tenant_id = request.data.get("tenant_id")
        if tenant_id:
            tenant = get_object_or_404(Tenant, id=tenant_id)
        else:
            membership = TenantMembership.objects.filter(user=user, role="admin").first()
            tenant = membership.tenant if membership else Tenant.objects.first()

        if not tenant:
            return Response({"error": "Kein Tenant gefunden."}, status=status.HTTP_404_NOT_FOUND)

        fields = [
            "primary_color", "secondary_color", "accent_color", "button_color",
            "logo_url", "favicon_url", "company_legal_name", "support_email",
            "custom_domain", "is_whitelabel_active"
        ]
        update_fields = []
        for f in fields:
            if f in request.data:
                setattr(tenant, f, request.data[f])
                update_fields.append(f)

        if update_fields:
            tenant.save(update_fields=update_fields)

        return Response({
            "success": True,
            "message": "Whitelabel-Einstellungen erfolgreich gespeichert.",
            "theming": {
                "tenant_id": str(tenant.id),
                "name": tenant.name,
                "is_whitelabel_active": tenant.is_whitelabel_active,
                "primary_color": tenant.primary_color,
                "secondary_color": tenant.secondary_color,
                "accent_color": tenant.accent_color,
                "button_color": tenant.button_color,
                "logo_url": tenant.logo_url,
                "favicon_url": tenant.favicon_url,
                "company_legal_name": tenant.company_legal_name,
                "support_email": tenant.support_email,
                "custom_domain": tenant.custom_domain,
            }
        })


class PublicTenantDomainLookupView(APIView):
    """
    GET /api/core/tenant/by-domain/?domain=portal.stadtwerke.de
    Erlaubt es dem Frontend beim ersten Seitenaufruf, das Theme anhand der Browser-Domain zu laden.
    """
    permission_classes = [AllowAny]

    def get(self, request):
        domain = request.query_params.get("domain", "").strip().lower()
        tenant = None
        if domain:
            tenant = Tenant.objects.filter(custom_domain__iexact=domain, is_whitelabel_active=True).first()

        if not tenant:
            # Standard Theme
            return Response({
                "whitelabel": False,
                "primary_color": "#10B981",
                "accent_color": "#6366F1",
                "name": "Sharegy",
                "logo_url": "",
                "company_legal_name": "Sharegy Technologies GmbH"
            })

        return Response({
            "whitelabel": True,
            "tenant_id": str(tenant.id),
            "name": tenant.name,
            "primary_color": tenant.primary_color,
            "secondary_color": tenant.secondary_color,
            "accent_color": tenant.accent_color,
            "button_color": tenant.button_color,
            "logo_url": tenant.logo_url,
            "favicon_url": tenant.favicon_url,
            "company_legal_name": tenant.company_legal_name or tenant.name,
            "support_email": tenant.support_email,
            "custom_domain": tenant.custom_domain,
        })
