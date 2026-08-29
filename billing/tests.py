###################
# billing/tests.py
###################

from decimal import Decimal
from datetime import datetime, timezone as dt_timezone

from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from django.utils import timezone

from core.models import Meter, AggregatedReading, BalanceSlot, Tenant
from billing.models import EMSSubscription, EMSInvoice
from billing.services_balance import compute_balance_range
from billing.services_subscription import (
    get_or_create_subscription,
    change_subscription_plan,
    update_billing_address,
    cancel_subscription,
    reactivate_subscription,
    get_subscription_overview,
    generate_invoice_pdf,
)

User = get_user_model()


class BillingBalanceSlotOptimizationTest(TestCase):
    """
    Testet Task 2.2: Batch-Aggregation und bulk_create in compute_balance_range.
    """

    def setUp(self):
        self.user = User.objects.create_user(
            username="meteruser",
            email="meter@sharegy.de",
            password="securepassword123",
        )
        self.meter1 = Meter.objects.create(
            owner_user=self.user,
            serial_number="METER-TEST-001",
        )
        self.meter2 = Meter.objects.create(
            owner_user=self.user,
            serial_number="METER-TEST-002",
        )

        # Erzeuge Zählerstände für 2 Slots (15-Min-Raster)
        self.t1 = datetime(2026, 8, 25, 10, 0, tzinfo=dt_timezone.utc)
        self.t2 = datetime(2026, 8, 25, 10, 15, tzinfo=dt_timezone.utc)

        # Meter 1: t1 = 5.0 kWh Bezug (1.8.0), t2 = 2.0 kWh Einspeisung (2.8.0)
        AggregatedReading.objects.create(
            meter=self.meter1,
            obis_code="1.8.0",
            period_start=self.t1,
            value=Decimal("5.000"),
        )
        AggregatedReading.objects.create(
            meter=self.meter1,
            obis_code="2.8.0",
            period_start=self.t2,
            value=Decimal("2.000"),
        )

        # Meter 2: t1 = 1.0 kWh Bezug (1.8.0), t2 = 8.0 kWh Einspeisung (2.8.0)
        AggregatedReading.objects.create(
            meter=self.meter2,
            obis_code="1.8.0",
            period_start=self.t1,
            value=Decimal("1.000"),
        )
        AggregatedReading.objects.create(
            meter=self.meter2,
            obis_code="2.8.0",
            period_start=self.t2,
            value=Decimal("8.000"),
        )

    def test_compute_balance_range_batch_aggregation(self):
        end_time = datetime(2026, 8, 25, 10, 30, tzinfo=dt_timezone.utc)
        
        # Aufruf der optimierten Funktion
        compute_balance_range(self.t1, end_time)

        # Prüfe, dass BalanceSlots für beide Zähler erzeugt wurden
        slots_t1 = BalanceSlot.objects.filter(period_start=self.t1)
        self.assertEqual(slots_t1.count(), 2)

        slot1_t1 = slots_t1.get(meter=self.meter1)
        self.assertEqual(slot1_t1.consumption_kwh, Decimal("5.000"))
        self.assertEqual(slot1_t1.generation_kwh, Decimal("0.000"))
        self.assertEqual(slot1_t1.grid_import_kwh, Decimal("5.000"))

        slots_t2 = BalanceSlot.objects.filter(period_start=self.t2)
        self.assertEqual(slots_t2.count(), 2)

        slot2_t2 = slots_t2.get(meter=self.meter2)
        self.assertEqual(slot2_t2.generation_kwh, Decimal("8.000"))
        self.assertEqual(slot2_t2.grid_import_kwh, Decimal("0.000"))
        self.assertEqual(slot2_t2.grid_export_kwh, Decimal("8.000"))


