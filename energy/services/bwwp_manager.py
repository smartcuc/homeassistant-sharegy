"""
energy/services/bwwp_manager.py

Intelligente Regelungs-Engine für das Lastmanagement von Brauchwasserwärmepumpen (BWWP)
und Wärmepumpen mit SG-Ready Schnittstelle, Temperatur- & Leistungsüberwachung,
Verdichterschutz (Anti-Takten) und geschlossener Aktorik zu ioBroker & Home Assistant.
"""

import logging
from decimal import Decimal
from datetime import timedelta
from django.utils import timezone
from django.core.cache import cache
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync

from devices.models import Device, DeviceLatestMetric
from energy.models import BWWPLoadManagementConfig
from energy.ems.services import build_device_signals
from market.models_tariff import HomeTariff
from market.services_tariff import get_home_tariff, calculate_effective_price
from market.models import SpotPrice

logger = logging.getLogger(__name__)


def actuate_bwwp_relay(device: Device, target_state: bool, channel: int = 0) -> bool:
    """
    Sendet einen Schaltbefehl über den Django Channels Layer an alle verbundenen
    Clients (ioBroker, Home Assistant, Dashboard) und aktualisiert den Redis-Cache.
    """
    cmd = "on" if target_state else "off"
    cache.set(f"device_relay_state_{device.id}", target_state, timeout=86400)
    cache.set(f"device_switchable_{device.id}", True, timeout=86400)

    channel_layer = get_channel_layer()
    if channel_layer:
        try:
            async_to_sync(channel_layer.group_send)(
                f"device_{device.id}",
                {
                    "type": "relay_command",
                    "command": cmd,
                    "channel": channel,
                },
            )
            async_to_sync(channel_layer.group_send)(
                f"device_{device.identifier}",
                {
                    "type": "relay_command",
                    "command": cmd,
                    "channel": channel,
                },
            )
            if hasattr(device, "home") and device.home_id:
                async_to_sync(channel_layer.group_send)(
                    f"home_{device.home_id}_devices",
                    {
                        "type": "relay_command",
                        "device_id": device.id,
                        "identifier": device.identifier,
                        "command": cmd,
                        "channel": channel,
                    },
                )
        except Exception as e:
            logger.warning("[BWWP-Manager] Fehler beim Senden an Channels-Layer: %s", e)

    logger.info(
        "[BWWP-Manager] ⚡ SG-Ready Relais für %s geschaltet -> %s",
        device.identifier,
        cmd.upper(),
    )
    return target_state


def get_bwwp_telemetry(device: Device) -> dict:
    """
    Liest die aktuellen Telemetriewerte (Leistung, Temperatur, Relaiszustand)
    aus dem Redis-Live-Cache oder den DB-Snapshots aus.
    """
    # 1. Relais-Zustand
    relay_state = cache.get(f"device_relay_state_{device.id}")
    if relay_state is None:
        m = DeviceLatestMetric.objects.filter(
            device=device, metric_key__in=["relay_state", "switch", "state", "sg_ready"]
        ).first()
        if m and m.value is not None:
            relay_state = bool(m.value)
        else:
            relay_state = False

    # 2. Wassertemperatur (°C)
    temp_c = cache.get(f"device:{device.id}:temp_water")
    if temp_c is None:
        temp_c = cache.get(f"device:{device.id}:temperature")
    if temp_c is None:
        temp_c = cache.get(f"device:{device.id}:temp")
    if temp_c is None:
        temp_m = DeviceLatestMetric.objects.filter(
            device=device,
            metric_key__in=["temp_water", "temperature", "temp", "water_temp", "tank_temperature", "sensor_temp"]
        ).first()
        if temp_m and temp_m.value is not None:
            temp_c = float(temp_m.value)

    if temp_c is None:
        temp_c = 48.5
    else:
        temp_c = float(temp_c)

    # 3. Leistung (W)
    power_w = cache.get(f"device:{device.id}:latest_power")
    if power_w is None:
        power_w = cache.get(f"device:{device.id}:power")
    if power_w is None:
        p_m = DeviceLatestMetric.objects.filter(
            device=device,
            metric_key__in=["power", "power_w", "active_power", "load_power", "consumption_w"]
        ).first()
        if p_m and p_m.value is not None:
            power_w = float(p_m.value)
        else:
            power_w = 0.0
    else:
        power_w = float(power_w)

    return {
        "relay_state": bool(relay_state),
        "temperature_c": round(temp_c, 1),
        "power_w": round(power_w, 1),
    }


