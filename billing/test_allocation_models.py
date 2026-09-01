"""
billing/test_allocation_models.py

Unit- und Integrationstests für Beteiligungsquoten & Allokationsmodelle (Säule 2):
1. Dynamische Allokation (Verbrauchsproportional)
2. Statische Allokation (Feste Beteiligungsquoten / MEA)
3. Hybride Allokation (Stufe 1 Quote + Stufe 2 Überlauf)
4. REST-APIs für Member Shares & Bulk-Normierung
5. Vergleichs- und Simulations-Engine
"""

from decimal import Decimal
from datetime import datetime, date
from django.test import TestCase
from django.utils import timezone
from rest_framework.test import APIClient

from accounts.models import User, TenantMembership
from core.models import Tenant, Meter, BalanceSlot
from billing.models import CommunityTariff, CommunityMemberShare, CommunityMonthlyStatement
from billing.services_sharing_settlement import (
    calculate_sharing_allocation_for_slot,
    calculate_monthly_community_statements,
    get_allocation_comparison_preview,
)


class AllocationModelsEngineTestCase(TestCase):
    def setUp(self):
        self.tenant = Tenant.objects.create(name="WEG Rheinquartier", slug="weg-rhein")
        self.user_a = User.objects.create_user(username="alice_rhein", email="alice@rhein.de", password="password123")
        self.user_b = User.objects.create_user(username="bob_rhein", email="bob@rhein.de", password="password123")
        self.user_c = User.objects.create_user(username="carol_rhein", email="carol@rhein.de", password="password123")

        self.mem_a = TenantMembership.objects.create(tenant=self.tenant, user=self.user_a, role="member")
        self.mem_b = TenantMembership.objects.create(tenant=self.tenant, user=self.user_b, role="member")
        self.mem_c = TenantMembership.objects.create(tenant=self.tenant, user=self.user_c, role="member")

        # Quoten: Alice = 50% (500/1000 MEA), Bob = 30% (300/1000 MEA), Carol = 20% (200/1000 MEA)
        self.share_a = CommunityMemberShare.objects.create(
            tenant=self.tenant, membership=self.mem_a, user=self.user_a,
            share_percent=Decimal("50.0000"), mea_numerator=500, mea_denominator=1000
        )
        self.share_b = CommunityMemberShare.objects.create(
            tenant=self.tenant, membership=self.mem_b, user=self.user_b,
            share_percent=Decimal("30.0000"), mea_numerator=300, mea_denominator=1000
        )
        self.share_c = CommunityMemberShare.objects.create(
            tenant=self.tenant, membership=self.mem_c, user=self.user_c,
            share_percent=Decimal("20.0000"), mea_numerator=200, mea_denominator=1000
        )

        self.shares_map = {
            str(self.mem_a.id): Decimal("0.50"),
            str(self.mem_b.id): Decimal("0.30"),
            str(self.mem_c.id): Decimal("0.20"),
        }

    def test_dynamic_allocation_proportional_to_consumption(self):
        """
        Dynamisches Modell: 10 kWh Erzeugung, Verbräuche A=2 kWh, B=6 kWh, C=2 kWh (Summe=10 kWh)
        -> Alle erhalten 100% Deckung.
        Bei 5 kWh Erzeugung -> A=1 kWh, B=3 kWh, C=1 kWh (proportional zum Verbrauch).
        """
        consumption = {
            str(self.mem_a.id): Decimal("2.0"),
            str(self.mem_b.id): Decimal("6.0"),
            str(self.mem_c.id): Decimal("2.0"),
        }
        
        # Fall 1: Generation = 5 kWh
        alloc = calculate_sharing_allocation_for_slot(
            consumption_by_member=consumption,
            total_generation=Decimal("5.0"),
            allocation_model="dynamic",
            member_shares_map=self.shares_map,
        )

        self.assertEqual(alloc["shared_by_member"][str(self.mem_a.id)], Decimal("1.0"))
        self.assertEqual(alloc["shared_by_member"][str(self.mem_b.id)], Decimal("3.0"))
        self.assertEqual(alloc["shared_by_member"][str(self.mem_c.id)], Decimal("1.0"))
        self.assertEqual(alloc["total_shared"], Decimal("5.0"))
        self.assertEqual(alloc["grid_export_total"], Decimal("0.0"))

    def test_static_allocation_fixed_shares(self):
        """
        Statisches Modell: Generation = 10 kWh.
        Zuweisung nach Quote: A(50%)=5 kWh, B(30%)=3 kWh, C(20%)=2 kWh.
        Tatsächlicher Verbrauch: A=2 kWh, B=6 kWh, C=2 kWh.
        Ergebnis:
        - Alice: Verbrauch 2 kWh < Quote 5 kWh -> nutzt 2 kWh (3 kWh ungenutzt)
        - Bob: Verbrauch 6 kWh > Quote 3 kWh -> nutzt 3 kWh (Rest 3 kWh Netzbezug)
        - Carol: Verbrauch 2 kWh == Quote 2 kWh -> nutzt 2 kWh
        - Gesamt geteilt = 2 + 3 + 2 = 7 kWh.
        - Netzeinspeisung = 3 kWh (Alice's ungenutzte Quote).
        """
        consumption = {
            str(self.mem_a.id): Decimal("2.0"),
            str(self.mem_b.id): Decimal("6.0"),
            str(self.mem_c.id): Decimal("2.0"),
        }

        alloc = calculate_sharing_allocation_for_slot(
            consumption_by_member=consumption,
            total_generation=Decimal("10.0"),
            allocation_model="static",
            member_shares_map=self.shares_map,
        )

        self.assertEqual(alloc["shared_by_member"][str(self.mem_a.id)], Decimal("2.0"))
        self.assertEqual(alloc["shared_by_member"][str(self.mem_b.id)], Decimal("3.0"))
        self.assertEqual(alloc["shared_by_member"][str(self.mem_c.id)], Decimal("2.0"))
        self.assertEqual(alloc["total_shared"], Decimal("7.0"))
        self.assertEqual(alloc["grid_export_total"], Decimal("3.0"))
        self.assertEqual(alloc["grid_import_by_member"][str(self.mem_b.id)], Decimal("3.0"))

    def test_hybrid_allocation_tier1_quota_tier2_overflow(self):
        """
        Hybrides Modell:
        Generation = 10 kWh.
        Verbrauch: A=2 kWh, B=6 kWh, C=2 kWh.
        - Stufe 1 (Quote): A=2 (3 Surplus), B=3 (3 Restbedarf), C=2 (0 Restbedarf).
        - Stufe 2 (Überlauf): 3 kWh Surplus von A geht an Bob (der noch 3 kWh Bedarf hat)!
        Ergebnis:
        - Alice: 2 kWh gedeckt
        - Bob: 3 kWh (Quote) + 3 kWh (Überlauf) = 6 kWh voll gedeckt!
        - Carol: 2 kWh gedeckt
        - Gesamt geteilt = 10.0 kWh (100% Community-Nutzung, 0 kWh Netzeinspeisung)!
        """
        consumption = {
            str(self.mem_a.id): Decimal("2.0"),
            str(self.mem_b.id): Decimal("6.0"),
            str(self.mem_c.id): Decimal("2.0"),
        }

        alloc = calculate_sharing_allocation_for_slot(
            consumption_by_member=consumption,
            total_generation=Decimal("10.0"),
            allocation_model="hybrid",
            member_shares_map=self.shares_map,
        )

        self.assertEqual(alloc["shared_by_member"][str(self.mem_a.id)], Decimal("2.0"))
        self.assertEqual(alloc["shared_by_member"][str(self.mem_b.id)], Decimal("6.0"))
        self.assertEqual(alloc["shared_by_member"][str(self.mem_c.id)], Decimal("2.0"))
        self.assertEqual(alloc["total_shared"], Decimal("10.0"))
        self.assertEqual(alloc["grid_export_total"], Decimal("0.0"))
        self.assertEqual(alloc["grid_import_by_member"][str(self.mem_b.id)], Decimal("0.0"))


