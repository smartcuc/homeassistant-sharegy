"""
energy/services/dispatch_hub.py

Zentrale Lastmanagement- & Dispatch-Engine für das gesamte Smart Home.
Koordiniert Prioritäten-Kaskade (Merit-Order), Live-Leistungsbudget, 24h-Fahrplan
und steuerbare Großverbraucher (BWWP, Speicher, Wallbox, Pool, Klima, Plugs, Heizstab).
"""

import logging
from decimal import Decimal
from datetime import timedelta
from django.utils import timezone
from django.core.cache import cache
from collections import defaultdict
from zoneinfo import ZoneInfo

from devices.models import Device, DeviceLatestMetric
from energy.models import LoadPriorityConfig, LoadConsumerConfig, BWWPLoadManagementConfig
from energy.ems.services import build_device_signals
from energy.services.bwwp_manager import evaluate_bwwp_load_management, find_or_create_bwwp_config, actuate_bwwp_relay
from market.models_tariff import HomeTariff
from market.services_tariff import get_home_tariff, calculate_effective_price
from market.models import SpotPrice
from forecast.models import SolarForecast

logger = logging.getLogger(__name__)


def get_or_create_priority_config(home) -> LoadPriorityConfig:
    """Holt oder initialisiert die Prioritäten-Kaskade für das Home."""
    cfg, _ = LoadPriorityConfig.objects.get_or_create(
        home=home,
        defaults={
            "master_mode": "autopilot",
            "priority_order": ["battery", "bwwp", "wallbox", "heatpump", "pool", "ac", "appliances", "heating_rod"],
            "min_pv_headroom_w": Decimal("200.0"),
            "auto_dispatch_enabled": True,
        }
    )
    return cfg


