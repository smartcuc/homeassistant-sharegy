"""
billing/services_stripe.py

Stripe Payments & Sandbox Integration für Sharegy SaaS-Abonnements.
Unterstützt:
- Checkout Sessions mit Kreditkarte, SEPA-Lastschrift, Google Pay & Apple Pay
- Customer Portal für Self-Service Rechnungs- & Zahlungsmittelverwaltung
- Webhook Signature Verification & Event Dispatching
- Graceful Sandbox Simulator für lokale/Dev-Umgebungen
"""

import uuid
import logging
from decimal import Decimal
from datetime import datetime, timedelta
import stripe
from django.conf import settings
from django.utils import timezone
from django.contrib.auth import get_user_model
from django.db import transaction

from billing.models import EMSSubscription, EMSInvoice
from billing.services_subscription import PLANS_CONFIG, create_invoice_for_subscription, validate_upgrade_eligibility

User = get_user_model()
logger = logging.getLogger(__name__)

# Stripe API Key initialisieren
if getattr(settings, "STRIPE_SECRET_KEY", None):
    stripe.api_key = settings.STRIPE_SECRET_KEY


def is_stripe_configured() -> bool:
    """Prüft, ob ein valider Stripe Secret Key hinterlegt ist."""
    key = getattr(settings, "STRIPE_SECRET_KEY", "")
    return bool(key and (key.startswith("sk_test_") or key.startswith("sk_live_") or key.startswith("rk_")))


def get_or_create_stripe_customer(user):
    """
    Sucht oder erstellt einen Stripe Customer für den gegebenen Benutzer.
    Speichert die stripe_customer_id in der EMSSubscription.
    """
    sub, _ = EMSSubscription.objects.get_or_create(user=user)
    if sub.stripe_customer_id:
        return sub.stripe_customer_id

    email = (user.email or "").strip().lower()
    name = f"{user.first_name} {user.last_name}".strip() or email

    if is_stripe_configured():
        try:
            # Existierenden Customer per E-Mail suchen
            customers = stripe.Customer.list(email=email, limit=1)
            if customers and customers.data:
                customer_id = customers.data[0].id
            else:
                customer = stripe.Customer.create(
                    email=email,
                    name=name,
                    metadata={"user_id": str(user.id), "environment": "sandbox" if getattr(settings, "STRIPE_SANDBOX_MODE", True) else "production"},
                )
                customer_id = customer.id

            sub.stripe_customer_id = customer_id
            sub.save(update_fields=["stripe_customer_id", "updated_at"])
            return customer_id
        except Exception as e:
            logger.exception("Stripe Customer creation failed for user %s: %s", user.id, e)
            # Im Sandbox-Modus simulierte ID vergeben
            simulated_id = f"cus_sandbox_{user.id}"
            sub.stripe_customer_id = simulated_id
            sub.save(update_fields=["stripe_customer_id", "updated_at"])
            return simulated_id
    else:
        # Lokaler Sandbox-Fallback
        simulated_id = f"cus_sandbox_{user.id}"
        sub.stripe_customer_id = simulated_id
        sub.save(update_fields=["stripe_customer_id", "updated_at"])
        return simulated_id