class EMSSubscriptionAndInvoiceTest(TestCase):
    """
    Testet das SaaS Subscription- und Billing-System für EMS-Nutzer.
    """

    def setUp(self):
        self.user = User.objects.create_user(
            username="billinguser",
            email="billing@sharegy.de",
            password="securepassword123",
            first_name="Max",
            last_name="Mustermann",
        )
        self.client = Client()

    def test_subscription_lifecycle_and_invoices(self):
        # 1. Default Free Plan
        sub = get_or_create_subscription(self.user)
        self.assertEqual(sub.plan, EMSSubscription.PLAN_FREE)
        self.assertEqual(sub.status, EMSSubscription.STATUS_ACTIVE)
        self.assertFalse(sub.is_pro_active)

        # 2. Upgrade to Pro Monthly
        sub_pro = change_subscription_plan(self.user, "pro_monthly")
        self.assertEqual(sub_pro.plan, "pro_monthly")
        self.assertTrue(sub_pro.is_pro_active)
        self.assertTrue(sub_pro.entitlements["spot_optimizer"])
        self.assertTrue(sub_pro.entitlements["battery_arbitrage"])

        # Prüfe, dass eine Rechnung erzeugt wurde
        invoices = EMSInvoice.objects.filter(user=self.user)
        self.assertEqual(invoices.count(), 1)
        inv = invoices.first()
        self.assertEqual(inv.amount_gross_eur, Decimal("4.99"))
        self.assertEqual(inv.status, EMSInvoice.STATUS_PAID)
        self.assertIn("SHG-", inv.invoice_number)

        # 3. PDF Generator Test
        pdf_response = generate_invoice_pdf(inv)
        self.assertEqual(pdf_response.status_code, 200)
        self.assertEqual(pdf_response["Content-Type"], "application/pdf")
        self.assertTrue(len(pdf_response.content) > 1000)

        # 4. Kündigung zum Periodenende
        sub_canceled = cancel_subscription(self.user, at_period_end=True)
        self.assertTrue(sub_canceled.cancel_at_period_end)
        self.assertTrue(sub_canceled.is_pro_active)  # Bleibt aktiv bis Periodenende

        # 5. Reaktivierung
        sub_reactivated = reactivate_subscription(self.user)
        self.assertFalse(sub_reactivated.cancel_at_period_end)

    def test_subscription_rest_apis(self):
        self.client.force_login(self.user)

        # 1. GET /api/billing/subscription/me/
        res_me = self.client.get("/api/billing/subscription/me/", HTTP_HOST="localhost")
        self.assertEqual(res_me.status_code, 200)
        data = res_me.json()
        self.assertIn("subscription", data)
        self.assertIn("billing_address", data)
        self.assertIn("available_plans", data)
        self.assertIn("invoices", data)

        # 2. POST /api/billing/subscription/update-address/
        res_addr = self.client.post(
            "/api/billing/subscription/update-address/",
            data={
                "billing_name": "Mustermann Solar GmbH",
                "customer_type": "business",
                "company_name": "Mustermann Solar GmbH",
                "vat_id": "DE123456789",
                "street": "Sonnenweg",
                "house_number": "42",
                "postal_code": "50667",
                "city": "Köln",
                "country": "DE",
            },
            content_type="application/json",
            HTTP_HOST="localhost",
        )
        self.assertEqual(res_addr.status_code, 200)
        self.assertEqual(res_addr.json()["status"], "success")

        # 3. POST /api/billing/subscription/change-plan/ -> Pro Yearly
        res_upgrade = self.client.post(
            "/api/billing/subscription/change-plan/",
            data={"plan": "pro_yearly"},
            content_type="application/json",
            HTTP_HOST="localhost",
        )
        self.assertEqual(res_upgrade.status_code, 200)
        up_data = res_upgrade.json()["data"]
        self.assertEqual(up_data["subscription"]["plan"], "pro_yearly")
        self.assertTrue(up_data["subscription"]["is_pro"])

        # 4. Invoice PDF Download via API
        inv = EMSInvoice.objects.filter(user=self.user).first()
        self.assertIsNotNone(inv)
        res_pdf = self.client.get(
            f"/api/billing/subscription/invoices/{inv.id}/pdf/",
            HTTP_HOST="localhost",
        )
        self.assertEqual(res_pdf.status_code, 200)
        self.assertEqual(res_pdf["Content-Type"], "application/pdf")


class CouponAndTermsValidationTest(TestCase):
    """
    Testet Gutschein-Einlösung, E-Mail-Validierung und AGB-Zustimmungs-Audit-Logging.
    """

    def setUp(self):
        self.user = User.objects.create_user(
            username="betatester",
            email="tester@sharegy.de",
            password="securepassword123",
        )
        self.client = Client()
        self.client.force_login(self.user)

    def test_coupon_validation_and_redemption(self):
        from billing.models import Coupon, CouponRedemption
        from accounts.models import UserTermsConsent

        coupon = Coupon.objects.create(
            code="BETA100",
            description="3 Monate Pro gratis",
            discount_type=Coupon.TYPE_FREE_MONTHS,
            discount_value=Decimal("100.00"),
            duration_months=3,
            max_redemptions=10,
        )

        # 1. Validieren via API
        res_val = self.client.post(
            "/api/billing/subscription/coupons/validate/",
            data={"code": "BETA100"},
            content_type="application/json",
            HTTP_HOST="localhost",
        )
        self.assertEqual(res_val.status_code, 200)
        self.assertEqual(res_val.json()["coupon"]["code"], "BETA100")

        # 2. Einlösen via API
        res_redeem = self.client.post(
            "/api/billing/subscription/coupons/redeem/",
            data={"code": "BETA100", "terms_accepted": True},
            content_type="application/json",
            HTTP_HOST="localhost",
        )
        self.assertEqual(res_redeem.status_code, 200)
        self.assertTrue(res_redeem.json()["data"]["subscription"]["is_pro"])

        # Prüfe CouponRedemption & AGB-Zustimmung
        self.assertTrue(CouponRedemption.objects.filter(coupon=coupon, user=self.user).exists())
        self.assertTrue(UserTermsConsent.objects.filter(user=self.user, consent_type="upgrade_pro").exists())

        # 3. Zweite Einlösung durch denselben User muss abgelehnt werden
        res_repeat = self.client.post(
            "/api/billing/subscription/coupons/redeem/",
            data={"code": "BETA100", "terms_accepted": True},
            content_type="application/json",
            HTTP_HOST="localhost",
        )
        self.assertEqual(res_repeat.status_code, 400)

    def test_disposable_email_rejection_on_pro_upgrade(self):
        disposable_user = User.objects.create_user(
            username="trashuser",
            email="spammer@mailinator.com",
            password="securepassword123",
        )
        self.client.force_login(disposable_user)

        res = self.client.post(
            "/api/billing/subscription/change-plan/",
            data={"plan": "pro_monthly", "terms_accepted": True},
            content_type="application/json",
            HTTP_HOST="localhost",
        )
        self.assertEqual(res.status_code, 400)
        self.assertIn("Wegwerf-E-Mail", res.json()["message"])

