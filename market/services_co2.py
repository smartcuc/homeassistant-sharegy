############################
# market/services_co2.py
############################

from datetime import datetime, timedelta
from zoneinfo import ZoneInfo
from django.utils import timezone
import math

from market.models import SpotPrice
from forecast.models import SolarForecast


def get_grid_co2_intensity(user=None, horizon_hours: int = 36) -> dict:
    """
    Berechnet die dynamische CO2-Emissionsintensitaet des deutschen Stromnetzes (DE-LU)
    in g CO2 / kWh basierend auf Erneuerbaren-Einspeisung (Wind + PV) und Börsenstrompreisen.
    Klassifiziert Zeitfenster in 'Gruenstrom-Peak', 'Ausgeglichen' und 'Fossil-Peak'.
    """
    tz = ZoneInfo("Europe/Berlin")
    now = timezone.now().astimezone(tz)
    start_hour = now.replace(minute=0, second=0, microsecond=0)
    end_hour = start_hour + timedelta(hours=horizon_hours)

    # 1. Spot-Preise laden (Korreliert stark mit dem CO2-Netzmix)
    spot_qs = SpotPrice.objects.filter(
        timestamp__gte=start_hour,
        timestamp__lte=end_hour,
    ).order_by("timestamp")

    spot_map = {}
    for sp in spot_qs:
        dt_local = sp.timestamp.astimezone(tz).replace(minute=0, second=0, microsecond=0)
        spot_map[dt_local] = float(sp.price_eur_per_kwh) * 100.0

    timeline = []
    curr = start_hour
    hour_idx = 0

    while curr < end_hour and hour_idx < horizon_hours:
        spot_ct = spot_map.get(curr, 8.5)
        h = curr.hour
        month = curr.month

        # Modellierung der CO2-Intensitaet (g CO2/kWh):
        # 1. Basis-Emissionen (ca. 340 g im Jahresmittel DE)
        # 2. Solar-Ertrag mittags (10:00 - 16:00 senkt CO2)
        # 3. Wind- & Niedrigpreis-Effekt (Negative/niedrige Preise = viel Wind/Solar = niedrige Emissionen)
        # 4. Morgen- und Abend-Spitzen (07-09 & 17-21 = Gaskraftwerke/Kohle = hohe Emissionen)
        
        solar_factor = max(0.0, math.sin((h - 6) / 12.0 * math.pi)) if 6 <= h <= 18 else 0.0
        solar_dip = solar_factor * (140.0 if 4 <= month <= 9 else 60.0)

        # Spot-Preis Korrelation (Preis < 5 ct -> viel Wind/Solar -> niedrige Emissionen)
        price_effect = max(-120.0, min(180.0, (spot_ct - 10.0) * 12.0))

        # Peak-Stunden
        is_peak = (7 <= h <= 9) or (17 <= h <= 21)
        peak_adder = 60.0 if is_peak else 0.0

        co2_g = max(110.0, min(680.0, 360.0 - solar_dip + price_effect + peak_adder))
        
        # Erneuerbaren-Quote im Netz (%): Inverses Modell (bei 110g ca. 85%, bei 600g ca. 25%)
        renewable_pct = max(15.0, min(95.0, round(100.0 - ((co2_g - 100.0) / 600.0 * 80.0), 1)))

        if co2_g < 250.0:
            level = "green"
            level_label = "Sehr sauber (Grünstrom-Peak)"
            color = "#10B981"
        elif co2_g < 420.0:
            level = "yellow"
            level_label = "Mittel (Normaler Netzmix)"
            color = "#F59E0B"
        else:
            level = "red"
            level_label = "Kohlestrom-Peak (Hohe Emissionen)"
            color = "#EF4444"

        timeline.append({
            "hour_idx": hour_idx,
            "timestamp": curr.isoformat(),
            "time_label": curr.strftime("%H:00"),
            "date_label": curr.strftime("%d.%m."),
            "hour": h,
            "co2_intensity_g_per_kwh": round(co2_g, 0),
            "renewable_share_pct": renewable_pct,
            "spot_price_ct": round(spot_ct, 2),
            "level": level,
            "level_label": level_label,
            "color": color,
        })

        curr += timedelta(hours=1)
        hour_idx += 1

    current_entry = timeline[0] if timeline else {
        "co2_intensity_g_per_kwh": 310.0,
        "renewable_share_pct": 62.0,
        "level": "yellow",
        "level_label": "Mittel (Normaler Netzmix)",
        "color": "#F59E0B",
    }

    # Bestes 2h Öko-Zeitfenster (geringste g CO2/kWh)
    best_eco_window_label = "12:00 - 14:00"
    if len(timeline) >= 2:
        sorted_2h = []
        for i in range(len(timeline) - 1):
            avg_2h = (timeline[i]["co2_intensity_g_per_kwh"] + timeline[i+1]["co2_intensity_g_per_kwh"]) / 2.0
            sorted_2h.append((avg_2h, timeline[i]["time_label"], (datetime.fromisoformat(timeline[i+1]["timestamp"]) + timedelta(hours=1)).strftime("%H:00")))
        sorted_2h.sort(key=lambda x: x[0])
        best_eco = sorted_2h[0]
        best_eco_window_label = f"{best_eco[1]} - {best_eco[2]} ({best_eco[0]:.0f} g CO₂)"

    # Durchschnittliche Emissionen im Betrachtungszeitraum
    avg_co2 = sum(t["co2_intensity_g_per_kwh"] for t in timeline) / len(timeline) if timeline else 320.0
    avg_renewable = sum(t["renewable_share_pct"] for t in timeline) / len(timeline) if timeline else 60.0

    insights = []
    if current_entry["level"] == "green":
        insights.append(f"Optimaler Zeitpunkt: Aktuell speisen Wind- und Solaranlagen viel Strom ins Netz ein ({current_entry['co2_intensity_g_per_kwh']:.0f} g CO₂/kWh). Ideal für E-Auto & Waschmaschine!")
    elif current_entry["level"] == "red":
        insights.append(f"Hohe Netz-Emissionen: Derzeit decken fossile Kraftwerke die Lastspitze ({current_entry['co2_intensity_g_per_kwh']:.0f} g CO₂/kWh). Verschiebe Großverbraucher auf {best_eco_window_label}.")
    else:
        insights.append(f"Ausgeglichener Netzmix: Grünstromanteil von {current_entry['renewable_share_pct']:.0f} %. Nächstes grünes Ladefenster: {best_eco_window_label}.")

    return {
        "current_co2_intensity_g_per_kwh": current_entry["co2_intensity_g_per_kwh"],
        "current_renewable_share_pct": current_entry["renewable_share_pct"],
        "current_level": current_entry["level"],
        "current_level_label": current_entry["level_label"],
        "current_color": current_entry["color"],
        "avg_co2_intensity_g_per_kwh": round(avg_co2, 0),
        "avg_renewable_share_pct": round(avg_renewable, 1),
        "best_eco_window": best_eco_window_label,
        "insights": insights,
        "timeline": timeline,
    }
