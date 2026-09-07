"""
energy/api/views_dispatch_hub.py

REST API Endpunkte für die zentrale Lastmanagement- & Dispatch-Zentrale (/app/control).
Bietet Live-Leistungsbudget, Prioritäten-Kaskade, 24h-Fahrplan und Schnellschalter.
"""

import logging
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from billing.services_subscription import get_or_create_subscription
from energy.services.dispatch_hub import (
    get_load_management_hub_data,
    get_or_create_priority_config,
    execute_hub_device_action,
)

logger = logging.getLogger(__name__)


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def load_management_hub_view(request):
    """
    Liefert das vollständige Lastmanagement-Dashboard (Live-Budget,
    alle 7 Verbraucher-Kategorien, aktive Prioritäten und 24h-Fahrplan).
    """
    home = request.user.homes.first()
    if not home:
        return Response({"error": "Kein Home für den aktuellen Benutzer gefunden."}, status=404)

    sub = get_or_create_subscription(request.user)
    is_pro = bool(sub and sub.is_pro_active)

    data = get_load_management_hub_data(home)
    data["is_pro"] = is_pro
    return Response(data)


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def load_management_priorities_view(request):
    """
    Aktualisiert die Prioritäten-Kaskade (Merit-Order) und den Master-Modus (Pro Feature).
    Body:
    {
        "priority_order": ["battery", "bwwp", "wallbox", "pool", "ac", ...],
        "master_mode": "autopilot" | "pv_only" | "price_saver" | "manual",
        "auto_dispatch_enabled": true
    }
    """
    home = request.user.homes.first()
    if not home:
        return Response({"error": "Kein Home für den aktuellen Benutzer gefunden."}, status=404)

    sub = get_or_create_subscription(request.user)
    if not (sub and sub.is_pro_active):
        return Response(
            {
                "status": "error",
                "code": "pro_required",
                "message": "Die automatisierte Laststeuerung und Prioritäten-Kaskade erfordern ein aktives Sharegy Pro Abonnement.",
            },
            status=403,
        )

    prio_cfg = get_or_create_priority_config(home)

    if "priority_order" in request.data and isinstance(request.data["priority_order"], list):
        prio_cfg.priority_order = request.data["priority_order"]

    if "master_mode" in request.data:
        mode = request.data["master_mode"]
        if mode in ("autopilot", "pv_only", "price_saver", "manual"):
            prio_cfg.master_mode = mode

    if "auto_dispatch_enabled" in request.data:
        prio_cfg.auto_dispatch_enabled = bool(request.data["auto_dispatch_enabled"])

    prio_cfg.save()
    logger.info("[Dispatch-Hub] Prioritäten für Home %s aktualisiert.", home.name)

    # Aktualisierte Daten zurückgeben
    updated_data = get_load_management_hub_data(home)
    updated_data["is_pro"] = True
    return Response(updated_data)


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def load_management_action_view(request):
    """
    Führt Sofort-Schaltungen und Aktions-Trigger für einzelne Lasten aus (Pro Feature).
    Body:
    {
        "category": "bwwp" | "pool" | "ac" | "wallbox" | "battery" | "appliances",
        "action": "boost" | "fast_charge" | "toggle" | "auto",
        "device_id": "custom_123" | "bwwp_1",
        "params": {}
    }
    """
    home = request.user.homes.first()
    if not home:
        return Response({"error": "Kein Home für den aktuellen Benutzer gefunden."}, status=404)

    sub = get_or_create_subscription(request.user)
    if not (sub and sub.is_pro_active):
        return Response(
            {
                "status": "error",
                "code": "pro_required",
                "message": "Direktschaltungen und Last-Overrides erfordern ein aktives Sharegy Pro Abonnement.",
            },
            status=403,
        )

    category = request.data.get("category", "")
    action = request.data.get("action", "")
    device_id = request.data.get("device_id")
    params = request.data.get("params", {})

    result = execute_hub_device_action(home, category, action, device_id=device_id, params=params)
    return Response(result)
