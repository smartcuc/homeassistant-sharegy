##################
# core/viewsets.py
##################

from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated

from core.permissions import HasTenantContext
from core.permissions_roles import RolePermission
from core.filter_backends import TenantFilterBackend


ADMIN_ROLES = {"admin", "owner", "user_admin", "manager"}


class TenantScopedViewSetMixin(viewsets.ModelViewSet):

    permission_classes = [
        IsAuthenticated,
        HasTenantContext,
        RolePermission,
    ]
    filter_backends = [TenantFilterBackend]


    def get_queryset(self):
        qs = super().get_queryset()

        # ✅ Community Scope
        if self.request.scope == "community":
            if hasattr(qs.model, "tenant") and self.request.tenant:
                qs = qs.filter(tenant=self.request.tenant)

            is_admin = getattr(self.request.member, "role", None) in ADMIN_ROLES or getattr(self.request.user, "is_superuser", False)
            if not is_admin and hasattr(qs.model, "owner_membership") and self.request.member:
                qs = qs.filter(owner_membership=self.request.member)

        # ✅ Personal Scope
        else:
            if hasattr(qs.model, "owner_user"):
                qs = qs.filter(owner_user=self.request.user)

            if hasattr(qs.model, "tenant"):
                qs = qs.filter(tenant__isnull=True)

        return qs


    def perform_create(self, serializer):
        data = {}

        if self.request.scope == "community":
            if hasattr(serializer.Meta.model, "tenant"):
                data["tenant"] = self.request.tenant

            if hasattr(serializer.Meta.model, "owner_membership"):
                data["owner_membership"] = self.request.member
        else:
            if hasattr(serializer.Meta.model, "owner_user"):
                data["owner_user"] = self.request.user

            if hasattr(serializer.Meta.model, "tenant"):
                data["tenant"] = None

        serializer.save(**data)


    def perform_update(self, serializer):
        data = {}

        if self.request.scope == "community":
            if hasattr(serializer.Meta.model, "tenant"):
                data["tenant"] = self.request.tenant

            if hasattr(serializer.Meta.model, "owner_membership"):
                data["owner_membership"] = self.request.member
        else:
            if hasattr(serializer.Meta.model, "owner_user"):
                data["owner_user"] = self.request.user

            if hasattr(serializer.Meta.model, "tenant"):
                data["tenant"] = None

        serializer.save(**data)