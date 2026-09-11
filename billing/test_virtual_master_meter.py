import uuid
from decimal import Decimal
from datetime import date, datetime, time, timedelta
from django.test import TestCase
from django.contrib.auth import get_user_model
from django.utils import timezone
from rest_framework.test import APIClient

from core.models import Tenant, Meter, BalanceSlot
from accounts.models import TenantMembership
from billing.models import CommunityTariff, CommunityMemberShare
from billing.services_virtual_meter import calculate_virtual_master_meter_timeline
from billing.tasks import generate_monthly_community_settlements_and_pdfs

User = get_user_model()


class VirtualMasterMeterAndSettlementTests(TestCase):
    def setUp(self):
        self.user_owner = User.objects.create_user(
            username="owner_user", email="owner@sharegy.de", password="password123"
        )
        self.user_tenant1 = User.objects.create_user(
            username="tenant1_user", email="tenant1@sharegy.de", password="password123"
        )
        self.user_tenant2 = User.objects.create_user(
            username="tenant2_user", email="tenant2@sharegy.de", password="password123"
        )

        self.tenant = Tenant.objects.create(
            name="MFH Sonnenallee 42",
            slug="mfh-sonnenallee-42",
        )

        self.m_owner = TenantMembership.objects.create(
            user=self.user_owner, tenant=self.tenant, role="owner", is_active=True
        )
        self.m_tenant1 = TenantMembership.objects.create(
            user=self.user_tenant1, tenant=self.tenant, role="member", is_active=True
        )
        self.m_tenant2 = TenantMembership.objects.create(
            user=self.user_tenant2, tenant=self.tenant, role="member", is_active=True
        )

        self.tariff = CommunityTariff.objects.create(
            tenant=self.tenant,
            name="MFH Quartierstarif",
            allocation_model=CommunityTariff.ALLOCATION_DYNAMIC,
            sharing_price_ct_kwh=Decimal("15.00"),
            producer_payout_ct_kwh=Decimal("12.00"),
            community_fee_ct_kwh=Decimal("1.50"),
            is_active=True,
        )

        self.meter = Meter.objects.create(
            tenant=self.tenant,
            owner_membership=self.m_owner,
            serial_number="METER-MFH-001",
            meter_type="electricity",
        )

        # 15-Minuten Balance Slots anlegen für den virtuellen Summenzähler
        today = timezone.now().date()
        base_dt = timezone.make_aware(datetime.combine(today, time(12, 0)))

        for i in range(4):
            slot_start = base_dt + timedelta(minutes=15 * i)
            BalanceSlot.objects.create(
                tenant=self.tenant,
                meter=self.meter,
                period_start=slot_start,
                generation_kwh=Decimal("8.000"),
                consumption_kwh=Decimal("5.000"),
                self_consumption_kwh=Decimal("5.000"),
                grid_import_kwh=Decimal("0.000"),
                grid_export_kwh=Decimal("3.000"),
            )

        self.client = APIClient()

    def test_calculate_virtual_master_meter_timeline(self):
        today = timezone.now().date()
        res = calculate_virtual_master_meter_timeline(
            tenant=self.tenant,
            start_date=today,
            end_date=today,
        )

        self.assertEqual(res["tenant"]["name"], "MFH Sonnenallee 42")
        self.assertEqual(res["period"]["slots_count"], 4)
        self.assertEqual(res["totals"]["total_generation_kwh"], 32.0)
        self.assertEqual(res["totals"]["total_consumption_kwh"], 20.0)
        self.assertAlmostEqual(res["totals"]["total_shared_kwh"], 20.0, places=2)
        self.assertAlmostEqual(res["totals"]["total_grid_export_kwh"], 12.0, places=2)
        self.assertAlmostEqual(res["totals"]["self_sufficiency_rate_pct"], 100.0, places=1)
        self.assertEqual(len(res["members"]), 3)

    def test_virtual_meter_api_endpoint(self):
        self.client.force_authenticate(user=self.user_owner)
        url = f"/api/billing/community/virtual-meter/?tenant_id={self.tenant.id}"
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertIn("timeline", data)
        self.assertIn("totals", data)
        self.assertIn("self_sufficiency_rate_pct", data["totals"])

    def test_monthly_settlement_and_pdf_generation_task(self):
        today = timezone.now().date()
        result = generate_monthly_community_settlements_and_pdfs(
            year=today.year,
            month=today.month,
            tenant_id=str(self.tenant.id),
        )

        self.assertEqual(result["status"], "success")
        self.assertEqual(result["tenants_settled"], 1)
        self.assertGreaterEqual(result["statements_generated"], 3)
        self.assertGreaterEqual(result["pdfs_rendered"], 3)
