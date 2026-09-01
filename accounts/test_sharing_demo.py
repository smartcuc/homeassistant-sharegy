"""
accounts/test_sharing_demo.py

Unit-Tests für die automatischen Demo-Logins für:
- Sharing Admin (Multi-Community Hub)
- Sharing User (Energy Sharing Cockpit)
"""

from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from accounts.services_demo_sharing import seed_sharing_demo_environment

User = get_user_model()


class SharingDemoTests(TestCase):
    def setUp(self):
        self.client = Client()

    def test_seed_sharing_demo_environment(self):
        """Testet das Seeding von Communities, Mitgliedschaften, Zählern, Quoten und Abrechnungen."""
        res = seed_sharing_demo_environment()
        self.assertIn("admin_user", res)
        self.assertIn("member_user", res)
        self.assertIn("tenant_sonnenfeld", res)

        admin = res["admin_user"]
        member = res["member_user"]
        tenant = res["tenant_sonnenfeld"]

        self.assertEqual(admin.email, "sharing-admin@sharegy.de")
        self.assertEqual(member.email, "sharing-user@sharegy.de")
        self.assertTrue(admin.is_staff)

        # Prüfe ob Tarif existiert
        self.assertTrue(tenant.community_tariffs.exists())
        # Prüfe ob Quoten existieren
        self.assertTrue(tenant.member_shares.exists())
        # Prüfe ob Zähler existieren
        self.assertTrue(tenant.meters.exists())

    def test_demo_sharing_admin_login_endpoint(self):
        """Testet den Endpoint /api/demo/sharing-admin/."""
        response = self.client.get("/api/demo/sharing-admin/")
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, "/admin/communities")

        # Prüfe ob eingeloggt
        user_id = self.client.session.get("_auth_user_id")
        self.assertIsNotNone(user_id)
        user = User.objects.get(id=user_id)
        self.assertEqual(user.email, "sharing-admin@sharegy.de")

    def test_demo_sharing_user_login_endpoint(self):
        """Testet den Endpoint /api/demo/sharing-user/."""
        response = self.client.get("/api/demo/sharing-user/")
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, "/app/tenant")

        # Prüfe ob eingeloggt
        user_id = self.client.session.get("_auth_user_id")
        self.assertIsNotNone(user_id)
        user = User.objects.get(id=user_id)
        self.assertEqual(user.email, "sharing-user@sharegy.de")

    def test_demo_login_with_query_params(self):
        """Testet /api/demo/?role=sharing-admin und /api/demo/?role=sharing-user."""
        res_admin = self.client.get("/api/demo/?role=sharing-admin")
        self.assertEqual(res_admin.status_code, 302)
        self.assertEqual(res_admin.url, "/admin/communities")

        res_user = self.client.get("/api/demo/?role=sharing-user")
        self.assertEqual(res_user.status_code, 302)
        self.assertEqual(res_user.url, "/app/tenant")
