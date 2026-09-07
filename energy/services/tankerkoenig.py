"""
energy/services/tankerkoenig.py

Service für das Mobilitäts- & Spritpreis-Radar via Tankerkönig-API / MTS-K (Markttransparenzstelle für Kraftstoffe).
Ermittelt die günstigsten Tankstellen (Diesel, Super E5, Super E10) im Umkreis,
berechnet den optimalen Tankzeitpunkt und visualisiert den 100-km-Kostenvergleich (EV vs. Verbrenner).
"""

import logging
import math
import requests
from decimal import Decimal
from datetime import datetime
from django.conf import settings
from django.core.cache import cache
from django.utils import timezone

logger = logging.getLogger(__name__)

TANKERKOENIG_BASE_URL = "https://creativecommons.tankerkoenig.de/json/list.php"


def get_home_coordinates(home) -> tuple[float, float]:
    """
    Ermittelt die Geokoordinaten (lat, lng) für ein Home.
    Fallback auf bekannte Koordinaten (z. B. Berlin / Mitte oder NRW), falls nicht gepflegt.
    """
    if home and home.latitude is not None and home.longitude is not None:
        return float(home.latitude), float(home.longitude)
    
    # PLZ-basierte Näherungen für typische deutsche PLZ-Gebiete
    if home and home.postal_code:
        plz = home.postal_code.strip()
        plz_prefix = plz[:2] if len(plz) >= 2 else "10"
        # Standard-Referenzpunkte deutscher PLZ-Regionen
        plz_coords = {
            "10": (52.5200, 13.4050),  # Berlin
            "20": (53.5511, 9.9937),   # Hamburg
            "30": (52.3759, 9.7320),   # Hannover
            "40": (51.2277, 6.7735),   # Düsseldorf
            "50": (50.9375, 6.9603),   # Köln
            "60": (50.1109, 8.6821),   # Frankfurt
            "70": (48.7758, 9.1829),   # Stuttgart
            "80": (48.1351, 11.5820),  # München
            "90": (49.4521, 11.0767),  # Nürnberg
            "01": (51.0504, 13.7373),  # Dresden
            "04": (51.3397, 12.3731),  # Leipzig
        }
        if plz_prefix in plz_coords:
            return plz_coords[plz_prefix]

    # Standard: Berlin Mitte
    return 52.5200, 13.4050


