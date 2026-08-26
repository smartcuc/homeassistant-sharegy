#######################
# billing/api/views.py
#######################

from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from billing.models import UserBalanceSlot, EMSInvoice
from billing.services_subscription import (
    get_subscription_overview,
    update_billing_address,
    change_subscription_plan,
    cancel_subscription,
    reactivate_subscription,
    generate_invoice_pdf,
    seed_demo_invoices,
)


@api_view(["GET"])
def consumption_view(request):
    qs = UserBalanceSlot.objects.order_by("period_start")[:100]

    data = [
        {
            "period_start": obj.period_start.isoformat(),
            "consumption_kwh": float(obj.consumption_kwh),
        }
        for obj in qs
    ]

    return Response(data)


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def subscription_me_view(request):
    """
    Liefert das aktuelle SaaS-Abonnement, Rechnungsadresse und Rechnungen.
    """
    data = get_subscription_overview(request.user)
    return Response(data)


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def update_billing_address_view(request):
    """
    Aktualisiert die Rechnungsadresse und Steuerdaten des Nutzers.
    """
    update_billing_address(request.user, request.data)
    data = get_subscription_overview(request.user)
    return Response(
        {
            "status": "success",
            "message": "Rechnungsadresse erfolgreich aktualisiert.",
            "data": data,
        }
    )


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def change_plan_view(request):
    """
    Wechselt den Abonnement-Plan (Upgrade/Downgrade).
    """
    plan = request.data.get("plan")
    payment_method = request.data.get("payment_method", "Kreditkarte (via Stripe)")
    if not plan:
        return Response(
            {"status": "error", "message": "Feld 'plan' ist erforderlich."},
            status=status.HTTP_400_BAD_REQUEST,
        )

    try:
        change_subscription_plan(request.user, plan, payment_method=payment_method)
        data = get_subscription_overview(request.user)
        return Response(
            {
                "status": "success",
                "message": f"Abonnement erfolgreich auf '{plan}' umgestellt.",
                "data": data,
            }
        )
    except ValueError as e:
        return Response(
            {"status": "error", "message": str(e)},
            status=status.HTTP_400_BAD_REQUEST,
        )


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def cancel_subscription_view(request):
    """
    Kündigt das Abonnement zum Ende des laufenden Abrechnungszeitraums.
    """
    at_period_end = request.data.get("at_period_end", True)
    cancel_subscription(request.user, at_period_end=at_period_end)
    data = get_subscription_overview(request.user)
    return Response(
        {
            "status": "success",
            "message": "Abonnement zum Periodenende gekündigt.",
            "data": data,
        }
    )


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def reactivate_subscription_view(request):
    """
    Reaktiviert ein gekündigtes Abonnement.
    """
    reactivate_subscription(request.user)
    data = get_subscription_overview(request.user)
    return Response(
        {
            "status": "success",
            "message": "Abonnement erfolgreich reaktiviert.",
            "data": data,
        }
    )


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def invoice_pdf_view(request, invoice_id):
    """
    Generiert und lädt die Rechnung als PDF herunter.
    """
    invoice = get_object_or_404(EMSInvoice, id=invoice_id, user=request.user)
    return generate_invoice_pdf(invoice)


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def seed_demo_billing_view(request):
    """
    Erzeugt Demo-Rechnungen für Entwicklungs- und Testzwecke.
    """
    seed_demo_invoices(request.user)
    data = get_subscription_overview(request.user)
    return Response(
        {
            "status": "success",
            "message": "Demo-Rechnungen erfolgreich erzeugt.",
            "data": data,
        }
    )