def get_all_load_consumers(home) -> list:
    """
    Sammelt alle steuerbaren Lasten des Haushalts (BWWP, Wallbox, Speicher,
    Pool, Klimaanlage, Haushaltsgeräte, Heizstab) mit Live-Status und Aktorik-Zustand.
    """
    consumers = []

    # 1. 🔋 Heimspeicher
    try:
        from producer.models import StorageSystem
        for ss in StorageSystem.objects.filter(home=home, active=True):
            live_soc = ss.get_live_soc() or 65.0
            live_power = ss.get_live_power() or 0.0
            consumers.append({
                "id": f"battery_{ss.id}",
                "category": "battery",
                "category_label": "Heimspeicher & Arbitrage",
                "name": ss.name or "Batteriespeicher",
                "icon": "🔋",
                "power_w": abs(float(live_power)),
                "is_active": True,
                "status_state": "charging" if live_power > 50 else ("discharging" if live_power < -50 else "idle"),
                "status_label": f"{live_soc:.0f}% SoC · {'Laden' if live_power > 50 else ('Entladen' if live_power < -50 else 'Bereit')}",
                "mode": ss.control_mode or "self_consumption",
                "details": {
                    "soc_pct": round(live_soc, 1),
                    "capacity_kwh": float(ss.capacity_kwh or 10.0),
                    "power_kw": round(abs(live_power) / 1000.0, 2),
                },
                "quick_action": "charge_now",
                "quick_action_label": "⚡ Grid-Charge (1h)",
            })
    except Exception as e:
        logger.debug("[Dispatch-Hub] Speicher laden: %s", e)

    # 2. ♨️ BWWP & Wärmepumpe
    bwwp_cfg = find_or_create_bwwp_config(home)
    if bwwp_cfg and bwwp_cfg.device:
        bwwp_eval = evaluate_bwwp_load_management(home, config=bwwp_cfg, force=False)
        telemetry = bwwp_eval.get("telemetry", {})
        sg_state = bwwp_eval.get("current_sg_state", "2_normal")
        consumers.append({
            "id": f"bwwp_{bwwp_cfg.device.id}",
            "device_id": bwwp_cfg.device.id,
            "category": "bwwp",
            "category_label": "Brauchwasserwärmepumpe",
            "name": bwwp_cfg.device.name,
            "icon": "♨️",
            "power_w": float(telemetry.get("power_w", 0.0)),
            "is_active": bwwp_cfg.active,
            "status_state": "boost" if sg_state == "3_boost" else ("on" if telemetry.get("relay_state") else "standby"),
            "status_label": f"{telemetry.get('temperature_c', 48.5)}°C · {bwwp_eval.get('current_sg_state_display', 'Normal')}",
            "mode": bwwp_cfg.control_mode,
            "details": {
                "temp_c": telemetry.get("temperature_c", 48.5),
                "target_temp_c": float(bwwp_cfg.target_temp_c),
                "boost_temp_c": float(bwwp_cfg.boost_temp_c),
                "sg_state": sg_state,
                "reason": bwwp_eval.get("decision_reason", ""),
            },
            "quick_action": "boost_bwwp",
            "quick_action_label": "🚀 Boost (1h)",
        })

    # 3. 🚗 Wallbox / E-Auto
    try:
        from devices.models_ocpp import ChargingStation
        for cs in ChargingStation.objects.filter(home=home):
            is_charging = (cs.status == "Charging")
            power_kw = float(cs.max_charge_power_kw or 11.0) if is_charging else 0.0
            consumers.append({
                "id": f"wallbox_{cs.id}",
                "category": "wallbox",
                "category_label": "Wallbox & E-Auto",
                "name": cs.name or f"Wallbox {cs.charge_point_id}",
                "icon": "🚗",
                "power_w": power_kw * 1000.0,
                "is_active": True,
                "status_state": "charging" if is_charging else "connected" if cs.status == "Preparing" else "available",
                "status_label": f"{cs.get_status_display()} ({power_kw:.1f} kW)",
                "mode": cs.charging_mode or "solar_surplus",
                "details": {
                    "charge_point_id": cs.charge_point_id,
                    "max_power_kw": float(cs.max_charge_power_kw or 11.0),
                    "min_current_a": cs.min_charge_current_a,
                },
                "quick_action": "fast_charge",
                "quick_action_label": "⚡ Schnellladen",
            })
    except Exception as e:
        logger.debug("[Dispatch-Hub] Wallbox laden: %s", e)



    # 4. Weitere flexible Großverbraucher aus LoadConsumerConfig
    custom_consumers = LoadConsumerConfig.objects.filter(home=home, is_active=True).select_related("device")
    for cc in custom_consumers:
        dev = cc.device
        relay_state = cache.get(f"device_relay_state_{dev.id}", False)
        live_power = cache.get(f"device:{dev.id}:latest_power") or cache.get(f"device:{dev.id}:power") or 0.0

        icon_map = {
            "pool": "🏊",
            "ac": "❄️",
            "appliances": "🧺",
            "heating_rod": "⚡",
            "other": "🔌",
        }

        consumers.append({
            "id": f"custom_{cc.id}",
            "device_id": dev.id,
            "category": cc.category,
            "category_label": cc.get_category_display(),
            "name": cc.name or dev.name,
            "icon": icon_map.get(cc.category, "🔌"),
            "power_w": float(live_power) if relay_state else 0.0,
            "is_active": cc.is_active,
            "status_state": "on" if relay_state else "standby",
            "status_label": f"{'Aktiv' if relay_state else 'Standby'} ({float(live_power):.0f} W)",
            "mode": cc.mode,
            "details": {
                "rated_power_w": float(cc.rated_power_w),
                "min_daily_runtime_min": cc.min_daily_runtime_minutes,
                "runtime_completed_min": cc.daily_runtime_completed_minutes,
                "custom_settings": cc.custom_settings,
            },
            "quick_action": f"toggle_{cc.category}",
            "quick_action_label": "▶️ Jetzt starten (1h)" if not relay_state else "⏹️ Stoppen",
        })

    # Auto-Discovery: Falls noch keine spezifischen LoadConsumerConfigs angelegt sind, erstelle Beispiel-Pool / Klima / Plugs
    if not custom_consumers.exists():
        # Suche nach Geräten mit Identifier wie "pool", "shelly_plug", "klima", "ac"
        discovered_devs = Device.objects.filter(
            home=home, active=True, pending_delete=False
        ).exclude(
            id__in=[c.get("device_id") for c in consumers if "device_id" in c]
        )

        for d in discovered_devs:
            ident = (d.identifier or "").lower()
            d_name = (d.name or "").lower()
            cat = None
            if "pool" in ident or "pool" in d_name or "pumpe" in d_name:
                cat = "pool"
            elif "ac" in ident or "klima" in ident or "climate" in ident:
                cat = "ac"
            elif any(k in ident or k in d_name for k in ["waschmaschine", "spülmaschine", "trockner", "plug", "steckdose"]):
                cat = "appliances"
            elif "heizstab" in ident or "ohmpilot" in ident or "rod" in ident:
                cat = "heating_rod"

            if cat:
                new_cc = LoadConsumerConfig.objects.create(
                    home=home,
                    device=d,
                    category=cat,
                    name=d.name or d.identifier,
                    rated_power_w=Decimal("800.0") if cat == "pool" else (Decimal("1500.0") if cat == "ac" else Decimal("2000.0")),
                    mode="hybrid",
                    min_daily_runtime_minutes=300 if cat == "pool" else 0,
                )
                relay_state = cache.get(f"device_relay_state_{d.id}", False)
                consumers.append({
                    "id": f"custom_{new_cc.id}",
                    "device_id": d.id,
                    "category": cat,
                    "category_label": new_cc.get_category_display(),
                    "name": new_cc.name,
                    "icon": "🏊" if cat == "pool" else ("❄️" if cat == "ac" else "🧺"),
                    "power_w": 0.0,
                    "is_active": True,
                    "status_state": "on" if relay_state else "standby",
                    "status_label": "Standby (Bereit für PV-Überschuss)",
                    "mode": "hybrid",
                    "details": {
                        "rated_power_w": float(new_cc.rated_power_w),
                        "min_daily_runtime_min": new_cc.min_daily_runtime_minutes,
                        "runtime_completed_min": 0,
                    },
                    "quick_action": f"toggle_{cat}",
                    "quick_action_label": "▶️ Jetzt starten (1h)",
                })

    return consumers