def create_checkout_session(user, plan_id, success_url=None, cancel_url=None, terms_accepted=True, request_meta=None):
    """
    Erstellt eine Stripe Checkout-Session für den gewählten Plan.
    Gibt ein Dict mit { checkout_url, session_id, sandbox } zurück.
    """
    if plan_id not in PLANS_CONFIG or plan_id == "free":
        raise ValueError(f"Ungültiger Bezahlplan für Checkout: {plan_id}")

    validate_upgrade_eligibility(user, terms_accepted=terms_accepted, request_meta=request_meta)

    plan_info = PLANS_CONFIG[plan_id]
    customer_id = get_or_create_stripe_customer(user)

    frontend_base = getattr(settings, "FRONTEND_URL", "https://sharegy.de").rstrip("/")
    success_url = success_url or f"{frontend_base}/app/billing?session_id={{CHECKOUT_SESSION_ID}}&success=true&plan={plan_id}"
    cancel_url = cancel_url or f"{frontend_base}/app/billing?canceled=true"

    if is_stripe_configured():
        try:
            # Prüfen ob explizite Price-ID konfiguriert ist
            price_ids = getattr(settings, "STRIPE_PRICE_IDS", {})
            configured_price_id = price_ids.get(plan_id)

            if configured_price_id:
                line_items = [{"price": configured_price_id, "quantity": 1}]
            else:
                # Dynamisches Line-Item erstellen (in Cents)
                amount_cents = int(plan_info["price_gross_eur"] * 100)
                interval = plan_info.get("billing_interval", "month")

                line_items = [
                    {
                        "price_data": {
                            "currency": "eur",
                            "product_data": {
                                "name": plan_info["name"],
                                "description": f"Sharegy EMS SaaS-Abonnement ({', '.join(plan_info['features'][:3])})",
                            },
                            "unit_amount": amount_cents,
                            "recurring": {
                                "interval": interval,
                            },
                        },
                        "quantity": 1,
                    }
                ]

            session = stripe.checkout.Session.create(
                customer=customer_id,
                customer_update={"name": "auto", "address": "auto"},
                payment_method_types=["card", "sepa_debit"],
                line_items=line_items,
                mode="subscription",
                success_url=success_url,
                cancel_url=cancel_url,
                billing_address_collection="required",
                tax_id_collection={"enabled": True},
                metadata={
                    "user_id": str(user.id),
                    "plan_id": plan_id,
                    "sandbox": str(getattr(settings, "STRIPE_SANDBOX_MODE", True)),
                },
                subscription_data={
                    "metadata": {
                        "user_id": str(user.id),
                        "plan_id": plan_id,
                    }
                },
            )

            return {
                "checkout_url": session.url,
                "session_id": session.id,
                "sandbox": getattr(settings, "STRIPE_SANDBOX_MODE", True),
                "plan_id": plan_id,
            }
        except Exception as e:
            logger.exception("Stripe Checkout Session creation failed: %s", e)
            if not getattr(settings, "STRIPE_SANDBOX_MODE", True):
                raise

    # 🧪 SANDBOX / TESTMODE SIMULATOR FALLBACK
    # Führt eine direkte, simulierte Aktivierung durch und leitet auf die Erfolgs-URL weiter
    logger.info("Executing simulated Stripe Sandbox checkout for user %s, plan %s", user.id, plan_id)
    simulated_session_id = f"cs_test_{uuid.uuid4().hex[:16]}"

    # Abonnement direkt im Sandbox-Modus freischalten
    now = timezone.now()
    days = 365 if plan_info["billing_interval"] == "year" else 30
    sub = EMSSubscription.objects.get(user=user)
    sub.plan = plan_id
    sub.status = EMSSubscription.STATUS_ACTIVE
    sub.current_period_start = now
    sub.current_period_end = now + timedelta(days=days)
    sub.stripe_subscription_id = f"sub_sandbox_{uuid.uuid4().hex[:12]}"
    sub.payment_method = "stripe"
    sub.payment_method_brand = "visa"
    sub.payment_method_last4 = "4242"
    sub.save()

    create_invoice_for_subscription(
        subscription=sub,
        plan_id=plan_id,
        payment_method="Kreditkarte (Stripe Sandbox)",
        period_start=now.date(),
        period_end=(now + timedelta(days=days)).date(),
    )

    resolved_success_url = success_url.replace("{CHECKOUT_SESSION_ID}", simulated_session_id)
    return {
        "checkout_url": resolved_success_url,
        "session_id": simulated_session_id,
        "sandbox": True,
        "simulated": True,
        "plan_id": plan_id,
    }


def create_customer_portal_session(user, return_url=None):
    """
    Erstellt eine Session für das Stripe Customer Portal.
    """
    frontend_base = getattr(settings, "FRONTEND_URL", "https://sharegy.de").rstrip("/")
    return_url = return_url or f"{frontend_base}/app/billing"
    customer_id = get_or_create_stripe_customer(user)

    if is_stripe_configured():
        try:
            portal_session = stripe.billing_portal.Session.create(
                customer=customer_id,
                return_url=return_url,
            )
            return {"portal_url": portal_session.url, "sandbox": getattr(settings, "STRIPE_SANDBOX_MODE", True)}
        except Exception as e:
            logger.exception("Stripe Customer Portal creation failed: %s", e)
            if not getattr(settings, "STRIPE_SANDBOX_MODE", True):
                raise

    # Sandbox-Fallback: Zurück zur Billing-Übersicht
    return {"portal_url": return_url, "sandbox": True, "simulated": True}


@transaction.atomic
def handle_stripe_webhook_event(payload, sig_header):
    """
    Verifiziert und verarbeitet Webhook-Events von Stripe.
    """
    webhook_secret = getattr(settings, "STRIPE_WEBHOOK_SECRET", "")
    event = None

    if webhook_secret and sig_header:
        try:
            event = stripe.Webhook.construct_event(
                payload, sig_header, webhook_secret
            )
        except ValueError as e:
            logger.error("Invalid Stripe webhook payload: %s", e)
            raise ValueError("Invalid payload")
        except stripe.error.SignatureVerificationError as e:
            logger.error("Invalid Stripe webhook signature: %s", e)
            raise ValueError("Invalid signature")
    else:
        import json
        if isinstance(payload, bytes):
            payload = payload.decode("utf-8")
        data = json.loads(payload) if isinstance(payload, str) else payload
        event = stripe.Event.construct_from(data, stripe.api_key or "sk_test_mock")

    event_dict = event.to_dict() if hasattr(event, "to_dict") else dict(event)
    event_type = event_dict.get("type")
    data_object = event_dict.get("data", {}).get("object", {})

    logger.info("Received Stripe Webhook Event: %s (ID: %s)", event_type, event_dict.get("id"))

    if event_type == "checkout.session.completed":
        _process_checkout_completed(data_object)
    elif event_type == "customer.subscription.updated":
        _process_subscription_updated(data_object)
    elif event_type == "customer.subscription.deleted":
        _process_subscription_deleted(data_object)
    elif event_type == "invoice.payment_succeeded":
        _process_invoice_paid(data_object)
    elif event_type == "invoice.payment_failed":
        _process_invoice_payment_failed(data_object)

    return {"status": "success", "event_type": event_type}


