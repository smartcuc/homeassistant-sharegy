##############################
# energy/services/optimizer.py
##############################

from datetime import timedelta
from zoneinfo import ZoneInfo
from django.utils import timezone
from collections import defaultdict

from devices.models import Device
from market.models_tariff import HomeTariff
from market.services_tariff import get_home_tariff, calculate_effective_price
from market.models import SpotPrice
from forecast.models import SolarForecast


def get_optimizer_schedule(user, horizon_hours: int = 36) -> dict:
    """
    Berechnet die optimale Zeitfenster-Empfehlungsmatrix für 1h, 2h und 4h
    basierend auf der PV-Erzeugungsprognose und den dynamischen Börsenstromtarifen.
    """
    home = user.homes.first() if hasattr(user, "homes") else None
    tz_name = home.timezone if home and home.timezone else "Europe/Berlin"
    tz = ZoneInfo(tz_name)

    now = timezone.now().astimezone(tz)
    start_hour = now.replace(minute=0, second=0, microsecond=0)
    end_hour = start_hour + timedelta(hours=horizon_hours)

    today = now.date()
    tariff = get_home_tariff(home, today) if home else None
    tariff_type = tariff.tariff_type if tariff else HomeTariff.TARIFF_DYNAMIC
    feed_in_type = tariff.feed_in_tariff_type if tariff else HomeTariff.FEED_IN_STATIC

    # 1. Einspeisevergütung bestimmen
    if feed_in_type == HomeTariff.FEED_IN_NONE:
        base_feed_in_ct = 0.0
    elif feed_in_type == HomeTariff.FEED_IN_STATIC and tariff and tariff.feed_in_tariff_eur_per_kwh is not None:
        base_feed_in_ct = round(float(tariff.feed_in_tariff_eur_per_kwh) * 100, 2)
    else:
        base_feed_in_ct = 8.2  # Standard 8,2 ct/kWh

    # 2. PV-Forecast laden
    pv_forecast_map = defaultdict(float)
    has_pv = False

    if home:
        # Prüfen ob Erzeuger-Geräte existieren
        has_pv = Device.objects.filter(
            home=home,
            active=True,
            config__role__key__in=["producer", "pv", "solar"],
        ).exists()

        for generator in home.generator_systems.all():
            for string in generator.strings.all():
                forecast_qs = SolarForecast.objects.filter(
                    generator_string=string,
                    timestamp__gte=start_hour,
                    timestamp__lte=end_hour,
                ).values("timestamp", "forecast_kwh")
                for row in forecast_qs:
                    ts_local = row["timestamp"].astimezone(tz).replace(minute=0, second=0, microsecond=0)
                    pv_forecast_map[ts_local] += float(row["forecast_kwh"] or 0)

    # 3. Börsenpreise (SpotPrice) laden
    spot_prices_map = {}
    spot_qs = SpotPrice.objects.filter(
        timestamp__gte=start_hour - timedelta(hours=1),
        timestamp__lte=end_hour + timedelta(hours=1),
    ).values("timestamp", "price_eur_per_kwh")

    for sp in spot_qs:
        ts_local = sp["timestamp"].astimezone(tz).replace(minute=0, second=0, microsecond=0)
        spot_prices_map[ts_local] = float(sp["price_eur_per_kwh"] or 0.10) * 100.0

    # 4. 36h Timeline zusammenstellen & Opportunitätskosten berechnen
    timeline = []
    costs_list = []

    for i in range(horizon_hours):
        slot_dt = start_hour + timedelta(hours=i)
        hour_val = slot_dt.hour

        # PV-Leistung für diese Stunde
        pv_kw = round(pv_forecast_map.get(slot_dt, 0.0), 2)
        if pv_kw == 0.0 and has_pv:
            # Physikalische Sinuskurve als realistischer Fallback tagsüber
            if 6 <= hour_val <= 20:
                peak_factor = 7.5  # 7.5 kW Peak für 10 kWp
                pv_kw = round(max(0.0, peak_factor * (1.0 - ((hour_val - 13) / 7.0) ** 2)), 2)

        # Netzpreis bestimmen
        if tariff_type == HomeTariff.TARIFF_STATIC and tariff and tariff.static_price_eur_per_kwh:
            grid_price_ct = round(float(tariff.static_price_eur_per_kwh) * 100, 2)
        else:
            # Dynamisch
            spot_ct = spot_prices_map.get(slot_dt, 11.5 + 4.0 * (1.0 if (7 <= hour_val <= 9 or 18 <= hour_val <= 21) else ( -1.5 if 1 <= hour_val <= 5 else 0.0 )))
            grid_price_ct = calculate_effective_price(home, slot_dt, spot_ct) if home else round(spot_ct + 17.59, 2)

        # Opportunitätskosten:
        # Wenn PV-Überschuss vorliegt (> 1.5 kW), kostet die kWh nur die entgangene Einspeisevergütung
        is_surplus = pv_kw >= 1.5
        if is_surplus:
            effective_cost_ct = base_feed_in_ct
            solar_share_pct = min(100.0, round((pv_kw / max(pv_kw, 2.5)) * 100.0, 0))
        else:
            effective_cost_ct = grid_price_ct
            solar_share_pct = round((pv_kw / 2.5) * 100.0, 0) if pv_kw > 0 else 0.0

        costs_list.append(effective_cost_ct)

        timeline.append({
            "timestamp": slot_dt.isoformat(),
            "time_label": slot_dt.strftime("%H:00"),
            "date_label": slot_dt.strftime("%d.%m."),
            "hour": hour_val,
            "is_today": slot_dt.date() == today,
            "pv_kw": pv_kw,
            "grid_price_ct": grid_price_ct,
            "effective_cost_ct": round(effective_cost_ct, 2),
            "is_surplus": is_surplus,
            "solar_share_pct": solar_share_pct,
        })

    avg_cost = sum(costs_list) / len(costs_list) if costs_list else 28.0

    # Status-Farbe (Grün / Gelb / Rot) zuweisen
    for item in timeline:
        c = item["effective_cost_ct"]
        if item["is_surplus"] or c <= avg_cost * 0.75:
            item["status"] = "green"
            item["status_label"] = "Optimal (Günstig)"
        elif c <= avg_cost * 1.08:
            item["status"] = "yellow"
            item["status_label"] = "Akzeptabel"
        else:
            item["status"] = "red"
            item["status_label"] = "Teuer (Vermeiden)"

    # =========================================================================
    # 5. Multi-Dauer Sliding Window Search für 1h, 2h und 4h
    # =========================================================================
    typical_devices = {
        "1h": {
            "power_kw": 2.0,
            "device_name": "Waschmaschine / Geschirrspüler / Booster",
            "icon": "🧺",
            "category": "household",
        },
        "2h": {
            "power_kw": 3.0,
            "device_name": "Wärmepumpe / Wäschetrockner",
            "icon": "♨️",
            "category": "heating",
        },
        "4h": {
            "power_kw": 11.0,
            "device_name": "Wallbox (E-Auto) / Hausspeicher",
            "icon": "🚗",
            "category": "mobility",
        },
    }

    windows = {}

    for dur_key, dur_hours in [("1h", 1), ("2h", 2), ("4h", 4)]:
        evaluated_windows = []

        for idx in range(len(timeline) - dur_hours + 1):
            slice_items = timeline[idx : idx + dur_hours]
            slice_costs = [it["effective_cost_ct"] for it in slice_items]
            avg_window_cost = sum(slice_costs) / dur_hours
            solar_slots = sum(1 for it in slice_items if it["is_surplus"])
            avg_solar_share = sum(it["solar_share_pct"] for it in slice_items) / dur_hours

            start_item = slice_items[0]
            end_slot = slice_items[-1]
            end_time_label = (start_hour + timedelta(hours=idx + dur_hours)).strftime("%H:00")

            is_night = all(it["hour"] <= 6 or it["hour"] >= 22 for it in slice_items)
            is_solar = solar_slots >= (dur_hours // 2 + 1) or avg_solar_share >= 50.0

            source = "pv_surplus" if is_solar else ("spot_trough" if is_night else "grid_mixed")

            evaluated_windows.append({
                "start_idx": idx,
                "start_timestamp": start_item["timestamp"],
                "start_label": start_item["time_label"],
                "date_label": start_item["date_label"],
                "end_label": end_time_label,
                "avg_cost_ct": round(avg_window_cost, 2),
                "solar_share_pct": round(avg_solar_share, 0),
                "source": source,
                "is_night": is_night,
                "is_solar": is_solar,
            })

        # Sortieren nach Kosten
        evaluated_windows.sort(key=lambda w: w["avg_cost_ct"])

        best_overall = evaluated_windows[0]
        worst_window = evaluated_windows[-1]

        # Bestes Nacht-Fenster
        night_candidates = [w for w in evaluated_windows if w["is_night"]]
        best_night = night_candidates[0] if night_candidates else None

        # Ersparnis berechnen
        power_kw = typical_devices[dur_key]["power_kw"]
        total_kwh = power_kw * dur_hours
        price_diff_eur = max(0.0, (worst_window["avg_cost_ct"] - best_overall["avg_cost_ct"]) / 100.0)
        savings_eur = round(price_diff_eur * total_kwh, 2)

        # Handlungsempfehlungen generieren
        if best_overall["source"] == "pv_surplus":
            best_text = f"☀️ 100% Solarenergie verfügbar. Ideal für {typical_devices[dur_key]['device_name']} – spart ca. {savings_eur:.2f} € gegenüber Spitzenzeiten."
        else:
            best_text = f"⚡ Niedrigster Börsenstrompreis des Tages ({best_overall['avg_cost_ct']:.1f} ct/kWh). Optimaler Zeitpunkt zum Netzbezug oder Akku-Laden."

        if best_night:
            night_text = f"🌙 Günstigster Nacht-Spotmarkt ({best_night['avg_cost_ct']:.1f} ct/kWh). Perfekt für verzögerte Gerätestarts oder E-Auto-Nachtladung."
        else:
            night_text = "🌙 Kein reines Nachtfenster im verbleibenden Prognosezeitraum verfügbar."

        worst_text = f"⚠️ Teuerste Spitzenlast ({worst_window['avg_cost_ct']:.1f} ct/kWh). Flexible Verbraucher vermeiden und Energie aus dem Speicher nutzen."

        best_overall["recommendation_text"] = best_text
        if best_night:
            best_night["recommendation_text"] = night_text
        worst_window["recommendation_text"] = worst_text

        windows[dur_key] = {
            "duration_hours": dur_hours,
            "device_info": typical_devices[dur_key],
            "total_kwh_typical": total_kwh,
            "savings_eur": savings_eur,
            "best_overall": best_overall,
            "best_night": best_night,
            "worst": worst_window,
            "all_ranked_top3": evaluated_windows[:3],
        }

    return {
        "horizon_hours": horizon_hours,
        "has_pv": has_pv,
        "tariff_type": tariff_type,
        "base_feed_in_ct": base_feed_in_ct,
        "avg_day_cost_ct": round(avg_cost, 2),
        "windows": windows,
        "timeline": timeline,
    }

