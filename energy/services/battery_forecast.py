######################################
# energy/services/battery_forecast.py
######################################

from zoneinfo import ZoneInfo
from django.utils import timezone
from django.db.models import Q

from devices.models import Device, DeviceLatestMetric
from forecast.services_load_forecast import get_household_load_forecast


def find_home_battery_storage(home):
    """
    Ermittelt, ob für den Haushalt ein Batteriespeicher konfiguriert ist oder
    über ein Wechselrichter- (SMA/Sungrow/Fronius/Deye), Home Assistant-
    oder ioBroker-Plugin erkannt wurde, und liefert das Gerät sowie Parameter zurück.
    """
    if not home:
        return None, False, {}

    # 0. Primär: Konfigurierte Speichersysteme (StorageSystem) aus Erzeuger- & Speicheranlagen
    from producer.models import StorageSystem
    storage_systems = list(StorageSystem.objects.filter(home=home, active=True).order_by("-updated_at"))
    if storage_systems:
        if len(storage_systems) == 1:
            storage_sys = storage_systems[0]
            live_soc = storage_sys.get_live_soc()
            has_live_soc = (live_soc is not None)
            current_soc_pct = live_soc if has_live_soc else 50.0
            c_eff = float(storage_sys.charge_efficiency_pct) / 100.0
            d_eff = float(storage_sys.discharge_efficiency_pct) / 100.0
            params = {
                "battery_name": storage_sys.name,
                "capacity_kwh": float(storage_sys.capacity_kwh),
                "current_soc_pct": current_soc_pct,
                "has_live_soc": has_live_soc,
                "min_soc_reserve_pct": float(storage_sys.min_soc_reserve_pct),
                "max_soc_pct": float(storage_sys.max_soc_pct),
                "max_charge_kw": float(storage_sys.max_charge_power_kw),
                "max_discharge_kw": float(storage_sys.max_discharge_power_kw),
                "charge_efficiency": c_eff,
                "discharge_efficiency": d_eff,
                "roundtrip_efficiency_pct": round(c_eff * d_eff * 100, 1),
            }
            return (storage_sys.primary_device or storage_sys.soc_device or storage_sys.power_device), True, params
        else:
            # Mehrere Batteriespeicher im Haushalt: Aggregation über Gesamtkapazität
            total_cap = sum(float(s.capacity_kwh) for s in storage_systems)
            total_charge_kw = sum(float(s.max_charge_power_kw) for s in storage_systems)
            total_discharge_kw = sum(float(s.max_discharge_power_kw) for s in storage_systems)

            weighted_soc_sum = 0.0
            has_any_live = False
            for s in storage_systems:
                s_soc = s.get_live_soc()
                if s_soc is not None:
                    has_any_live = True
                else:
                    s_soc = 50.0
                weighted_soc_sum += (float(s.capacity_kwh) * s_soc)

            current_soc_pct = round(weighted_soc_sum / max(0.001, total_cap), 1)
            min_soc = min(float(s.min_soc_reserve_pct) for s in storage_systems)
            max_soc = max(float(s.max_soc_pct) for s in storage_systems)

            c_eff = sum(float(s.charge_efficiency_pct) * float(s.capacity_kwh) for s in storage_systems) / (max(0.001, total_cap) * 100.0)
            d_eff = sum(float(s.discharge_efficiency_pct) * float(s.capacity_kwh) for s in storage_systems) / (max(0.001, total_cap) * 100.0)

            names = " + ".join([s.name for s in storage_systems])
            params = {
                "battery_name": names,
                "capacity_kwh": round(total_cap, 2),
                "current_soc_pct": current_soc_pct,
                "has_live_soc": has_any_live,
                "min_soc_reserve_pct": min_soc,
                "max_soc_pct": max_soc,
                "max_charge_kw": round(total_charge_kw, 2),
                "max_discharge_kw": round(total_discharge_kw, 2),
                "charge_efficiency": c_eff,
                "discharge_efficiency": d_eff,
                "roundtrip_efficiency_pct": round(c_eff * d_eff * 100, 1),
            }
            primary_dev = next((s.primary_device or s.soc_device for s in storage_systems if (s.primary_device or s.soc_device)), None)
            return primary_dev, True, params

    # 1. Direkt als Battery/Storage/Akku konfiguriertes Gerät
    bat_device = Device.objects.filter(
        home=home,
        active=True,
        pending_delete=False,
    ).filter(
        Q(config__role__key__in=["battery", "storage", "akku"])
        | Q(config__energy_signal_type__key__in=["battery", "battery_storage"])
        | Q(identifier__icontains="battery")
        | Q(identifier__icontains="storage")
        | Q(identifier__icontains="akku")
    ).first()

    # 2. Falls kein explizites Batterie-Gerät: Suche nach Hybrid-Wechselrichter mit Batterie-/SoC-Telemetrie
    # (z. B. SMA / Sungrow / Fronius / Deye Plugin oder Home Assistant / ioBroker Sync)
    if not bat_device:
        bat_device = Device.objects.filter(
            home=home,
            active=True,
            pending_delete=False,
        ).filter(
            latest_metrics__metric_key__in=["soc", "battery_soc", "state_of_charge", "battery_percent", "soc_pct", "battery_power", "battery_w"]
        ).distinct().first()

    # Wenn kein Batteriespeicher konfiguriert oder über Plugins erkannt wurde:
    if not bat_device:
        return None, False, {}

    # Standard-Parameter
    capacity_kwh = 10.0
    max_charge_kw = 5.0
    max_discharge_kw = 5.0
    min_soc_pct = 10.0  # Tiefentladeschutz & Notstromreserve
    max_soc_pct = 100.0
    charge_efficiency = 0.95
    discharge_efficiency = 0.95
    current_soc_pct = 50.0

    # Kapazität aus DeviceResource / DeviceConfig auslesen
    if hasattr(bat_device, "resource") and bat_device.resource and bat_device.resource.attributes:
        attrs = bat_device.resource.attributes
        cap = attrs.get("capacity_kwh") or attrs.get("battery_capacity_kwh") or attrs.get("capacity")
        if cap:
            try:
                capacity_kwh = float(cap)
            except (ValueError, TypeError):
                pass
        max_c = attrs.get("max_charge_kw") or attrs.get("max_power_kw")
        if max_c:
            try:
                max_charge_kw = float(max_c)
                max_discharge_kw = float(max_c)
            except (ValueError, TypeError):
                pass

    # SoC aus Live-Metriken abfragen
    latest_soc = DeviceLatestMetric.objects.filter(
        device=bat_device,
        metric_key__in=["soc", "battery_soc", "state_of_charge", "battery_percent", "soc_pct", "battery_level", "value"],
    ).first()

    # Falls nicht direkt auf bat_device, suche auf allen Geräten des Hauses
    if not latest_soc or latest_soc.value is None:
        latest_soc = DeviceLatestMetric.objects.filter(
            device__home=home,
            device__active=True,
            metric_key__in=["soc", "battery_soc", "state_of_charge", "battery_percent", "soc_pct", "battery_level"],
        ).first()

    has_live_soc = (latest_soc is not None and latest_soc.value is not None)
    if has_live_soc:
        try:
            current_soc_pct = max(0.0, min(100.0, float(latest_soc.value)))
        except (ValueError, TypeError):
            has_live_soc = False
            current_soc_pct = 50.0
    else:
        current_soc_pct = 50.0

    battery_name = (
        bat_device.config.name
        if (hasattr(bat_device, "config") and bat_device.config and bat_device.config.name)
        else bat_device.identifier
    )

    params = {
        "battery_name": battery_name,
        "capacity_kwh": capacity_kwh,
        "current_soc_pct": current_soc_pct,
        "has_live_soc": has_live_soc,
        "min_soc_reserve_pct": min_soc_pct,
        "max_soc_pct": max_soc_pct,
        "max_charge_kw": max_charge_kw,
        "max_discharge_kw": max_discharge_kw,
        "charge_efficiency": charge_efficiency,
        "discharge_efficiency": discharge_efficiency,
        "roundtrip_efficiency_pct": round(charge_efficiency * discharge_efficiency * 100, 1),
    }

    return bat_device, True, params


