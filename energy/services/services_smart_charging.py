##############################################
# energy/services/services_smart_charging.py
##############################################

import logging
import sys
from decimal import Decimal
from django.utils import timezone
from django.core.cache import cache
from django.conf import settings

from devices.models_ocpp import ChargingStation

logger = logging.getLogger("django")


def calculate_smart_charging_current(
    station: ChargingStation,
    pv_power_w: float = 0.0,
    load_power_w: float = 0.0,
    battery_charge_w: float = 0.0,
    spot_price_ct: float = 20.0
) -> float:
    """
    Berechnet den optimalen Ladestrom je Phase (in Ampere) für eine Wallbox.
    Unterstützt 5 Betriebsmodi:
      - off: 0.0 A (Pausiert)
      - instant: max_current_a (z.B. 16A = 11 kW)
      - spot_price: max_current_a wenn spot_price <= price_threshold_ct, sonst 0.0 A
      - pv_surplus: Reine Überschussladung (6A - 16A/32A)
      - min_pv: Mindestens 6A + solarer Booster
    """
    # 1. Wenn die Wallbox reserviert, gestört oder außer Betrieb ist -> Ladevorgang blockieren (0.0 A)
    if station.status in ["Reserved", "Unavailable", "Faulted", "SuspendedEVSE"]:
        return 0.0

    mode = station.smart_charging_mode
    max_a = float(station.max_current_a or 16.0)
    min_a = float(station.min_current_a or 6.0)
    phases = int(station.phases or 3)
    voltage = float(station.voltage_v or 230.0)

    if mode == "off":
        return 0.0

    if mode == "instant":
        return max_a

    if mode == "spot_price":
        threshold = float(station.price_threshold_ct or 15.0)
        if spot_price_ct <= threshold:
            return max_a
        return 0.0

    # Aktuelle Wallbox-Last herausrechnen, um die wahre verfügbare Leistung zu kennen
    current_wb_power_w = float(station.active_power_w or 0.0)
    household_load_without_wb = max(0.0, load_power_w - current_wb_power_w)

    # Netto-Solarüberschuss = PV - Hauslast - Batterieladung
    # (Batterie hat Vorrang, es sei denn der Nutzer priorisiert das Auto)
    net_surplus_w = max(0.0, pv_power_w - household_load_without_wb - max(0.0, battery_charge_w))
    
    # Gesamte für die Wallbox zur Verfügung stehende Leistung
    total_available_wb_power_w = net_surplus_w + current_wb_power_w

    # Berechne verfügbaren Strom je Phase: P = phases * U * I => I = P / (phases * U)
    power_per_phase_w = total_available_wb_power_w / max(1, phases)
    calculated_current_a = power_per_phase_w / max(1.0, voltage)

    if mode == "min_pv":
        # Mindestens 6A, bei Überschuss mehr bis max_a
        return round(max(min_a, min(max_a, calculated_current_a)), 1)

    if mode == "pv_surplus":
        # Einschalt-Schwelle: Mindestens 6A (bei 3 Phasen ca. 4.140 W, bei 1 Phase ca. 1.380 W)
        min_required_power_w = min_a * voltage * phases
        
        # 10% Hysterese-Toleranz gegen Flattern bei Wolken
        if total_available_wb_power_w < (min_required_power_w * 0.9):
            return 0.0
            
        return round(max(min_a, min(max_a, calculated_current_a)), 1)

    return min_a


def dispatch_wallbox_charging_profile(station: ChargingStation, target_current_a: float) -> dict:
    """
    Überträgt ein neues Ladeprofil (SetChargingProfile) über Django Channels an die Wallbox.
    Enthält einen Hysterese-Filter, um überflüssigen Netzwerkverkehr zu vermeiden.
    """
    # Wenn Station blockiert / reserviert / gestört ist, Strom immer auf 0.0A begrenzen
    if station.status in ["Reserved", "Unavailable", "Faulted"]:
        target_current_a = 0.0

    target_current_a = round(float(target_current_a), 1)
    previous_current_a = float(station.target_current_a or 0.0)

    # Hysterese: Nur senden wenn Änderung >= 0.5A oder Ein/Ausschalten
    is_state_toggle = (target_current_a == 0.0 and previous_current_a > 0.0) or (target_current_a > 0.0 and previous_current_a == 0.0)
    has_significant_change = abs(target_current_a - previous_current_a) >= 0.5

    if not is_state_toggle and not has_significant_change and previous_current_a > 0.0:
        return {"dispatched": False, "reason": "Hysteresis delta < 0.5A", "current_a": previous_current_a}

    is_testing = "test" in sys.argv or getattr(settings, "TESTING", False)

    if not is_testing:
        try:
            from asgiref.sync import async_to_sync
            from channels.layers import get_channel_layer
            channel_layer = get_channel_layer()
            if channel_layer:
                async_to_sync(channel_layer.group_send)(
                    f"ocpp_{station.charge_point_id}",
                    {
                        "type": "ocpp_set_charging_profile",
                        "current_a": target_current_a,
                        "connector_id": 1,
                    }
                )
        except Exception as e:
            logger.warning(f"Konnte SetChargingProfile nicht per ChannelLayer an {station.charge_point_id} senden: {e}")

    station.target_current_a = target_current_a
    station.save(update_fields=["target_current_a"])

    return {
        "dispatched": True,
        "charge_point_id": station.charge_point_id,
        "target_current_a": target_current_a,
        "phases": station.phases,
        "power_kw": round(target_current_a * (station.voltage_v or 230.0) * station.phases / 1000.0, 2)
    }


def run_all_wallboxes_smart_charging_cycle():
    """
    Periodischer Dispatcher-Zyklus:
    Prüft alle online geschalteten Wallboxen und passt deren Ladeleistung dynamisch an.
    """
    from energy.ems.services import build_device_signals
    from market.models import SpotPrice

    stations = ChargingStation.objects.filter(is_online=True)
    results = []

    for station in stations:
        try:
            home = station.home
            user = home.user if home else None
            signals = build_device_signals(user) if user else {}
            
            pv_power_w = float(signals.get("pv", {}).get("production", 0.0) or 0.0)
            load_power_w = float(signals.get("load", {}).get("consumption", 0.0) or 0.0)
            battery_charge_w = float(signals.get("battery", {}).get("charge", 0.0) or 0.0)

            latest_spot = SpotPrice.objects.filter(timestamp__lte=timezone.now()).order_by("-timestamp").first()
            spot_price_ct = float(latest_spot.price_ct_kwh) if latest_spot else 20.0

            target_a = calculate_smart_charging_current(
                station=station,
                pv_power_w=pv_power_w,
                load_power_w=load_power_w,
                battery_charge_w=battery_charge_w,
                spot_price_ct=spot_price_ct
            )

            res = dispatch_wallbox_charging_profile(station, target_a)
            results.append(res)
        except Exception as e:
            logger.error(f"Fehler beim Smart Charging Dispatch für Wallbox {station.charge_point_id}: {e}", exc_info=True)

    return results