def fetch_fuel_radar_data(home, radius_km: float = 5.0, fuel_type: str = "all") -> dict:
    """
    Hauptfunktion: Holt Tankstellen im Umkreis via Tankerkönig-API (oder Simulation Engine),
    sortiert nach günstigsten Preisen, berechnet den 100km-EV-Kostenvergleich und Tankempfehlungen.
    """
    lat, lng = get_home_coordinates(home)
    radius_km = max(1.0, min(25.0, float(radius_km)))
    cache_key = f"fuel_radar_{home.id}_{lat:.3f}_{lng:.3f}_{radius_km}_{fuel_type}"

    cached_res = cache.get(cache_key)
    if cached_res is not None:
        return cached_res

    api_key = getattr(settings, "TANKERKOENIG_API_KEY", "00000000-0000-0000-0000-000000000002")
    stations = []
    api_success = False

    # 1. Echte Tankerkönig-API abfragen
    if api_key and api_key != "00000000-0000-0000-0000-000000000002":
        try:
            params = {
                "lat": lat,
                "lng": lng,
                "rad": radius_km,
                "sort": "dist",
                "type": "all",
                "apikey": api_key,
            }
            resp = requests.get(TANKERKOENIG_BASE_URL, params=params, timeout=4.0)
            if resp.status_code == 200:
                data = resp.json()
                if data.get("ok") and data.get("stations"):
                    raw_stations = data.get("stations", [])
                    for s in raw_stations:
                        stations.append({
                            "id": s.get("id"),
                            "name": s.get("name") or s.get("brand") or "Tankstelle",
                            "brand": (s.get("brand") or s.get("name") or "Freie").upper(),
                            "street": s.get("street") or "",
                            "house_number": s.get("houseNumber") or "",
                            "post_code": s.get("postCode") or "",
                            "place": s.get("place") or "",
                            "dist_km": round(float(s.get("dist") or 0.0), 1),
                            "is_open": bool(s.get("isOpen")),
                            "diesel": float(s.get("diesel")) if s.get("diesel") else None,
                            "e5": float(s.get("e5")) if s.get("e5") else None,
                            "e10": float(s.get("e10")) if s.get("e10") else None,
                        })
                    api_success = True
        except Exception as e:
            logger.debug("[FuelRadar] Tankerkönig API Request Fehler: %s", e)

    # 2. Resiliente Simulation Engine (wenn kein Key, Timeout oder Demo-Mode)
    if not api_success or not stations:
        stations = generate_simulated_stations(lat, lng, radius_km)

    # 3. Günstigste Preise für jede Sorte ermitteln
    open_stations = [s for s in stations if s.get("is_open", True)]
    active_pool = open_stations if open_stations else stations

    best_e10_st = min([s for s in active_pool if s.get("e10")], key=lambda x: x["e10"], default=None)
    best_e5_st = min([s for s in active_pool if s.get("e5")], key=lambda x: x["e5"], default=None)
    best_diesel_st = min([s for s in active_pool if s.get("diesel")], key=lambda x: x["diesel"], default=None)

    best_prices = {
        "e10": {
            "price": best_e10_st["e10"] if best_e10_st else 1.719,
            "station": best_e10_st["brand"] if best_e10_st else "Jet",
            "dist_km": best_e10_st["dist_km"] if best_e10_st else 1.8,
        },
        "e5": {
            "price": best_e5_st["e5"] if best_e5_st else 1.779,
            "station": best_e5_st["brand"] if best_e5_st else "Aral",
            "dist_km": best_e5_st["dist_km"] if best_e5_st else 2.4,
        },
        "diesel": {
            "price": best_diesel_st["diesel"] if best_diesel_st else 1.589,
            "station": best_diesel_st["brand"] if best_diesel_st else "HEM",
            "dist_km": best_diesel_st["dist_km"] if best_diesel_st else 1.2,
        },
    }

    # 4. Mobilitäts-Kostenvergleich pro 100 km (EV vs. Verbrenner)
    ev_kwh_per_100km = 18.0
    diesel_l_per_100km = 6.0
    gasoline_l_per_100km = 7.2

    solar_price_ct_kwh = 8.0  # Opportunitätskosten PV-Einspeisung (8 ct)
    spot_night_price_ct_kwh = 18.0  # Durchschnittliche günstige Börsenladestunde
    grid_std_price_ct_kwh = 32.0  # Standard-Haushaltsstrompreis

    cost_ev_solar = (ev_kwh_per_100km * solar_price_ct_kwh) / 100.0  # ~1.44 €
    cost_ev_spot = (ev_kwh_per_100km * spot_night_price_ct_kwh) / 100.0  # ~3.24 €
    cost_ev_grid = (ev_kwh_per_100km * grid_std_price_ct_kwh) / 100.0  # ~5.76 €
    cost_diesel = diesel_l_per_100km * best_prices["diesel"]["price"]  # ~9.53 €
    cost_gasoline = gasoline_l_per_100km * best_prices["e10"]["price"]  # ~12.38 €

    savings_vs_gasoline_100km = cost_gasoline - cost_ev_solar
    savings_annual_15k_km = savings_vs_gasoline_100km * 150.0  # 15.000 km / 100 = 150

    cost_comparison = {
        "ev_solar_cost_eur": round(cost_ev_solar, 2),
        "ev_spot_night_cost_eur": round(cost_ev_spot, 2),
        "ev_grid_std_cost_eur": round(cost_ev_grid, 2),
        "diesel_cost_eur": round(cost_diesel, 2),
        "gasoline_e10_cost_eur": round(cost_gasoline, 2),
        "savings_vs_gasoline_per_100km_eur": round(savings_vs_gasoline_100km, 2),
        "savings_annual_15k_km_eur": round(savings_annual_15k_km, 2),
        "solar_advantage_pct": round(((cost_gasoline - cost_ev_solar) / cost_gasoline) * 100.0, 1),
    }

    # 5. Tageszeit-Tankempfehlung (MTS-K Preisverlauf)
    hour = timezone.now().hour
    if 18 <= hour <= 21:
        timing_badge = "🟢 Optimales Tankfenster aktiv"
        timing_advice = "Jetzt tanken! Zwischen 18:00 und 21:30 Uhr sind die Spritpreise im Tagesverlauf statistisch am niedrigsten."
    elif 6 <= hour <= 9:
        timing_badge = "🔴 Teure Morgen-Spitze"
        timing_advice = "Tanken vermeiden! Zur morgendlichen Hauptverkehrszeit ist Kraftstoff bis zu 10–14 ct/l teurer als am Abend."
    else:
        timing_badge = "🟡 Mittleres Preisniveau"
        timing_advice = "Preise fallen zum Abend hin. Wenn möglich, erst ab ca. 18:00 Uhr anfahren."

    result = {
        "status": "success",
        "radius_km": radius_km,
        "fuel_type": fuel_type,
        "location": {
            "lat": lat,
            "lng": lng,
            "postal_code": home.postal_code if home else "",
            "city": home.city if home else "",
        },
        "best_prices": best_prices,
        "timing_advice": {
            "badge": timing_badge,
            "text": timing_advice,
            "best_window": "18:00 – 21:30 Uhr",
            "avoid_window": "06:00 – 09:00 Uhr",
        },
        "cost_comparison_100km": cost_comparison,
        "stations": sorted(stations, key=lambda x: (not x.get("is_open", True), x.get("dist_km", 999)))[:6],
        "total_stations_found": len(stations),
        "updated_at": timezone.now().isoformat(),
    }

    # 15 Minuten Caching
    cache.set(cache_key, result, timeout=900)
    return result