class MemberSharesAPITestCase(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.tenant = Tenant.objects.create(name="Quartier Sonnenfeld", slug="sonnenfeld")
        self.admin_user = User.objects.create_user(username="admin_sonnenfeld", email="admin@sonnenfeld.de", password="password123")
        self.member_user = User.objects.create_user(username="member_sonnenfeld", email="member@sonnenfeld.de", password="password123")

        self.admin_mem = TenantMembership.objects.create(tenant=self.tenant, user=self.admin_user, role="admin")
        self.user_mem = TenantMembership.objects.create(tenant=self.tenant, user=self.member_user, role="member")

        self.tariff = CommunityTariff.objects.create(
            tenant=self.tenant,
            name="Sonnenfeld Standard",
            allocation_model="dynamic",
            sharing_price_ct_kwh=Decimal("14.00"),
            producer_payout_ct_kwh=Decimal("10.00"),
            community_fee_ct_kwh=Decimal("2.00"),
        )

    def test_get_member_shares_list(self):
        self.client.force_authenticate(user=self.admin_user)
        response = self.client.get(f"/api/billing/community/shares/?tenant_id={self.tenant.id}")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(len(data["shares"]), 2)
        self.assertFalse(data["is_balanced_100"])

    def test_create_and_update_member_share(self):
        self.client.force_authenticate(user=self.admin_user)
        payload = {
            "tenant_id": str(self.tenant.id),
            "membership_id": str(self.user_mem.id),
            "mea_numerator": 450,
            "mea_denominator": 1000,
            "assigned_kwp": "4.5",
        }
        response = self.client.post("/api/billing/community/shares/", payload, format="json")
        self.assertEqual(response.status_code, 201)
        data = response.json()["share"]
        self.assertEqual(data["share_percent"], 45.0)
        self.assertEqual(data["mea_numerator"], 450)

    def test_bulk_shares_update_with_normalization(self):
        self.client.force_authenticate(user=self.admin_user)
        payload = {
            "tenant_id": str(self.tenant.id),
            "normalize_to_100": True,
            "shares": [
                {
                    "membership_id": str(self.admin_mem.id),
                    "share_percent": 60,
                    "mea_numerator": 600,
                },
                {
                    "membership_id": str(self.user_mem.id),
                    "share_percent": 60,  # 60 + 60 = 120 -> normiert auf 50% / 50%
                    "mea_numerator": 600,
                },
            ]
        }
        response = self.client.post("/api/billing/community/shares/bulk/", payload, format="json")
        self.assertEqual(response.status_code, 200)

        # Prüfen, ob beide auf 50.0000% normiert wurden
        share_admin = CommunityMemberShare.objects.get(membership=self.admin_mem)
        share_user = CommunityMemberShare.objects.get(membership=self.user_mem)
        self.assertEqual(share_admin.share_percent, Decimal("50.0000"))
        self.assertEqual(share_user.share_percent, Decimal("50.0000"))

    def test_allocation_preview_endpoint(self):
        self.client.force_authenticate(user=self.admin_user)
        response = self.client.get(f"/api/billing/community/allocation-preview/?tenant_id={self.tenant.id}&year=2026&month=8")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn("comparison", data)
        self.assertIn("dynamic", data["comparison"])
        self.assertIn("static", data["comparison"])
        self.assertIn("hybrid", data["comparison"])
