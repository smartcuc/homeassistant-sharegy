#########################
# core/filter_backends.py
#########################

from rest_framework.filters import BaseFilterBackend

ADMIN_ROLES = {"admin", "owner", "user_admin", "manager"}

class TenantFilterBackend(BaseFilterBackend):
    def filter_queryset(self, request, queryset, view):
        tenant = getattr(request, "tenant", None)
        membership = getattr(request, "member", None)

        if not tenant or not membership:
            return queryset.none()

        # ✅ 1. Striktes Tenant-Scoping: Nur Objekte dieses Tenants
        if hasattr(queryset.model, "tenant"):
            queryset = queryset.filter(tenant=tenant)

        # ✅ 2. Rollen-Differenzierung innerhalb des Tenants:
        # Community-Admins sehen alle Zähler/Objekte der eigenen Community
        # Reguläre Mitglieder sehen nur ihre eigenen Zähler/Objekte
        is_community_admin = getattr(membership, "role", None) in ADMIN_ROLES or getattr(request.user, "is_superuser", False)
        if not is_community_admin and hasattr(queryset.model, "owner_membership"):
            queryset = queryset.filter(owner_membership=membership)

        return queryset