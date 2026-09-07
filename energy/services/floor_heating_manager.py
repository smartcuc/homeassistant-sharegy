"""
energy/services/floor_heating_manager.py

Intelligente Fußbodenheizungs- & Estrich-Vorladungs-Engine (Thermal Battery Dispatch).
Nutzt den Gebäudebeton / Estrich als thermischen Speicher (+0,5°C bis +1,5°C Vorladung
bei PV-Überschuss oder negativen / günstigen EPEX-Börsenstrompreisen).
"""

import logging
from decimal import Decimal
from datetime import timedelta
from django.utils import timezone
from django.core.cache import cache

from devices.models import Device, DeviceLatestMetric
from energy.models import FloorHeatingConfig
from market.models_tariff import HomeTariff
from market.services_tariff import get_home_tariff, calculate_effective_price
from market.models import SpotPrice
from forecast.models import SolarForecast

logger = logging.getLogger(__name__)


def find_or_create_floor_heating_config(home) -> FloorHeatingConfig | None:
    """
    Holt die bestehende FloorHeatingConfig oder führt ein Auto-Discovery
    auf Geräten mit 'heizung', 'floor', 'fussboden', 'estrich', 'hvac' oder 'pump' durch.
    """
    cfg = FloorHeatingConfig.objects.filter(home=home).first()
    if cfg:
        return cfg

    # Auto-Discovery nach passendem Relais / Sensor
    dev = Device.objects.filter(
        home=home, active=True, pending_delete=False
    ).filter(
        identifier__iregex=r'(heiz|floor|fussboden|estrich|hvac|pump|heat)'
    ).first()

    temp_dev = Device.objects.filter(
        home=home, active=True, pending_delete=False
    ).filter(
        identifier__iregex=r'(temp|sensor|thermo|climate|raum)'
    ).first()

    cfg = FloorHeatingConfig.objects.create(
        home=home,
        device=dev,
        temp_sensor_device=temp_dev,
        active=True,
        control_mode="autopilot",
        target_room_temp_c=Decimal("21.0"),
        boost_delta_k=Decimal("1.0"),
        max_floor_temp_c=Decimal("24.5"),
        min_pv_surplus_w=Decimal("1000.0"),
        max_spot_price_ct_kwh=Decimal("16.00"),
        estrich_area_sqm=Decimal("120.0"),
    )
    return cfg


def calculate_thermal_storage_metrics(config: FloorHeatingConfig, current_temp: float) -> dict:
    """
    Berechnet die physikalischen Speicherkennzahlen des Estrichs:
    - Masse m = Fläche * 0.07m * 2000 kg/m³
    - Thermische Kapazität C_th (kWh/K) = m * 1.0 kJ/(kg*K) / 3600
    - Gespeicherte thermische Energie Q_th (kWh)
    - Thermischer Ladezustand (SoC_th in %)
    """
    area_sqm = float(config.estrich_area_sqm or Decimal("120.0"))
    # 7cm Estrichdicke, 2000 kg/m³ Rohdichte
    estrich_mass_kg = area_sqm * 0.07 * 2000.0  # z. B. 16.800 kg bei 120 m²
    # 1.0 kJ/(kg·K) spezifische Wärmekapazität
    c_th_kwh_per_k = (estrich_mass_kg * 1.0) / 3600.0  # z. B. ~4.67 kWh/K reiner Estrich

    target_temp = float(config.target_room_temp_c)
    boost_delta = float(config.boost_delta_k)
    max_boost_temp = target_temp + boost_delta

    # Thermischer SoC: 0% bei target - 0.5°C, 100% bei target + boost_delta
    min_temp_bound = target_temp - 0.5
    soc_range = max_boost_temp - min_temp_bound
    if soc_range > 0:
        soc_pct = ((current_temp - min_temp_bound) / soc_range) * 100.0
        soc_pct = max(0.0, min(100.0, soc_pct))
    else:
        soc_pct = 50.0

    # Gespeicherte thermische Energie bezogen auf Basis-Solltemperatur
    temp_diff = current_temp - min_temp_bound
    stored_kwh_th = max(0.0, temp_diff * c_th_kwh_per_k)
    max_capacity_kwh_th = (max_boost_temp - min_temp_bound) * c_th_kwh_per_k

    # Äquivalente elektrische Energie bei WP COP 3.5
    cop = 3.5
    stored_kwh_el = stored_kwh_th / cop
    max_capacity_kwh_el = max_capacity_kwh_th / cop

    return {
        "estrich_mass_kg": round(estrich_mass_kg, 0),
        "thermal_capacity_kwh_k": round(c_th_kwh_per_k, 2),
        "thermal_soc_pct": round(soc_pct, 1),
        "stored_energy_kwh_th": round(stored_kwh_th, 1),
        "max_capacity_kwh_th": round(max_capacity_kwh_th, 1),
        "stored_energy_kwh_el": round(stored_kwh_el, 1),
        "max_capacity_kwh_el": round(max_capacity_kwh_el, 1),
    }


