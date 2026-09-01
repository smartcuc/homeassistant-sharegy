"""
billing/test_community_tariffs_and_settlement.py

Tests für Sharing-Tarife, Cent/kWh-Vergütungen und monatliche Abrechnungsnachweise.
"""

from decimal import Decimal
from datetime import date, timedelta
from django.test import TestCase
from django.utils import timezone
from rest_framework.test import APIClient

from accounts.models import User, TenantMembership
from core.models import Tenant, Meter, BalanceSlot
from billing.models import CommunityTariff, CommunityMonthlyStatement
from billing.services_sharing_settlement import (
    get_active_community_tariff,
    calculate_monthly_community_statements,
)


class CommunityTariffsAndSettlementTests(TestCase):
    def setUp(self):
        self.client = APIClient()

        # 1. Tenants anlegen
        self.tenant = Tenant.objects.create(name="Bonn-Share Solar", slug="bonn-share")
        self.other_tenant = Tenant.objects.create(name="Köln Solar", slug="koeln-solar")

        # 2. Users & Memberships anlegen
        self.admin_user = User.objects.create_user(username="admin@bonn.de", email="admin@bonn.de", password="pw")
        self.producer_user = User.objects.create_user(username="producer@bonn.de", email="producer@bonn.de", password="pw")
        self.consumer_user = User.objects.create_user(username="consumer@bonn.de", email="consumer@bonn.de", password="pw")
        self.other_user = User.objects.create_user(username="stranger@koeln.de", email="stranger@koeln.de", password="pw")

        self.m_admin = TenantMembership.objects.create(tenant=self.tenant, user=self.admin_user, role="admin", is_active=True)
        self.m_producer = TenantMembership.objects.create(tenant=self.tenant, user=self.producer_user, role="member", is_active=True)
        self.m_consumer = TenantMembership.objects.create(tenant=self.tenant, user=self.consumer_user, role="member", is_active=True)
        self.m_other = TenantMembership.objects.create(tenant=self.other_tenant, user=self.other_user, role="member", is_active=True)

        # 3. Zähler anlegen (über Membership)
        self.meter_producer = Meter.objects.create(
            tenant=self.tenant,
            serial_number="MSB-BONN-PROD-01",
            owner_membership=self.m_producer,
        )
        self.meter_consumer = Meter.objects.create(
            tenant=self.tenant,
            serial_number="MSB-BONN-CONS-01",
            owner_membership=self.m_consumer,
        )

        # 4. Tarif anlegen (12 Ct Bezug, 10 Ct Vergütung, 2 Ct Umlage)
        self.tariff = CommunityTariff.objects.create(
            tenant=self.tenant,
            name="Bonn Solar Standard 2026",
            sharing_price_ct_kwh=Decimal("12.00"),
            producer_payout_ct_kwh=Decimal("10.00"),
            community_fee_ct_kwh=Decimal("2.00"),
            valid_from=timezone.now() - timedelta(days=60),
            is_active=True,
        )

        # 5. BalanceSlots für den Monat August 2026 erzeugen
        slot_dt = timezone.make_aware(timezone.datetime(2026, 8, 15, 12, 0, 0))
        # Producer erzeugt 100 kWh, speist 20 kWh ins Netz ein -> 80 kWh an Community abgegeben
        BalanceSlot.objects.create(
            meter=self.meter_producer,
            tenant=self.tenant,
            period_start=slot_dt,
            consumption_kwh=Decimal("0.0"),
            generation_kwh=Decimal("100.0"),
            self_consumption_kwh=Decimal("0.0"),
            grid_import_kwh=Decimal("0.0"),
            grid_export_kwh=Decimal("20.0"),
        )
        # Consumer verbraucht 60 kWh, bezieht 10 kWh Reststrom -> 50 kWh von Community bezogen
        BalanceSlot.objects.create(
            meter=self.meter_consumer,
            tenant=self.tenant,
            period_start=slot_dt,
            consumption_kwh=Decimal("60.0"),
            generation_kwh=Decimal("0.0"),
            self_consumption_kwh=Decimal("0.0"),
            grid_import_kwh=Decimal("10.0"),
            grid_export_kwh=Decimal("0.0"),
        )

    def test_tariff_get_and_post_api(self):
        """Prüft Abruf von Tarifen und Neuanlage durch Admin."""
        # Consumer darf Tarife nur lesen, nicht erstellen
        self.client.force_authenticate(user=self.consumer_user)
        res_get = self.client.get("/api/billing/community/tariffs/", HTTP_X_TENANT_ID=str(self.tenant.id))
        self.assertEqual(res_get.status_code, 200)
        self.assertEqual(res_get.data["active_tariff"]["name"], "Bonn Solar Standard 2026")
        self.assertEqual(res_get.data["active_tariff"]["sharing_price_ct_kwh"], 12.0)

        # Consumer POST -> 403 Forbidden
        res_post_forbidden = self.client.post(
            "/api/billing/community/tariffs/",
            {"name": "Hacker Tarif", "sharing_price_ct_kwh": "1.00"},
            HTTP_X_TENANT_ID=str(self.tenant.id),
        )
        self.assertEqual(res_post_forbidden.status_code, 403)

        # Admin POST -> 201 Created
        self.client.force_authenticate(user=self.admin_user)
        res_post = self.client.post(
            "/api/billing/community/tariffs/",
            {
                "name": "Bonn Solar Sommer 2026",
                "sharing_price_ct_kwh": "11.50",
                "producer_payout_ct_kwh": "9.50",
                "community_fee_ct_kwh": "2.00",
            },
            HTTP_X_TENANT_ID=str(self.tenant.id),
        )
        self.assertEqual(res_post.status_code, 201)
        self.assertEqual(res_post.data["tariff"]["name"], "Bonn Solar Sommer 2026")

    def test_monthly_settlement_calculation_and_statements_api(self):
        """Prüft die monatliche Abrechnungsberechnung und API-Sichtbarkeit."""
        # 1. Abrechnung für August 2026 durchführen
        statements = calculate_monthly_community_statements(self.tenant, 2026, 8)
        self.assertGreaterEqual(len(statements), 2)

        # Producer Abrechnung prüfen:
        # 80 kWh geteilt * 10 Ct/kWh = 8,00 € Gutschrift
        producer_stmt = CommunityMonthlyStatement.objects.get(membership=self.m_producer, period_start=date(2026, 8, 1))
        self.assertEqual(producer_stmt.produced_total_kwh, Decimal("100.0"))
        self.assertEqual(producer_stmt.shared_exported_kwh, Decimal("80.0"))
        self.assertEqual(producer_stmt.credit_shared_export_eur, Decimal("8.00"))
        self.assertEqual(producer_stmt.net_balance_eur, Decimal("8.00"))  # Reiner Erzeuger = +8,00 €

        # Consumer Abrechnung prüfen:
        # 50 kWh bezogen * 12 Ct/kWh = 6,00 € Bezugskosten + 50 * 2 Ct/kWh = 1,00 € Umlage
        # Netto-Saldo: -7,00 € (Nachzahlung)
        consumer_stmt = CommunityMonthlyStatement.objects.get(membership=self.m_consumer, period_start=date(2026, 8, 1))
        self.assertEqual(consumer_stmt.consumed_total_kwh, Decimal("60.0"))
        self.assertEqual(consumer_stmt.shared_imported_kwh, Decimal("50.0"))
        self.assertEqual(consumer_stmt.charge_shared_import_eur, Decimal("6.00"))
        self.assertEqual(consumer_stmt.community_fee_eur, Decimal("1.00"))
        self.assertEqual(consumer_stmt.net_balance_eur, Decimal("-7.00"))

        # 2. Consumer ruft API ab -> sieht NUR sein eigenes Statement
        self.client.force_authenticate(user=self.consumer_user)
        res = self.client.get("/api/billing/community/statements/", HTTP_X_TENANT_ID=str(self.tenant.id))
        self.assertEqual(res.status_code, 200)
        self.assertEqual(len(res.data["statements"]), 1)
        self.assertEqual(res.data["statements"][0]["net_balance_eur"], -7.0)
        self.assertFalse(res.data["statements"][0]["is_payout"])

        # 3. Admin ruft API ab -> sieht ALLE Statements der Community
        self.client.force_authenticate(user=self.admin_user)
        res_admin = self.client.get("/api/billing/community/statements/", HTTP_X_TENANT_ID=str(self.tenant.id))
        self.assertEqual(res_admin.status_code, 200)
        self.assertGreaterEqual(len(res_admin.data["statements"]), 2)
