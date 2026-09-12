from django.test import TestCase
from rest_framework.test import APIClient
from rest_framework import status
from django.contrib.auth import get_user_model
from core.models import Tenant, Meter
from accounts.models import TenantMembership

User = get_user_model()


class MarketCommunicationApiTest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.admin_user = User.objects.create_user(
            username="admin@sonnenfeld.de",
            email="admin@sonnenfeld.de",
            password="testpassword123"
        )
        self.tenant = Tenant.objects.create(
            name="Quartier Sonnenfeld",
            slug="quartier-sonnenfeld"
        )
        self.membership = TenantMembership.objects.create(
            user=self.admin_user,
            tenant=self.tenant,
            role="admin"
        )
        Meter.objects.create(
            tenant=self.tenant,
            owner_membership=self.membership,
            serial_number="MSB-100200300"
        )
        self.client.force_authenticate(user=self.admin_user)

    def test_mscons_export_view(self):
        res = self.client.post("/api/billing/mako/export/", data={
            "tenant_id": str(self.tenant.id),
            "mako_type": "MSCONS",
            "provider": "powercloud"
        }, format="json")
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertTrue(res.data["success"])
        self.assertIn("MSCONS", res.data["raw_edifact_sample"])

    def test_utilmd_export_view(self):
        res = self.client.post("/api/billing/mako/export/", data={
            "tenant_id": str(self.tenant.id),
            "mako_type": "UTILMD",
            "provider": "schleupen"
        }, format="json")
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertTrue(res.data["success"])
        self.assertIn("UTILMD", res.data["raw_edifact_sample"])

    def test_mako_logs_view(self):
        res = self.client.get("/api/billing/mako/logs/")
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertTrue(len(res.data["logs"]) > 0)
