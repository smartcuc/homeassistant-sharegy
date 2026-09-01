"""
energy/api/views_grid.py

REST-API Endpunkte für § 14a EnWG Steuerbox & Dimm-Management (Cloud-SaaS).
- Inbound-Signal Triggering für VNBs, wMSBs (Smart Meter Gateway CLS) & Installateure
- Status- & Budget-Abfrage nach dem BNetzA Summenleistungs-Modell
- SteuVE-Gerätekonfiguration & Priorisierung
"""

from decimal import Decimal
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response

from devices.models import Home, Device
from energy.models import SteuVEDeviceConfig, GridDimmingSignal
from energy.services_dimming import (
    get_active_dimming_signal,
    evaluate_home_power_budget,
    trigger_grid_dimming,
    clear_grid_dimming,
)


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def grid_dimming_status_view(request):
    """
    Liefert den aktuellen § 14a EnWG Dimmstatus, das dynamische Leistungsbudget
    sowie die konfigurierten steuerbaren Verbrauchseinrichtungen (SteuVE).
    """
    user = request.user
    home_id = request.GET.get("home_id")

    if home_id:
        home = Home.objects.filter(id=home_id).first()
    else:
        home = Home.objects.filter(user=user).first()

    if not home:
        return Response({"error": "No home found for user."}, status=404)

    budget_data = evaluate_home_power_budget(home)
    steuve_configs = SteuVEDeviceConfig.objects.filter(device__home=home).select_related("device")

    steuve_list = [
        {
            "id": str(cfg.id),
            "device_id": str(cfg.device_id),
            "device_name": cfg.device.config.name if hasattr(cfg.device, "config") and cfg.device.config and cfg.device.config.name else cfg.device.identifier,
            "steuve_type": cfg.steuve_type,
            "steuve_type_display": cfg.get_steuve_type_display(),
            "rated_power_kw": float(cfg.rated_power_kw),
            "minimum_power_kw": float(cfg.minimum_power_kw),
            "priority": cfg.priority,
            "is_dimmable": cfg.is_dimmable,
            "is_currently_dimmed": cfg.is_currently_dimmed,
            "current_power_limit_kw": float(cfg.current_power_limit_kw) if cfg.current_power_limit_kw else None,
        }
        for cfg in steuve_configs
    ]

    return Response({
        "budget": budget_data,
        "steuve_devices": steuve_list,
        "enwg_info": {
            "paragraph": "§ 14a EnWG",
            "model": "Summenleistungs-Modell (BNetzA BK6-22-300)",
            "statutory_min_grid_kw": 4.2,
            "notes": "Erlaubte Leistung = 4,2 kW (Netz) + PV-Erzeugung + Batterie-Entladung - Grundlast",
        },
    })