def compute_24h_dispatch_schedule(home, consumers: list, priority_order: list) -> list:
    """
    Berechnet die 24h-Fahrplan-Timeline für alle Verbraucher unter Berücksichtigung
    der stündlichen Solarprognose, Spotmarkt-Preise und der Prioritäten-Kaskade.
    """
    tz_name = home.timezone if home and home.timezone else "Europe/Berlin"
    tz = ZoneInfo(tz_name)
    now = timezone.now().astimezone(tz)
    start_hour = now.replace(minute=0, second=0, microsecond=0)

    # 1. Solarprognose & Börsenpreise für die nächsten 24 Stunden laden
    pv_map = defaultdict(float)
    for generator in home.generator_systems.all():
        for string in generator.strings.all():
            for row in SolarForecast.objects.filter(
                generator_string=string,
                timestamp__gte=start_hour,
                timestamp__lt=start_hour + timedelta(hours=24)
            ).values("timestamp", "forecast_kwh"):
                ts_loc = row["timestamp"].astimezone(tz).replace(minute=0, second=0, microsecond=0)
                pv_map[ts_loc] += float(row["forecast_kwh"] or 0)

    spot_map = {}
    for sp in SpotPrice.objects.filter(
        timestamp__gte=start_hour,
        timestamp__lt=start_hour + timedelta(hours=24)
    ).values("timestamp", "price_eur_per_kwh"):
        ts_loc = sp["timestamp"].astimezone(tz).replace(minute=0, second=0, microsecond=0)
        spot_map[ts_loc] = float(sp["price_eur_per_kwh"] or 0.10) * 100.0

    timeline = []

    for i in range(24):
        slot_dt = start_hour + timedelta(hours=i)
        hour_val = slot_dt.hour

        # PV-Erzeugung (kW)
        pv_kw = round(pv_map.get(slot_dt, 0.0), 2)
        if pv_kw == 0.0 and 6 <= hour_val <= 20:
            pv_kw = round(max(0.0, 6.0 * (1.0 - ((hour_val - 13) / 7.0) ** 2)), 2)

        # Börsenpreis
        spot_ct = spot_map.get(slot_dt, 12.0 + (5.0 if (7 <= hour_val <= 9 or 18 <= hour_val <= 21) else (-2.0 if 1 <= hour_val <= 5 else 0.0)))
        effective_price_ct = calculate_effective_price(home, slot_dt, spot_ct) if home else (spot_ct + 17.59)

        # Baseline Haushalt
        base_load_kw = 0.35
        remaining_surplus_kw = max(0.0, pv_kw - base_load_kw)

        # Zuteilung der Lasten nach Prioritäten-Kaskade
        scheduled_devices = []
        is_cheap_spot = effective_price_ct <= 20.0 or (1 <= hour_val <= 5)

        for cat in priority_order:
            matching = [c for c in consumers if c.get("category") == cat]
            for dev in matching:
                req_kw = float(dev.get("details", {}).get("rated_power_w", 1000.0)) / 1000.0
                if cat == "battery":
                    req_kw = 2.5
                elif cat == "wallbox":
                    req_kw = 7.4
                elif cat == "bwwp":
                    req_kw = 0.65

                # Entscheidung ob das Gerät in dieser Stunde laufen soll
                should_run = False
                run_reason = ""

                if remaining_surplus_kw >= (req_kw * 0.5):
                    should_run = True
                    remaining_surplus_kw = max(0.0, remaining_surplus_kw - req_kw)
                    run_reason = "☀️ PV-Überschuss"
                elif is_cheap_spot and cat in ("battery", "wallbox", "bwwp", "appliances"):
                    should_run = True
                    run_reason = "⚡ Börsen-Tiefstpreis"

                if should_run:
                    scheduled_devices.append({
                        "device_id": dev["id"],
                        "name": dev["name"],
                        "category": cat,
                        "icon": dev["icon"],
                        "power_kw": round(req_kw, 2),
                        "reason": run_reason,
                    })

        timeline.append({
            "timestamp": slot_dt.isoformat(),
            "time_label": slot_dt.strftime("%H:00"),
            "hour": hour_val,
            "pv_kw": pv_kw,
            "price_ct": round(effective_price_ct, 1),
            "surplus_kw": round(remaining_surplus_kw, 2),
            "scheduled_devices": scheduled_devices,
            "total_controlled_kw": round(sum(d["power_kw"] for d in scheduled_devices), 2),
        })

    return timeline


