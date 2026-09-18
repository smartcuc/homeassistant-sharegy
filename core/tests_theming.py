from django.test import TestCase
from rest_framework.test import APIClient
from rest_framework import status
from django.contrib.auth import get_user_model
from core.models import Tenant
from accounts.models import TenantMembership

User = get_user_model()


class TenantThemingApiTest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.admin_user = User.objects.create_user(
            username="admin@stadtwerke-nord.de",
            email="admin@stadtwerke-nord.de",
            password="testpassword123"
        )
        self.tenant = Tenant.objects.create(
            name="Stadtwerke Nord",
            slug="stadtwerke-nord",
            primary_color="#0284C7",
            custom_domain="portal.stadtwerke-nord.de",
            is_whitelabel_active=True
        )
        TenantMembership.objects.create(
            user=self.admin_user,
            tenant=self.tenant,
            role="admin"
        )
        self.client.force_authenticate(user=self.admin_user)

    def test_get_and_patch_theming(self):
        res = self.client.get(f"/api/core/tenant/theming/?tenant_id={self.tenant.id}", secure=True)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data["primary_color"], "#0284C7")
        self.assertTrue(res.data["is_whitelabel_active"])

        patch_res = self.client.patch("/api/core/tenant/theming/", data={
            "tenant_id": str(self.tenant.id),
            "primary_color": "#0EA5E9",
            "accent_color": "#F59E0B",
            "company_legal_name": "Stadtwerke Nord Energie GmbH"
        }, format="json", secure=True)
        self.assertEqual(patch_res.status_code, status.HTTP_200_OK)
        self.assertEqual(patch_res.data["theming"]["primary_color"], "#0EA5E9")

    def test_public_domain_lookup(self):
        anon_client = APIClient()
        res = anon_client.get("/api/core/tenant/by-domain/?domain=portal.stadtwerke-nord.de", secure=True)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertTrue(res.data["whitelabel"])
        self.assertEqual(res.data["name"], "Stadtwerke Nord")