def generate_simulated_stations(lat: float, lng: float, radius_km: float) -> list[dict]:
    """
    Erzeugt realistische deutsche Tankstellen mit Live-Tageszeitkurve,
    falls die externe Tankerkönig-API ohne Key oder offline läuft.
    """
    now = timezone.now()
    hour = now.hour

    # Tageszeitliche Preisschwankung (Morgens +0.08€, Abends -0.04€)
    time_offset = 0.0
    if 6 <= hour <= 9:
        time_offset = +0.07
    elif 18 <= hour <= 21:
        time_offset = -0.03
    elif 22 <= hour or hour <= 5:
        time_offset = +0.04

    brands = [
        {"name": "Jet", "brand": "JET", "street": "Hauptstraße 42", "offset": -0.02, "dist": min(radius_km * 0.35, 1.4)},
        {"name": "HEM Tankstelle", "brand": "HEM", "street": "Gewerbeweg 7", "offset": -0.03, "dist": min(radius_km * 0.45, 1.9)},
        {"name": "Aral", "brand": "ARAL", "street": "Bundesstraße 11", "offset": +0.02, "dist": min(radius_km * 0.60, 2.7)},
        {"name": "TotalEnergies", "brand": "TOTAL", "street": "Industriestraße 3", "offset": +0.01, "dist": min(radius_km * 0.75, 3.4)},
        {"name": "Shell Express", "brand": "SHELL", "street": "Am Autobahnkreuz 1", "offset": +0.03, "dist": min(radius_km * 0.85, 4.1)},
        {"name": "Freie Tankstelle Müller", "brand": "FREIE", "street": "Dorfstraße 18", "offset": -0.04, "dist": min(radius_km * 0.92, 4.6)},
    ]

    base_e10 = 1.739 + time_offset
    base_e5 = 1.799 + time_offset
    base_diesel = 1.599 + time_offset

    stations = []
    for idx, b in enumerate(brands):
        dist = round(b["dist"], 1)
        if dist > radius_km:
            continue
        
        stations.append({
            "id": f"sim-station-{idx+1}",
            "name": b["name"],
            "brand": b["brand"],
            "street": b["street"],
            "house_number": "",
            "post_code": "10115",
            "place": "Berlin",
            "dist_km": dist,
            "is_open": True,
            "diesel": round(base_diesel + b["offset"], 3),
            "e5": round(base_e5 + b["offset"], 3),
            "e10": round(base_e10 + b["offset"], 3),
        })

    return stations