@api_view(["POST"])
@permission_classes([AllowAny])
def grid_dimming_signal_webhook(request):
    """
    Inbound-Webhook für Netzbetreiber (VNB), Smart Meter Gateway (wMSB CLS)
    oder lokale Steuerbox-Koppelrelais (Shelly / Home Assistant).
    """
    data = request.data or {}
    home_id = data.get("home_id")
    tenant_id = data.get("tenant_id")

    home = None
    if home_id:
        home = Home.objects.filter(id=home_id).first()
    elif tenant_id:
        home = Home.objects.filter(tenant_id=tenant_id).first()
    elif request.user and request.user.is_authenticated:
        home = Home.objects.filter(owner_user=request.user).first()

    if not home:
        # Fallback: Erstes Home als Demo / Test
        home = Home.objects.first()

    if not home:
        return Response({"error": "Target home not found for § 14a signal."}, status=404)

    action = data.get("action", "dim")  # 'dim' | 'clear'
    if action == "clear":
        res = clear_grid_dimming(home)
        return Response(res, status=200)

    source = data.get("source", "vnb_api")
    target_max_kw = Decimal(str(data.get("target_max_grid_kw", "4.20")))
    duration_minutes = int(data.get("duration_minutes", 120))

    signal = trigger_grid_dimming(
        home=home,
        source=source,
        target_max_kw=target_max_kw,
        duration_minutes=duration_minutes,
        raw_payload=data,
        user=request.user if request.user.is_authenticated else None,
    )

    budget_info = evaluate_home_power_budget(home)

    return Response({
        "message": f"§ 14a EnWG Dimmsignal erfolgreich aktiviert ({target_max_kw} kW via {source}).",
        "signal_id": str(signal.id),
        "is_active": signal.is_active,
        "target_max_grid_kw": float(signal.target_max_grid_kw),
        "expires_at": signal.expires_at.isoformat() if signal.expires_at else None,
        "budget": budget_info,
    }, status=201)


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def grid_dimming_clear_view(request):
    """
    Hebt ein aktives § 14a EnWG Dimmsignal manuell auf (z. B. für Tests oder nach Netz-Entwarnung).
    """
    home_id = request.data.get("home_id")
    if home_id:
        home = Home.objects.filter(id=home_id).first()
    else:
        home = Home.objects.filter(user=request.user).first()

    if not home:
        return Response({"error": "No home found for user."}, status=404)

    res = clear_grid_dimming(home)
    return Response(res, status=200)


@api_view(["GET", "POST"])
@permission_classes([IsAuthenticated])
def steuve_devices_config_view(request):
    """
    GET: Listet alle steuerbaren Verbrauchseinrichtungen (SteuVE).
    POST: Registriert oder aktualisiert eine SteuVE-Konfiguration für ein Device.
    """
    user = request.user
    if request.method == "POST":
        device_id = request.data.get("device_id")
        device = Device.objects.filter(id=device_id).first()
        if not device:
            return Response({"error": "Device not found."}, status=404)

        steuve_type = request.data.get("steuve_type", "wallbox")
        rated_power_kw = Decimal(str(request.data.get("rated_power_kw", "11.00")))
        minimum_power_kw = Decimal(str(request.data.get("minimum_power_kw", "1.40")))
        priority = int(request.data.get("priority", 2))
        is_dimmable = bool(request.data.get("is_dimmable", True))

        cfg, created = SteuVEDeviceConfig.objects.update_or_create(
            device=device,
            defaults={
                "steuve_type": steuve_type,
                "rated_power_kw": rated_power_kw,
                "minimum_power_kw": minimum_power_kw,
                "priority": priority,
                "is_dimmable": is_dimmable,
            }
        )

        d_name = cfg.device.config.name if hasattr(cfg.device, "config") and cfg.device.config and cfg.device.config.name else cfg.device.identifier
        return Response({
            "message": "SteuVE configuration saved.",
            "steuve": {
                "id": str(cfg.id),
                "device_id": str(cfg.device_id),
                "device_name": d_name,
                "steuve_type": cfg.steuve_type,
                "rated_power_kw": float(cfg.rated_power_kw),
                "priority": cfg.priority,
                "is_dimmable": cfg.is_dimmable,
            }
        }, status=201 if created else 200)

    # GET
    configs = SteuVEDeviceConfig.objects.all().select_related("device", "device__config")
    return Response({
        "count": configs.count(),
        "results": [
            {
                "id": str(c.id),
                "device_id": str(c.device_id),
                "device_name": c.device.config.name if hasattr(c.device, "config") and c.device.config and c.device.config.name else c.device.identifier,
                "steuve_type": c.steuve_type,
                "steuve_type_display": c.get_steuve_type_display(),
                "rated_power_kw": float(c.rated_power_kw),
                "priority": c.priority,
                "is_dimmable": c.is_dimmable,
                "is_currently_dimmed": c.is_currently_dimmed,
                "current_power_limit_kw": float(c.current_power_limit_kw) if c.current_power_limit_kw else None,
            }
            for c in configs
        ]
    })
