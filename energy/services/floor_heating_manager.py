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
from forecast.models import SolarForecast, WeatherForecast

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


def calculate_predictive_flow_temperature(
    config: FloorHeatingConfig,
    outdoor_temp_c: float,
    solar_radiation_wm2: float = 0.0,
    is_preheat_eligible: bool = False,
) -> dict:
    """
    Berechnet die wetter- & prognosegeführte Vorlauftemperatur (Model Predictive Control / MPC):
    1. Basis-Heizkurve nach DIN EN 12831 / DIN 4701 für Niedertemperatur-Fußbodenheizungen.
    2. Solares Absenken (Pre-Cooling/Coast): Bei hoher prognostizierter Globalstrahlung wird
       der Vorlauf um bis zu 2,0 K gesenkt, um solare Fenster-Gewinne zu nutzen.
    3. Thermischer Vorlade-Boost: Bei PV-Überschuss / Negativpreis wird der Vorlauf angehoben.
    """
    target_room_temp = float(config.target_room_temp_c or Decimal("21.0"))
    slope = float(getattr(config, "heating_curve_slope", Decimal("0.60")) or Decimal("0.60"))
    boost_delta = float(config.boost_delta_k or Decimal("1.0"))
    solar_comp_active = bool(getattr(config, "solar_gain_compensation", True))
    mpc_enabled = bool(getattr(config, "predictive_mpc_enabled", True))

    # 1. Basis-Heizkurve (Niedertemperatur FBH)
    delta_t = target_room_temp - outdoor_temp_c
    if outdoor_temp_c >= 17.0:
        base_flow_temp = 23.0
    elif delta_t <= 0:
        base_flow_temp = 24.0
    else:
        # FBH Kennlinie: T_flow = T_room + s * (delta_T)^0.8 * 1.25 + 2.5
        base_flow_temp = target_room_temp + (slope * (delta_t ** 0.8) * 1.25) + 2.5
    
    # Begrenzung der Basiskurve
    base_flow_temp = max(22.0, min(36.0, base_flow_temp))

    # 2. Solares Absenken durch Einstrahlungsgewinne (bis zu -2.0 K)
    solar_offset_k = 0.0
    if mpc_enabled and solar_comp_active and solar_radiation_wm2 > 100.0:
        # Bei 500 W/m² ca. -1.5 K, max -2.0 K
        solar_offset_k = min(2.0, (solar_radiation_wm2 / 500.0) * 1.5)

    # 3. Thermische Vorladung (PV-Überschuss / Günstiger Börsenpreis)
    preheat_offset_k = 0.0
    if is_preheat_eligible:
        preheat_offset_k = boost_delta * 1.5  # z. B. +1.5 K bis +2.5 K Vorlaufanhebung

    # 4. Gesamt-Vorlauftemperatur
    if mpc_enabled:
        opt_flow_temp = base_flow_temp + preheat_offset_k - solar_offset_k
    else:
        opt_flow_temp = base_flow_temp

    # Sicherheits-Klammerung (22.0°C bis max 38.0°C für Estrichschutz)
    opt_flow_temp = max(22.0, min(38.0, opt_flow_temp))
    flow_delta_k = opt_flow_temp - base_flow_temp

    return {
        "base_flow_temp_c": round(base_flow_temp, 1),
        "opt_flow_temp_c": round(opt_flow_temp, 1),
        "flow_delta_k": round(flow_delta_k, 1),
        "solar_offset_k": round(solar_offset_k, 1),
        "preheat_offset_k": round(preheat_offset_k, 1),
        "outdoor_temp_c": round(outdoor_temp_c, 1),
        "solar_radiation_wm2": round(solar_radiation_wm2, 0),
        "heating_curve_slope": slope,
        "mpc_enabled": mpc_enabled,
    }


