"""
energy/services_dimming.py

§ 14a EnWG Steuerbox- & Dimm-Engine für Sharegy Cloud-EMS (SaaS).
Implementiert das BNetzA-Summenleistungs-Modell (BK6-22-300):
- Gesetzlicher Mindestbezug aus dem Netz: 4,2 kW
- Dynamisches Gesamtbudget: P_allow = 4,2 kW (Netz) + P_PV (Erzeugung) + P_Batt (Speicher)
- Priorisierte Steuerung steuerbarer Verbrauchseinrichtungen (SteuVE: Wärmepumpen, Wallboxen, Speicher).
"""

from decimal import Decimal
from datetime import timedelta
from django.utils import timezone
from django.db.models import Sum, Q

from devices.models import Home, Device, DeviceMetric
from energy.models import GridDimmingSignal, SteuVEDeviceConfig
from tracking.models import EventLog


def get_active_dimming_signal(home: Home = None, tenant = None) -> GridDimmingSignal | None:
    """
    Ermittelt das aktuell aktive § 14a Dimmsignal für ein Home oder Tenant.
    Bereinigt automatisch abgelaufene Signale.
    """
    now = timezone.now()
    qs = GridDimmingSignal.objects.filter(is_active=True)

    if home:
        qs = qs.filter(home=home)
    elif tenant:
        qs = qs.filter(tenant=tenant)

    active_signal = qs.order_by("-started_at").first()

    if active_signal and active_signal.expires_at and active_signal.expires_at <= now:
        # Signal abgelaufen -> automatisch auflösen
        active_signal.is_active = False
        active_signal.cleared_at = now
        active_signal.save(update_fields=["is_active", "cleared_at"])
        if home:
            clear_steuve_limits(home)
        return None

    return active_signal


def clear_steuve_limits(home: Home) -> None:
    """
    Setzt alle Drosselungen für die SteuVE eines Haushalts zurück.
    """
    devices = Device.objects.filter(home=home)
    SteuVEDeviceConfig.objects.filter(device__in=devices).update(
        is_currently_dimmed=False,
        current_power_limit_kw=None,
    )


def evaluate_home_power_budget(home: Home) -> dict:
    """
    Berechnet das aktuelle Leistungsbudget für SteuVE nach dem § 14a EnWG Summenleistungs-Modell:
    Budget = 4,2 kW (Netzkontingent) + P_PV (Erzeugung) + P_Batt (Entladung) - P_Base (Haushaltsgrundlast)
    """
    active_signal = get_active_dimming_signal(home=home)
    is_dimmed = active_signal is not None
    max_grid_kw = active_signal.target_max_grid_kw if active_signal else Decimal("4.20")

    pv_power_kw = Decimal("0.00")
    batt_discharge_kw = Decimal("0.00")
    base_load_kw = Decimal("0.00")

    devices = list(
        Device.objects.filter(home=home, active=True)
        .select_related("config", "config__role")
        .prefetch_related("latest_metrics")
    )

    for dev in devices:
        latest_m = next((m for m in dev.latest_metrics.all() if m.metric_key in ("power_w", "power", "active_power")), None)
        power_w = latest_m.value if latest_m and latest_m.value is not None else 0.0
        power_kw = Decimal(str(power_w)) / Decimal("1000.0")

        cfg = getattr(dev, "config", None)
        role_key = (cfg.role.key if cfg and cfg.role else "").lower()
        dev_name = (cfg.name if cfg and cfg.name else dev.identifier).lower()

        if "pv" in role_key or "solar" in role_key or "generator" in dev_name:
            pv_power_kw += max(power_kw, Decimal("0.00"))
        elif "storage" in role_key or "battery" in dev_name:
            if power_kw < Decimal("0.00"):
                batt_discharge_kw += abs(power_kw)
        elif not hasattr(dev, "steuve_config") or not dev.steuve_config:
            base_load_kw += max(power_kw, Decimal("0.00"))

    if is_dimmed:
        # Summenmodell: 4,2 kW Netz + PV + Batterie - ungedimmte Grundlast
        allowed_steuve_kw = max(
            (max_grid_kw + pv_power_kw + batt_discharge_kw - base_load_kw),
            Decimal("1.40")  # Gesetzliche Mindeststufe (z.B. 1-phasig 6A)
        ).quantize(Decimal("0.01"))
    else:
        allowed_steuve_kw = None

    return {
        "home_id": str(home.id),
        "home_name": home.name,
        "is_dimmed": is_dimmed,
        "active_signal": {
            "id": str(active_signal.id),
            "source": active_signal.source,
            "source_display": active_signal.get_source_display(),
            "target_max_grid_kw": float(active_signal.target_max_grid_kw),
            "started_at": active_signal.started_at.isoformat(),
            "expires_at": active_signal.expires_at.isoformat() if active_signal.expires_at else None,
        } if active_signal else None,
        "max_grid_kw": float(max_grid_kw),
        "current_pv_gen_kw": float(pv_power_kw),
        "current_batt_discharge_kw": float(batt_discharge_kw),
        "current_base_load_kw": float(base_load_kw),
        "allowed_steuve_budget_kw": float(allowed_steuve_kw) if allowed_steuve_kw is not None else None,
    }


