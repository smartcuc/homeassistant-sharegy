from decimal import Decimal
from django.test import TestCase
from django.utils import timezone
from rest_framework.test import APIClient

from accounts.models import User, TenantMembership, UserProfile
from core.models import Tenant, Meter
from billing.models import CommunityTariff, CommunityMonthlyStatement


class CommunityExportsTests(TestCase):
    """
    Tests für PDF-Monatsabrechnungsnachweise und CSV/XLSX/XML-Exporte.
    """

    def setUp(self):
        self.client = APIClient()

        self.admin_user = User.objects.create_superuser(
            username="admin", email="admin@sharegy.local", password="password123"
        )
        self.member_user = User.objects.create_user(
            username="max", email="max.mustermann@bonn.de", password="password123", first_name="Max", last_name="Mustermann"
        )
        self.other_user = User.objects.create_user(
            username="other", email="other@bonn.de", password="password123"
        )

        UserProfile.objects.create(
            user=self.member_user,
            street="Musterstraße",
            house_number="42",
            postal_code="53111",
            city="Bonn",
        )

        self.tenant = Tenant.objects.create(name="Bonn Energy Sharing", slug="bonn-share", is_public=True)
        self.m_member = TenantMembership.objects.create(tenant=self.tenant, user=self.member_user, role="member", is_active=True)
        self.m_admin = TenantMembership.objects.create(tenant=self.tenant, user=self.admin_user, role="admin", is_active=True)

        self.tariff = CommunityTariff.objects.create(
            tenant=self.tenant,
            name="Bonn Standard Sharing",
            sharing_price_ct_kwh=Decimal("12.00"),
            producer_payout_ct_kwh=Decimal("10.00"),
            community_fee_ct_kwh=Decimal("2.00"),
            is_active=True,
            valid_from=timezone.now().date(),
        )

        self.statement = CommunityMonthlyStatement.objects.create(
            tenant=self.tenant,
            membership=self.m_member,
            user=self.member_user,
            tariff=self.tariff,
            statement_number="SHR-BONN-202608-MB0001",
            period_start=timezone.now().date().replace(day=1),
            period_end=timezone.now().date(),
            produced_total_kwh=Decimal("120.50"),
            consumed_total_kwh=Decimal("80.00"),
            shared_imported_kwh=Decimal("60.00"),
            shared_exported_kwh=Decimal("100.00"),
            grid_residual_import_kwh=Decimal("20.00"),
            charge_shared_import_eur=Decimal("7.20"),
            credit_shared_export_eur=Decimal("10.00"),
            community_fee_eur=Decimal("1.20"),
            net_balance_eur=Decimal("1.60"),
            status="finalized",
        )

    def test_pdf_download_as_owner(self):
        """Mitglied kann sein eigenes Abrechnungs-PDF herunterladen."""
        self.client.force_authenticate(user=self.member_user)
        response = self.client.get(f"/api/billing/community/statements/{self.statement.id}/pdf/")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response["Content-Type"], "application/pdf")
        self.assertIn("attachment", response["Content-Disposition"])
        self.assertGreater(len(response.content), 1000)

    def test_pdf_download_unauthorized(self):
        """Fremder User darf fremdes Statement nicht herunterladen."""
        self.client.force_authenticate(user=self.other_user)
        response = self.client.get(f"/api/billing/community/statements/{self.statement.id}/pdf/")
        self.assertEqual(response.status_code, 403)

    def test_export_statements_csv(self):
        """Prüft CSV-Export von Abrechnungsdaten."""
        self.client.force_authenticate(user=self.admin_user)
        response = self.client.get(f"/api/billing/community/statements/export/?export_format=csv&tenant_id={self.tenant.id}")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response["Content-Type"], "text/csv; charset=utf-8")
        content = response.content.decode("utf-8")
        self.assertIn("SHR-BONN-202608-MB0001", content)
        self.assertIn("max.mustermann@bonn.de", content)
        self.assertIn("Gutschrift", content)

    def test_export_statements_xlsx(self):
        """Prüft Excel XLSX-Export von Abrechnungsdaten."""
        self.client.force_authenticate(user=self.admin_user)
        response = self.client.get(f"/api/billing/community/statements/export/?export_format=xlsx&tenant_id={self.tenant.id}")
        self.assertEqual(response.status_code, 200)
        self.assertIn("openxmlformats", response["Content-Type"])
        self.assertGreater(len(response.content), 2000)

    def test_export_statements_xml(self):
        """Prüft XML-Export für ERP-Systeme."""
        self.client.force_authenticate(user=self.admin_user)
        response = self.client.get(f"/api/billing/community/statements/export/?export_format=xml&tenant_id={self.tenant.id}")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response["Content-Type"], "application/xml; charset=utf-8")
        content = response.content.decode("utf-8")
        self.assertIn("<EnergySharingSettlementExport", content)
        self.assertIn('number="SHR-BONN-202608-MB0001"', content)