def find_or_create_bwwp_config(home) -> BWWPLoadManagementConfig | None:
    """
    Findet eine bestehende BWWP-Konfiguration für das Home oder sucht
    automatisch nach einem passenden Gerät (BWWP / Wärmepumpe).
    """
    from django.db.models import Q
    cfg = BWWPLoadManagementConfig.objects.filter(home=home).select_related("device").first()
    if cfg:
        return cfg

    # Auto-Discovery: Suche nach Geräten mit passendem Identifier oder Config-Rolle
    bwwp_device = Device.objects.filter(
        home=home,
        active=True,
        pending_delete=False,
    ).filter(
        Q(identifier__icontains="bwwp")
        | Q(identifier__icontains="brauchwasser")
        | Q(identifier__icontains="warmwasser")
        | Q(identifier__icontains="waermepumpe")
        | Q(identifier__icontains="heatpump")
        | Q(config__name__icontains="bwwp")
        | Q(config__name__icontains="brauchwasser")
        | Q(config__name__icontains="wärmepumpe")
        | Q(config__role__key__in=["heatpump", "bwwp", "heating", "consumer"])
    ).first()

    if bwwp_device:
        cfg = BWWPLoadManagementConfig.objects.create(
            home=home,
            device=bwwp_device,
            active=True,
            control_mode="hybrid",
        )
        return cfg

    return None