def get_load_management_hub_data(home) -> dict:
    """
    Haupt-Aggregationsfunktion für das Smart Load Management & Dispatch Dashboard.
    """
    now = timezone.now()
    prio_cfg = get_or_create_priority_config(home)
    consumers = get_all_load_consumers(home)

    # 1. Live-Leistungsbudget
    signals = build_device_signals(home.user)
    grid_export_w = float(signals["grid"].get("export", 0.0))
    grid_import_w = float(signals["grid"].get("import", 0.0))
    pv_production_w = float(signals["pv"].get("production", 0.0))
    house_load_w = float(signals["load"].get("consumption", 0.0))
    battery_charge_w = float(signals["battery"].get("charge", 0.0))

    # Batterie-SoC
    soc_val = cache.get(f"home:{home.id}:battery_soc")
    if soc_val is None:
        try:
            from producer.models import StorageSystem
            storage = StorageSystem.objects.filter(home=home, active=True).first()
            if storage:
                soc_val = storage.get_live_soc()
        except Exception:
            pass
    battery_soc = float(soc_val) if soc_val is not None else 65.0

    # Spotpreis
    spot_obj = SpotPrice.objects.filter(timestamp__lte=now).order_by("-timestamp").first()
    spot_ct = (float(spot_obj.price_eur_per_kwh) * 100.0) if spot_obj else 12.5
    effective_price_ct = calculate_effective_price(home, now, spot_ct) if home else (spot_ct + 17.59)

    # Netto-Überschuss
    available_surplus_w = grid_export_w
    if battery_soc >= 80.0:
        available_surplus_w += battery_charge_w

    # 2. 24h-Fahrplan berechnen
    dispatch_schedule = compute_24h_dispatch_schedule(home, consumers, prio_cfg.priority_order)

    # 3. Zusammenfassung der gesteuerten Lasten
    total_controlled_power_w = sum(c.get("power_w", 0.0) for c in consumers)
    active_running_count = sum(1 for c in consumers if c.get("power_w", 0.0) > 10.0 or c.get("status_state") in ("on", "boost", "charging"))

    return {
        "home_id": home.id,
        "home_name": home.name,
        "master_mode": prio_cfg.master_mode,
        "master_mode_display": prio_cfg.get_master_mode_display(),
        "auto_dispatch_enabled": prio_cfg.auto_dispatch_enabled,
        "priority_order": prio_cfg.priority_order,
        "live_budget": {
            "pv_production_w": round(pv_production_w, 0),
            "house_load_w": round(house_load_w, 0),
            "available_surplus_w": round(available_surplus_w, 0),
            "grid_import_w": round(grid_import_w, 0),
            "grid_export_w": round(grid_export_w, 0),
            "battery_soc_pct": round(battery_soc, 0),
            "current_price_ct": round(effective_price_ct, 1),
            "total_controlled_w": round(total_controlled_power_w, 0),
            "active_devices_count": active_running_count,
            "total_devices_count": len(consumers),
        },
        "consumers": consumers,
        "dispatch_schedule": dispatch_schedule,
        "evaluated_at": now.isoformat(),
    }


