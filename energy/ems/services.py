########################
# energy/ems/services.py
########################

from django.core.cache import cache
from devices.models import Device, DeviceLatestMetric
from devices.services.metrics import get_latest_values
from energy.models import EMSSignalSource


def build_device_signals(user):
    signals = {
        "grid": {"import": 0, "export": 0},
        "load": {"consumption": None},
        "pv": {"production": 0},
        "battery": {"charge": 0, "discharge": 0},
    }

    # 1. Holt alle konfigurierten Geräte des Benutzers (1 Query)
    all_devices = list(
        Device.objects.filter(
            home__user=user,
            active=True,
            pending_delete=False,
        ).select_related(
            "config__role",
            "config__generator_type",
            "config__energy_signal_type",
        )
    )

    values = get_latest_values([device.id for device in all_devices])

    # 2. Explizite EMS-Signalquellen aus der DB holen
    sources = list(
        EMSSignalSource.objects.filter(
            home__user=user,
        ).select_related("signal_type")
    )

    pv_device_ids = {
        src.device_id for src in sources
        if src.signal_type and src.signal_type.key in ["pv", "solar", "producer"]
    }
    grid_device_ids = {
        src.device_id for src in sources
        if src.signal_type and src.signal_type.key in ["grid", "grid_feed_in", "grid_import"]
    }
    battery_device_ids = {
        src.device_id for src in sources
        if src.signal_type and src.signal_type.key in ["battery", "storage", "speicher"]
    }
    load_device_ids = {
        src.device_id for src in sources
        if src.signal_type and src.signal_type.key in ["load", "consumer", "consumption"]
    }

    # 3. Fallback: Nur wenn fuer einen Signal-Typ KEINE explizite EMS-Signalquelle existiert
    def _is_non_power_sensor(d):
        c = getattr(d, "config", None)
        if c and c.metric_definition:
            u = (c.metric_definition.unit or "").strip().lower()
            k = (c.metric_definition.key or "").strip().lower()
            if u in ["a", "v", "%", "°c", "c", "bar", "hz"] or k in [
                "current", "battery_current", "voltage", "battery_voltage",
                "soc", "battery_soc", "battery_level", "temperature", "frequency"
            ]:
                return True
        d_name = (d.identifier or "").lower()
        if any(w in d_name for w in ["_current", "_voltage", "_soc", "_level", "stromstärke", "spannung"]):
            if not any(w in d_name for w in ["power", "leistung", "wirkleistung", "watt"]):
                return True
        return False

    # Aus konfigurierten Erzeuger- & Speichersystemen binden
    try:
        from producer.models import GeneratorSystem, StorageSystem
        for gs in GeneratorSystem.objects.filter(home__user=user, active=True).select_related("device"):
            if gs.device_id and not _is_non_power_sensor(gs.device):
                pv_device_ids.add(gs.device_id)

        for ss in StorageSystem.objects.filter(home__user=user, active=True).select_related("power_device", "primary_device", "soc_device"):
            if ss.power_device_id and not _is_non_power_sensor(ss.power_device):
                battery_device_ids.add(ss.power_device_id)
            if ss.primary_device_id and not _is_non_power_sensor(ss.primary_device):
                battery_device_ids.add(ss.primary_device_id)
            if ss.soc_device_id and not _is_non_power_sensor(ss.soc_device):
                battery_device_ids.add(ss.soc_device_id)
    except Exception:
        pass

    for dev in all_devices:
        if _is_non_power_sensor(dev):
            continue

        cfg = getattr(dev, "config", None)
        if not cfg:
            continue

        sig_key = cfg.energy_signal_type.key if cfg.energy_signal_type else None
        role_key = cfg.role.key if cfg.role else None

        # Batterie (nur falls noch keine Batterie-Source definiert)
        if (
            sig_key in ["battery", "storage", "speicher"]
            or role_key in ["battery", "storage", "speicher"]
        ):
            battery_device_ids.add(dev.id)

        # PV (nur falls noch keine PV-Source definiert)
        elif (
            sig_key in ["pv", "solar", "producer"]
            or role_key in ["producer", "pv"]
        ):
            pv_device_ids.add(dev.id)

        # Netz (nur falls noch keine Grid-Source definiert)
        elif (
            sig_key in ["grid", "grid_feed_in", "grid_import"]
            or role_key in ["grid", "meter"]
        ):
            grid_device_ids.add(dev.id)

        # Last (nur reine Verbraucher, NIEMALS Speicher/Batterie/PV/Netz)
        elif (
            sig_key in ["load", "consumer", "consumption"]
            or role_key == "consumer"
        ) and dev.id not in battery_device_ids and dev.id not in pv_device_ids and dev.id not in grid_device_ids:
            load_device_ids.add(dev.id)

    # Bereinigung: Last darf niemals Batterie-, PV- oder Netzgeräte enthalten
    load_device_ids = load_device_ids - battery_device_ids - pv_device_ids - grid_device_ids

    # 4. PV-Erzeugung berechnen
    pv_power = sum(max(values.get(d_id, 0), 0) for d_id in pv_device_ids)
    if pv_power <= 0:
        for dev in all_devices:
            if dev.id in battery_device_ids or dev.id in grid_device_ids or dev.id in load_device_ids:
                continue
            p_val = cache.get(f"device:{dev.id}:pv_power")
            if p_val is None and dev.id in pv_device_ids:
                p_val = cache.get(f"device:{dev.id}:latest_power")
            if p_val is None:
                m = DeviceLatestMetric.objects.filter(device=dev, metric_key="pv_power").first()
                if not m and dev.id in pv_device_ids:
                    m = DeviceLatestMetric.objects.filter(device=dev, metric_key="power").first()
                if m and m.value is not None:
                    p_val = float(m.value)
            if p_val is not None and float(p_val) > 0:
                pv_power = float(p_val)
                break
    signals["pv"]["production"] = max(0.0, round(pv_power, 2))

    # 5. Last (Direkte Messung aus Hybrid-Wechselrichter oder getrackten Einzelgeräten)
    tracked_load_devs = [
        d_id for d_id in load_device_ids
        if d_id not in grid_device_ids and d_id not in pv_device_ids and d_id not in battery_device_ids
    ]
    load_power = sum(max(values.get(d_id, 0), 0) for d_id in tracked_load_devs)

    measured_load = None
    for dev in all_devices:
        l_p = cache.get(f"device:{dev.id}:load_power")
        if l_p is None:
            m = DeviceLatestMetric.objects.filter(device=dev, metric_key="load_power").first()
            if m and m.value is not None:
                l_p = float(m.value)
        if l_p is not None and float(l_p) > 0:
            measured_load = float(l_p)
            break

    # 6. Batterie-Leistung (Discharge / Charge)
    battery_power = None
    try:
        from producer.models import StorageSystem
        for storage in StorageSystem.objects.filter(home__user=user, active=True):
            live_p = storage.get_live_power()
            if live_p is not None and abs(float(live_p)) > 0.01:
                battery_power = float(live_p)
                break
    except Exception:
        pass

    if battery_power is None:
        for dev in all_devices:
            b_p = cache.get(f"device:{dev.id}:battery_power")
            if b_p is None:
                m = DeviceLatestMetric.objects.filter(device=dev, metric_key="battery_power").first()
                if m and m.value is not None:
                    b_p = float(m.value)
            if b_p is not None and abs(float(b_p)) > 0.01:
                battery_power = float(b_p)
                break

    if battery_power is None:
        battery_power = sum(values.get(d_id, 0) for d_id in battery_device_ids if d_id not in pv_device_ids)

    # Lade- / Entladerichtung des Speichers physikalisch & vorzeichengenau bestimmen
    bat_val = float(battery_power or 0.0)
    eff_load_est = measured_load if (measured_load and measured_load > 0) else max(load_power, 300.0)

    # SoC prüfen
    soc_val = None
    try:
        from producer.models import StorageSystem
        for storage in StorageSystem.objects.filter(home__user=user, active=True):
            s = storage.get_live_soc()
            if s is not None:
                soc_val = float(s)
                break
    except Exception:
        pass

    if soc_val is None:
        for dev in all_devices:
            s = cache.get(f"device:{dev.id}:battery_soc")
            if s is None:
                m = DeviceLatestMetric.objects.filter(device=dev, metric_key="battery_soc").first()
                if m and m.value is not None:
                    s = float(m.value)
            if s is not None:
                soc_val = float(s)
                break

    # Wenn Speicher VOLL ist (>= 98%) oder keine Ladeleistung vorliegt, kann er NICHT laden!
    if soc_val is not None and soc_val >= 98.0:
        signals["battery"]["charge"] = 0.0
        if bat_val > 50 and pv_power < eff_load_est:
            signals["battery"]["discharge"] = round(bat_val, 2)
        else:
            signals["battery"]["discharge"] = 0.0
    elif abs(bat_val) > 0.01:
        # 1. Explizites Vorzeichen: Negativ bedeutet physikalisch immer Laden (z. B. Grid-Charging / Sungrow / Modbus / MQTT)
        if bat_val < 0:
            signals["battery"]["charge"] = round(abs(bat_val), 2)
            signals["battery"]["discharge"] = 0.0
        # 2. Wenn PV-Erzeugung den Hausverbrauch übersteigt (oder PV aktiv ist und Speicher noch Kapazität hat), lädt der Speicher
        elif pv_power > (eff_load_est + 50) or (pv_power > 100 and soc_val is not None and soc_val < 98.0 and bat_val > 0):
            signals["battery"]["charge"] = round(abs(bat_val), 2)
            signals["battery"]["discharge"] = 0.0
        # 3. Nacht / keine PV-Erzeugung: Speicher liefert Energie an das Haus (Entladung)
        else:
            signals["battery"]["discharge"] = round(abs(bat_val), 2)
            signals["battery"]["charge"] = 0.0
    else:
        # Fallback: Falls Inverter/Runner 0 W für den Speicher meldet, aber ein geladener Speicher (SoC > 5%)
        # vorhanden ist und das Haus mehr Strom braucht als PV liefert:
        deficit = max(0.0, eff_load_est - pv_power)
        if soc_val is not None and soc_val > 5.0 and deficit > 30:
            signals["battery"]["charge"] = 0.0
            signals["battery"]["discharge"] = round(deficit, 2)
        else:
            signals["battery"]["charge"] = 0.0
            signals["battery"]["discharge"] = 0.0

    # 7. Grid-Leistung (Import / Export)
    grid_power = sum(values.get(d_id, 0) for d_id in grid_device_ids if d_id not in pv_device_ids and d_id not in battery_device_ids)
    if not grid_device_ids or abs(grid_power) < 0.01:
        for dev in all_devices:
            if dev.id in battery_device_ids:
                continue
            g_p = cache.get(f"device:{dev.id}:grid_power")
            if g_p is None:
                m = DeviceLatestMetric.objects.filter(device=dev, metric_key="grid_power").first()
                if m and m.value is not None:
                    g_p = float(m.value)
            if g_p is not None and abs(float(g_p)) > 0.01:
                grid_power = float(g_p)
                break

    if abs(grid_power) > 0.01:
        # Standard Smart-Meter-Konvention (z.B. DTSU666):
        # positiv (> 0): Netzbezug (Import)
        # negativ (< 0): Netzeinspeisung (Export / Überschusseinspeisung)
        if grid_power >= 0:
            signals["grid"]["import"] = round(grid_power, 2)
            signals["grid"]["export"] = 0.0
        else:
            raw_export = abs(grid_power)
            # WICHTIG: Wenn der Speicher lädt, darf die Batterieladung nicht als Einspeisung gewertet werden
            if signals["battery"]["charge"] > 0 and raw_export >= signals["battery"]["charge"] and (pv_power - signals["battery"]["charge"] - eff_load_est) < 50:
                actual_export = max(0.0, pv_power - signals["battery"]["charge"] - eff_load_est)
                signals["grid"]["export"] = round(actual_export, 2)
            else:
                signals["grid"]["export"] = round(raw_export, 2)
            signals["grid"]["import"] = 0.0
    else:
        signals["grid"]["import"] = 0.0
        signals["grid"]["export"] = 0.0

    # 8. Gesamthausbedarf & Netz-Balancierung
    signals["load"]["tracked_consumption"] = load_power

    if measured_load is not None and measured_load > 0:
        signals["load"]["consumption"] = round(measured_load, 2)
        # Falls Netzleistung nicht direkt übermittelt wurde, physikalische Netzeinspeisung/Netzbezug berechnen
        if signals["grid"]["import"] == 0 and signals["grid"]["export"] == 0:
            surplus = (
                signals["pv"]["production"]
                + signals["battery"]["discharge"]
                - signals["load"]["consumption"]
                - signals["battery"]["charge"]
            )
            if surplus > 20:
                signals["grid"]["export"] = round(surplus, 2)
            elif surplus < -20:
                signals["grid"]["import"] = round(abs(surplus), 2)
    elif load_power > 0:
        # Direkte Messung durch Einzelmesswerte / Submeter
        signals["load"]["consumption"] = round(load_power, 2)
        if signals["grid"]["import"] == 0 and signals["grid"]["export"] == 0:
            surplus = (
                signals["pv"]["production"]
                + signals["battery"]["discharge"]
                - signals["load"]["consumption"]
                - signals["battery"]["charge"]
            )
            if surplus > 20:
                signals["grid"]["export"] = round(surplus, 2)
            elif surplus < -20:
                signals["grid"]["import"] = round(abs(surplus), 2)
    else:
        # Physikalische Bilanz: Bedarf = PV + Bat_Discharge + Grid_Import - Bat_Charge - Grid_Export
        derived = (
            signals["pv"]["production"]
            + signals["battery"]["discharge"]
            + signals["grid"]["import"]
            - signals["battery"]["charge"]
            - signals["grid"]["export"]
        )
        if derived > 10:
            signals["load"]["consumption"] = round(derived, 2)
        else:
            # Falls Grid-Export noch nicht gemessen wurde, ist der PV-Überschuss nach Batterieladung Einspeisung
            if signals["grid"]["export"] == 0 and signals["pv"]["production"] > (signals["battery"]["charge"] + 50):
                base_load = max(load_power, 250.0)
                surplus = signals["pv"]["production"] - signals["battery"]["charge"] - base_load
                if surplus > 0:
                    signals["grid"]["export"] = round(surplus, 2)
                    signals["load"]["consumption"] = round(base_load, 2)
                else:
                    signals["load"]["consumption"] = max(round(derived, 2), load_power, 0.0)
            else:
                signals["load"]["consumption"] = max(round(derived, 2), load_power, 0.0)

    return signals
