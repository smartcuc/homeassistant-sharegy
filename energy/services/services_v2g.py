###########################################
# energy/services/services_v2g.py
# V2G & V2H Bidirektionales Lademanagement (ISO 15118-20)
###########################################

import logging
from decimal import Decimal
from typing import Dict, Any, Optional
from django.utils import timezone
from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer

logger = logging.getLogger("django")


class V2GDispatchEngine:
    """
    Berechnet und steuert bidirektionales Laden & Entladen für Vehicle-to-Home (V2H)
    und Vehicle-to-Grid (V2G) auf Basis von ISO 15118-20 und OCPP 2.0.1 / 2.1.
    """

    # Hysteresen & Schutzgrenzen
    MIN_DISCHARGE_POWER_W = 500.0       # Mindestentladung 500W
    DISCHARGE_HYSTERESIS_W = 150.0      # Glättung gegen Schwingungen
    DEFAULT_MAX_DISCHARGE_KW = 11.0     # 11 kW 3-phasige Entladung

    @classmethod
    def calculate_v2x_dispatch(
        cls,
        station,
        home_metric: Optional[Any] = None,
        spot_price_eur_mwh: float = 80.0
    ) -> Dict[str, Any]:
        """
        Berechnet den optimalen bidirektionalen Sollwert für die Wallbox:
        - Rückgabe: {
            "mode": "charging" | "discharging" | "idle" | "blocked",
            "target_power_w": float (+ für Laden, - für Entladen),
            "target_current_a": float,
            "reason": str,
            "soc_protected": bool
          }
        """
        if not station or not station.supports_bidirectional or station.v2g_mode == "off":
            return {
                "mode": "charging",
                "target_power_w": 0.0,
                "target_current_a": 0.0,
                "reason": "V2G inaktiv oder nicht unterstützt",
                "soc_protected": False
            }

        if station.status in ["Faulted", "Unavailable", "Reserved"]:
            return {
                "mode": "blocked",
                "target_power_w": 0.0,
                "target_current_a": 0.0,
                "reason": f"Wallbox Status '{station.status}'",
                "soc_protected": False
            }

        # 1. SoC Schutzprüfung (Mindest-SoC für Fahrzeugreichweite)
        current_soc = station.ev_soc_pct if station.ev_soc_pct is not None else 70.0
        min_soc = float(station.v2g_min_soc_pct or 50)
        
        if current_soc <= min_soc:
            return {
                "mode": "idle",
                "target_power_w": 0.0,
                "target_current_a": 0.0,
                "reason": f"Fahrzeug-SoC ({current_soc:.1f}%) <= Mindest-Reserve ({min_soc:.0f}%)",
                "soc_protected": True
            }

        # 2. Haus-Telemetrie auslesen
        pv_power_w = 0.0
        house_load_w = 0.0
        stationary_battery_soc = 100.0

        if home_metric:
            pv_power_w = float(getattr(home_metric, "pv_power_w", 0.0) or 0.0)
            house_load_w = float(getattr(home_metric, "house_power_w", 0.0) or 0.0)
            stationary_battery_soc = float(getattr(home_metric, "battery_soc_pct", 100.0) or 100.0)

        net_house_demand_w = max(0.0, house_load_w - pv_power_w)
        max_discharge_w = float(station.v2g_max_discharge_power_kw or cls.DEFAULT_MAX_DISCHARGE_KW) * 1000.0
        spot_price_ct_kwh = spot_price_eur_mwh / 10.0

        # ==========================================================
        # MODUS A: V2H (Vehicle-to-Home Heimspeicher)
        # Deckt Hauslast ab, wenn keine PV da ist und Heimspeicher leer ist (< 20%)
        # ==========================================================
        if station.v2g_mode == "v2h_home":
            if pv_power_w > 500.0:
                # PV-Überschuss vorhanden -> V2H pausieren (oder PV laden)
                return {
                    "mode": "idle",
                    "target_power_w": 0.0,
                    "target_current_a": 0.0,
                    "reason": "PV-Erzeugung aktiv, V2H Heimentladung pausiert",
                    "soc_protected": False
                }

            if net_house_demand_w < cls.MIN_DISCHARGE_POWER_W:
                return {
                    "mode": "idle",
                    "target_power_w": 0.0,
                    "target_current_a": 0.0,
                    "reason": "Hauslast zu gering für V2H",
                    "soc_protected": False
                }

            # Stationärer Speicher hat Vorrang, falls > 25%
            if stationary_battery_soc > 25.0 and home_metric and getattr(home_metric, "battery_power_w", 0.0) > 200.0:
                return {
                    "mode": "idle",
                    "target_power_w": 0.0,
                    "target_current_a": 0.0,
                    "reason": f"Stationärer Heimspeicher aktiv ({stationary_battery_soc:.0f}%)",
                    "soc_protected": False
                }

            # Entladeleistung entspricht genau dem Hausnetzbedarf (bis Max-Limit)
            discharge_w = min(net_house_demand_w, max_discharge_w)
            phases = int(station.phases or 3)
            current_a = round(discharge_w / (230.0 * phases), 1)

            return {
                "mode": "discharging",
                "target_power_w": -round(discharge_w, 0),
                "target_current_a": current_a,
                "reason": f"V2H: Versorgt Haus mit {discharge_w/1000.0:.2f} kW (SoC: {current_soc:.0f}%)",
                "soc_protected": False
            }

        # ==========================================================
        # MODUS B: V2G (Vehicle-to-Grid Börsenpreis-Arbitrage)
        # Speist bei extremen Preisspitzen (> 30 ct/kWh) mit Maximalleistung ins Netz
        # ==========================================================
        elif station.v2g_mode == "v2g_grid":
            HIGH_PRICE_THRESHOLD_CT = 30.0 # ct/kWh
            if spot_price_ct_kwh >= HIGH_PRICE_THRESHOLD_CT:
                discharge_w = max_discharge_w
                phases = int(station.phases or 3)
                current_a = round(discharge_w / (230.0 * phases), 1)
                return {
                    "mode": "discharging",
                    "target_power_w": -round(discharge_w, 0),
                    "target_current_a": current_a,
                    "reason": f"V2G: Netzeinspeisung bei Spitzenpreis {spot_price_ct_kwh:.1f} ct/kWh (+{discharge_w/1000.0:.1f} kW)",
                    "soc_protected": False
                }
            else:
                return {
                    "mode": "idle",
                    "target_power_w": 0.0,
                    "target_current_a": 0.0,
                    "reason": f"Börsenpreis ({spot_price_ct_kwh:.1f} ct) unter V2G-Schwelle ({HIGH_PRICE_THRESHOLD_CT} ct)",
                    "soc_protected": False
                }

        # ==========================================================
        # MODUS C: V2X Smart Auto (Kombiniert V2H & V2G intelligent)
        # ==========================================================
        elif station.v2g_mode == "v2x_auto":
            # 1. Wenn extremer Börsenspitzenpreis -> volle Netzeinspeisung
            if spot_price_ct_kwh >= 35.0:
                discharge_w = max_discharge_w
                phases = int(station.phases or 3)
                return {
                    "mode": "discharging",
                    "target_power_w": -round(discharge_w, 0),
                    "target_current_a": round(discharge_w / (230.0 * phases), 1),
                    "reason": f"V2X Auto: Hohe Börsenvergütung ({spot_price_ct_kwh:.1f} ct/kWh) -> Max Netzeinspeisung",
                    "soc_protected": False
                }

            # 2. Wenn Hausbedarf da und keine PV -> Haus versorgen (V2H)
            if pv_power_w < 300.0 and net_house_demand_w >= cls.MIN_DISCHARGE_POWER_W:
                discharge_w = min(net_house_demand_w, max_discharge_w)
                phases = int(station.phases or 3)
                return {
                    "mode": "discharging",
                    "target_power_w": -round(discharge_w, 0),
                    "target_current_a": round(discharge_w / (230.0 * phases), 1),
                    "reason": f"V2X Auto: Hauspuffer aktiv ({discharge_w/1000.0:.2f} kW bei {spot_price_ct_kwh:.1f} ct/kWh)",
                    "soc_protected": False
                }

            return {
                "mode": "idle",
                "target_power_w": 0.0,
                "target_current_a": 0.0,
                "reason": "V2X Auto: Keine Entladung erforderlich",
                "soc_protected": False
            }

        return {
            "mode": "idle",
            "target_power_w": 0.0,
            "target_current_a": 0.0,
            "reason": "V2G inaktiv",
            "soc_protected": False
        }

    @classmethod
    def dispatch_v2x_command(cls, station, dispatch_result: Dict[str, Any]):
        """Sendet den berechneten V2G/V2H Entlade- oder Ladebefehl über den Channel Layer an die Wallbox."""
        if not station:
            return

        target_power_w = float(dispatch_result.get("target_power_w", 0.0))
        target_current_a = float(dispatch_result.get("target_current_a", 0.0))
        mode = dispatch_result.get("mode", "idle")

        channel_layer = get_channel_layer()
        if not channel_layer:
            return

        # Station in DB aktualisieren
        if mode == "discharging" and target_power_w < 0:
            station.v2g_discharge_power_w = abs(target_power_w)
            station.active_power_w = 0.0
            station.target_current_a = target_current_a
        else:
            station.v2g_discharge_power_w = 0.0
            station.target_current_a = target_current_a if mode == "charging" else 0.0

        station.save(update_fields=["v2g_discharge_power_w", "active_power_w", "target_current_a"])

        # Über WebSocket-Kanal senden (OCPP 2.0.1 / 2.1 SetChargingProfile mit negativem Power-Limit)
        group_name = f"ocpp_{station.charge_point_id}"
        async_to_sync(channel_layer.group_send)(
            group_name,
            {
                "type": "ocpp_set_v2g_profile",
                "power_w": target_power_w,
                "current_a": target_current_a,
                "connector_id": 1
            }
        )
        logger.info(f"🔄 V2G Dispatch an {station.charge_point_id}: {target_power_w:.0f} W ({dispatch_result.get('reason')})")