def get_battery_soc_forecast(user, horizon_hours: int = 48) -> dict:
    """
    Simuliert die vorausschauende 24h/48h Batterie- und SoC-Kurve basierend auf
    PV-Ertrag, Haushaltslast, Wirkungsgraden und Mindest-Notstromreserven.
    Wird nur ausgeführt, wenn ein realer oder über Plugins erkannter Speicher existiert.
    """
    home = user.homes.first() if hasattr(user, "homes") else None
    tz_name = home.timezone if home and home.timezone else "Europe/Berlin"
    tz = ZoneInfo(tz_name)

    # 1. Batteriespeicher-Gerät und Parameter prüfen
    bat_device, has_battery, params = find_home_battery_storage(home)

    if not has_battery:
        return {
            "horizon_hours": horizon_hours,
            "has_battery": False,
            "reason": "no_battery_configured",
            "parameters": {},
            "kpis": {},
            "timeline": [],
        }

    battery_capacity_kwh = params["capacity_kwh"]
    current_soc_pct = params["current_soc_pct"]
    min_soc_pct = params["min_soc_reserve_pct"]
    max_soc_pct = params["max_soc_pct"]
    max_charge_kw = params["max_charge_kw"]
    max_discharge_kw = params["max_discharge_kw"]
    charge_efficiency = params["charge_efficiency"]
    discharge_efficiency = params["discharge_efficiency"]

    # 2. Last- und Solarprognose laden
    load_forecast = get_household_load_forecast(user, horizon_hours=horizon_hours)
    base_timeline = load_forecast.get("timeline", [])

    # 3. 48h Simulation durchführen
    sim_soc_pct = current_soc_pct
    current_stored_kwh = (sim_soc_pct / 100.0) * battery_capacity_kwh

    sim_timeline = []
    total_charged_kwh = 0.0
    total_discharged_kwh = 0.0
    total_grid_import_with_bat_kwh = 0.0
    total_grid_export_with_bat_kwh = 0.0

    full_charge_slot = None
    depleted_slot = None

    night_slots_count = 0
    night_autarky_slots = 0

    for idx, slot in enumerate(base_timeline):
        pv_kw = float(slot.get("pv_forecast_kw", 0.0))
        load_kw = float(slot.get("total_load_kw", 0.0))
        hour = slot.get("hour", 0)
        is_night = (hour <= 6 or hour >= 22)

        if is_night:
            night_slots_count += 1

        delta_kw = pv_kw - load_kw  # > 0: Überschuss, < 0: Defizit
        bat_flow_kw = 0.0
        grid_import_kw = 0.0
        grid_export_kw = 0.0

        if delta_kw > 0.0:
            # PV-Überschuss -> Laden
            surplus_kw = delta_kw
            room_kwh = ((max_soc_pct - sim_soc_pct) / 100.0) * battery_capacity_kwh
            max_possible_charge_kw = min(surplus_kw, max_charge_kw, (room_kwh / charge_efficiency))

            if max_possible_charge_kw > 0.01:
                bat_flow_kw = max_possible_charge_kw  # Positiv = Laden
                energy_added_kwh = bat_flow_kw * charge_efficiency
                current_stored_kwh = min(battery_capacity_kwh, current_stored_kwh + energy_added_kwh)
                sim_soc_pct = (current_stored_kwh / battery_capacity_kwh) * 100.0
                total_charged_kwh += energy_added_kwh
            else:
                bat_flow_kw = 0.0

            # Restlicher Überschuss ins Netz
            grid_export_kw = max(0.0, surplus_kw - bat_flow_kw)
            grid_import_kw = 0.0

            if is_night:
                night_autarky_slots += 1

        else:
            # Defizit / Nacht -> Entladen
            deficit_kw = abs(delta_kw)
            avail_kwh = max(0.0, current_stored_kwh - (min_soc_pct / 100.0) * battery_capacity_kwh)
            max_possible_discharge_kw = min(deficit_kw, max_discharge_kw, (avail_kwh * discharge_efficiency))

            if max_possible_discharge_kw > 0.01:
                bat_flow_kw = -max_possible_discharge_kw  # Negativ = Entladen
                energy_removed_kwh = abs(bat_flow_kw) / discharge_efficiency
                current_stored_kwh = max(
                    (min_soc_pct / 100.0) * battery_capacity_kwh,
                    current_stored_kwh - energy_removed_kwh,
                )
                sim_soc_pct = (current_stored_kwh / battery_capacity_kwh) * 100.0
                total_discharged_kwh += abs(bat_flow_kw)
            else:
                bat_flow_kw = 0.0

            # Restlicher Defizit aus dem Netz
            grid_import_kw = max(0.0, deficit_kw - abs(bat_flow_kw))
            grid_export_kw = 0.0

            if is_night and grid_import_kw <= 0.05:
                night_autarky_slots += 1

        total_grid_import_with_bat_kwh += grid_import_kw
        total_grid_export_with_bat_kwh += grid_export_kw

        # Status & Events erkennen
        status = "idle"
        if bat_flow_kw > 0.1:
            status = "charging"
        elif bat_flow_kw < -0.1:
            status = "discharging"
        elif sim_soc_pct <= min_soc_pct + 1.0:
            status = "empty_reserve"
        elif sim_soc_pct >= max_soc_pct - 1.0:
            status = "full"

        if full_charge_slot is None and sim_soc_pct >= 98.0:
            full_charge_slot = f"{slot['date_label']} {slot['time_label']}"

        if depleted_slot is None and sim_soc_pct <= min_soc_pct + 1.0 and abs(bat_flow_kw) < 0.05 and idx > 0:
            depleted_slot = f"{slot['date_label']} {slot['time_label']}"

        sim_timeline.append({
            "timestamp": slot["timestamp"],
            "time_label": slot["time_label"],
            "date_label": slot["date_label"],
            "weekday_label": slot["weekday_label"],
            "hour": hour,
            "soc_pct": round(sim_soc_pct, 1),
            "stored_kwh": round(current_stored_kwh, 2),
            "bat_flow_kw": round(bat_flow_kw, 2),
            "pv_kw": round(pv_kw, 2),
            "load_kw": round(load_kw, 2),
            "grid_import_kw": round(grid_import_kw, 2),
            "grid_export_kw": round(grid_export_kw, 2),
            "status": status,
            "is_night": is_night,
        })

    night_autarky_pct = round((night_autarky_slots / max(1, night_slots_count)) * 100.0, 1)

    return {
        "horizon_hours": horizon_hours,
        "has_battery": True,
        "parameters": params,
        "kpis": {
            "has_live_soc": params.get("has_live_soc", False),
            "start_soc_pct": round(current_soc_pct, 1),
            "end_soc_pct": round(sim_soc_pct, 1),
            "total_charged_kwh": round(total_charged_kwh, 2),
            "total_discharged_kwh": round(total_discharged_kwh, 2),
            "grid_import_with_bat_kwh": round(total_grid_import_with_bat_kwh, 2),
            "grid_export_with_bat_kwh": round(total_grid_export_with_bat_kwh, 2),
            "night_autarky_pct": min(100.0, night_autarky_pct),
            "full_charge_time": full_charge_slot or "Wird nicht voll (PV reicht nicht)",
            "depleted_time": depleted_slot or "Reicht durchgehend (kein Leerlaufen)",
            "saved_grid_costs_eur": round(total_discharged_kwh * 0.28, 2),
        },
        "timeline": sim_timeline,
    }