def evaluate_bwwp_load_management(home, config: BWWPLoadManagementConfig = None, force: bool = False) -> dict:
    """
    Zentrale Entscheidungs- & Regelungs-Engine für das BWWP Lastmanagement.
    Prüft physikalische Grenzwerte, PV-Überschuss, Börsenpreise und Verdichterschutz.
    """
    now = timezone.now()
    if not config:
        config = find_or_create_bwwp_config(home)

    if not config or not config.device:
        return {
            "status": "unconfigured",
            "message": "Keine Brauchwasserwärmepumpe konfiguriert.",
            "device": None,
        }

    device = config.device
    telemetry = get_bwwp_telemetry(device)
    temp_c = telemetry["temperature_c"]
    power_w = telemetry["power_w"]
    current_relay = telemetry["relay_state"]

    # 1. EMS-Signale (PV-Erzeugung, Überschuss, Batterie-SoC) ermitteln
    signals = build_device_signals(home.user)
    grid_export_w = float(signals["grid"].get("export", 0.0))
    grid_import_w = float(signals["grid"].get("import", 0.0))
    pv_production_w = float(signals["pv"].get("production", 0.0))
    battery_charge_w = float(signals["battery"].get("charge", 0.0))

    # Batterie-SoC prüfen
    soc_val = cache.get(f"home:{home.id}:battery_soc")
    if soc_val is None:
        try:
            from producer.models import StorageSystem
            storage = StorageSystem.objects.filter(home=home, active=True).first()
            if storage:
                soc_val = storage.get_live_soc()
        except Exception:
            pass
    battery_soc = float(soc_val) if soc_val is not None else 100.0

    # Verfügbarer PV-Überschuss
    available_surplus_w = grid_export_w
    if battery_soc >= float(config.battery_soc_reserve_pct):
        available_surplus_w += max(0.0, battery_charge_w * 0.5)

    # 2. Dynamischen Börsenstrompreis & Tarif prüfen
    today = now.date()
    tariff = get_home_tariff(home, today)
    spot_obj = SpotPrice.objects.filter(timestamp__lte=now).order_by("-timestamp").first()
    spot_price_eur = float(spot_obj.price_eur_per_kwh) if spot_obj else 0.10
    spot_price_ct = spot_price_eur * 100.0
    current_effective_price_ct = calculate_effective_price(home, now, spot_price_ct) if home else (spot_price_ct + 17.59)

    # 3. Laufzeit & Verdichter-Schutzzeiten (Anti-Takten) berechnen
    last_switch = config.last_switched_at or (now - timedelta(hours=2))
    elapsed_minutes = int((now - last_switch).total_seconds() / 60)

    min_run_time = int(config.min_run_time_minutes)
    min_cooldown = int(config.min_cooldown_minutes)

    t_min = float(config.min_temp_c)
    t_target = float(config.target_temp_c)
    t_boost = float(config.boost_temp_c)
    t_max_safety = float(config.max_safety_temp_c)
    min_surplus_w = float(config.min_pv_surplus_w)
    max_price_ct = float(config.max_price_threshold_ct)
    battery_reserve = float(config.battery_soc_reserve_pct)

    target_relay = current_relay
    sg_state = config.current_sg_state or "2_normal"
    reason = ""
    protection_active = False

    # =========================================================================
    # 4. ENTSCHEIDUNGSMATRIX
    # =========================================================================

    # Stufe 0: Manuelle Übersteuerung oder inaktiver Zustand
    if not config.active or config.control_mode == "manual":
        reason = "Automatisches Lastmanagement pausiert (Manueller Modus)."
        target_relay = current_relay
    elif config.manual_override_until and config.manual_override_until > now:
        reason = f"Manueller Override aktiv bis {config.manual_override_until.astimezone(timezone.get_current_timezone()).strftime('%H:%M')} Uhr."
        target_relay = current_relay

    # Stufe 1: Absoluter Überhitzungsschutz (Priorität 1)
    elif temp_c >= t_max_safety:
        target_relay = False
        sg_state = "1_lock"
        reason = f"🛑 Überhitzungsschutz: Wassertemperatur ({temp_c:.1f}°C) >= Maximalwert ({t_max_safety:.1f}°C)."

    # Stufe 2: Verdichterschutz (Mindestlaufzeit nach Einschalten)
    elif current_relay and elapsed_minutes < min_run_time and not force:
        target_relay = True
        protection_active = True
        remaining = min_run_time - elapsed_minutes
        reason = f"🔒 Verdichterschutz: Mindestlaufzeit aktiv (noch {remaining} Min. verbleibend)."

    # Stufe 3: Taktschutz (Mindestruhezeit nach Ausschalten)
    elif not current_relay and elapsed_minutes < min_cooldown and temp_c > t_min and not force:
        target_relay = False
        protection_active = True
        remaining = min_cooldown - elapsed_minutes
        reason = f"⏳ Taktschutz: Mindestpause aktiv (noch {remaining} Min. bis Neuanlauf)."

    # Stufe 4: Komfort-Sicherung (Temperatur unter Mindestgrenze)
    elif temp_c < t_min:
        target_relay = True
        sg_state = "4_force"
        reason = f"🔥 Komfort-Sicherung: Temperatur ({temp_c:.1f}°C) unter Minimum ({t_min:.1f}°C) -> Zwangsheizung aktiv."

    # Stufe 5: Regelung nach Modus (PV-Überschuss / Börsenpreis / Hybrid)
    else:
        is_surplus_eligible = (
            config.control_mode in ("pv_surplus", "hybrid")
            and available_surplus_w >= min_surplus_w
            and battery_soc >= battery_reserve
            and temp_c < t_boost
        )

        is_cheap_price_eligible = (
            config.control_mode in ("spot_price", "hybrid")
            and current_effective_price_ct <= max_price_ct
            and temp_c < t_boost
        )

        if is_surplus_eligible:
            target_relay = True
            sg_state = "3_boost"
            reason = f"☀️ PV-Überschuss ({available_surplus_w:.0f} W >= {min_surplus_w:.0f} W) & Akku ({battery_soc:.0f}%) -> SG-Ready Boost bis {t_boost:.0f}°C aktiv."

        elif is_cheap_price_eligible:
            target_relay = True
            sg_state = "3_boost"
            reason = f"⚡ Günstiger Börsenstrompreis ({current_effective_price_ct:.1f} ct/kWh <= {max_price_ct:.1f} ct) -> SG-Ready Boost aktiv."

        elif temp_c >= t_boost:
            target_relay = False
            sg_state = "2_normal"
            reason = f"✨ Boost-Solltemperatur erreicht ({temp_c:.1f}°C >= {t_boost:.1f}°C) -> SG-Ready Normalbetrieb."

        elif temp_c >= t_target:
            target_relay = False
            sg_state = "2_normal"
            reason = f"✅ Standard-Solltemperatur erreicht ({temp_c:.1f}°C >= {t_target:.1f}°C) & kein PV-Überschuss."

        else:
            target_relay = False
            sg_state = "2_normal"
            reason = f"⚖️ Temperatur ({temp_c:.1f}°C) im Sollbereich. Warte auf PV-Überschuss oder günstigen Tarif."

    # =========================================================================
    # 5. AKTORIK AUSFÜHREN (WSS / CHANNELS)
    # =========================================================================
    state_changed = (target_relay != current_relay)

    if state_changed or force:
        actuate_bwwp_relay(device, target_relay)
        config.last_switched_at = now
        telemetry["relay_state"] = target_relay

    config.current_sg_state = sg_state
    config.last_decision_reason = reason
    config.save(update_fields=["current_sg_state", "last_decision_reason", "last_switched_at", "updated_at"])

    # 6. Status-Dictionary für Frontend & API
    result_data = {
        "status": "active" if config.active else "disabled",
        "home_id": home.id,
        "device_id": device.id,
        "device_name": device.name,
        "identifier": device.identifier,
        "control_mode": config.control_mode,
        "control_mode_display": config.get_control_mode_display(),
        "telemetry": telemetry,
        "current_sg_state": sg_state,
        "current_sg_state_display": config.get_current_sg_state_display(),
        "relay_state": telemetry["relay_state"],
        "state_changed": state_changed,
        "decision_reason": reason,
        "protection_active": protection_active,
        "metrics": {
            "water_temperature_c": temp_c,
            "power_w": power_w,
            "pv_production_w": pv_production_w,
            "available_surplus_w": available_surplus_w,
            "battery_soc_pct": battery_soc,
            "grid_price_ct": round(current_effective_price_ct, 2),
        },
        "thresholds": {
            "min_temp_c": t_min,
            "target_temp_c": t_target,
            "boost_temp_c": t_boost,
            "max_safety_temp_c": t_max_safety,
            "min_pv_surplus_w": min_surplus_w,
            "max_price_threshold_ct": max_price_ct,
            "battery_soc_reserve_pct": battery_reserve,
            "min_run_time_minutes": min_run_time,
            "min_cooldown_minutes": min_cooldown,
        },
        "last_switched_at": config.last_switched_at.isoformat() if config.last_switched_at else None,
        "evaluated_at": now.isoformat(),
    }

    cache.set(f"bwwp_load_mgmt_status_{home.id}", result_data, timeout=300)
    return result_data
