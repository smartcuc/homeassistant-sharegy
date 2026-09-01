"""
billing/test_stripe_integration.py

Umfassende Unit-Tests für die Stripe Sandbox / Testmode Integration:
- Config Endpoint
- Checkout Session Erstellung & Plan-Aktivierung
- Customer Portal Generierung
- Webhook Event Dispatching (checkout.session.completed, subscription.updated, subscription.deleted, invoice.payment_succeeded)
"""

import json
from decimal import Decimal
from datetime import timedelta
from unittest.mock import patch, MagicMock

from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from django.utils import timezone

from billing.models import EMSSubscription, EMSInvoice
from billing.services_stripe import (
    create_checkout_session,
    create_customer_portal_session,
    handle_stripe_webhook_event,
    get_or_create_stripe_customer,
)

User = get_user_model()


class StripeIntegrationTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username="stripe-tester@sharegy.de",
            email="stripe-tester@sharegy.de",
            password="TestPassword123!",
            first_name="Max",
            last_name="Mustermann",
        )
        self.client.force_login(self.user)

    def test_stripe_config_endpoint(self):
        """Testet den öffentlichen Stripe Config Endpoint."""
        response = self.client.get("/api/billing/stripe/config/")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn("sandbox_mode", data)
        self.assertIn("public_key", data)
        self.assertIn("is_configured", data)

    def test_get_or_create_stripe_customer_sandbox(self):
        """Testet das Erstellen/Zuordnen eines Stripe Customers im Sandbox-Modus."""
        customer_id = get_or_create_stripe_customer(self.user)
        self.assertTrue(customer_id.startswith("cus_"))

        sub = EMSSubscription.objects.get(user=self.user)
        self.assertEqual(sub.stripe_customer_id, customer_id)

    def test_create_checkout_session(self):
        """Testet die Checkout-Session Generierung (Stripe API oder Sandbox-Simulator)."""
        res = create_checkout_session(
            user=self.user,
            plan_id="pro_monthly",
            terms_accepted=True,
        )

        self.assertIn("checkout_url", res)
        self.assertIn("session_id", res)
        self.assertTrue(res.get("sandbox"))

        if res.get("simulated"):
            # Prüfe ob Pro-Abonnement im Simulator direkt aktiviert wurde
            sub = EMSSubscription.objects.get(user=self.user)
            self.assertEqual(sub.plan, "pro_monthly")
            self.assertEqual(sub.status, EMSSubscription.STATUS_ACTIVE)
            self.assertTrue(sub.is_pro_active)
            self.assertTrue(sub.invoices.filter(plan_name__icontains="Pro").exists())
        else:
            # Bei Live-Stripe-API leitet checkout_url zu Stripe Hosted Page
            self.assertTrue(res["checkout_url"].startswith("https://checkout.stripe.com/"))

    def test_stripe_checkout_api_endpoint(self):
        """Testet den REST-Endpoint /api/billing/stripe/checkout/."""
        response = self.client.post(
            "/api/billing/stripe/checkout/",
            data=json.dumps({"plan": "pro_yearly", "terms_accepted": True}),
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["status"], "success")
        self.assertIn("checkout_url", data)
        self.assertIn("session_id", data)

    def test_stripe_customer_portal_api_endpoint(self):
        """Testet den REST-Endpoint /api/billing/stripe/portal/."""
        response = self.client.post(
            "/api/billing/stripe/portal/",
            data=json.dumps({"return_url": "https://sharegy.de/app/billing"}),
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["status"], "success")
        self.assertIn("portal_url", data)

    def test_webhook_checkout_session_completed(self):
        """Testet die Verarbeitung des Webhooks checkout.session.completed."""
        sub = EMSSubscription.objects.get(user=self.user)
        sub.plan = "free"
        sub.save()

        mock_event = {
            "type": "checkout.session.completed",
            "data": {
                "object": {
                    "id": "cs_test_9999",
                    "customer": "cus_test_1234",
                    "subscription": "sub_test_5678",
                    "metadata": {
                        "user_id": str(self.user.id),
                        "plan_id": "landlord_monthly",
                    },
                }
            },
        }

        res = handle_stripe_webhook_event(json.dumps(mock_event), sig_header="")
        self.assertEqual(res["status"], "success")

        sub.refresh_from_db()
        self.assertEqual(sub.plan, "landlord_monthly")
        self.assertEqual(sub.status, EMSSubscription.STATUS_ACTIVE)
        self.assertEqual(sub.stripe_subscription_id, "sub_test_5678")

    def test_webhook_customer_subscription_updated(self):
        """Testet die Synchronisation bei Statusänderungen (z. B. past_due)."""
        sub = EMSSubscription.objects.get(user=self.user)
        sub.stripe_subscription_id = "sub_test_update_123"
        sub.save()

        mock_event = {
            "type": "customer.subscription.updated",
            "data": {
                "object": {
                    "id": "sub_test_update_123",
                    "status": "past_due",
                    "cancel_at_period_end": True,
                }
            },
        }

        res = handle_stripe_webhook_event(json.dumps(mock_event), sig_header="")
        self.assertEqual(res["status"], "success")

        sub.refresh_from_db()
        self.assertEqual(sub.status, EMSSubscription.STATUS_PAST_DUE)
        self.assertTrue(sub.cancel_at_period_end)

    def test_webhook_customer_subscription_deleted(self):
        """Testet das Zurücksetzen auf Free bei Kündigung / Löschung."""
        sub = EMSSubscription.objects.get(user=self.user)
        sub.plan = "pro_monthly"
        sub.stripe_subscription_id = "sub_test_del_456"
        sub.save()

        mock_event = {
            "type": "customer.subscription.deleted",
            "data": {
                "object": {
                    "id": "sub_test_del_456",
                    "status": "canceled",
                }
            },
        }

        res = handle_stripe_webhook_event(json.dumps(mock_event), sig_header="")
        self.assertEqual(res["status"], "success")

        sub.refresh_from_db()
        self.assertEqual(sub.plan, "free")
        self.assertIsNone(sub.stripe_subscription_id)

    def test_webhook_invoice_payment_succeeded(self):
        """Testet die Erstellung einer Rechnung bei Zahlungseingang."""
        sub = EMSSubscription.objects.get(user=self.user)
        sub.plan = "pro_monthly"
        sub.stripe_subscription_id = "sub_test_inv_789"
        sub.save()

        initial_count = sub.invoices.count()

        mock_event = {
            "type": "invoice.payment_succeeded",
            "data": {
                "object": {
                    "id": "in_test_12345",
                    "subscription": "sub_test_inv_789",
                    "amount_paid": 499,
                }
            },
        }

        res = handle_stripe_webhook_event(json.dumps(mock_event), sig_header="")
        self.assertEqual(res["status"], "success")

        self.assertEqual(sub.invoices.count(), initial_count + 1)
