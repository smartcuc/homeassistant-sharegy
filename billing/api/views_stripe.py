"""
billing/api/views_stripe.py

REST-API Endpoints für Stripe Checkout, Customer Portal & Webhooks.
"""

import logging
from django.conf import settings
from django.http import HttpResponse
from django.utils.decorators import method_decorator
from django.views import View
from django.views.decorators.csrf import csrf_exempt

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework import status

from billing.services_stripe import (
    create_checkout_session,
    create_customer_portal_session,
    handle_stripe_webhook_event,
    is_stripe_configured,
)

logger = logging.getLogger(__name__)


class StripeConfigView(APIView):
    """
    Gibt die öffentliche Stripe-Konfiguration für das Frontend zurück.
    """
    permission_classes = [AllowAny]

    def get(self, request):
        return Response({
            "public_key": getattr(settings, "STRIPE_PUBLIC_KEY", ""),
            "sandbox_mode": getattr(settings, "STRIPE_SANDBOX_MODE", True),
            "is_configured": is_stripe_configured(),
        })


class StripeCheckoutView(APIView):
    """
    Erstellt eine Stripe Checkout Session für einen gewünschten Plan.
    """
    permission_classes = [IsAuthenticated]

    def post(self, request):
        plan_id = request.data.get("plan")
        terms_accepted = request.data.get("terms_accepted", True)
        success_url = request.data.get("success_url")
        cancel_url = request.data.get("cancel_url")

        if not plan_id:
            return Response(
                {"status": "error", "message": "Parameter 'plan' ist erforderlich."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            session_data = create_checkout_session(
                user=request.user,
                plan_id=plan_id,
                success_url=success_url,
                cancel_url=cancel_url,
                terms_accepted=terms_accepted,
                request_meta=request.META,
            )
            return Response({
                "status": "success",
                "checkout_url": session_data["checkout_url"],
                "session_id": session_data["session_id"],
                "sandbox": session_data.get("sandbox", True),
                "plan_id": session_data.get("plan_id"),
            })
        except ValueError as e:
            return Response(
                {"status": "error", "message": str(e)},
                status=status.HTTP_400_BAD_REQUEST,
            )
        except Exception as e:
            logger.exception("Stripe checkout error for user %s: %s", request.user.id, e)
            return Response(
                {"status": "error", "message": "Fehler beim Erstellen der Stripe Checkout-Session."},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


class StripeCustomerPortalView(APIView):
    """
    Erstellt eine Session für das Stripe Customer Portal zur Selbstverwaltung.
    """
    permission_classes = [IsAuthenticated]

    def post(self, request):
        return_url = request.data.get("return_url")
        try:
            portal_data = create_customer_portal_session(
                user=request.user,
                return_url=return_url,
            )
            return Response({
                "status": "success",
                "portal_url": portal_data["portal_url"],
                "sandbox": portal_data.get("sandbox", True),
            })
        except Exception as e:
            logger.exception("Stripe portal error for user %s: %s", request.user.id, e)
            return Response(
                {"status": "error", "message": "Fehler beim Öffnen des Kundenportals."},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


@method_decorator(csrf_exempt, name="dispatch")
class StripeWebhookView(View):
    """
    Empfängt asynchrone Webhooks von Stripe (Zahlungen, Statusänderungen, Kündigungen).
    """
    def post(self, request):
        payload = request.body
        sig_header = request.META.get("HTTP_STRIPE_SIGNATURE", "")

        try:
            result = handle_stripe_webhook_event(payload, sig_header)
            return HttpResponse(status=200)
        except ValueError as e:
            logger.error("Stripe webhook validation error: %s", e)
            return HttpResponse(status=400)
        except Exception as e:
            logger.exception("Stripe webhook processing error: %s", e)
            return HttpResponse(status=500)