def evaluate_floor_heating(home, config: FloorHeatingConfig = None, force: bool = False) -> dict:
    """
    Haupt-Evaluierungsfunktion der Fußbodenheizungs- & Estrich-Engine.
    Prüft:
    1. Aktuelle Raum- & Estrichtemperatur
    2. PV-Überschuss ($P_\\text{surplus}$) & Börsenstrompreis ($P_\\text{spot}$)
    3. Sicherheitsgrenzen (Überhitzungsschutz $T_\\text{max}$, Mindesttemperatur)
    4. Anti-Cycling Mindestlaufzeit und Mindestruhezeit
    5. Aktorik-Schaltung
    """
    if config is None:
        config = find_or_create_floor_heating_config(home)

    if not config:
        return {"active": False, "reason": "Keine Konfiguration vorhanden"}

    now = timezone.now()

    # 1. Telemetrie & Temperatur erfassen
    live_temp = 21.2  # Fallback
    relay_device_id = config.device.id if config.device else None
    
    if config.temp_sensor_device:
        cached_t = cache.get(f"device:{config.temp_sensor_device.id}:temp_room") or \
                   cache.get(f"device:{config.temp_sensor_device.id}:temperature")
        if cached_t is not None:
            live_temp = float(cached_t)
        else:
            lm = DeviceLatestMetric.objects.filter(
                device=config.temp_sensor_device,
                metric_key__in=["temperature", "temp_c", "room_temp", "temp_room"]
            ).first()
            if lm and lm.value is not None:
                live_temp = float(lm.value)
    elif relay_device_id:
        cached_t = cache.get(f"device:{relay_device_id}:temp_room") or \
                   cache.get(f"device:{relay_device_id}:temperature")
        if cached_t is not None:
            live_temp = float(cached_t)

    # Aktueller Relais-Zustand (True = Heizkreis aktiv, False = Standby)
    current_relay_state = False
    if relay_device_id:
        current_relay_state = bool(cache.get(f"device_relay_state_{relay_device_id}", False))

    # Live-Power
    live_power_w = 0.0
    if relay_device_id:
        cached_p = cache.get(f"device:{relay_device_id}:latest_power") or \
                   cache.get(f"device:{relay_device_id}:power")
        if cached_p is not None:
            live_power_w = float(cached_p)
        elif current_relay_state:
            live_power_w = 1200.0  # Schätzwert wenn an

    # 2. Netz- & Markt-Signale
    # Solarüberschuss aus Cache oder Berechnung
    cached_surplus = cache.get(f"home_{home.id}_pv_surplus_w")
    if cached_surplus is not None:
        pv_surplus_w = float(cached_surplus)
    else:
        # Näherung über Live-Metriken
        pv_p = cache.get(f"home_{home.id}_pv_power_w", 0.0)
        home_load = cache.get(f"home_{home.id}_load_power_w", 0.0)
        pv_surplus_w = max(0.0, float(pv_p) - float(home_load))

    # Aktueller Börsenstrompreis
    cached_spot = cache.get("latest_spot_price_ct_kwh")
    if cached_spot is not None:
        current_spot_price_ct = float(cached_spot)
    else:
        sp = SpotPrice.objects.filter(timestamp__lte=now).order_by("-timestamp").first()
        spot_raw = float(sp.price_ct_kwh) if sp and hasattr(sp, "price_ct_kwh") else 12.5
        current_spot_price_ct = float(calculate_effective_price(home, now, spot_raw))

    # 3. Thermische Speicherkennzahlen
    storage_metrics = calculate_thermal_storage_metrics(config, live_temp)

    # 4. Entscheidungslogik
    target_temp = float(config.target_room_temp_c)
    boost_delta = float(config.boost_delta_k)
    max_floor_temp = float(config.max_floor_temp_c)
    min_surplus_req = float(config.min_pv_surplus_w)
    max_price_req = float(config.max_spot_price_ct_kwh)
    mode = config.control_mode

    desired_relay_state = current_relay_state
    preheating_active = False
    decision_reason = "Normalbetrieb"

    # A. Priorisierter Überhitzungsschutz
    if live_temp >= max_floor_temp:
        desired_relay_state = False
        preheating_active = False
        decision_reason = f"🛡️ Überhitzungsschutz aktiv ({live_temp:.1f}°C >= {max_floor_temp:.1f}°C). Heizung pausiert."

    # B. Priorisierter Untertemperaturschutz (Komfort-Garantie)
    elif live_temp < (target_temp - 0.5):
        desired_relay_state = True
        preheating_active = False
        decision_reason = f"❄️ Raumtemperatur ({live_temp:.1f}°C) unter Komfortschwelle ({target_temp - 0.5:.1f}°C). Heizung heizt auf."

    # C. Manuelle Steuerung
    elif mode == "manual":
        desired_relay_state = current_relay_state
        decision_reason = "Manuelle Steuerung aktiv (Automatik pausiert)."

    # D. Komfortbetrieb (Feste Solltemperatur ohne Vorladung)
    elif mode == "comfort":
        if live_temp < target_temp:
            desired_relay_state = True
            decision_reason = f"Komfort-Heizen auf Zieltemperatur {target_temp:.1f}°C."
        else:
            desired_relay_state = False
            decision_reason = f"Zieltemperatur {target_temp:.1f}°C erreicht."

    # E. Autopilot / PV-Only / Price-Saver (Smarte thermische Vorladung)
    else:
        has_solar_surplus = (pv_surplus_w >= min_surplus_req)
        has_cheap_price = (current_spot_price_ct <= max_price_req)
        max_preheat_temp = target_temp + boost_delta

        is_preheat_eligible = False
        if mode == "pv_only" and has_solar_surplus:
            is_preheat_eligible = True
            preheat_source = f"☀️ Solarüberschuss ({pv_surplus_w:.0f} W >= {min_surplus_req:.0f} W)"
        elif mode == "price_saver" and has_cheap_price:
            is_preheat_eligible = True
            preheat_source = f"💰 Günstiger Börsenpreis ({current_spot_price_ct:.1f} ct <= {max_price_req:.1f} ct)"
        elif mode == "autopilot" and (has_solar_surplus or has_cheap_price):
            is_preheat_eligible = True
            preheat_source = f"☀️ Solar ({pv_surplus_w:.0f} W)" if has_solar_surplus else f"💰 Börsenpreis ({current_spot_price_ct:.1f} ct)"

        if is_preheat_eligible and live_temp < max_preheat_temp:
            desired_relay_state = True
            preheating_active = True
            decision_reason = f"🔥 Thermische Estrich-Vorladung aktiv via {preheat_source}. Ziel: {max_preheat_temp:.1f}°C (Ist: {live_temp:.1f}°C)."
        elif live_temp >= target_temp:
            # Kein Vorlade-Bedarf & Basis-Temperatur erreicht -> Estrich gibt passiv Wärme ab
            desired_relay_state = False
            preheating_active = False
            decision_reason = f"🛋️ Passive Estrich-Entladung aktiv. Gespeicherte Wärme deckt Raumwärmebedarf ab ({live_temp:.1f}°C >= {target_temp:.1f}°C)."
        else:
            desired_relay_state = True
            preheating_active = False
            decision_reason = f"Heizbedarf zur Einhaltung der Solltemperatur {target_temp:.1f}°C."

    # 5. Anti-Cycling & Mindestlauf-/Ruhezeiten
    now_ts = now
    last_switched = config.last_switched_at
    if last_switched and not force and (live_temp < max_floor_temp):
        minutes_since_switch = (now_ts - last_switched).total_seconds() / 60.0
        if current_relay_state and not desired_relay_state:
            # Abschaltung gefordert -> Mindestlaufzeit prüfen
            if minutes_since_switch < config.min_run_minutes:
                desired_relay_state = True
                decision_reason += f" (Verdichter-/Pumpenschutz: Mindestlaufzeit {config.min_run_minutes}m, noch {config.min_run_minutes - minutes_since_switch:.1f}m)."
        elif not current_relay_state and desired_relay_state:
            # Einschaltung gefordert -> Mindestruhezeit prüfen
            if minutes_since_switch < config.min_rest_minutes:
                desired_relay_state = False
                decision_reason = f"⏳ Mindestruhezeit aktiv (noch {config.min_rest_minutes - minutes_since_switch:.1f}m bis Freigabe)."

    # 6. Aktorik anwenden & State persistieren
    if desired_relay_state != current_relay_state or force:
        actuate_floor_heating_relay(home, config, desired_relay_state)
        config.last_switched_at = now
        config.is_preheating_active = preheating_active
        config.save(update_fields=["last_switched_at", "is_preheating_active"])
    elif config.is_preheating_active != preheating_active:
        config.is_preheating_active = preheating_active
        config.save(update_fields=["is_preheating_active"])

    return {
        "active": config.active,
        "control_mode": config.control_mode,
        "control_mode_display": config.get_control_mode_display(),
        "is_preheating_active": preheating_active,
        "relay_state": desired_relay_state,
        "power_w": live_power_w if desired_relay_state else 0.0,
        "temperature": {
            "current_c": round(live_temp, 1),
            "target_c": float(config.target_room_temp_c),
            "boost_delta_k": float(config.boost_delta_k),
            "boost_target_c": float(config.target_room_temp_c + config.boost_delta_k),
            "max_floor_c": float(config.max_floor_temp_c),
        },
        "storage": storage_metrics,
        "signals": {
            "pv_surplus_w": round(pv_surplus_w, 0),
            "min_pv_surplus_w": float(config.min_pv_surplus_w),
            "spot_price_ct_kwh": round(current_spot_price_ct, 2),
            "max_spot_price_ct_kwh": float(config.max_spot_price_ct_kwh),
        },
        "decision_reason": decision_reason,
        "config_id": str(config.id),
        "device_id": relay_device_id,
        "device_name": config.device.name if config.device else "Fußbodenheizungs-Pumpe / Relais",
    }


