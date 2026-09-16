"""
energy/views_cls.py

BNetzA Smart Meter Gateway (SMGW) & CLS-Kanal (§ 14a EnWG) Schnittstellen:
- BSI TR-03109-1 konformer Dimm-Signal Ingest
- Automatische VNB-Quittierung (Dispatch Acknowledgment)
- Status- und Telemetrie-Abfrage für SteuVE (Wallboxen, Wärmepumpen, Speicher)
- Entwarnungs- / Freigabe-Endpunkt zur Wiederherstellung des Normalbetriebs
"""

from decimal import Decimal
from datetime import timedelta
import logging

from django.utils import timezone
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework import status

from devices.models import Home, Device
from energy.models import GridDimmingSignal, SteuVEDeviceConfig, EnWG14aDimmingAuditLog
from energy.services_dimming import (
    trigger_grid_dimming,
    clear_grid_dimming,
    get_active_dimming_signal,
    evaluate_home_power_budget,
)

logger = logging.getLogger("energy.cls")


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def cls_dimming_signal_ingest(request):
    """
    POST /api/energy/cls/signal/
    
    Empfängt netzdienliche Drosselungsbefehle vom Smart Meter Gateway (SMGW) / CLS-Proxy.
    Führt die automatische Allokation auf alle SteuVE im Haushalt durch und quittiert
    den Befehl an das VNB-Leitsystem.
    """
    data = request.data
    user = request.user

    # Home auflösen
    home_id = data.get("home_id")
    home = None
    if home_id:
        home = Home.objects.filter(id=home_id).first()
    if not home:
        home = Home.objects.filter(user=user).first()
    if not home and hasattr(user, "homes"):
        home = user.homes.first()

    if not home:
        return Response(
            {"error": "Kein gültiger Haushalt (Home) für das CLS-Signal gefunden."},
            status=status.HTTP_400_BAD_REQUEST
        )

    # Parameter mit § 14a Defaults
    target_max_grid_kw = Decimal(str(data.get("target_max_grid_kw", "4.20")))
    duration_minutes = int(data.get("duration_minutes", 120))
    raw_source = str(data.get("source", "wmsb_cls"))
    # Sicherstellen, dass source in choices passt (max 30 Zeichen)
    valid_sources = {"vnb_api", "wmsb_cls", "shelly_input", "manual_test"}
    source_choice = raw_source if raw_source in valid_sources else "wmsb_cls"

    # Drosselungslogik ausführen
    signal = trigger_grid_dimming(
        home=home,
        source=source_choice,
        target_max_kw=target_max_grid_kw,
        duration_minutes=duration_minutes,
        raw_payload=data,
        user=user,
    )

    # Budget & alle SteuVE im Haushalt ermitteln
    budget = evaluate_home_power_budget(home)
    all_steuve = SteuVEDeviceConfig.objects.filter(
        device__home=home
    ).select_related("device", "device__config")

    steuve_summary = []
    for s in all_steuve:
        dev_name = s.device.config.name if hasattr(s.device, "config") and s.device.config else s.device.identifier
        steuve_summary.append({
            "device_id": str(s.device_id),
            "device_name": dev_name,
            "steuve_type": s.steuve_type,
            "rated_power_kw": float(s.rated_power_kw),
            "allocated_limit_kw": float(s.current_power_limit_kw or s.rated_power_kw),
            "is_dimmed": s.is_currently_dimmed,
        })

    logger.info(
        f"[CLS SMGW Ingest] Signal {signal.id} für Home '{home.name}' aktiviert. "
        f"Erlaubtes Netzbudget: {target_max_grid_kw} kW. {len(steuve_summary)} SteuVE gesteuert."
    )

    # VNB Acknowledgment Payload (FNN Steuerbox konform)
    return Response({
        "status": "acknowledged",
        "dispatch_id": str(signal.id),
        "protocol": "BSI-TR-03109-1 / FNN-Steuerbox CLS",
        "home_id": str(home.id),
        "home_name": home.name,
        "execution_timestamp_utc": timezone.now().isoformat(),
        "target_max_grid_kw": float(target_max_grid_kw),
        "expires_at": signal.expires_at.isoformat() if signal.expires_at else None,
        "steuve_affected_count": len(steuve_summary),
        "steuve_allocation": steuve_summary,
        "power_budget": budget,
        "compliance": "§ 14a EnWG BNetzA BK6-22-300 / BK8-22/010-A",
    }, status=status.HTTP_200_OK)


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def cls_dimming_status(request):
    """
    GET /api/energy/cls/status/
    
    Liefert den aktuellen § 14a Drosselungsstatus, aktive SteuVE-Limits und Budget-Werte.
    """
    user = request.user
    home_id = request.query_params.get("home_id")
    home = None
    if home_id:
        home = Home.objects.filter(id=home_id).first()
    if not home:
        home = Home.objects.filter(user=user).first()
    if not home and hasattr(user, "homes"):
        home = user.homes.first()

    if not home:
        return Response({"is_dimmed": False, "message": "Kein Haushalt gefunden."})

    active_signal = get_active_dimming_signal(home=home)
    budget = evaluate_home_power_budget(home)

    all_steuve = SteuVEDeviceConfig.objects.filter(
        device__home=home
    ).select_related("device", "device__config")

    steuve_list = []
    for s in all_steuve:
        dev_name = s.device.config.name if hasattr(s.device, "config") and s.device.config else s.device.identifier
        steuve_list.append({
            "id": str(s.id),
            "device_id": str(s.device_id),
            "device_name": dev_name,
            "steuve_type": s.steuve_type,
            "rated_power_kw": float(s.rated_power_kw),
            "minimum_power_kw": float(s.minimum_power_kw),
            "priority": s.priority,
            "is_dimmed": s.is_currently_dimmed,
            "current_limit_kw": float(s.current_power_limit_kw) if s.current_power_limit_kw else None,
        })

    # Letzte Audit-Logs
    recent_audits = EnWG14aDimmingAuditLog.objects.filter(
        home=home
    ).order_by("-created_at")[:5]

    audit_list = []
    for a in recent_audits:
        audit_list.append({
            "action": a.action,
            "created_at": a.created_at.isoformat(),
            "commanded_power_limit_kw": float(a.commanded_power_limit_kw) if a.commanded_power_limit_kw else None,
            "vnb_operator_id": a.vnb_operator_id,
            "reason": a.reason,
            "compliance_verified": a.compliance_verified,
        })

    return Response({
        "home_id": str(home.id),
        "home_name": home.name,
        "is_dimmed": active_signal is not None,
        "active_signal": {
            "id": str(active_signal.id),
            "source": active_signal.source,
            "started_at": active_signal.started_at.isoformat(),
            "expires_at": active_signal.expires_at.isoformat() if active_signal.expires_at else None,
            "target_max_grid_kw": float(active_signal.target_max_grid_kw),
        } if active_signal else None,
        "power_budget": budget,
        "steuve_devices": steuve_list,
        "recent_audit_log": audit_list,
    })


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def cls_dimming_clear(request):
    """
    POST /api/energy/cls/clear/
    
    Hebt eine bestehende § 14a Drosselung manuell oder durch VNB-Entwarnung auf.
    """
    user = request.user
    home_id = request.data.get("home_id")
    home = None
    if home_id:
        home = Home.objects.filter(id=home_id).first()
    if not home:
        home = Home.objects.filter(user=user).first()
    if not home and hasattr(user, "homes"):
        home = user.homes.first()

    if not home:
        return Response({"error": "Kein Haushalt gefunden."}, status=status.HTTP_400_BAD_REQUEST)

    clear_result = clear_grid_dimming(home=home)

    return Response({
        "status": "cleared",
        "home_id": str(home.id),
        "cleared_signals_count": clear_result.get("cleared_signals_count", 0),
        "timestamp_utc": timezone.now().isoformat(),
        "message": "§ 14a EnWG Drosselung erfolgreich aufgehoben. Normalbetrieb wiederhergestellt."
    })
