###########################################
# energy/services/services_v2g.py
# V2G & V2H Bidirektionales Lademanagement (ISO 15118-20)
###########################################

import logging
import datetime
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
    
    Funktionen:
      1. Smart Departure Guarantee: Rückwärtsberechnung der Ladezeit für garantierten Ziel-SoC.
      2. Grid Peak Shaving: Lastspitzenkappung für Haus/Gewerbe (§ 14a EnWG).
      3. Battery Care & C-Rate Protection: Schutz vor übermäßiger Batteriedegradation.
      4. Dynamic Spot Market Arbitrage: Börsenstrom-Arbitrage bereinigt um Zyklisierungskosten.
      5. Vehicle-to-Home (V2H): Primäre Deckung des Eigenbedarfs bei Dunkelheit.
    """

    # Hysteresen & Schutzgrenzen
    MIN_DISCHARGE_POWER_W = 400.0       # Mindestentladung 400W
    DISCHARGE_HYSTERESIS_W = 150.0      # Glättung gegen Schwingungen
    DEFAULT_MAX_DISCHARGE_KW = 11.0     # 11 kW 3-phasige Entladung
    DEGRADATION_COST_CT_KWH = 3.5       # Batterieverschleiß & Wandlungsverluste (ct/kWh)
    CHARGING_EFFICIENCY = 0.92          # AC/DC Wirkungsgrad

    @classmethod
    def calculate_departure_schedule(
        cls,
        station,
        current_time: Optional[datetime.datetime] = None
    ) -> Dict[str, Any]:
        """
        Prüft den ISO 15118-20 Abfahrtsplan:
        Berechnet, ob vor der Abfahrt geladen werden muss und welcher Mindest-SoC
        während der V2H-Entladung gelockt werden muss.
        """
        if not station or not getattr(station, "departure_time", None):
            return {
                "has_departure_schedule": False,
                "charging_must_start": False,
                "time_needed_hours": 0.0,
                "hours_until_departure": 999.0,
                "target_soc": float(getattr(station, "target_departure_soc_pct", 80) or 80),
                "min_locked_soc": float(getattr(station, "v2g_min_soc_pct", 50) or 50)
            }

        now = current_time or timezone.localtime(timezone.now())
        dep_time = station.departure_time
        target_soc = float(station.target_departure_soc_pct or 80)
        current_soc = float(station.ev_soc_pct if station.ev_soc_pct is not None else 70.0)
        capacity_kwh = float(station.ev_battery_capacity_kwh or 77.0)
        base_min_soc = float(station.v2g_min_soc_pct or 50.0)

        # Heutige oder morgige Abfahrtszeit ermitteln
        today_dep = now.replace(hour=dep_time.hour, minute=dep_time.minute, second=0, microsecond=0)
        if today_dep <= now:
            # Abfahrt liegt am nächsten Kalendertag
            departure_dt = today_dep + datetime.timedelta(days=1)
        else:
            departure_dt = today_dep

        seconds_until_departure = (departure_dt - now).total_seconds()
        hours_until_departure = max(0.0, seconds_until_departure / 3600.0)

        # Ladeleistung ermitteln (Standard 11 kW oder stationsspezifisch)
        phases = int(station.phases or 3)
        max_current_a = float(station.max_current_a or 16.0)
        max_charge_power_w = max_current_a * 230.0 * phases

        # Zeitbedarf zur Erreichung des Ziel-SoC
        if current_soc < target_soc:
            energy_needed_kwh = ((target_soc - current_soc) / 100.0) * capacity_kwh
            time_needed_hours = energy_needed_kwh / ((max_charge_power_w / 1000.0) * cls.CHARGING_EFFICIENCY)
            buffer_hours = 0.5  # 30 Minuten Sicherheitspuffer
            charging_must_start = hours_until_departure <= (time_needed_hours + buffer_hours)

            # Max. nachladbare Energie in der verbleibenden Zeit
            max_chargeable_kwh = max(0.0, hours_until_departure - buffer_hours) * ((max_charge_power_w / 1000.0) * cls.CHARGING_EFFICIENCY)
            max_chargeable_soc = (max_chargeable_kwh / max(1.0, capacity_kwh)) * 100.0
            min_locked_soc = max(base_min_soc, target_soc - max_chargeable_soc)
        else:
            charging_must_start = False
            time_needed_hours = 0.0
            min_locked_soc = base_min_soc

        return {
            "has_departure_schedule": True,
            "charging_must_start": charging_must_start,
            "time_needed_hours": round(time_needed_hours, 2),
            "hours_until_departure": round(hours_until_departure, 2),
            "target_soc": target_soc,
            "min_locked_soc": round(min_locked_soc, 1),
            "departure_dt": departure_dt.isoformat()
        }

    @classmethod
    def apply_battery_care_limits(
        cls,
        station,
        requested_discharge_w: float,
        current_soc: float,
        effective_min_soc: float
    ) -> float:
        """
        Begrenzt die Entladeleistung zum Schutz der Batteriegesundheit (C-Rate & DoD-Puffer).
        """
        if requested_discharge_w <= 0.0:
            return 0.0

        capacity_kwh = float(station.ev_battery_capacity_kwh or 77.0)
        configured_max_w = float(station.v2g_max_discharge_power_kw or cls.DEFAULT_MAX_DISCHARGE_KW) * 1000.0

        # C-Rate Begrenzung (z.B. max 0.5C bei 77 kWh = 38.5 kW, begrenzt durch Hardware)
        if getattr(station, "battery_care_mode", True):
            max_c_rate = float(getattr(station, "max_c_rate", 0.5) or 0.5)
            c_rate_limit_w = max_c_rate * capacity_kwh * 1000.0
            max_allowed_w = min(configured_max_w, c_rate_limit_w)
        else:
            max_allowed_w = configured_max_w

        # SoC Schutz & Soft-Rampdown
        if current_soc <= effective_min_soc:
            return 0.0

        # Soft Rampdown in den letzten 3% vor Erreichen des Mindest-SoC
        soc_headroom = current_soc - effective_min_soc
        if soc_headroom < 3.0:
            scale = max(0.0, soc_headroom / 3.0)
            max_allowed_w *= scale

        return min(requested_discharge_w, max_allowed_w)

    @classmethod
    def calculate_v2x_dispatch(
        cls,
        station,
        home_metric: Optional[Any] = None,
        spot_price_eur_mwh: float = 80.0,
        current_time: Optional[datetime.datetime] = None
    ) -> Dict[str, Any]:
        """
        Berechnet den optimalen bidirektionalen Sollwert für die Wallbox:
        - Rückgabe: {
            "mode": "charging" | "discharging" | "idle" | "blocked",
            "target_power_w": float (+ für Laden, - für Entladen),
            "target_current_a": float,
            "reason": str,
            "soc_protected": bool,
            "departure_info": dict
          }
        """
        if not station or not station.supports_bidirectional or station.v2g_mode == "off":
            return {
                "mode": "charging",
                "target_power_w": 0.0,
                "target_current_a": 0.0,
                "reason": "V2G inaktiv oder nicht unterstützt",
                "soc_protected": False,
                "departure_info": {}
            }

        if station.status in ["Faulted", "Unavailable", "Reserved"]:
            return {
                "mode": "blocked",
                "target_power_w": 0.0,
                "target_current_a": 0.0,
                "reason": f"Wallbox Status '{station.status}'",
                "soc_protected": False,
                "departure_info": {}
            }

        # 1. Abfahrtszeit & Mindest-SoC Schutzprüfung (ISO 15118-20 Smart Departure)
        current_soc = float(station.ev_soc_pct if station.ev_soc_pct is not None else 70.0)
        phases = int(station.phases or 3)
        max_current_a = float(station.max_current_a or 16.0)
        departure_plan = cls.calculate_departure_schedule(station, current_time=current_time)
        effective_min_soc = departure_plan.get("min_locked_soc", float(station.v2g_min_soc_pct or 50.0))

        # Wenn die Abfahrtszeit unmittelbar bevorsteht und geladen werden muss:
        if departure_plan.get("charging_must_start", False):
            charge_power_w = max_current_a * 230.0 * phases
            return {
                "mode": "charging",
                "target_power_w": round(charge_power_w, 0),
                "target_current_a": max_current_a,
                "reason": f"⏱️ Smart Departure: Vorab-Laden für Ziel-SoC {departure_plan['target_soc']}% (Abfahrt in {departure_plan['hours_until_departure']:.1f}h)",
                "soc_protected": False,
                "departure_info": departure_plan
            }

        # 2. SoC Schutzprüfung
        if current_soc <= effective_min_soc:
            return {
                "mode": "idle",
                "target_power_w": 0.0,
                "target_current_a": 0.0,
                "reason": f"Fahrzeug-SoC ({current_soc:.1f}%) <= Mindest-Reserve ({effective_min_soc:.0f}%)",
                "soc_protected": True,
                "departure_info": departure_plan
            }

        # 3. Haus-Telemetrie auslesen
        pv_power_w = 0.0
        house_load_w = 0.0
        stationary_battery_soc = 100.0
        stationary_battery_power_w = 0.0

        if home_metric:
            pv_power_w = float(getattr(home_metric, "pv_power_w", 0.0) or 0.0)
            house_load_w = float(getattr(home_metric, "house_power_w", 0.0) or 0.0)
            stationary_battery_soc = float(getattr(home_metric, "battery_soc_pct", 100.0) or 100.0)
            stationary_battery_power_w = float(getattr(home_metric, "battery_power_w", 0.0) or 0.0)

        net_house_demand_w = max(0.0, house_load_w - pv_power_w)
        spot_price_ct_kwh = spot_price_eur_mwh / 10.0
        peak_threshold_w = float(getattr(station, "peak_shaving_threshold_w", 4200.0) or 4200.0)

        # ==========================================================
        # MODUS 1: PEAK SHAVING (Lastspitzenkappung § 14a EnWG)
        # ==========================================================
        if station.v2g_mode == "peak_shaving":
            if net_house_demand_w > peak_threshold_w:
                excess_demand_w = net_house_demand_w - peak_threshold_w
                safe_discharge_w = cls.apply_battery_care_limits(station, excess_demand_w, current_soc, effective_min_soc)
                if safe_discharge_w >= cls.MIN_DISCHARGE_POWER_W:
                    current_a = round(safe_discharge_w / (230.0 * phases), 1)
                    return {
                        "mode": "discharging",
                        "target_power_w": -round(safe_discharge_w, 0),
                        "target_current_a": current_a,
                        "reason": f"⚡ Peak Shaving: Kappt {safe_discharge_w/1000.0:.2f} kW Lastspitze über {peak_threshold_w/1000.0:.1f} kW Limit",
                        "soc_protected": False,
                        "departure_info": departure_plan
                    }

            return {
                "mode": "idle",
                "target_power_w": 0.0,
                "target_current_a": 0.0,
                "reason": f"Peak Shaving: Netzlast ({net_house_demand_w:.0f} W) unter Grenzwert ({peak_threshold_w:.0f} W)",
                "soc_protected": False,
                "departure_info": departure_plan
            }

        # ==========================================================
        # MODUS 2: V2H (Vehicle-to-Home Heimspeicher)
        # ==========================================================
        if station.v2g_mode == "v2h_home":
            if pv_power_w > 500.0:
                return {
                    "mode": "idle",
                    "target_power_w": 0.0,
                    "target_current_a": 0.0,
                    "reason": "PV-Erzeugung aktiv, V2H Heimentladung pausiert",
                    "soc_protected": False,
                    "departure_info": departure_plan
                }

            if net_house_demand_w < cls.MIN_DISCHARGE_POWER_W:
                return {
                    "mode": "idle",
                    "target_power_w": 0.0,
                    "target_current_a": 0.0,
                    "reason": "Hauslast zu gering für V2H",
                    "soc_protected": False,
                    "departure_info": departure_plan
                }

            # Stationärer Speicher hat Vorrang, falls > 25% und liefert Leistung
            if stationary_battery_soc > 25.0 and stationary_battery_power_w > 200.0:
                return {
                    "mode": "idle",
                    "target_power_w": 0.0,
                    "target_current_a": 0.0,
                    "reason": f"Stationärer Heimspeicher aktiv ({stationary_battery_soc:.0f}%)",
                    "soc_protected": False,
                    "departure_info": departure_plan
                }

            safe_discharge_w = cls.apply_battery_care_limits(station, net_house_demand_w, current_soc, effective_min_soc)
            if safe_discharge_w >= cls.MIN_DISCHARGE_POWER_W:
                current_a = round(safe_discharge_w / (230.0 * phases), 1)
                return {
                    "mode": "discharging",
                    "target_power_w": -round(safe_discharge_w, 0),
                    "target_current_a": current_a,
                    "reason": f"🏠 V2H: Versorgt Haus mit {safe_discharge_w/1000.0:.2f} kW (SoC: {current_soc:.0f}%)",
                    "soc_protected": False,
                    "departure_info": departure_plan
                }

            return {
                "mode": "idle",
                "target_power_w": 0.0,
                "target_current_a": 0.0,
                "reason": "V2H: Mindestentladeleistung nicht erreicht",
                "soc_protected": False,
                "departure_info": departure_plan
            }

        # ==========================================================
        # MODUS 3: V2G (Vehicle-to-Grid Börsenpreis-Arbitrage)
        # ==========================================================
        elif station.v2g_mode == "v2g_grid":
            high_price_threshold_ct = 30.0 + cls.DEGRADATION_COST_CT_KWH  # z.B. 33.5 ct/kWh
            if spot_price_ct_kwh >= high_price_threshold_ct:
                raw_max_w = float(station.v2g_max_discharge_power_kw or cls.DEFAULT_MAX_DISCHARGE_KW) * 1000.0
                safe_discharge_w = cls.apply_battery_care_limits(station, raw_max_w, current_soc, effective_min_soc)
                if safe_discharge_w >= cls.MIN_DISCHARGE_POWER_W:
                    current_a = round(safe_discharge_w / (230.0 * phases), 1)
                    return {
                        "mode": "discharging",
                        "target_power_w": -round(safe_discharge_w, 0),
                        "target_current_a": current_a,
                        "reason": f"⚡ V2G: Netzeinspeisung bei Spitzenpreis {spot_price_ct_kwh:.1f} ct/kWh (+{safe_discharge_w/1000.0:.1f} kW)",
                        "soc_protected": False,
                        "departure_info": departure_plan
                    }

            return {
                "mode": "idle",
                "target_power_w": 0.0,
                "target_current_a": 0.0,
                "reason": f"Börsenpreis ({spot_price_ct_kwh:.1f} ct) unter V2G-Schwelle ({high_price_threshold_ct:.1f} ct)",
                "soc_protected": False,
                "departure_info": departure_plan
            }

        # ==========================================================
        # MODUS 4: V2X Smart Auto (Kombiniert Peak Shaving, V2H & V2G intelligent)
        # ==========================================================
        elif station.v2g_mode == "v2x_auto":
            # A. Peak Shaving Prio 1: Wenn Hauslast Grenzwert überschreitet
            if net_house_demand_w > peak_threshold_w:
                excess_demand_w = net_house_demand_w - peak_threshold_w
                safe_discharge_w = cls.apply_battery_care_limits(station, excess_demand_w, current_soc, effective_min_soc)
                if safe_discharge_w >= cls.MIN_DISCHARGE_POWER_W:
                    return {
                        "mode": "discharging",
                        "target_power_w": -round(safe_discharge_w, 0),
                        "target_current_a": round(safe_discharge_w / (230.0 * phases), 1),
                        "reason": f"V2X Auto: Lastspitzenkappung ({safe_discharge_w/1000.0:.2f} kW über {peak_threshold_w/1000.0:.1f} kW)",
                        "soc_protected": False,
                        "departure_info": departure_plan
                    }

            # B. Hohe Börsenvergütung Prio 2: Einspeisung bei extremen Preisen
            if spot_price_ct_kwh >= 35.0:
                raw_max_w = float(station.v2g_max_discharge_power_kw or cls.DEFAULT_MAX_DISCHARGE_KW) * 1000.0
                safe_discharge_w = cls.apply_battery_care_limits(station, raw_max_w, current_soc, effective_min_soc)
                if safe_discharge_w >= cls.MIN_DISCHARGE_POWER_W:
                    return {
                        "mode": "discharging",
                        "target_power_w": -round(safe_discharge_w, 0),
                        "target_current_a": round(safe_discharge_w / (230.0 * phases), 1),
                        "reason": f"V2X Auto: Hohe Börsenvergütung ({spot_price_ct_kwh:.1f} ct/kWh) -> Max Netzeinspeisung",
                        "soc_protected": False,
                        "departure_info": departure_plan
                    }

            # C. Hausbedarf decken Prio 3: Wenn keine PV da ist (V2H)
            if pv_power_w < 300.0 and net_house_demand_w >= cls.MIN_DISCHARGE_POWER_W:
                if stationary_battery_soc <= 25.0 or stationary_battery_power_w <= 200.0:
                    safe_discharge_w = cls.apply_battery_care_limits(station, net_house_demand_w, current_soc, effective_min_soc)
                    if safe_discharge_w >= cls.MIN_DISCHARGE_POWER_W:
                        return {
                            "mode": "discharging",
                            "target_power_w": -round(safe_discharge_w, 0),
                            "target_current_a": round(safe_discharge_w / (230.0 * phases), 1),
                            "reason": f"V2X Auto: Hauspuffer aktiv ({safe_discharge_w/1000.0:.2f} kW bei {spot_price_ct_kwh:.1f} ct/kWh)",
                            "soc_protected": False,
                            "departure_info": departure_plan
                        }

            return {
                "mode": "idle",
                "target_power_w": 0.0,
                "target_current_a": 0.0,
                "reason": "V2X Auto: Keine Entladung erforderlich",
                "soc_protected": False,
                "departure_info": departure_plan
            }

        return {
            "mode": "idle",
            "target_power_w": 0.0,
            "target_current_a": 0.0,
            "reason": "V2G inaktiv",
            "soc_protected": False,
            "departure_info": departure_plan
        }

    @classmethod
    def dispatch_v2x_command(cls, station, dispatch_result: Dict[str, Any]):
        """Sendet den berechneten V2G/V2H Entlade- oder Ladebefehl über den Channel Layer an die Wallbox."""
        if not station:
            return

        target_power_w = float(dispatch_result.get("target_power_w", 0.0))
        target_current_a = float(dispatch_result.get("target_current_a", 0.0))
        mode = dispatch_result.get("mode", "idle")

        # Station in DB aktualisieren
        if mode == "discharging" and target_power_w < 0:
            station.v2g_discharge_power_w = abs(target_power_w)
            station.active_power_w = 0.0
            station.target_current_a = target_current_a
        elif mode == "charging" and target_power_w > 0:
            station.v2g_discharge_power_w = 0.0
            station.active_power_w = target_power_w
            station.target_current_a = target_current_a
        else:
            station.v2g_discharge_power_w = 0.0
            station.target_current_a = 0.0

        station.save(update_fields=["v2g_discharge_power_w", "active_power_w", "target_current_a"])

        channel_layer = get_channel_layer()
        if not channel_layer:
            return

        # Über WebSocket-Kanal senden (OCPP 2.0.1 / 2.1 SetChargingProfile mit negativem Power-Limit)
        group_name = f"ocpp_{station.charge_point_id}"
        try:
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
        except Exception as e:
            logger.warning(f"Konnte V2G Dispatch nicht an {station.charge_point_id} senden: {e}")