def execute_hub_device_action(home, category: str, action: str, device_id: str = None, params: dict = None) -> dict:
    """
    Führt Sofort-Aktionen (Quick Actions) für alle Verbraucher-Kategorien aus.
    """
    params = params or {}
    now = timezone.now()

    if category == "bwwp":
        bwwp_cfg = find_or_create_bwwp_config(home)
        if not bwwp_cfg:
            return {"error": "Keine BWWP vorhanden."}

        if action in ("boost", "boost_bwwp"):
            actuate_bwwp_relay(bwwp_cfg.device, True)
            bwwp_cfg.current_sg_state = "3_boost"
            bwwp_cfg.last_decision_reason = "🚀 Manueller Sofort-Boost aus Dispatch-Hub aktiviert."
            bwwp_cfg.manual_override_until = now + timedelta(minutes=60)
            bwwp_cfg.save()
            return {"status": "success", "message": "BWWP SG-Ready Boost für 60 Min. aktiviert."}

        elif action in ("normal", "auto"):
            bwwp_cfg.manual_override_until = None
            bwwp_cfg.save()
            evaluate_bwwp_load_management(home, config=bwwp_cfg, force=True)
            return {"status": "success", "message": "BWWP auf Automatik zurückgesetzt."}

    elif category in ("pool", "ac", "appliances", "heating_rod", "other"):
        # Custom Consumer
        if device_id:
            raw_id = device_id.replace("custom_", "")
            cc = LoadConsumerConfig.objects.filter(id=raw_id, home=home).first()
            if cc and cc.device:
                curr_state = cache.get(f"device_relay_state_{cc.device.id}", False)
                target_state = not curr_state if action == "toggle" else (action in ("on", "start", "boost"))
                actuate_bwwp_relay(cc.device, target_state)
                return {
                    "status": "success",
                    "device": cc.name,
                    "relay_state": target_state,
                    "message": f"{cc.name} {'eingeschaltet' if target_state else 'ausgeschaltet'}.",
                }

    elif category == "battery":
        try:
            from producer.models import StorageSystem
            ss = StorageSystem.objects.filter(home=home, active=True).first()
            if ss:
                ss.control_mode = "price_optimized" if action == "charge_now" else "self_consumption"
                ss.save(update_fields=["control_mode"])
                return {"status": "success", "message": f"Speicher-Modus auf {ss.get_control_mode_display()} gesetzt."}
        except Exception as e:
            logger.exception("Fehler bei Speicher-Aktion: %s", e)

    return {"status": "ignored", "message": "Aktion verarbeitet."}
