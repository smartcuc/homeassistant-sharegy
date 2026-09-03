###########################
# energy/services/energy.py
###########################

from energy.services.signals import get_ems_signals
from energy.flow_engine import calculate_energy_flow
from energy.services.sankey import build_live_sankey
from energy.services.kpis import get_today_consumption
from energy.services.charts import get_dashboard_chart, get_house_demand_chart
from energy.ems.models import (EMSSignalSource,)

from user_settings.models import UserPreference


def get_energy_data(user):
    # 1. Usereinstellungen laden (Sehr schlank)
    preference, _ = UserPreference.objects.get_or_create(
        user=user,
        key="sankey",
    )
    settings = preference.value or {}
    show_floors = settings.get("showFloors", True)
    show_rooms = settings.get("showRooms", True)

    # 2. Signale und Flüsse holen (Jetzt blitzschnell via Redis-Cache!)
    signals = get_ems_signals(user)
    flow = calculate_energy_flow(signals)

    # 3. Sankey-Diagramm generieren
    sankey = build_live_sankey(
        user,
        flow,
        signals,
        show_floors=show_floors,
        show_rooms=show_rooms,
    )

    # 💡 OPTIMIERUNG: "ready"-Check ohne DB-Abfragen!
    # Wir prüfen einfach direkt in den Live-Signalen, ob Werte für Erzeugung (PV)
    # oder Verbrauch (Load) existieren. Das spart 2 schwere SQL-Queries!
    load = signals.get("load", {})
    pv = signals.get("pv", {})
    grid = signals.get("grid", {})
    battery = signals.get("battery", {})

    # 4. Reiner Hausbedarf (Bedarf) aus dem ausbalancierten Flow
    house_demand = float(flow.get("total_consumption") or 0.0)
    if house_demand <= 0:
        c_val = load.get("consumption")
        if c_val is not None and float(c_val) > 0:
            house_demand = float(c_val)
        else:
            house_demand = (
                (pv.get("production") or 0)
                + (battery.get("discharge") or 0)
                + (grid.get("import") or 0)
                - (battery.get("charge") or 0)
                - (grid.get("export") or 0)
            )
    house_demand = max(0.0, float(house_demand or 0.0))
    today = get_today_consumption(user)
    from energy.services.system_health import check_home_system_status
    system_status = check_home_system_status(user)

    # 5. Device-IDs fuer die Dashboard-Historiencharts sammeln (Batch-Abfrage)
    sources = list(
        EMSSignalSource.objects.filter(
            home__user=user,
        ).select_related("signal_type")
    )

    from devices.models import Device
    all_user_devices = list(
        Device.objects.filter(
            home__user=user,
            active=True,
            pending_delete=False,
        ).select_related("config__role", "config__generator_type", "config__energy_signal_type")
    )

    grid_ids = {src.device_id for src in sources if src.signal_type and src.signal_type.key in ["grid", "grid_feed_in", "grid_import"]}
    pv_ids = {src.device_id for src in sources if src.signal_type and src.signal_type.key in ["pv", "solar", "producer"]}
    battery_ids = {src.device_id for src in sources if src.signal_type and src.signal_type.key in ["battery", "storage", "speicher"]}
    load_ids = {src.device_id for src in sources if src.signal_type and src.signal_type.key in ["load", "consumer", "consumption"]}

    for dev in all_user_devices:
        cfg = getattr(dev, "config", None)
        if not cfg:
            continue
        sig_key = cfg.energy_signal_type.key if cfg.energy_signal_type else None
        role_key = cfg.role.key if cfg.role else None

        if not battery_ids and (
            sig_key in ["battery", "storage", "speicher"]
            or role_key in ["battery", "storage", "speicher"]
        ):
            battery_ids.add(dev.id)
        elif not pv_ids and (
            sig_key in ["pv", "solar", "producer"]
            or role_key in ["producer", "pv"]
        ):
            pv_ids.add(dev.id)
        elif not grid_ids and (
            sig_key in ["grid", "grid_feed_in", "grid_import"]
            or role_key == "grid"
        ):
            grid_ids.add(dev.id)
        elif not load_ids and (
            sig_key in ["load", "consumer", "consumption"]
            or role_key == "consumer"
        ):
            load_ids.add(dev.id)

    battery_net = (battery.get("discharge") or 0) - (battery.get("charge") or 0)

    kpis = {
        "load": round(house_demand, 2),
        "tracked_load": load.get("consumption", 0),
        "pv": pv.get("production", 0),
        "grid": grid.get("import", 0) - grid.get("export", 0),
        "grid_import": grid.get("import", 0),
        "grid_export": grid.get("export", 0),
        "battery": round(battery_net, 2),
        "battery_discharge": battery.get("discharge", 0),
        "battery_charge": battery.get("charge", 0),
        "today": today["value"] if today else 0,
        "today_source": today["source"] if today else None,
    }

    all_dev_ids = [d.id for d in all_user_devices]

    eff_grid_ids = list(grid_ids) if grid_ids else all_dev_ids
    eff_pv_ids = list(pv_ids) if pv_ids else all_dev_ids
    eff_battery_ids = list(battery_ids) if battery_ids else all_dev_ids
    eff_load_ids = list(load_ids) if load_ids else all_dev_ids

    demand_chart = get_house_demand_chart(
        eff_pv_ids,
        eff_grid_ids,
        eff_battery_ids,
    )
    if not demand_chart and all_user_devices:
        demand_chart = get_dashboard_chart(all_dev_ids, metric_keys=["load_power", "consumption", "power", "value"])

    grid_sparkline = get_dashboard_chart(eff_grid_ids, metric_keys=["grid_power", "power_grid", "power", "value"])
    battery_sparkline = get_dashboard_chart(eff_battery_ids, metric_keys=["battery_power", "power_battery", "power", "value"])
    pv_sparkline = get_dashboard_chart(eff_pv_ids, metric_keys=["pv_power", "solar_power", "power", "value"])
    load_sparkline = demand_chart or get_dashboard_chart(eff_load_ids, metric_keys=["load_power", "consumption", "power", "value"])

    charts = {
        "load": load_sparkline,
        "pv": pv_sparkline,
        "grid": grid_sparkline,
        "battery": battery_sparkline,
        "today": today["history"] if today else [],
    }


    has_grid = len(grid_ids) > 0
    has_load = load.get("consumption") is not None
    ready = has_grid or len(all_user_devices) > 0

    pv_power_w = float(pv.get("production") or 0.0)
    load_power_w = float(house_demand or 0.0)
    grid_power_w = float((grid.get("import") or 0.0) - (grid.get("export") or 0.0))
    battery_power_w = float(battery_net or 0.0)

    # State of charge ermitteln
    home_obj = user.homes.first() if hasattr(user, "homes") else None
    battery_soc_pct = None
    try:
        from producer.models import StorageSystem
        st = StorageSystem.objects.filter(home=home_obj, active=True).first() if home_obj else None
        if st:
            live_s = st.get_live_soc()
            if live_s is not None:
                battery_soc_pct = float(live_s)
    except Exception:
        pass

    if battery_soc_pct is None:
        from energy.services.battery_forecast import find_home_battery_storage
        _, has_batt, batt_params = find_home_battery_storage(home_obj)
        battery_soc_pct = float(batt_params.get("current_soc_pct", 65.0)) if has_batt else 65.0

    kpis["pv_power_w"] = pv_power_w
    kpis["load_power_w"] = load_power_w
    kpis["grid_power_w"] = grid_power_w
    kpis["battery_power_w"] = battery_power_w
    kpis["battery_soc_pct"] = battery_soc_pct

    return {
        "ready": ready,
        "sankey": sankey,
        "kpis": kpis,
        "charts": charts,
        "system_status": system_status,
        "pv_power_w": pv_power_w,
        "load_power_w": load_power_w,
        "grid_power_w": grid_power_w,
        "battery_power_w": battery_power_w,
        "battery_soc_pct": battery_soc_pct,
    }