def apply_grid_dimming_to_home(home: Home, signal: GridDimmingSignal) -> dict:
    """
    Wendet das § 14a EnWG Dimmsignal auf alle steuerbaren Verbraucher des Haushalts an.
    Verteilt das Budget priorisiert:
    1. Wärme (Wärmepumpen): Hohe Prio, Erhalt des Heizbetriebs
    2. Batteriespeicher: Netzladung sperren
    3. Wallbox / E-Auto: Drosselung auf verbleibendes Restbudget (z.B. 6A = 4.1 kW)
    """
    budget_info = evaluate_home_power_budget(home)
    total_budget_kw = Decimal(str(budget_info["allowed_steuve_budget_kw"] or "4.20"))
    remaining_budget = total_budget_kw

    steuve_configs = list(
        SteuVEDeviceConfig.objects.filter(
            device__home=home,
            device__active=True,
            is_dimmable=True,
        ).select_related("device", "device__config").order_by("priority", "-rated_power_kw")
    )

    controlled_devices = []

    for cfg in steuve_configs:
        allocated_kw = Decimal("0.00")
        if remaining_budget >= cfg.rated_power_kw:
            allocated_kw = cfg.rated_power_kw
            is_dimmed = False
        elif remaining_budget >= cfg.minimum_power_kw:
            allocated_kw = remaining_budget
            is_dimmed = True
        else:
            allocated_kw = cfg.minimum_power_kw
            is_dimmed = True

        remaining_budget = max(remaining_budget - allocated_kw, Decimal("0.00"))

        cfg.is_currently_dimmed = is_dimmed
        cfg.current_power_limit_kw = allocated_kw.quantize(Decimal("0.01"))
        cfg.save(update_fields=["is_currently_dimmed", "current_power_limit_kw", "updated_at"])

        d_name = cfg.device.config.name if hasattr(cfg.device, "config") and cfg.device.config and cfg.device.config.name else cfg.device.identifier
        controlled_devices.append({
            "device_id": str(cfg.device_id),
            "device_name": d_name,
            "steuve_type": cfg.steuve_type,
            "priority": cfg.priority,
            "rated_power_kw": float(cfg.rated_power_kw),
            "power_limit_kw": float(cfg.current_power_limit_kw),
            "is_currently_dimmed": cfg.is_currently_dimmed,
        })

    EventLog.objects.create(
        name="grid_dimming_applied",
        user=home.user,
        context="global",
        metadata={
            "signal_id": str(signal.id),
            "source": signal.source,
            "target_max_grid_kw": float(signal.target_max_grid_kw),
            "total_budget_kw": float(total_budget_kw),
            "controlled_count": len(controlled_devices),
        },
    )

    return {
        "status": "dimming_applied",
        "home_id": str(home.id),
        "signal_id": str(signal.id),
        "total_budget_kw": float(total_budget_kw),
        "controlled_devices": controlled_devices,
    }


def trigger_grid_dimming(
    home: Home,
    source: str = "vnb_api",
    target_max_kw: Decimal = Decimal("4.20"),
    duration_minutes: int = 120,
    raw_payload: dict = None,
    user = None,
) -> GridDimmingSignal:
    """
    Aktiviert ein neues § 14a EnWG Dimmsignal für ein Home und stößt die Aktorik-Drosselung an.
    """
    now = timezone.now()
    expires_at = now + timedelta(minutes=duration_minutes) if duration_minutes > 0 else None

    # Vorherige Signale für dieses Home deaktivieren
    GridDimmingSignal.objects.filter(home=home, is_active=True).update(
        is_active=False,
        cleared_at=now,
    )

    signal = GridDimmingSignal.objects.create(
        home=home,
        owner_user=user or home.user,
        source=source,
        target_max_grid_kw=target_max_kw,
        started_at=now,
        expires_at=expires_at,
        is_active=True,
        raw_payload=raw_payload or {},
    )

    apply_grid_dimming_to_home(home, signal)
    return signal


def clear_grid_dimming(home: Home) -> dict:
    """
    Beendet alle aktiven Dimmsignale für ein Home und stellt den Normalbetrieb wieder her.
    """
    now = timezone.now()
    updated_count = GridDimmingSignal.objects.filter(home=home, is_active=True).update(
        is_active=False,
        cleared_at=now,
    )

    clear_steuve_limits(home)

    EventLog.objects.create(
        name="grid_dimming_cleared",
        user=home.user,
        context="global",
        metadata={"home_id": str(home.id), "cleared_signals": updated_count},
    )

    return {
        "status": "cleared",
        "home_id": str(home.id),
        "cleared_signals_count": updated_count,
        "message": "§ 14a EnWG Drosselung erfolgreich aufgehoben. Normalbetrieb wiederhergestellt.",
    }
