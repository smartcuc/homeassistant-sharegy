#########################################
# accounts/permissions.py
#########################################

from functools import wraps
from rest_framework.permissions import BasePermission
from rest_framework.response import Response

from accounts.models import TenantMembership
from core.models import Tenant


# ✅ Rollen → Rechte Mapping (Enterprise Multi-Tenant)
ROLE_PERMISSIONS = {
    "admin": [
        "manage_community",
        "manage_members",
        "manage_invites",
        "manage_tickets",
        "manage_vpp",
        "manage_dimming",
        "manage_statements",
        "view_reports",
        "edit_data",
        "view_data",
        "view_audit_log",
        "export_data",
    ],
    "dispatcher": [
        "manage_vpp",
        "manage_dimming",
        "view_data",
        "view_reports",
    ],
    "billing": [
        "manage_statements",
        "view_reports",
        "view_data",
        "export_data",
    ],
    "installer": [
        "manage_devices",
        "view_protocols",
        "view_data",
    ],
    "user_admin": [
        "manage_members",
        "manage_invites",
        "view_data",
    ],
    "helpdesk": [
        "manage_tickets",
        "view_data",
    ],
    "auditor": [
        "view_reports",
        "view_data",
        "view_audit_log",
        "export_data",
    ],
    "member": [
        "view_data",
    ],
    # Legacy Fallbacks
    "editor": [
        "edit_data",
        "view_data",
    ],
    "viewer": [
        "view_data",
    ],
}


# ✅ zentrale Permission Funktion
def has_permission(user, tenant, permission):
    if not user or not user.is_authenticated:
        return False

    # Platform Admins have super-access
    if getattr(user, "is_platform_admin", False) or user.is_superuser:
        return True

    membership = TenantMembership.objects.filter(
        user=user,
        tenant=tenant,
        is_active=True
    ).first()

    if not membership:
        return False

    role = membership.role
    return permission in ROLE_PERMISSIONS.get(role, [])


def can_manage_members(user, tenant) -> bool:
    return has_permission(user, tenant, "manage_members")


def can_manage_invites(user, tenant) -> bool:
    return has_permission(user, tenant, "manage_invites")


def can_handle_community_tickets(user, tenant) -> bool:
    return has_permission(user, tenant, "manage_tickets")


def can_view_community_reports(user, tenant) -> bool:
    return has_permission(user, tenant, "view_reports")


def can_dispatch_vpp(user, tenant=None) -> bool:
    if getattr(user, "is_dispatcher", False) or getattr(user, "is_platform_admin", False) or user.is_superuser:
        return True
    return has_permission(user, tenant, "manage_vpp") if tenant else False


def can_manage_billing(user, tenant=None) -> bool:
    if getattr(user, "is_finance_admin", False) or getattr(user, "is_platform_admin", False) or user.is_superuser:
        return True
    return has_permission(user, tenant, "manage_statements") if tenant else False


def can_view_audit_log(user, tenant=None) -> bool:
    if getattr(user, "is_auditor", False) or getattr(user, "is_platform_admin", False) or user.is_superuser:
        return True
    return has_permission(user, tenant, "view_audit_log") if tenant else False



# ✅ einfacher Zugriff (ohne spezielle Permission)
def has_tenant_access(user, tenant):
    return TenantMembership.objects.filter(
        user=user,
        tenant=tenant,
        is_active=True
    ).exists()


# ✅ DRF Permission: gleicher Tenant Zugriff
class IsSameTenant(BasePermission):

    def has_object_permission(self, request, view, obj):
        return has_tenant_access(request.user, obj.tenant)


# ✅ DRF Permission: darf Objekt bearbeiten
class CanEditTenantObject(BasePermission):

    def has_object_permission(self, request, view, obj):
        return has_permission(request.user, obj.tenant, "edit_data")


# ✅ DECORATOR für Views (sehr stark)
def require_permission(permission):
    def decorator(view_func):

        @wraps(view_func)
        def wrapper(self, request, *args, **kwargs):

            tenant_id = request.data.get("tenant_id")
            
            if not tenant_id:
                return Response(
                    {"error": "tenant_id missing"},
                    status=400
                )

            try:
                tenant = Tenant.objects.get(id=tenant_id)
            except Tenant.DoesNotExist:
                return Response(
                    {"error": "tenant not found"},
                    status=404
                )

            # ✅ Check Permission
            if not has_permission(request.user, tenant, permission):
                return Response(
                    {"error": "not allowed"},
                    status=403
                )

            # ✅ Tenant an Request hängen
            request.tenant = tenant

            return view_func(self, request, *args, **kwargs)

        return wrapper
    return decorator