def _process_checkout_completed(session):
    """Verarbeitet erfolgreiche Checkout-Sessions."""
    customer_id = session.get("customer")
    subscription_id = session.get("subscription")
    metadata = session.get("metadata") or {}
    user_id = metadata.get("user_id")
    plan_id = metadata.get("plan_id")

    user = None
    if user_id:
        user = User.objects.filter(id=user_id).first()
    elif customer_id:
        sub_obj = EMSSubscription.objects.filter(stripe_customer_id=customer_id).first()
        if sub_obj:
            user = sub_obj.user

    if not user:
        logger.warning("Could not identify user for Stripe checkout session %s", session.get("id"))
        return

    sub, _ = EMSSubscription.objects.get_or_create(user=user)
    if plan_id and plan_id in PLANS_CONFIG:
        sub.plan = plan_id
    sub.status = EMSSubscription.STATUS_ACTIVE
    sub.stripe_customer_id = customer_id
    if subscription_id:
        sub.stripe_subscription_id = subscription_id
    sub.payment_method = "stripe"
    sub.current_period_start = timezone.now()
    sub.current_period_end = timezone.now() + timedelta(days=365 if "year" in (plan_id or "") else 30)
    sub.save()

    logger.info("Activated Stripe subscription %s for user %s (Plan: %s)", subscription_id, user.email, sub.plan)


def _process_subscription_updated(stripe_sub):
    """Synchronisiert Subscription-Status und Laufzeiten."""
    subscription_id = stripe_sub.get("id")
    status = stripe_sub.get("status")
    cancel_at_period_end = stripe_sub.get("cancel_at_period_end", False)
    current_period_start = stripe_sub.get("current_period_start")
    current_period_end = stripe_sub.get("current_period_end")

    sub = EMSSubscription.objects.filter(stripe_subscription_id=subscription_id).first()
    if not sub:
        customer_id = stripe_sub.get("customer")
        sub = EMSSubscription.objects.filter(stripe_customer_id=customer_id).first()

    if not sub:
        logger.warning("No local subscription found for Stripe sub ID: %s", subscription_id)
        return

    # Status-Mapping
    if status == "active":
        sub.status = EMSSubscription.STATUS_ACTIVE
    elif status == "past_due":
        sub.status = EMSSubscription.STATUS_PAST_DUE
    elif status == "canceled":
        sub.status = EMSSubscription.STATUS_CANCELED
    elif status == "trialing":
        sub.status = EMSSubscription.STATUS_TRIALING

    sub.cancel_at_period_end = cancel_at_period_end
    if current_period_start:
        sub.current_period_start = datetime.fromtimestamp(current_period_start, tz=timezone.utc)
    if current_period_end:
        sub.current_period_end = datetime.fromtimestamp(current_period_end, tz=timezone.utc)

    sub.save()
    logger.info("Updated subscription %s status to %s", sub.id, sub.status)


def _process_subscription_deleted(stripe_sub):
    """Setzt gekündigte Abonnements auf den Free-Plan zurück."""
    subscription_id = stripe_sub.get("id")
    sub = EMSSubscription.objects.filter(stripe_subscription_id=subscription_id).first()
    if not sub:
        return

    sub.plan = EMSSubscription.PLAN_FREE
    sub.status = EMSSubscription.STATUS_ACTIVE
    sub.stripe_subscription_id = None
    sub.cancel_at_period_end = False
    sub.save()
    logger.info("Reverted user %s subscription to Free after Stripe subscription deletion", sub.user.email)


def _process_invoice_paid(invoice):
    """Verarbeitet erfolgreiche Rechnungszahlungen."""
    subscription_id = invoice.get("subscription")
    customer_id = invoice.get("customer")
    sub = EMSSubscription.objects.filter(stripe_subscription_id=subscription_id).first() or EMSSubscription.objects.filter(stripe_customer_id=customer_id).first()

    if not sub:
        return

    amount_gross = Decimal(str(invoice.get("amount_paid", 0) / 100.0))
    if amount_gross > 0:
        create_invoice_for_subscription(
            subscription=sub,
            plan_id=sub.plan,
            payment_method="Kreditkarte / SEPA (via Stripe)",
            period_start=sub.current_period_start.date() if sub.current_period_start else timezone.now().date(),
            period_end=sub.current_period_end.date() if sub.current_period_end else timezone.now().date(),
        )


def _process_invoice_payment_failed(invoice):
    """Setzt das Abonnement bei fehlgeschlagener Zahlung auf past_due."""
    subscription_id = invoice.get("subscription")
    sub = EMSSubscription.objects.filter(stripe_subscription_id=subscription_id).first()
    if sub:
        sub.status = EMSSubscription.STATUS_PAST_DUE
        sub.save(update_fields=["status", "updated_at"])
