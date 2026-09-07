#########################################
# accounts/tests.py
# Enterprise Multi-Tenant RBAC Test Suite
#########################################

from django.test import TestCase
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient

from core.models import Tenant
from accounts.models import TenantMembership, TenantInvite
from accounts.permissions import has_permission, can_manage_members, can_manage_invites, can_handle_community_tickets

User = get_user_model()


class EnterpriseRBACTest(TestCase):
    def setUp(self):
        self.client = APIClient()

        # Users
        self.sys_admin = User.objects.create_user(
            username="sysadmin",
            email="sysadmin@sharegy.de",
            password="testpassword123",
            platform_role=User.PLATFORM_ROLE_SYSTEM_ADMIN,
        )
        self.finance_user = User.objects.create_user(
            username="finance_lead",
            email="finance@sharegy.de",
            password="testpassword123",
            platform_role=User.PLATFORM_ROLE_FINANCE,
        )
        self.global_user_admin = User.objects.create_user(
            username="user_admin_global",
            email="globaluseradmin@sharegy.de",
            password="testpassword123",
            platform_role=User.PLATFORM_ROLE_USER_ADMIN,
        )
        self.platform_helpdesk = User.objects.create_user(
            username="platform_agent",
            email="agent@sharegy.de",
            password="testpassword123",
            platform_role=User.PLATFORM_ROLE_HELPDESK,
        )

        # Community Users
        self.energy_admin = User.objects.create_user(
            username="energy_admin_user",
            email="admin@quartier-sonne.de",
            password="testpassword123",
        )
        self.energy_user_admin = User.objects.create_user(
            username="energy_user_admin_user",
            email="useradmin@quartier-sonne.de",
            password="testpassword123",
        )
        self.energy_helpdesk = User.objects.create_user(
            username="energy_helpdesk_user",
            email="helpdesk@quartier-sonne.de",
            password="testpassword123",
        )
        self.energy_auditor = User.objects.create_user(
            username="energy_auditor_user",
            email="auditor@quartier-sonne.de",
            password="testpassword123",
        )
        self.community_member = User.objects.create_user(
            username="member_user",
            email="member@quartier-sonne.de",
            password="testpassword123",
        )

        # Tenant (Energy Community)
        self.tenant = Tenant.objects.create(name="Quartier Sonnenfeld", slug="quartier-sonnenfeld")

        # Memberships
        TenantMembership.objects.create(user=self.energy_admin, tenant=self.tenant, role=TenantMembership.ROLE_ADMIN)
        TenantMembership.objects.create(user=self.energy_user_admin, tenant=self.tenant, role=TenantMembership.ROLE_USER_ADMIN)
        TenantMembership.objects.create(user=self.energy_helpdesk, tenant=self.tenant, role=TenantMembership.ROLE_HELPDESK)
        TenantMembership.objects.create(user=self.energy_auditor, tenant=self.tenant, role=TenantMembership.ROLE_AUDITOR)
        TenantMembership.objects.create(user=self.community_member, tenant=self.tenant, role=TenantMembership.ROLE_MEMBER)

    def test_platform_role_properties(self):
        self.assertTrue(self.sys_admin.is_platform_admin)
        self.assertTrue(self.sys_admin.is_finance_admin)
        self.assertTrue(self.sys_admin.is_global_user_admin)
        self.assertTrue(self.sys_admin.is_platform_helpdesk)

        self.assertFalse(self.finance_user.is_platform_admin)
        self.assertTrue(self.finance_user.is_finance_admin)
        self.assertFalse(self.finance_user.is_global_user_admin)

        self.assertFalse(self.global_user_admin.is_platform_admin)
        self.assertTrue(self.global_user_admin.is_global_user_admin)

        self.assertFalse(self.platform_helpdesk.is_platform_admin)
        self.assertTrue(self.platform_helpdesk.is_platform_helpdesk)

    def test_permission_helpers(self):
        # Admin has all permissions
        self.assertTrue(can_manage_members(self.energy_admin, self.tenant))
        self.assertTrue(can_manage_invites(self.energy_admin, self.tenant))
        self.assertTrue(can_handle_community_tickets(self.energy_admin, self.tenant))

        # User-Admin has member & invite management, but no ticket handling
        self.assertTrue(can_manage_members(self.energy_user_admin, self.tenant))
        self.assertTrue(can_manage_invites(self.energy_user_admin, self.tenant))
        self.assertFalse(can_handle_community_tickets(self.energy_user_admin, self.tenant))

        # Helpdesk has ticket handling, but cannot manage members
        self.assertFalse(can_manage_members(self.energy_helpdesk, self.tenant))
        self.assertTrue(can_handle_community_tickets(self.energy_helpdesk, self.tenant))

        # Member has no admin rights
        self.assertFalse(can_manage_members(self.community_member, self.tenant))
        self.assertFalse(can_manage_invites(self.community_member, self.tenant))

    def test_user_me_api_returns_rbac_details(self):
        self.client.force_login(self.energy_admin)
        resp = self.client.get("/api/auth/me/")
        self.assertEqual(resp.status_code, 200)
        data = resp.json()

        self.assertEqual(data["email"], "admin@quartier-sonne.de")
        self.assertEqual(len(data["memberships"]), 1)
        membership = data["memberships"][0]
        self.assertEqual(membership["role"], "admin")
        self.assertEqual(membership["role_display"], "Energy Admin")
        self.assertIn("manage_community", membership["permissions"])
        self.assertIn("manage_members", membership["permissions"])

    def test_create_invite_hierarchy(self):
        # 1. Energy Admin can invite any role
        self.client.force_login(self.energy_admin)
        resp = self.client.post(
            "/api/create-invite/",
            data={"tenant_id": str(self.tenant.id), "role": "user_admin"},
            format="json",
        )
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.json()["role"], "user_admin")

        # 2. Energy User Admin can invite members & helpdesk
        self.client.force_login(self.energy_user_admin)
        resp_mem = self.client.post(
            "/api/create-invite/",
            data={"tenant_id": str(self.tenant.id), "role": "member"},
            format="json",
        )
        self.assertEqual(resp_mem.status_code, 200)

        # 3. Energy User Admin CANNOT invite an Energy Admin
        resp_forbidden = self.client.post(
            "/api/create-invite/",
            data={"tenant_id": str(self.tenant.id), "role": "admin"},
            format="json",
        )
        self.assertEqual(resp_forbidden.status_code, 403)

        # 4. Community Member cannot invite anyone
        self.client.force_login(self.community_member)
        resp_member_fail = self.client.post(
            "/api/create-invite/",
            data={"tenant_id": str(self.tenant.id), "role": "member"},
            format="json",
        )
        self.assertEqual(resp_member_fail.status_code, 403)

    def test_update_member_role_hierarchy(self):
        # 1. Energy Admin can update member to helpdesk
        self.client.force_login(self.energy_admin)
        resp = self.client.post(
            "/api/update-role/",
            data={
                "tenant_id": str(self.tenant.id),
                "user_id": str(self.community_member.id),
                "role": "helpdesk",
            },
            format="json",
        )
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.json()["role"], "helpdesk")

        # 2. Energy User Admin can promote member to auditor
        self.client.force_login(self.energy_user_admin)
        resp_aud = self.client.post(
            "/api/update-role/",
            data={
                "tenant_id": str(self.tenant.id),
                "user_id": str(self.community_member.id),
                "role": "auditor",
            },
            format="json",
        )
        self.assertEqual(resp_aud.status_code, 200)

        # 3. Energy User Admin CANNOT promote member to Admin
        resp_admin_fail = self.client.post(
            "/api/update-role/",
            data={
                "tenant_id": str(self.tenant.id),
                "user_id": str(self.community_member.id),
                "role": "admin",
            },
            format="json",
        )
        self.assertEqual(resp_admin_fail.status_code, 403)

        # 4. Energy User Admin CANNOT modify Energy Admin's role
        resp_demote_admin = self.client.post(
            "/api/update-role/",
            data={
                "tenant_id": str(self.tenant.id),
                "user_id": str(self.energy_admin.id),
                "role": "member",
            },
            format="json",
        )
        self.assertEqual(resp_demote_admin.status_code, 403)

    def test_avatar_save_and_me_retrieval(self):
        self.client.force_login(self.community_member)

        # 1. Post avatar and billing_email update
        resp = self.client.post(
            "/api/profile/",
            data={
                "first_name": "Max",
                "last_name": "Mustermann",
                "avatar": "solar_pro",
                "company_name": "Sonnenenergie GmbH",
                "billing_name": "Buchhaltung",
                "billing_email": "invoices@sonnenenergie.de",
                "vat_id": "DE987654321",
                "street": "Sonnenstraße",
                "house_number": "10",
                "postal_code": "10115",
                "city": "Berlin",
                "country": "DE",
            },
            format="json",
        )
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.json()["avatar"], "solar_pro")

        # 2. Verify via /api/profile/
        resp_prof = self.client.get("/api/profile/")
        self.assertEqual(resp_prof.status_code, 200)
        self.assertEqual(resp_prof.json()["avatar"], "solar_pro")
        self.assertEqual(resp_prof.json()["billing_email"], "invoices@sonnenenergie.de")
        self.assertEqual(resp_prof.json()["company_name"], "Sonnenenergie GmbH")

        # 3. Verify via /api/auth/me/
        resp_me = self.client.get("/api/auth/me/")
        self.assertEqual(resp_me.status_code, 200)
        self.assertEqual(resp_me.json()["avatar"], "solar_pro")
        self.assertEqual(resp_me.json()["profile"]["avatar"], "solar_pro")
        self.assertEqual(resp_me.json()["profile"]["billing_email"], "invoices@sonnenenergie.de")
        self.assertEqual(resp_me.json()["profile"]["company_name"], "Sonnenenergie GmbH")

    def test_email_change_multilingual_dispatch(self):
        from django.core import mail
        from accounts.models import UserSettings

        # Set user language to English
        settings_obj, _ = UserSettings.objects.get_or_create(user=self.community_member)
        settings_obj.language = "en"
        settings_obj.save()

        self.client.force_login(self.community_member)
        mail.outbox = []

        resp = self.client.post(
            "/api/change-email/",
            data={"new_email": "new.english.member@quartier-sonne.de"},
            format="json",
        )
        self.assertEqual(resp.status_code, 200)

        # Should send 2 emails: verification to new address + security alert to old address
        self.assertEqual(len(mail.outbox), 2)

        # Verification email in English
        verification_mail = mail.outbox[0]
        self.assertIn("Confirm your new email address for Sharegy", verification_mail.subject)
        self.assertEqual(verification_mail.to, ["new.english.member@quartier-sonne.de"])
        self.assertIn("30 minutes", verification_mail.body)

        # Security alert in English
        alert_mail = mail.outbox[1]
        self.assertIn("Security Alert", alert_mail.subject)
        self.assertEqual(alert_mail.to, ["member@quartier-sonne.de"])


