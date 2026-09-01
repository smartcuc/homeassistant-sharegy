from decimal import Decimal
from django.test import TestCase
from django.utils import timezone
from rest_framework.test import APIClient

from accounts.models import User, TenantMembership
from core.models import Tenant, Meter, BalanceSlot
from billing.models import CommunityTariff, CommunityAnnouncement, CommunityMonthlyStatement


class MultiCommunityManagementTests(TestCase):
    """
    Tests für das zentrale Multi-Community-Management:
    - Portfolio Overview (Superadmin & Manager)
    - Drilldown-Ansicht für einzelne Gemeinschaften
    - Community-Ankündigungen & Kommunikation
    - Einstellungs-Updates
    """

    def setUp(self):
        self.client = APIClient()

        # 1. Users
        self.admin_user = User.objects.create_superuser(
            username="admin", email="admin@sharegy.local", password="password123"
        )
        self.manager_user = User.objects.create_user(
            username="manager", email="manager@bonn.de", password="password123"
        )
        self.member_user = User.objects.create_user(
            username="member", email="member@bonn.de", password="password123"
        )

        # 2. Tenants (Communities)
        self.tenant_bonn = Tenant.objects.create(name="Bonn Energy Sharing", slug="bonn-share", is_public=True)
        self.tenant_koeln = Tenant.objects.create(name="Köln Solar Quartier", slug="koeln-solar", is_public=True)

        # 3. Memberships
        self.m_manager = TenantMembership.objects.create(
            tenant=self.tenant_bonn, user=self.manager_user, role="admin", is_active=True
        )
        self.m_member = TenantMembership.objects.create(
            tenant=self.tenant_bonn, user=self.member_user, role="member", is_active=True
        )

        # 4. Zähler
        self.meter_bonn = Meter.objects.create(
            tenant=self.tenant_bonn,
            serial_number="BONN-METER-01",
            owner_membership=self.m_member,
        )

        # 5. Tarife
        self.tariff_bonn = CommunityTariff.objects.create(
            tenant=self.tenant_bonn,
            name="Bonn Standard Sharing 2026",
            sharing_price_ct_kwh=Decimal("12.00"),
            producer_payout_ct_kwh=Decimal("10.00"),
            community_fee_ct_kwh=Decimal("2.00"),
            is_active=True,
            valid_from=timezone.now().date(),
        )

        # 6. BalanceSlots
        now = timezone.now()
        BalanceSlot.objects.create(
            tenant=self.tenant_bonn,
            meter=self.meter_bonn,
            period_start=now,
            consumption_kwh=Decimal("15.00"),
            generation_kwh=Decimal("20.00"),
            self_consumption_kwh=Decimal("15.00"),
            grid_import_kwh=Decimal("0.00"),
            grid_export_kwh=Decimal("5.00"),
        )

    def test_portfolio_overview_as_admin(self):
        """Prüft Portfolio-Übersicht für Superadmin."""
        self.client.force_authenticate(user=self.admin_user)
        response = self.client.get("/api/billing/communities/overview/")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        
        self.assertIn("portfolio", data)
        self.assertIn("communities", data)
        self.assertEqual(data["portfolio"]["total_communities"], 2)
        self.assertGreaterEqual(len(data["communities"]), 2)
        
        bonn = next((c for c in data["communities"] if c["slug"] == "bonn-share"), None)
        self.assertIsNotNone(bonn)
        self.assertEqual(bonn["members_count"], 2)
        self.assertEqual(bonn["meters_count"], 1)
        self.assertEqual(bonn["month_produced_kwh"], 20.0)
        self.assertEqual(bonn["month_consumed_kwh"], 15.0)
        self.assertEqual(bonn["month_shared_kwh"], 15.0)
        self.assertEqual(bonn["autarky_pct"], 100.0)

    def test_community_drilldown_view(self):
        """Prüft detaillierte Drilldown-Ansicht für eine Community."""
        self.client.force_authenticate(user=self.manager_user)
        response = self.client.get(f"/api/billing/communities/{self.tenant_bonn.id}/drilldown/")
        self.assertEqual(response.status_code, 200)
        data = response.json()

        self.assertEqual(data["community"]["name"], "Bonn Energy Sharing")
        self.assertEqual(len(data["members"]), 2)
        self.assertIsNotNone(data["active_tariff"])
        self.assertEqual(data["active_tariff"]["name"], "Bonn Standard Sharing 2026")

    def test_community_announcements_flow(self):
        """Prüft Erstellung und Abruf von Community-Rundschreiben."""
        self.client.force_authenticate(user=self.manager_user)
        
        # POST
        post_res = self.client.post(
            f"/api/billing/communities/{self.tenant_bonn.id}/announcements/",
            {
                "title": "Wartungsfenster Zählerwechsel",
                "message": "Am kommenden Dienstag werden die neuen IMSys-Gateways montiert.",
                "category": "maintenance",
            },
            format="json",
        )
        self.assertEqual(post_res.status_code, 201)

        # GET
        get_res = self.client.get(f"/api/billing/communities/{self.tenant_bonn.id}/announcements/")
        self.assertEqual(get_res.status_code, 200)
        items = get_res.json()["announcements"]
        self.assertEqual(len(items), 1)
        self.assertEqual(items[0]["title"], "Wartungsfenster Zählerwechsel")

    def test_community_settings_update(self):
        """Prüft Aktualisierung der Community-Einstellungen."""
        self.client.force_authenticate(user=self.manager_user)
        res = self.client.post(
            f"/api/billing/communities/{self.tenant_bonn.id}/settings/",
            {
                "name": "Bonn Solar Quartier Plus",
                "primary_color": "#10b981",
                "latitude": 50.7374,
                "longitude": 7.0982,
            },
            format="json",
        )
        self.assertEqual(res.status_code, 200)
        self.tenant_bonn.refresh_from_db()
        self.assertEqual(self.tenant_bonn.name, "Bonn Solar Quartier Plus")
        self.assertEqual(self.tenant_bonn.primary_color, "#10b981")
