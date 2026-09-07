##########################
# energy/flow_engine.py
##########################

def calculate_energy_flow(signals):
    """
    Enterprise-Grade Energy Flow Balancing Engine.

    Physische Verteilung:
    1. PV → Hauslast (Direktverbrauch zuerst)
    2. PV → Batterie (Überschussladung)
    3. PV → Netz (Tatsächliche Netzeinspeisung)
    4. Batterie → Hauslast (Entladung bei PV-Defizit)
    5. Netz → Batterie (Netzladung / Grid-Charging)
    6. Netz → Hauslast (Netzbezug für verbleibende Last)

    Liefert alle Kanten-Werte in Watt (W) sowie berechnete KPIs (Autarkie, Eigenverbrauchsquote).
    """
    signals = signals or {}

    grid = signals.get("grid", {})
    load = signals.get("load", {})
    pv = signals.get("pv", {})
    battery = signals.get("battery", {})

    production = max(0.0, float(pv.get("production") or 0.0))
    battery_charge = max(0.0, float(battery.get("charge") or 0.0))
    battery_discharge = max(0.0, float(battery.get("discharge") or 0.0))
    grid_import = max(0.0, float(grid.get("import") or 0.0))
    grid_export = max(0.0, float(grid.get("export") or 0.0))
    consumption = max(0.0, float(load.get("consumption") or 0.0))

    # 1. Batterieladung aufteilen: Aus PV oder aus Netz?
    pv_available_for_battery = max(0.0, production)
    pv_to_battery = 0.0
    grid_to_battery = 0.0

    if battery_charge > 0:
        # PV-Überschuss zuerst in die Batterie
        pv_to_battery = min(pv_available_for_battery, battery_charge)
        # Verbleibende Batterieladung kommt aus dem Netz (Grid-Charging)
        grid_to_battery = max(0.0, battery_charge - pv_to_battery)
        if grid_import > 0:
            grid_to_battery = min(grid_to_battery, grid_import)

    remaining_pv = max(0.0, production - pv_to_battery)
    remaining_grid_import = max(0.0, grid_import - grid_to_battery)

    # Ungemessene PV-Erzeugung (z.B. 2. Wechselrichter / Balkonkraftwerk) erkennen & berücksichtigen
    if grid_export > (remaining_pv + battery_discharge):
        unmeasured_pv = (grid_export - (remaining_pv + battery_discharge)) + consumption
        production = round(production + unmeasured_pv, 2)
        remaining_pv = round(remaining_pv + unmeasured_pv, 2)

    # 2. Reinen Hausverbrauch (Bedarf) berechnen / bereinigen:
    # Physikalische Bilanz: Wenn mehr Energie aus PV/Speicher/Netz ins Haus fließt als Submeter einzeln erfassen,
    # ist der Gesamthausbedarf die physikalische Summe aller zufließenden Quellen abzüglich Netzeinspeisung:
    derived_consumption = (
        remaining_pv + battery_discharge + remaining_grid_import - grid_export
    )
    if consumption <= 0 or (derived_consumption > 0 and derived_consumption > consumption):
        consumption = max(0.0, derived_consumption)
    else:
        # Falls die übergebene consumption fälschlicherweise die Batterieladung enthielt:
        if battery_charge > 0 and consumption >= battery_charge and abs(consumption - (remaining_grid_import + grid_to_battery)) < 30:
            consumption = max(0.0, consumption - grid_to_battery)

    # 3. Flüsse berechnen
    flow = {
        "pv_to_load": 0.0,
        "pv_to_battery": round(pv_to_battery, 2),
        "pv_to_grid": 0.0,
        "battery_to_load": 0.0,
        "grid_to_load": 0.0,
        "grid_to_battery": round(grid_to_battery, 2),
        "total_consumption": round(consumption, 2),
        "total_production": round(production, 2),
    }

    # 4. PV → Hauslast (Direktverbrauch)
    pv_to_load = min(remaining_pv, consumption)
    flow["pv_to_load"] = round(pv_to_load, 2)

    remaining_load = max(0.0, consumption - pv_to_load)
    remaining_pv = max(0.0, remaining_pv - pv_to_load)

    # 5. PV → Netz (Netzeinspeisung): Nur wenn tatsächlich Netzeinspeisung gemessen wurde!
    if grid_export > 0:
        flow["pv_to_grid"] = round(min(remaining_pv, grid_export), 2)
    else:
        flow["pv_to_grid"] = 0.0

    # 6. Batterie → Hauslast (Defizitausgleich)
    if battery_discharge > 0 and remaining_load > 0:
        battery_to_load = min(remaining_load, battery_discharge)
        flow["battery_to_load"] = round(battery_to_load, 2)
        remaining_load = max(0.0, remaining_load - battery_to_load)

    # 7. Netz → Hauslast (Netzbezug für verbleibende Last)
    if remaining_grid_import > 0 and remaining_load > 0:
        flow["grid_to_load"] = round(min(remaining_load, remaining_grid_import), 2)
    elif remaining_load > 0 and grid_import > 0:
        flow["grid_to_load"] = round(min(remaining_load, grid_import - flow["grid_to_battery"]), 2)
    else:
        flow["grid_to_load"] = 0.0

    # 8. Reale Summe des Hausverbrauchs: Physikalische Summe aller zufließenden Pfade!
    # (pv_to_load + battery_to_load + grid_to_load)
    # Garantiert, dass der Bedarf niemals physisch ungedeckte Phantasiewerte annehmen kann.
    actual_house_load = flow["pv_to_load"] + flow["battery_to_load"] + flow["grid_to_load"]
    flow["total_consumption"] = round(actual_house_load, 2)

    # 9. KPI Quoten berechnen
    self_consumption_watts = flow["pv_to_load"] + flow["pv_to_battery"]
    flow["self_consumption_rate"] = (
        round((self_consumption_watts / production * 100.0), 1) if production > 0 else 100.0
    )
    autarky_watts = flow["pv_to_load"] + flow["battery_to_load"]
    flow["autarky_rate"] = (
        round((autarky_watts / flow["total_consumption"] * 100.0), 1) if flow["total_consumption"] > 0 else (100.0 if production > 0 else 0.0)
    )

    return flow


