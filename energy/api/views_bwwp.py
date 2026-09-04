"""
energy/api/views_bwwp.py

REST-API Endpunkte für das BWWP- / Wärmepumpen-Lastmanagement (SG-Ready).
Ermöglicht Statusabfrage, Schwellenwert-Konfiguration und manuelle Steuerung.
"""

import logging
from decimal import Decimal
from django.shortcuts import get_object_or_404
from django.utils import timezone
from datetime import timedelta
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from devices.models import Device
from energy.models import BWWPLoadManagementConfig
from energy.services.bwwp_manager import (
    evaluate_bwwp_load_management,
    find_or_create_bwwp_config,
    actuate_bwwp_relay,
    get_bwwp_telemetry,
)

logger = logging.getLogger(__name__)


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def bwwp_status_view(request):
    """
    Liefert den aktuellen Live-Status der BWWP (Wassertemperatur, Leistung,
    SG-Ready Zustand, PV-Überschuss, Börsenpreis und Entscheidungsgrund).
    """
    home = request.user.homes.first()
    if not home:
        return Response({"error": "Kein Home für den aktuellen Benutzer gefunden."}, status=404)

    force_eval = request.query_params.get("evaluate", "true").lower() in ("true", "1")
    config = find_or_create_bwwp_config(home)

    if not config:
        return Response({
            "status": "unconfigured",
            "message": "Keine Brauchwasserwärmepumpe oder Wärmepumpe im System gefunden.",
            "available_devices": list(
                Device.objects.filter(home=home, active=True, pending_delete=False).values("id", "identifier")
            ),
        })

    result = evaluate_bwwp_load_management(home, config=config, force=False)
    return Response(result)


@api_view(["POST", "PATCH"])
@permission_classes([IsAuthenticated])
def bwwp_config_view(request):
    """
    Aktualisiert die Schwellenwerte und Betriebsmodi für das BWWP-Lastmanagement.
    """
    home = request.user.homes.first()
    if not home:
        return Response({"error": "Kein Home für den aktuellen Benutzer gefunden."}, status=404)

    config = find_or_create_bwwp_config(home)
    if not config:
        # Erstelle Konfiguration für explizit übergebenes Gerät
        device_id = request.data.get("device_id")
        if not device_id:
            return Response({"error": "device_id ist erforderlich."}, status=400)
        device = get_object_or_404(Device, id=device_id, home=home)
        config = BWWPLoadManagementConfig.objects.create(
            home=home,
            device=device,
            active=True,
            control_mode=request.data.get("control_mode", "hybrid"),
        )

    # Wenn device_id geändert wird
    if "device_id" in request.data:
        new_device = get_object_or_404(Device, id=request.data["device_id"], home=home)
        config.device = new_device

    if "active" in request.data:
        config.active = bool(request.data["active"])

    if "control_mode" in request.data:
        mode = request.data["control_mode"]
        if mode in ("hybrid", "pv_surplus", "spot_price", "manual"):
            config.control_mode = mode

    # Numerische Schwellenwerte
    float_fields = {
        "min_temp_c": (35.0, 60.0),
        "target_temp_c": (40.0, 65.0),
        "boost_temp_c": (45.0, 70.0),
        "max_safety_temp_c": (55.0, 75.0),
        "min_pv_surplus_w": (0.0, 10000.0),
        "max_price_threshold_ct": (-50.0, 100.0),
        "battery_soc_reserve_pct": (0.0, 100.0),
    }

    for field_name, (val_min, val_max) in float_fields.items():
        if field_name in request.data:
            try:
                v = float(request.data[field_name])
                if val_min <= v <= val_max:
                    setattr(config, field_name, Decimal(str(round(v, 2))))
            except (ValueError, TypeError):
                pass

    int_fields = {
        "min_run_time_minutes": (0, 120),
        "min_cooldown_minutes": (0, 120),
    }
    for field_name, (val_min, val_max) in int_fields.items():
        if field_name in request.data:
            try:
                v = int(request.data[field_name])
                if val_min <= v <= val_max:
                    setattr(config, field_name, v)
            except (ValueError, TypeError):
                pass

    config.save()
    logger.info("[BWWP-Config] Konfiguration für %s aktualisiert.", config.device.identifier)

    # Direkt neu evaluieren
    updated_status = evaluate_bwwp_load_management(home, config=config, force=True)
    return Response(updated_status)


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def bwwp_switch_view(request):
    """
    Manuelle Steuerung / Sofort-Boost oder Pausieren der BWWP.
    Body:
    {
        "action": "boost" | "normal" | "off" | "auto",
        "duration_minutes": 60
    }
    """
    home = request.user.homes.first()
    if not home:
        return Response({"error": "Kein Home für den aktuellen Benutzer gefunden."}, status=404)

    config = find_or_create_bwwp_config(home)
    if not config or not config.device:
        return Response({"error": "Keine BWWP konfiguriert."}, status=400)

    action = str(request.data.get("action", "boost")).lower().strip()
    duration_min = int(request.data.get("duration_minutes", 60))
    now = timezone.now()

    if action == "auto":
        config.manual_override_until = None
        config.control_mode = "hybrid" if config.control_mode == "manual" else config.control_mode
        config.save(update_fields=["manual_override_until", "control_mode"])
        return Response(evaluate_bwwp_load_management(home, config=config, force=True))

    elif action in ("boost", "on"):
        actuate_bwwp_relay(config.device, True)
        config.current_sg_state = "3_boost"
        config.last_decision_reason = f"🚀 Manueller Sofort-Boost aktiviert (bis {(now + timedelta(minutes=duration_min)).strftime('%H:%M')} Uhr)."
        config.manual_override_until = now + timedelta(minutes=duration_min)
        config.last_switched_at = now
        config.save(update_fields=["current_sg_state", "last_decision_reason", "manual_override_until", "last_switched_at"])

    elif action in ("normal", "off"):
        actuate_bwwp_relay(config.device, False)
        config.current_sg_state = "2_normal"
        config.last_decision_reason = f"✋ Manuell auf Normalbetrieb/Aus gestellt (bis {(now + timedelta(minutes=duration_min)).strftime('%H:%M')} Uhr)."
        config.manual_override_until = now + timedelta(minutes=duration_min)
        config.last_switched_at = now
        config.save(update_fields=["current_sg_state", "last_decision_reason", "manual_override_until", "last_switched_at"])

    else:
        return Response({"error": "Ungültige Aktion. Erlaubt: 'boost', 'normal', 'off', 'auto'."}, status=400)

    status_data = evaluate_bwwp_load_management(home, config=config, force=False)
    return Response(status_data)
