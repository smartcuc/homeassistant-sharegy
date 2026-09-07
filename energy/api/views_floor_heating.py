"""
energy/api/views_floor_heating.py

REST API Endpunkte für intelligente Fußbodenheizungs-Steuerung & Estrich-Vorladung.
"""

import logging
from decimal import Decimal
from django.utils import timezone
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from devices.models import Home, Device
from energy.models import FloorHeatingConfig
from energy.services.floor_heating_manager import (
    evaluate_floor_heating,
    find_or_create_floor_heating_config,
    trigger_floor_heating_boost,
    actuate_floor_heating_relay,
)

logger = logging.getLogger(__name__)


def _get_home_for_request(request) -> Home | None:
    """Holt das Home für die aktuelle Anfrage."""
    home_id = request.query_params.get("home_id") if hasattr(request, "query_params") else None
    if not home_id and isinstance(request.data, dict):
        home_id = request.data.get("home_id")

    if home_id:
        h = Home.objects.filter(id=home_id).first()
        if h:
            return h

    if request.user.is_authenticated:
        return Home.objects.filter(user=request.user).first() or Home.objects.first()

    return Home.objects.first()


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def floor_heating_status_view(request):
    """
    GET /api/energy/floor-heating/
    Liefert den aktuellen Evaluierungszustand, thermischen SoC, Temperaturen und Aktorik-Status.
    """
    home = _get_home_for_request(request)
    if not home:
        return Response({"error": "Kein Home für den aktuellen Benutzer gefunden."}, status=404)

    config = find_or_create_floor_heating_config(home)
    result = evaluate_floor_heating(home, config=config, force=False)
    return Response(result)


@api_view(["POST", "PATCH"])
@permission_classes([IsAuthenticated])
def floor_heating_config_view(request):
    """
    POST /api/energy/floor-heating/config/
    Aktualisiert Betriebsmodus, Solltemperatur, Boost-Delta und Parameter.
    """
    home = _get_home_for_request(request)
    if not home:
        return Response({"error": "Kein Home gefunden."}, status=404)

    config = find_or_create_floor_heating_config(home)
    data = request.data or {}

    if "control_mode" in data:
        config.control_mode = data["control_mode"]
    if "target_room_temp_c" in data:
        config.target_room_temp_c = Decimal(str(data["target_room_temp_c"]))
    if "boost_delta_k" in data:
        config.boost_delta_k = Decimal(str(data["boost_delta_k"]))
    if "max_floor_temp_c" in data:
        config.max_floor_temp_c = Decimal(str(data["max_floor_temp_c"]))
    if "min_pv_surplus_w" in data:
        config.min_pv_surplus_w = Decimal(str(data["min_pv_surplus_w"]))
    if "max_spot_price_ct_kwh" in data:
        config.max_spot_price_ct_kwh = Decimal(str(data["max_spot_price_ct_kwh"]))
    if "estrich_area_sqm" in data:
        config.estrich_area_sqm = Decimal(str(data["estrich_area_sqm"]))
    if "heating_curve_slope" in data:
        config.heating_curve_slope = Decimal(str(data["heating_curve_slope"]))
    if "predictive_mpc_enabled" in data:
        config.predictive_mpc_enabled = bool(data["predictive_mpc_enabled"])
    if "solar_gain_compensation" in data:
        config.solar_gain_compensation = bool(data["solar_gain_compensation"])
    if "active" in data:
        config.active = bool(data["active"])

    if "device_id" in data:
        dev_id = data["device_id"]
        config.device = Device.objects.filter(id=dev_id, home=home).first() if dev_id else None

    if "temp_sensor_device_id" in data:
        sensor_id = data["temp_sensor_device_id"]
        config.temp_sensor_device = Device.objects.filter(id=sensor_id, home=home).first() if sensor_id else None

    config.save()

    eval_res = evaluate_floor_heating(home, config=config, force=True)
    return Response({
        "status": "success",
        "message": "Fußbodenheizungs-Konfiguration erfolgreich aktualisiert.",
        "data": eval_res,
    })


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def floor_heating_boost_view(request):
    """
    POST /api/energy/floor-heating/boost/
    Löst sofortigen 1-Klick Estrich-Vorladeboost für X Stunden aus.
    """
    home = _get_home_for_request(request)
    if not home:
        return Response({"error": "Kein Home gefunden."}, status=404)

    duration_hours = float(request.data.get("duration_hours", 2.0))
    result = trigger_floor_heating_boost(home, duration_hours=duration_hours)
    return Response(result)


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def floor_heating_toggle_view(request):
    """
    POST /api/energy/floor-heating/toggle/
    Schaltet das Relais manuell ein/aus.
    """
    home = _get_home_for_request(request)
    if not home:
        return Response({"error": "Kein Home gefunden."}, status=404)

    config = find_or_create_floor_heating_config(home)
    target_state = bool(request.data.get("state", True))

    actuate_floor_heating_relay(home, config, target_state=target_state)
    config.is_preheating_active = False if not target_state else config.is_preheating_active
    config.last_switched_at = timezone.now()
    config.save(update_fields=["is_preheating_active", "last_switched_at"])

    eval_res = evaluate_floor_heating(home, config=config, force=False)
    eval_res["relay_state"] = target_state
    return Response({
        "status": "success",
        "message": f"Fußbodenheizung {'eingeschaltet' if target_state else 'ausgeschaltet'}.",
        "data": eval_res,
    })
