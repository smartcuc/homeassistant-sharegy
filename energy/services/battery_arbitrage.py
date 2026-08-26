########################################
# energy/services/battery_arbitrage.py
########################################

from datetime import datetime, timedelta
from zoneinfo import ZoneInfo
from django.utils import timezone
from collections import defaultdict

from devices.models import Device
from market.models_tariff import HomeTariff
from market.services_tariff import get_home_tariff, calculate_effective_price
from market.models import SpotPrice
from forecast.models import SolarForecast
from energy.services.battery_forecast import find_home_battery_storage


def calculate_battery_arbitrage(user, horizon_hours: int = 36) -> dict:
    """
    Berechnet das finanzielle Ertragspotenzial fuer netzdienliches Laden (Grid-Charging Arbitrage)
    des Batteriespeichers bei dynamischen Börsenstromtarifen und Negativpreisen.
    Beruecksichtigt:
    - Speicherkapazitaet (kWh) und Ladeleistung (kW)
    - Wirkungsgrad (Roundtrip ~90%)
    - Min-Reserve (10%) und Max-SoC (100%)
    - 24h/36h Day-Ahead EPEX Spot-Preise
    - PV-Eigenertragsprognose (um PV-Überschuss immer Vorrang zu geben!)
    """
    home = user.homes.first() if hasattr(user, "homes") else None
    tz_name = home.timezone if home and home.timezone else "Europe/Berlin"
    tz = ZoneInfo(tz_name)

    now = timezone.now().astimezone(tz)
    start_hour = now.replace(minute=0, second=0, microsecond=0)
    end_hour = start_hour + timedelta(hours=horizon_hours)

    # 1. Batteriespeicher-Parameter laden
    batt_dev, has_batt, batt_params = find_home_battery_storage(home)
    capacity_kwh = float(batt_params.get("capacity_kwh", 10.0))
    current_soc_pct = float(batt_params.get("current_soc_pct", 45.0))
    min_soc_pct = float(batt_params.get("min_soc_reserve_pct", 10.0))
    max_soc_pct = float(batt_params.get("max_soc_pct", 100.0))
    max_charge_kw = float(batt_params.get("max_charge_kw", 4.6))
    c_eff = float(batt_params.get("charge_efficiency", 0.95))
    d_eff = float(batt_params.get("discharge_efficiency", 0.95))
    roundtrip_eff = c_eff * d_eff

    usable_capacity_kwh = capacity_kwh * ((max_soc_pct - min_soc_pct) / 100.0)
    current_energy_kwh = capacity_kwh * (current_soc_pct / 100.0)
    needed_to_full_kwh = max(0.0, (capacity_kwh * (max_soc_pct / 100.0)) - current_energy_kwh)

    # 2. Tarif & Spot-Preise laden
    today = now.date()
    tariff = get_home_tariff(home, today) if home else None
    tariff_type = tariff.tariff_type if tariff else HomeTariff.TARIFF_DYNAMIC

    spot_prices_qs = SpotPrice.objects.filter(
        timestamp__gte=start_hour,
        timestamp__lte=end_hour,
    ).order_by("timestamp")

    spot_map = {}
    for sp in spot_prices_qs:
        dt_local = sp.timestamp.astimezone(tz)
        spot_map[dt_local.replace(minute=0, second=0, microsecond=0)] = float(sp.price_eur_per_kwh) * 100.0

    # 3. PV-Forecast laden (um PV-Ueberschuss nicht durch Netzstrom zu blockieren)
    pv_map = defaultdict(float)
    if home:
        for gen in home.generator_systems.all():
            for s in gen.strings.all():
                for sf in SolarForecast.objects.filter(generator_string=s, timestamp__gte=start_hour, timestamp__lte=end_hour):
                    t_loc = sf.timestamp.astimezone(tz).replace(minute=0, second=0, microsecond=0)
                    pv_map[t_loc] += float(sf.expected_power_w or 0)

    # 4. Stunden-Slots aufbauen
    slots = []
    curr = start_hour
    hour_idx = 0

    while curr < end_hour and hour_idx < horizon_hours:
        base_spot_ct = spot_map.get(curr, 8.5 + (4.0 if 17 <= curr.hour <= 21 else (-3.0 if 1 <= curr.hour <= 5 else 0.0)))
        if tariff_type == HomeTariff.TARIFF_DYNAMIC:
            eff_ct = calculate_effective_price(home, curr, base_spot_ct) if home else (base_spot_ct + 17.59)
        else:
            eff_ct = float(tariff.static_price_eur_per_kwh * 100.0) if (tariff and tariff.static_price_eur_per_kwh) else 32.50

        pv_w = pv_map.get(curr, 0.0)
        is_solar_surplus = (pv_w > 1200.0)

        slots.append({
            "hour_idx": hour_idx,
            "timestamp": curr.isoformat(),
            "time_label": curr.strftime("%H:00"),
            "date_label": curr.strftime("%d.%m."),
            "hour": curr.hour,
            "spot_price_ct": round(base_spot_ct, 2),
            "effective_price_ct": round(eff_ct, 2),
            "pv_power_w": round(pv_w, 0),
            "is_solar_surplus": is_solar_surplus,
            "is_night": (curr.hour <= 5 or curr.hour >= 23),
            "action": "hold",
            "action_label": "Standby / Eigenstrom",
        })
        curr += timedelta(hours=1)
        hour_idx += 1

    if not slots:
        return {
            "has_battery": has_batt,
            "capacity_kwh": capacity_kwh,
            "current_soc_pct": current_soc_pct,
            "potential_annual_savings_eur": 0.0,
            "recommended_schedule": [],
        }

    # 5. Arbitrage-Optimierung: Günstigste Lade-Slots vs. Teuerste Entlade-Slots
    # Günstigste Slots ohne starken PV-Überschuss für Netzladung
    non_solar_slots = [s for s in slots if not s["is_solar_surplus"]]
    sorted_by_price = sorted(non_solar_slots, key=lambda s: s["effective_price_ct"])

    # Wieviele Stunden brauchen wir zum Laden? (z. B. 10 kWh / 3 kW = 3.3 h -> 3 Slots)
    charge_hours_needed = max(1, min(4, int(needed_to_full_kwh / max(1.0, max_charge_kw)) + 1))
    best_charge_slots = sorted_by_price[:charge_hours_needed]
    best_charge_indices = {s["hour_idx"] for s in best_charge_slots}

    # Teuerste Slots für Entladung (typischerweise Morgen- oder Abendspitze)
    expensive_slots = sorted(slots, key=lambda s: s["effective_price_ct"], reverse=True)
    best_discharge_slots = [s for s in expensive_slots if s["hour_idx"] not in best_charge_indices][:charge_hours_needed]
    best_discharge_indices = {s["hour_idx"] for s in best_discharge_slots}

    avg_charge_price_ct = sum(s["effective_price_ct"] for s in best_charge_slots) / len(best_charge_slots) if best_charge_slots else 20.0
    avg_discharge_price_ct = sum(s["effective_price_ct"] for s in best_discharge_slots) / len(best_discharge_slots) if best_discharge_slots else 35.0

    # Arbitrage-Spanne berechnen:
    # Gewinn = (Vermiedener Bezugspreis * Wirkungsgrad) - Ladekosten
    spread_ct = (avg_discharge_price_ct * roundtrip_eff) - avg_charge_price_ct
    is_arbitrage_profitable = (spread_ct > 3.5)  # Mindestens 3,5 ct/kWh Netto-Spanne nach Verlusten

    # Aktionen zuweisen
    for s in slots:
        if s["is_solar_surplus"]:
            s["action"] = "solar_charge"
            s["action_label"] = "Solar-Überschuss laden"
            s["color"] = "#10B981"
        elif is_arbitrage_profitable and s["hour_idx"] in best_charge_indices:
            s["action"] = "grid_charge"
            s["action_label"] = f"Netzladen ({s['effective_price_ct']} ct)"
            s["color"] = "#6366F1"
        elif s["hour_idx"] in best_discharge_indices:
            s["action"] = "discharge"
            s["action_label"] = f"Einspeisen/Haus ({s['effective_price_ct']} ct)"
            s["color"] = "#F59E0B"
        else:
            s["action"] = "hold"
            s["action_label"] = "Normalbetrieb"
            s["color"] = "#94A3B8"

    # Finanzielle Einsparung pro Zyklus & Jahr
    kwh_shifted = min(usable_capacity_kwh, charge_hours_needed * max_charge_kw)
    daily_profit_eur = max(0.0, round((kwh_shifted * spread_ct) / 100.0, 2)) if is_arbitrage_profitable else 0.0
    # Im Winter ~120 Arbitrage-Tage, im Sommer PV-Dominanz
    projected_monthly_savings_eur = round(daily_profit_eur * 22.0, 2)
    projected_yearly_savings_eur = round(daily_profit_eur * 150.0, 2)

    charge_window_label = f"{best_charge_slots[0]['time_label']} - {(datetime.fromisoformat(best_charge_slots[-1]['timestamp']) + timedelta(hours=1)).strftime('%H:00')}" if best_charge_slots else "Keine"
    discharge_window_label = f"{best_discharge_slots[0]['time_label']} - {(datetime.fromisoformat(best_discharge_slots[-1]['timestamp']) + timedelta(hours=1)).strftime('%H:00')}" if best_discharge_slots else "Keine"

    advice = []
    if is_arbitrage_profitable:
        advice.append(f"Günstiges Netzfenster: Lade den Speicher nachts von {charge_window_label} zu durchschnittlich {avg_charge_price_ct:.1f} ct/kWh.")
        advice.append(f"Peak-Entlastung: Nutze den gespeicherten Strom während der Verbrauchsspitze ({discharge_window_label}, Preis {avg_discharge_price_ct:.1f} ct/kWh).")
        advice.append(f"Ersparnis: Durch die Preisdifferenz von {spread_ct:.1f} ct/kWh sparst du ca. {daily_profit_eur:.2f} € pro Zyklus (~{projected_yearly_savings_eur:.0f} €/Jahr).")
    else:
        advice.append("Aktuell ist die Preisspreizung an der Strombörse zu gering für Netzladen. Reguläre PV-Optimierung ist heute rentabler.")

    return {
        "has_battery": has_batt,
        "battery_name": batt_params.get("battery_name", "Hausspeicher"),
        "capacity_kwh": capacity_kwh,
        "current_soc_pct": current_soc_pct,
        "usable_capacity_kwh": round(usable_capacity_kwh, 1),
        "roundtrip_efficiency_pct": round(roundtrip_eff * 100.0, 1),
        "is_arbitrage_profitable": is_arbitrage_profitable,
        "price_spread_ct_per_kwh": round(spread_ct, 2),
        "avg_charge_price_ct": round(avg_charge_price_ct, 2),
        "avg_discharge_price_ct": round(avg_discharge_price_ct, 2),
        "best_charge_window": charge_window_label,
        "best_discharge_window": discharge_window_label,
        "daily_profit_eur": daily_profit_eur,
        "projected_monthly_savings_eur": projected_monthly_savings_eur,
        "projected_yearly_savings_eur": projected_yearly_savings_eur,
        "advice": advice,
        "timeline": slots,
    }