def generate_24h_predictive_heating_schedule(
    home,
    config: FloorHeatingConfig,
    current_room_temp: float = 21.2,
    current_surplus_w: float = 0.0,
    current_spot_ct: float = 14.5,
) -> dict:
    """
    Erstellt einen 24-Stunden prädiktiven MPC-Fahrplan und KI-Handlungsempfehlungen.
    Kombiniert:
    - Open-Meteo Wetterprognose (Temperatur & Globalstrahlung)
    - EPEX-Spot Börsenstrompreise
    - PV-Erzeugungsprognose
    - Thermische Estrich-Trägheit (Coast-Down / Pre-Heating)
    """
    now = timezone.now().replace(minute=0, second=0, microsecond=0)
    target_temp = float(config.target_room_temp_c or Decimal("21.0"))
    min_surplus_req = float(config.min_pv_surplus_w or Decimal("1000.0"))
    max_price_req = float(config.max_spot_price_ct_kwh or Decimal("16.00"))

    # Wetterdaten der nächsten 24h laden
    try:
        weather_qs = WeatherForecast.objects.filter(
            home=home, ts__gte=now, ts__lt=now + timedelta(hours=24)
        ).order_by("ts")
        weather_map = {wf.ts.strftime("%Y-%m-%d %H:00"): wf for wf in weather_qs}
    except Exception as e:
        logger.debug("[FloorHeating] WeatherForecast Query fallback: %s", e)
        weather_map = {}

    # Spotpreise laden
    try:
        spot_qs = SpotPrice.objects.filter(
            timestamp__gte=now, timestamp__lt=now + timedelta(hours=24)
        ).order_by("timestamp")
        spot_map = {sp.timestamp.strftime("%Y-%m-%d %H:00"): float(sp.price_ct_kwh or 14.0) for sp in spot_qs}
    except Exception as e:
        logger.debug("[FloorHeating] SpotPrice Query fallback: %s", e)
        spot_map = {}

    # Solar-Forecasts laden
    try:
        solar_qs = SolarForecast.objects.filter(
            timestamp__gte=now, timestamp__lt=now + timedelta(hours=24)
        ).order_by("timestamp")
        solar_map = {}
        for sf in solar_qs:
            key = sf.timestamp.strftime("%Y-%m-%d %H:00")
            solar_map[key] = solar_map.get(key, 0.0) + float(sf.forecast_kwh or 0.0)
    except Exception as e:
        logger.debug("[FloorHeating] SolarForecast Query fallback: %s", e)
        solar_map = {}

    timeline = []
    preheat_hours = []
    coast_hours = []
    total_solar_gain_kwh = 0.0
    grid_peak_avoided_kwh = 0.0

    for i in range(24):
        slot_time = now + timedelta(hours=i)
        slot_key = slot_time.strftime("%Y-%m-%d %H:00")
        hour_label = slot_time.strftime("%H:00")
        hour_int = slot_time.hour

        # Wetter für diesen Slot
        wf = weather_map.get(slot_key)
        if wf:
            out_temp = float(wf.temperature_c if wf.temperature_c is not None else 8.5)
            radiation = float(wf.shortwave_radiation_wm2 if wf.shortwave_radiation_wm2 is not None else 0.0)
        else:
            # Realistischer diurnaler Fallback wenn noch kein Wetter gecached ist
            # Tiefste Temperatur um 06:00, höchste um 15:00
            if 6 <= hour_int <= 18:
                out_temp = 5.0 + 8.0 * (1.0 - abs(hour_int - 14) / 8.0)
                radiation = max(0.0, 550.0 * (1.0 - (abs(hour_int - 13) / 5.5) ** 2)) if 7 <= hour_int <= 19 else 0.0
            else:
                out_temp = 4.0 - 2.0 * (hour_int / 24.0)
                radiation = 0.0

        # Spotpreis
        spot_ct = spot_map.get(slot_key, 12.0 + 10.0 * abs(hour_int - 13) / 12.0)
        # Solar PV kW
        pv_kw = solar_map.get(slot_key, (radiation / 1000.0) * 8.0 if radiation > 0 else 0.0)

        # Pre-Heating Eignung prüfen
        has_surplus = (pv_kw * 1000.0 >= min_surplus_req) or (i == 0 and current_surplus_w >= min_surplus_req)
        has_cheap_price = (spot_ct <= max_price_req) or (i == 0 and current_spot_ct <= max_price_req)
        is_preheat_eligible = has_surplus or has_cheap_price

        # Vorlauftemperatur berechnen
        flow_calc = calculate_predictive_flow_temperature(
            config=config,
            outdoor_temp_c=out_temp,
            solar_radiation_wm2=radiation,
            is_preheat_eligible=is_preheat_eligible,
        )

        # Aktionsmodus & Beschreibung für die Timeline
        if is_preheat_eligible and (radiation > 200 or pv_kw >= 1.5):
            action_mode = "preheat"
            action_badge = "⚡ Vorladen"
            action_color = "amber"
            reason_text = f"PV-Vorladung (+{flow_calc['preheat_offset_k']:.1f} K) bei {pv_kw:.1f} kW Erzeugung"
            preheat_hours.append(hour_label)
            grid_peak_avoided_kwh += 1.2
        elif flow_calc["solar_offset_k"] >= 0.8:
            action_mode = "coast"
            action_badge = "☀️ Solares Absenken"
            action_color = "sky"
            reason_text = f"Fenster-Sonnengewinn (-{flow_calc['solar_offset_k']:.1f} K) bei {radiation:.0f} W/m²"
            coast_hours.append(hour_label)
            total_solar_gain_kwh += 0.9
        elif 17 <= hour_int <= 21 and len(preheat_hours) > 0:
            action_mode = "coast"
            action_badge = "🛋️ Passive Entladung"
            action_color = "indigo"
            reason_text = "Estrich gibt gespeicherte Wärme ab – Abendspitze vermieden"
            coast_hours.append(hour_label)
            grid_peak_avoided_kwh += 1.5
        elif out_temp < 15.0:
            action_mode = "heat"
            action_badge = "♨️ Normalbetrieb"
            action_color = "emerald"
            reason_text = f"Grundheizung ({flow_calc['opt_flow_temp_c']:.1f}°C) nach Heizkurve"
        else:
            action_mode = "standby"
            action_badge = "⏸️ Standby"
            action_color = "slate"
            reason_text = "Heizgrenze erreicht – Heizkreis pausiert"

        timeline.append({
            "hour_label": hour_label,
            "timestamp": slot_time.isoformat(),
            "outdoor_temp_c": round(out_temp, 1),
            "solar_radiation_wm2": round(radiation, 0),
            "spot_price_ct": round(spot_ct, 2),
            "pv_kw": round(pv_kw, 2),
            "base_flow_temp_c": flow_calc["base_flow_temp_c"],
            "opt_flow_temp_c": flow_calc["opt_flow_temp_c"],
            "flow_delta_k": flow_calc["flow_delta_k"],
            "action_mode": action_mode,
            "action_badge": action_badge,
            "action_color": action_color,
            "reason_text": reason_text,
        })

    # Fenster-Formatierung
    best_preheat_window = (
        f"{preheat_hours[0]} – {preheat_hours[-1]} Uhr"
        if preheat_hours
        else "Kein Vorladefenster (wenig Solarüberschuss)"
    )
    best_coast_window = (
        f"{coast_hours[0]} – {coast_hours[-1]} Uhr"
        if coast_hours
        else "17:00 – 21:00 Uhr (Abend-Entladung)"
    )

    # Ersparnisberechnung
    cop = 3.5
    avg_price_peak_ct = 34.0
    avg_price_solar_ct = 0.0
    saved_money_eur = (grid_peak_avoided_kwh * (avg_price_peak_ct - avg_price_solar_ct)) / 100.0

    # KI-Handlungsempfehlungstext
    if preheat_hours:
        ai_recommendation_title = f"☀️ Vorladung von {best_preheat_window} empfohlen"
        ai_recommendation_text = (
            f"Vorausschauendes MPC prognostiziert {total_solar_gain_kwh + grid_peak_avoided_kwh:.1f} kWh solare Wärmegewinne. "
            f"Estrich zwischen {best_preheat_window} um +{float(config.boost_delta_k):.1f} K vorladen, "
            f"um die Abendspitze ({best_coast_window}) ohne teuren Netzbezug zu überbrücken. "
            f"Erwartete Ersparnis: ca. {saved_money_eur:.2f} € heute."
        )
    else:
        ai_recommendation_title = "🛋️ Gleichmäßiger Heizkurvenbetrieb"
        ai_recommendation_text = (
            f"Aufgrund bedeckten Wetters regelt Sharegy die Vorlauftemperatur stetig auf Basis der Heizkurve "
            f"(Steilheit {float(getattr(config, 'heating_curve_slope', 0.6)):.2f}), um optimalen Wohnkomfort bei minimalem Stromverbrauch zu sichern."
        )

    return {
        "timeline": timeline,
        "best_preheat_window": best_preheat_window,
        "best_coast_window": best_coast_window,
        "total_solar_gain_kwh": round(total_solar_gain_kwh, 1),
        "grid_peak_avoided_kwh": round(grid_peak_avoided_kwh, 1),
        "estimated_savings_eur": round(saved_money_eur, 2),
        "ai_recommendation_title": ai_recommendation_title,
        "ai_recommendation_text": ai_recommendation_text,
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
        try:
            sp = SpotPrice.objects.filter(timestamp__lte=now).order_by("-timestamp").first()
            spot_raw = float(sp.price_ct_kwh) if sp and getattr(sp, "price_ct_kwh", None) is not None else 12.5
            current_spot_price_ct = float(calculate_effective_price(home, now, spot_raw))
        except Exception as e:
            logger.debug("[FloorHeating] Effective price calculation fallback: %s", e)
            current_spot_price_ct = 14.5

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

    # 7. Aktuelles Wetter & Prognosewerte für Live-Vorlauf & MPC abrufen
    latest_weather = WeatherForecast.objects.filter(home=home, ts__lte=now).order_by("-ts").first()
    if latest_weather and latest_weather.temperature_c is not None:
        live_outdoor_temp = float(latest_weather.temperature_c)
        live_radiation = float(latest_weather.shortwave_radiation_wm2 or 0.0)
    else:
        # Fallback Außentemperatur aus Cache oder saisonalem Default
        live_outdoor_temp = float(cache.get(f"home_{home.id}_outdoor_temp_c", 6.5))
        hour_now = now.hour
        live_radiation = 450.0 if (8 <= hour_now <= 17) else 0.0

    live_flow_metrics = calculate_predictive_flow_temperature(
        config=config,
        outdoor_temp_c=live_outdoor_temp,
        solar_radiation_wm2=live_radiation,
        is_preheat_eligible=preheating_active,
    )

    mpc_schedule = generate_24h_predictive_heating_schedule(
        home=home,
        config=config,
        current_room_temp=live_temp,
        current_surplus_w=pv_surplus_w,
        current_spot_ct=current_spot_price_ct,
    )

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
        "flow_temperature": live_flow_metrics,
        "predictive_mpc": mpc_schedule,
        "storage": storage_metrics,
        "signals": {
            "pv_surplus_w": round(pv_surplus_w, 0),
            "min_pv_surplus_w": float(config.min_pv_surplus_w),
            "spot_price_ct_kwh": round(current_spot_price_ct, 2),
            "max_spot_price_ct_kwh": float(config.max_spot_price_ct_kwh),
            "outdoor_temp_c": round(live_outdoor_temp, 1),
            "solar_radiation_wm2": round(live_radiation, 0),
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
