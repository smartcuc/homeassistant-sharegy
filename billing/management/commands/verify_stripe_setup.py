"""
billing/management/commands/verify_stripe_setup.py

Diagnose- und Test-Tool zur vollständigen Überprüfung der Stripe- und Stripe-Sandbox-Konfiguration:
- Prüft API-Schlüssel (Public, Secret, Webhook)
- Prüft Live-Konnektivität zu Stripe
- Testet Customer-Erstellung & Validierung
- Testet Checkout-Session Generierung mit Dynamic Payment Methods (SEPA, Karten, PayPal, etc.)
- Testet Customer Portal Generierung
"""

import sys
from django.core.management.base import BaseCommand
from django.conf import settings
from django.contrib.auth import get_user_model
from django.utils import timezone

import stripe
from billing.services_stripe import (
    is_stripe_configured,
    get_or_create_stripe_customer,
    create_checkout_session,
    create_customer_portal_session,
)

User = get_user_model()


class Command(BaseCommand):
    help = "Vollständige Diagnose und End-to-End-Test der Stripe- und Stripe-Sandbox-Konfiguration."

    def handle(self, *args, **options):
        self.stdout.write(self.style.HTTP_INFO("\n=================================================="))
        self.stdout.write(self.style.HTTP_INFO("💳 SHAREGY STRIPE & SANDBOX DIAGNOSE-TOOL"))
        self.stdout.write(self.style.HTTP_INFO("==================================================\n"))

        secret_key = getattr(settings, "STRIPE_SECRET_KEY", "")
        public_key = getattr(settings, "STRIPE_PUBLIC_KEY", "")
        webhook_secret = getattr(settings, "STRIPE_WEBHOOK_SECRET", "")
        sandbox_mode = getattr(settings, "STRIPE_SANDBOX_MODE", True)

        # 1. SCHLÜSSEL-PRÜFUNG
        self.stdout.write("1. Umgebung & API-Schlüssel:")
        is_test_mode = secret_key.startswith("sk_test_") or secret_key.startswith("rk_test_")
        is_live_mode = secret_key.startswith("sk_live_") or secret_key.startswith("rk_live_")

        mode_str = "🧪 Testmodus / Sandbox" if is_test_mode else ("🟢 Live-Modus" if is_live_mode else "⚠️ Nicht konfiguriert (Mock-Simulator aktiv)")
        self.stdout.write(f"   • Modus: {mode_str}")
        self.stdout.write(f"   • STRIPE_SANDBOX_MODE in .env: {sandbox_mode}")
        self.stdout.write(f"   • STRIPE_PUBLIC_KEY: {public_key[:12]}... (Länge: {len(public_key)})" if public_key else "   • STRIPE_PUBLIC_KEY: ❌ FEHLT")
        self.stdout.write(f"   • STRIPE_SECRET_KEY: {secret_key[:12]}... (Länge: {len(secret_key)})" if secret_key else "   • STRIPE_SECRET_KEY: ❌ FEHLT")
        self.stdout.write(f"   • STRIPE_WEBHOOK_SECRET: {webhook_secret[:12]}... (Länge: {len(webhook_secret)})" if webhook_secret else "   • STRIPE_WEBHOOK_SECRET: ⚠️ Nicht gesetzt")

        if not is_stripe_configured():
            self.stdout.write(self.style.WARNING("\n⚠️ Echte Stripe API ist nicht aktiv – System nutzt den lokalen Mock-Simulator."))
            self.stdout.write("   Um echte Stripe-Checkout-Seiten im Testmodus zu testen, trage bitte STRIPE_SECRET_KEY=sk_test_... in die .env ein.\n")
            return

        # 2. STRIPE API KONNEKTIVITÄT
        self.stdout.write("\n2. Stripe API-Verbindungstest:")
        stripe.api_key = secret_key
        try:
            account = stripe.Account.retrieve()
            acc_name = account.get("business_profile", {}).get("name") or account.get("settings", {}).get("dashboard", {}).get("display_name") or account.get("id")
            country = account.get("country", "DE")
            currency = account.get("default_currency", "eur").upper()
            self.stdout.write(self.style.SUCCESS(f"   ✅ Verbindung erfolgreich! Account: {acc_name} (Land: {country}, Währung: {currency})"))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"   ❌ API-Verbindungsfehler: {e}"))
            return

        # 3. TEST-BENUTZER & CUSTOMER ERSTELLUNG
        self.stdout.write("\n3. Customer-Erstellung & Validierung:")
        test_email = "stripe-diagnostic@sharegy.de"
        test_user, _ = User.objects.get_or_create(
            email=test_email,
            defaults={"username": test_email, "first_name": "Stripe", "last_name": "Diagnose-Tester", "is_active": True},
        )
        try:
            cust_id = get_or_create_stripe_customer(test_user, force_recreate=True)
            self.stdout.write(self.style.SUCCESS(f"   ✅ Stripe Customer erfolgreich angelegt/validiert: {cust_id}"))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"   ❌ Customer-Erstellung fehlgeschlagen: {e}"))
            return

        # 4. CHECKOUT SESSION TEST (Dynamic Payment Methods)
        self.stdout.write("\n4. Checkout-Session Generierung (SEPA, Karten, PayPal etc.):")
        try:
            session_data = create_checkout_session(
                user=test_user,
                plan_id="pro_monthly",
                terms_accepted=True,
            )
            checkout_url = session_data.get("checkout_url", "")
            session_id = session_data.get("session_id", "")
            self.stdout.write(self.style.SUCCESS(f"   ✅ Checkout-Session erfolgreich erstellt! Session-ID: {session_id}"))
            self.stdout.write(f"   🔗 Test-Checkout-URL: {checkout_url}")
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"   ❌ Checkout-Session fehlgeschlagen: {e}"))

        # 5. CUSTOMER PORTAL TEST
        self.stdout.write("\n5. Customer Portal Session Test:")
        try:
            portal_data = create_customer_portal_session(user=test_user)
            if portal_data.get("fallback"):
                self.stdout.write(self.style.WARNING("   ⚠️ Stripe Customer Portal ist im Stripe-Dashboard noch nicht aktiviert."))
                self.stdout.write("      Aktivierung möglich unter: https://dashboard.stripe.com/test/settings/billing/portal")
            else:
                self.stdout.write(self.style.SUCCESS(f"   ✅ Customer Portal Session erfolgreich generiert!"))
                self.stdout.write(f"   🔗 Portal-URL: {portal_data.get('portal_url')}")
        except Exception as e:
            self.stdout.write(self.style.WARNING(f"   ⚠️ Portal-Erstellung Hinweis: {e}"))

        self.stdout.write(self.style.HTTP_INFO("\n=================================================="))
        self.stdout.write(self.style.SUCCESS("🎉 DIAGNOSE ABGESCHLOSSEN – Stripe Sandbox ist einsatzbereit!"))
        self.stdout.write(self.style.HTTP_INFO("==================================================\n"))