def actuate_floor_heating_relay(home, config: FloorHeatingConfig, target_state: bool) -> bool:
    """
    Schaltet das Relais / Ventil der Fußbodenheizung über Redis-Cache & Outbound WebSocket JSON-RPC.
    """
    if not config.device:
        logger.debug("[FloorHeating] Kein Aktor-Gerät zugewiesen.")
        return False

    dev = config.device
    cache.set(f"device_relay_state_{dev.id}", target_state, timeout=86400)

    # WebSocket Push falls verbunden
    try:
        from asgiref.sync import async_to_sync
        from channels.layers import get_channel_layer
        channel_layer = get_channel_layer()
        if channel_layer:
            async_to_sync(channel_layer.group_send)(
                f"home_{home.id}",
                {
                    "type": "device_control_event",
                    "device_id": str(dev.id),
                    "action": "Switch.Set",
                    "params": {"id": 0, "on": target_state},
                }
            )
    except Exception as e:
        logger.debug("[FloorHeating] Channel-Layer Broadcast Fehler: %s", e)

    return True


def trigger_floor_heating_boost(home, duration_hours: float = 2.0) -> dict:
    """
    Löst einen sofortigen thermischen Estrich-Vorladeboost für X Stunden aus.
    """
    config = find_or_create_floor_heating_config(home)
    if not config:
        return {"status": "error", "message": "Konfiguration nicht gefunden"}

    # Temporären Boost-Key im Cache setzen
    boost_key = f"floor_heating_boost_{home.id}"
    cache.set(boost_key, True, timeout=int(duration_hours * 3600))

    # Aktorik sofort schalten
    actuate_floor_heating_relay(home, config, target_state=True)
    config.is_preheating_active = True
    config.last_switched_at = timezone.now()
    config.save(update_fields=["is_preheating_active", "last_switched_at"])

    return {
        "status": "success",
        "message": f"🔥 Thermischer Estrich-Vorladeboost für {duration_hours}h aktiviert.",
        "duration_hours": duration_hours,
        "expires_at": (timezone.now() + timedelta(hours=duration_hours)).isoformat(),
    }
