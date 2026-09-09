#################################
# energy/services/system_health.py
#################################

import logging
from typing import Dict, Any, List
from django.core.cache import cache

from devices.models import Device, DeviceLatestMetric
from energy.ems.models import EMSSignalSource
from producer.models import StorageSystem, GeneratorSystem

logger = logging.getLogger(__name__)


def check_home_system_status(user) -> Dict[str, Any]:
    """
    Analysiert den Einrichtungs- und Vollständigkeitsgrad des Energiesystems für den Nutzer (Omi-Test).
    Prüft die 4 Kernsäulen:
    1. PV-Erzeugung (Solar)
    2. Netzübergabepunkt (Zähler/Bezug/Einspeisung)
    3. Batteriespeicher (Kapazität & Ladestand)
    4. Hauslast (Gesamtverbrauch)
    sowie die Submeter-Ebene (Geräte, Räume, Etagen).

    Liefert konkrete, laienverständliche Handlungsempfehlungen und einen System Readiness Score.
    """
    home = None
    try:
        if user and hasattr(user, "homes"):
            home = user.homes.first()
        if not home and user:
            home = Home.objects.filter(user=user).first()
        if not home:
            home = Home.objects.first()

        if not home:
            return {
                "score": 0,
                "status_code": "no_home",
                "title": "Kein Haushalt angelegt",
                "description": "Bitte richte deinen Haushalt ein, um Geräte zu verbinden.",
                "pillars": {},
                "submeters": {"count": 0, "rooms_count": 0, "floors_count": 0},
                "recommendations": [
                    {
                        "priority": "high",
                        "action": "setup_home",
                        "title": "Haushalt anlegen",
                        "text": "Erstelle deinen Haushalt, um Wechselrichter oder Zähler hinzuzufügen.",
                    }
                ],
            }

        # 1. Alle Geräte des Nutzers abrufen
        devices = list(
            Device.objects.filter(home=home, pending_delete=False)
            .select_related(
                "config__role",
                "config__generator_type",
                "config__metric_definition",
                "config__energy_signal_type",
                "config__room",
                "config__floor",
            )
            .prefetch_related("latest_metrics")
        )
        active_devices = [d for d in devices if d.active]

        from devices.models import CloudDeviceIntegration
        cloud_inverter_integrations = list(
            CloudDeviceIntegration.objects.filter(device__home=home)
            .select_related("device")
        )
        cloud_inverter_ids = {ci.device_id for ci in cloud_inverter_integrations}

        ems_sources = list(
            EMSSignalSource.objects.filter(home=home)
            .select_related("device", "signal_type")
        )
        ems_pv_device_ids = {s.device_id for s in ems_sources if s.signal_type and s.signal_type.key in ["pv", "solar", "producer", "generation"]}
        ems_grid_device_ids = {s.device_id for s in ems_sources if s.signal_type and s.signal_type.key in ["grid", "grid_import", "grid_feed_in", "meter"]}
        ems_batt_device_ids = {s.device_id for s in ems_sources if s.signal_type and s.signal_type.key in ["battery", "storage", "speicher"]}

        generators = list(GeneratorSystem.objects.filter(home=home))
        storages = list(StorageSystem.objects.filter(home=home))

        generator_device_ids = {getattr(g, "device_id", None) for g in generators if getattr(g, "device_id", None)}
        storage_device_ids = {
            id_val for st in storages for id_val in [
                getattr(st, "primary_device_id", None),
                getattr(st, "soc_device_id", None),
                getattr(st, "power_device_id", None),
                getattr(st, "device_id", None),
            ] if id_val
        }

        # ---------------------------------------------------------
        # 🔍 PARAMETER-BASIERTE KLASSIFIZIERUNG JEDES GERÄTS
        # ---------------------------------------------------------
        # Verwendete Parameter:
        # 1. Rolle im Energiesystem: cfg.role.key (producer, grid, battery, consumer)
        # 2. Primäre Messgröße: cfg.metric_definition.key (power, energy, soc, etc.)
        # 3. Erzeugertyp: cfg.generator_type (PV, BKW, Wind, etc.)
        # 4. Signalart: cfg.energy_signal_type.key (pv, grid, battery, load)
        # 5. Netzzähler-Flag: getattr(cfg, 'is_grid_source', False)
        # 6. Multi-Channel Hardware: CloudDeviceIntegration (Sungrow, Growatt, etc.)
        # ---------------------------------------------------------

        pv_devices = []
        grid_devices = []
        battery_devices = []
        load_devices = []
        inverter_devices = []

        for d in active_devices:
            cfg = getattr(d, "config", None)
            role = (cfg.role.key if cfg and cfg.role else "").lower()
            sig = (cfg.energy_signal_type.key if cfg and cfg.energy_signal_type else "").lower()
            metric_def = (cfg.metric_definition.key if cfg and cfg.metric_definition else "").lower()
            gen_type = getattr(cfg, "generator_type", None)
            is_grid_source = getattr(cfg, "is_grid_source", False)
            name_lower = (d.name or d.identifier or "").lower()

            metrics_map = {m.metric_key.lower(): m.value for m in d.latest_metrics.all()}
            metrics_keys = set(metrics_map.keys())

            is_cloud_inv = d.id in cloud_inverter_ids
            has_inv_keywords = any(kw in name_lower for kw in ["sungrow", "growatt", "fronius", "solaredge", "kostal", "deye", "huawei", "goodwe", "solis", "victron", "wechselrichter", "inverter"])
            is_hybrid_inverter = is_cloud_inv or (has_inv_keywords and any(k in metrics_keys for k in ["pv_power", "grid_power", "battery_power", "load_power"])) or role == "inverter"

            if is_hybrid_inverter:
                inverter_devices.append(d)

            # Prüfen auf reine Batterie-/SoC-Kennzeichnung:
            is_battery_profile = (
                role in ["battery", "storage", "speicher", "akku"]
                or sig in ["battery", "storage", "speicher"]
                or metric_def in ["soc", "battery_soc", "battery_power", "battery_level"]
                or d.id in storage_device_ids
                or d.id in ems_batt_device_ids
                or (("batterie" in name_lower or "battery" in name_lower or "soc" in name_lower) and not is_hybrid_inverter)
            )

            # 1. Säule PV (Solar / Erzeugung)
            # Ausschluss: Reine Batterie/SoC-Geräte dürfen NIEMALS in PV landen!
            if not is_battery_profile and (
                gen_type is not None
                or role in ["producer", "pv", "hybrid", "inverter", "generator"]
                or sig in ["pv", "solar", "producer", "generation"]
                or d.id in generator_device_ids
                or d.id in ems_pv_device_ids
                or is_cloud_inv
                or is_hybrid_inverter
                or any(k in metrics_keys for k in ["pv_power", "solar_power", "power_pv", "yield_power", "production"])
            ):
                pv_devices.append(d)

            # 2. Säule Grid (Netzzähler / SmartMeter)
            # Nur echte Zähler / Hauptmessungen oder dedizierte Zähler-Signale:
            if (
                is_grid_source
                or role in ["grid", "meter", "smart_meter", "zaehler", "main_meter"]
                or sig in ["grid", "grid_import", "grid_feed_in", "meter"]
                or d.id in ems_grid_device_ids
                or any(kw in name_lower for kw in ["dtsu666", "sdm630", "shelly pro 3em", "tibber", "pulse", "powerfox", "hichi", "lesekopf", "smart meter", "em3"])
                or any(k in metrics_keys for k in ["grid_power", "power_grid", "grid_import_power", "grid_feed_in_power"])
            ):
                grid_devices.append(d)

            # 3. Säule Battery (Batteriespeicher / Ladestand)
            if is_battery_profile or any(k in metrics_keys for k in ["battery_power", "power_battery", "battery_soc", "soc", "battery_level", "capacity_kwh"]):
                battery_devices.append(d)

            # 4. Säule Load (Gesamt-Hausverbrauch direkt)
            # Ausschluss von Einzelverbrauchern / Zwischensteckern (Submetern)
            is_submeter_or_appliance = any(kw in name_lower for kw in [
                "plug", "steckdose", "klima", "aircon", "waschmaschine", "geschirr", "trockner",
                "tv", "kühlschrank", "fridge", "wallbox", "charger", "wärmepumpe", "heatpump", "submeter"
            ])
            if not is_submeter_or_appliance and (
                role in ["house", "hauslast", "total_load", "main_load"]
                or (role in ["consumer", "load"] and sig in ["house", "total_load", "main_load"])
                or any(k in metrics_keys for k in ["house_power", "total_load", "load_power", "power_load", "power_house"])
            ):
                load_devices.append(d)

        # ---------------------------------------------------------
        # ☀️ SÄULE 1: PV-ERZEUGUNG
        # ---------------------------------------------------------
        def _pv_rank(dev):
            score = 0
            if dev.id in cloud_inverter_ids:
                score += 100
            cfg = getattr(dev, "config", None)
            if cfg and getattr(cfg, "generator_type", None):
                score += 50
            if cfg and cfg.role and cfg.role.key in ["producer", "pv", "inverter"]:
                score += 40
            name_low = (dev.name or "").lower()
            if any(kw in name_low for kw in ["sungrow", "growatt", "fronius", "solaredge", "kostal", "wechselrichter", "inverter"]):
                score += 30
            if "batterie" in name_low or "soc" in name_low:
                score -= 80
            return score

        pv_devices.sort(key=_pv_rank, reverse=True)

        has_pv = len(pv_devices) > 0 or len(generators) > 0 or len(ems_pv_device_ids) > 0 or len(cloud_inverter_ids) > 0
        pv_dev = pv_devices[0] if pv_devices else (inverter_devices[0] if inverter_devices else None)

        pv_device_name = None
        if generators and generators[0].name:
            pv_device_name = generators[0].name
        elif pv_dev:
            pv_device_name = pv_dev.name or pv_dev.identifier

        pv_power = None
        if pv_dev:
            m_pv = next((float(m.value) for m in pv_dev.latest_metrics.all() if m.metric_key.lower() in ["pv_power", "solar_power", "power_pv", "yield_power", "pac", "production", "power"] and m.value is not None), None)
            pv_power = m_pv if m_pv is not None else cache.get(f"device:{pv_dev.id}:pv_power")

        pv_status = "ok" if has_pv else "missing"
        if has_pv:
            if pv_power is not None and float(pv_power) > 0:
                pv_status_text = f"Erzeugt {float(pv_power):.0f} W Solarstrom"
            else:
                pv_status_text = "Aktiv und einsatzbereit (0 W / Standby)"
        else:
            pv_status_text = "Nicht angebunden"

        # ---------------------------------------------------------
        # ⚡ SÄULE 2: NETZZÄHLER
        # ---------------------------------------------------------
        def _grid_rank(dev):
            score = 0
            cfg = getattr(dev, "config", None)
            if cfg and getattr(cfg, "is_grid_source", False):
                score += 100
            if cfg and cfg.role and cfg.role.key in ["grid", "meter", "smart_meter", "zaehler", "main_meter"]:
                score += 80
            if cfg and cfg.energy_signal_type and cfg.energy_signal_type.key in ["grid", "grid_import", "grid_feed_in", "meter"]:
                score += 60
            name_low = (dev.name or "").lower()
            if any(kw in name_low for kw in ["dtsu666", "sdm630", "shelly pro 3em", "tibber", "pulse", "powerfox", "hichi", "lesekopf"]):
                score += 50
            return score

        grid_devices.sort(key=_grid_rank, reverse=True)

        grid_dev = None
        grid_device_name = None
        has_grid = False

        if grid_devices:
            grid_dev = grid_devices[0]
            grid_device_name = grid_dev.name or grid_dev.identifier
            has_grid = True
        elif inverter_devices:
            # Fallback auf Wechselrichter-integrierten Zählerkanal
            inv_with_grid = next((inv for inv in inverter_devices if any(m.metric_key.lower() in ["grid_power", "power_grid", "dtsu666"] for m in inv.latest_metrics.all())), None)
            if inv_with_grid:
                grid_dev = inv_with_grid
                grid_device_name = f"{inv_with_grid.name or inv_with_grid.identifier} (Inverter SmartMeter)"
                has_grid = True

        grid_power = None
        if grid_dev:
            m_grid = next((float(m.value) for m in grid_dev.latest_metrics.all() if m.metric_key.lower() in ["grid_power", "power_grid", "obis_1_8_0"] and m.value is not None), None)
            grid_power = m_grid if m_grid is not None else cache.get(f"device:{grid_dev.id}:grid_power")

        grid_status_text = "Zweirichtungszähler erfasst Bezug & Einspeisung"
        if has_grid and grid_power is not None:
            if float(grid_power) > 20:
                grid_status_text = f"Netzbezug: {float(grid_power):.0f} W"
            elif float(grid_power) < -20:
                grid_status_text = f"Netzeinspeisung: {abs(float(grid_power)):.0f} W"
            else:
                grid_status_text = "Netz ausgeglichen (0 W)"

        # ---------------------------------------------------------
        # 🔋 SÄULE 3: BATTERIESPEICHER
        # ---------------------------------------------------------
        has_battery = len(storages) > 0 or len(battery_devices) > 0 or any(any(m.metric_key.lower() in ["battery_soc", "battery_power", "soc"] for m in inv.latest_metrics.all()) for inv in inverter_devices)

        battery_dev = battery_devices[0] if battery_devices else (inverter_devices[0] if inverter_devices else None)
        battery_name = None
        if storages and storages[0].name:
            battery_name = storages[0].name
        elif battery_dev:
            battery_name = battery_dev.name or battery_dev.identifier

        battery_capacity = float(storages[0].capacity_kwh) if storages and storages[0].capacity_kwh else None

        batt_soc = None
        batt_pwr = None
        if battery_dev:
            m_soc = next((float(m.value) for m in battery_dev.latest_metrics.all() if m.metric_key.lower() in ["battery_soc", "soc", "battery_level"] and m.value is not None), None)
            batt_soc = m_soc if m_soc is not None else cache.get(f"device:{battery_dev.id}:battery_soc")
            m_pwr = next((float(m.value) for m in battery_dev.latest_metrics.all() if m.metric_key.lower() in ["battery_power", "power_battery"] and m.value is not None), None)
            batt_pwr = m_pwr if m_pwr is not None else cache.get(f"device:{battery_dev.id}:battery_power")

        if has_battery:
            if batt_soc is not None and batt_pwr is not None and abs(float(batt_pwr)) > 20:
                if float(batt_pwr) < 0:
                    battery_status_text = f"Lädt mit {abs(float(batt_pwr)):.0f} W ({float(batt_soc):.1f}% SoC)"
                else:
                    battery_status_text = f"Entlädt mit {float(batt_pwr):.0f} W ({float(batt_soc):.1f}% SoC)"
            elif batt_soc is not None:
                battery_status_text = f"Ladestand: {float(batt_soc):.1f}% SoC"
            elif battery_capacity:
                battery_status_text = f"Speicher aktiv ({battery_capacity:.1f} kWh)"
            else:
                battery_status_text = "Speicher aktiv"
        else:
            battery_status_text = "Kein Speicher (Optional)"

        # ---------------------------------------------------------
        # 🏠 SÄULE 4: HAUSVERBRAUCH
        # ---------------------------------------------------------
        # 4. Zeitzone prüfen
        user_settings = getattr(user, "settings", None) if user else None
        tz_val = user_settings.timezone if (user_settings and getattr(user_settings, "timezone", None)) else None
        has_timezone = bool(tz_val)

        # 5. Energie-Profil des Nutzers ermitteln
        from energy.services.energy_profile import get_user_energy_profile
        energy_profile = get_user_energy_profile(user)
        user_solar_type = energy_profile.get("solar_type", "none")
        user_has_no_solar = (user_solar_type == "none") and not has_pv
        user_expects_battery = bool(energy_profile.get("has_battery", False)) or has_battery

        # 6. Hausverbrauch ermitteln
        has_direct_load = len(load_devices) > 0 or any(any(m.metric_key.lower() in ["load_power", "house_power"] for m in inv.latest_metrics.all()) for inv in inverter_devices)
        load_dev = load_devices[0] if load_devices else None
        load_device_name = (load_dev.name or load_dev.identifier) if load_dev else None
        
        # Bei einem Haushalt ohne Solaranlage ist der Netzbezug direkt gleich dem Hausverbrauch!
        can_calculate_load = has_direct_load or (has_pv and has_grid) or (user_has_no_solar and has_grid)

        # 7. Submeter (Geräte, Räume, Etagen)
        assigned_device_ids = {
            dev.id for dev in (pv_devices + grid_devices + battery_devices + load_devices)
        }
        submeter_devices = [
            d for d in active_devices
            if d.id not in assigned_device_ids
        ]
        rooms_set = {
            d.config.room.name
            for d in submeter_devices
            if getattr(d, "config", None) and d.config.room
        }
        floors_set = {
            d.config.floor.name
            for d in submeter_devices
            if getattr(d, "config", None) and d.config.floor
        }

        # 8. Aktive Alarme & Störungen (z. B. via Sungrow Webhook oder Modbus/MQTT)
        active_alarms = []
        for d in active_devices:
            alarm_info = cache.get(f"device:{d.id}:sungrow_alarm")
            if not alarm_info:
                alarm_m = next((m for m in d.latest_metrics.all() if m.metric_key == "state.alarm" and m.value and float(m.value) > 0), None)
                if alarm_m:
                    alarm_data = alarm_m.data if isinstance(alarm_m.data, dict) else {}
                    alarm_info = {
                        "device_id": d.id,
                        "device_name": d.name or d.identifier,
                        "code": alarm_data.get("code") or int(alarm_m.value),
                        "name": alarm_data.get("name") or "Gerätestörung",
                        "level": alarm_data.get("level", "warning"),
                        "timestamp": alarm_m.timestamp.isoformat() if alarm_m.timestamp else None,
                    }
            if alarm_info:
                active_alarms.append(alarm_info)

        # Prüfen, ob unkonfigurierte Geräte vorliegen
        configured_device_ids = {
            dev.id for dev in (pv_devices + grid_devices + battery_devices + load_devices + inverter_devices)
        } | cloud_inverter_ids | ems_pv_device_ids | ems_grid_device_ids | ems_batt_device_ids
        unconfigured_devices = [
            d for d in active_devices
            if not getattr(d, "configured", False)
            and d.id not in configured_device_ids
            and (not getattr(d, "config", None) or not getattr(d.config, "role", None) or d.config.role.key in ["unknown", "unassigned", "default"])
        ]

        # 9. Readiness Score & Status-Ampel berechnen (Profil-abhängig 0 .. 100%)
        score = 0
        if user_has_no_solar:
            # Haushalt ohne Solar: Netzzähler (50%), Hauslast (35%), Zeitzone (15%)
            if has_grid:
                score += 50
            if can_calculate_load:
                score += 35
            if has_timezone:
                score += 15
        elif user_expects_battery:
            # PV + Speicher Prosumer
            if has_pv:
                score += 30
            if has_grid:
                score += 30
            if can_calculate_load:
                score += 20
            if has_battery:
                score += 10
            if has_timezone:
                score += 10
        else:
            # PV / BKW ohne Speicher Prosumer
            if has_pv:
                score += 35
            if has_grid:
                score += 35
            if can_calculate_load:
                score += 20
            if has_timezone:
                score += 10

        if unconfigured_devices:
            score = max(0, score - min(25, len(unconfigured_devices) * 10))

        if active_alarms:
            # Bei aktiven Hardware-Störungen Score anpassen
            score = max(20, score - 30)

        recommendations: List[Dict[str, Any]] = []

        for alarm in active_alarms:
            recommendations.append({
                "priority": "critical",
                "pillar": "device_fault",
                "title": f"🚨 Störung: {alarm.get('name')}",
                "text": f"{alarm.get('device_name')} meldet eine Störung (Code {alarm.get('code')}). Bitte Anlage und Verbindung prüfen.",
                "action": "check_device_fault",
            })

        if user_has_no_solar:
            if not has_grid:
                recommendations.append({
                    "priority": "critical",
                    "pillar": "grid",
                    "title": "Stromzähler verknüpfen",
                    "text": "Verbinde deinen digitalen Stromzähler (z. B. Tibber Pulse, Shelly 3EM oder Powerfox), um deinen Verbrauch live zu erfassen.",
                    "action": "connect_grid_meter",
                })
        else:
            if not has_pv and not has_grid:
                recommendations.append({
                    "priority": "critical",
                    "pillar": "pv_or_grid",
                    "title": "Verbinde deine erste Energiequelle",
                    "text": "Verknüpfe deinen Wechselrichter (z. B. Sungrow, Fronius, SMA) oder deinen digitalen Stromzähler (z. B. Tibber Pulse, Shelly 3EM).",
                    "action": "connect_inverter_or_meter",
                })
            elif has_pv and not has_grid:
                recommendations.append({
                    "priority": "high",
                    "pillar": "grid",
                    "title": "Netzzähler fehlt für Autarkie-Berechnung",
                    "text": "Deine Solaranlage ist verbunden! Damit wir deinen Netzbezug, Einspeisevergütung und echte Autarkie berechnen können, verknüpfe deinen Netzstromzähler (z. B. Tibber Pulse, Shelly Pro 3EM oder Powerfox).",
                    "action": "connect_grid_meter",
                })
            elif has_grid and not has_pv:
                recommendations.append({
                    "priority": "medium",
                    "pillar": "pv",
                    "title": "Solaranlage hinzufügen",
                    "text": "Dein Netzstromzähler ist aktiv. Wenn du eine Solaranlage oder ein Balkonkraftwerk besitzt, kannst du sie jetzt verbinden, um deine Einsparungen live zu sehen.",
                    "action": "connect_pv",
                })

        if not submeter_devices:
            recommendations.append({
                "priority": "low",
                "pillar": "submeters",
                "title": "Räume & Einzelgeräte aufschlüsseln (Optional)",
                "text": "Möchtest du sehen, wie viel Strom deine Wärmepumpe, Wallbox oder Waschmaschine verbraucht? Füge einfach smarte Zwischenstecker (z. B. Shelly Plug) hinzu.",
                "action": "add_submeter",
            })

        if unconfigured_devices:
            cnt = len(unconfigured_devices)
            recommendations.append({
                "priority": "high",
                "pillar": "devices",
                "title": f"{cnt} Gerät{'e' if cnt > 1 else ''} konfigurieren",
                "text": f"{cnt} neue{'s' if cnt == 1 else ''} Gerät{'e' if cnt > 1 else ''} erkannt. Bitte weise Gerätetyp und Raum zu, damit alle Energieflüsse präzise berechnet werden.",
                "action": "configure_devices",
                "count": cnt,
            })

        if not has_timezone:
            recommendations.append({
                "priority": "medium",
                "pillar": "settings",
                "title": "Zeitzone einstellen",
                "text": "Für minutengenaue Auswertungen, Solarprognosen und dynamische Strompreise sollte deine lokale Zeitzone eingestellt sein.",
                "action": "set_timezone",
            })

        # Pillar-Status anpassen bei Störungen
        for alarm in active_alarms:
            if any(p.id == alarm.get("device_id") for p in pv_devices):
                pv_status = "fault"
                pv_status_text = f"🚨 Störung: {alarm.get('name')} (Code {alarm.get('code')})"

        # 10. Pillar-Datenstrukturen aufbereiten
        pv_pillar_data = {
            "installed": has_pv,
            "configured": has_pv or user_has_no_solar,
            "status": "optional" if user_has_no_solar else pv_status,
            "optional": user_has_no_solar,
            "method": "direct" if has_pv else "none",
            "label": "Solarerzeugung",
            "device_name": pv_device_name or ("Nicht vorhanden (Haushalt ohne Solar)" if user_has_no_solar else None),
            "status_text": "Nicht vorhanden (Haushalt ohne Solar)" if user_has_no_solar else pv_status_text,
        }

        grid_pillar_data = {
            "installed": has_grid,
            "configured": has_grid,
            "status": "ok" if has_grid else "missing",
            "optional": False,
            "method": "direct" if has_grid else "none",
            "label": "Netzanschluss & Zähler",
            "device_name": grid_device_name,
            "status_text": grid_status_text if has_grid else "Zähler fehlt noch",
        }

        battery_pillar_data = {
            "installed": has_battery,
            "configured": has_battery or not user_expects_battery,
            "status": ("ok" if has_battery else ("missing" if user_expects_battery else "optional")),
            "optional": not user_expects_battery,
            "method": "direct" if has_battery else "none",
            "label": "Batteriespeicher",
            "device_name": battery_name or ("Kein Speicher (Optional)" if not user_expects_battery else None),
            "capacity_kwh": battery_capacity,
            "status_text": battery_status_text,
        }

        load_device_display = (
            load_device_name
            or ("Direkt über Netzzähler erfasst" if (user_has_no_solar and has_grid) else ("Berechnet (PV + Netz ± Speicher)" if can_calculate_load else None))
        )
        load_status_display = (
            "Vollständig in Echtzeit erfasst" if has_direct_load
            else ("Direkt über Netzzähler erfasst" if (user_has_no_solar and has_grid)
            else ("Wird aus PV & Netz berechnet" if can_calculate_load else "Nicht berechenbar"))
        )

        load_pillar_data = {
            "installed": can_calculate_load,
            "configured": can_calculate_load,
            "status": "ok" if can_calculate_load else "missing",
            "optional": False,
            "method": "direct" if has_direct_load else ("calculated" if can_calculate_load else "none"),
            "label": "Hausverbrauch",
            "device_name": load_device_display,
            "is_direct": has_direct_load or (user_has_no_solar and has_grid),
            "status_text": load_status_display,
        }

        timezone_pillar_data = {
            "installed": has_timezone,
            "configured": has_timezone,
            "status": "ok" if has_timezone else "missing",
            "optional": False,
            "method": "direct" if has_timezone else "none",
            "label": "Zeitzone",
            "device_name": tz_val if tz_val else "Nicht festgelegt",
            "status_text": f"Aktiv ({tz_val})" if tz_val else "Zeitzone fehlt",
        }

        return {
            "score": min(100, score),
            "status": "fault" if active_alarms else ("ready" if score >= 70 else ("partial" if score > 0 else "empty")),
            "alarms": active_alarms,
            "home_name": home.name,
            "energy_profile": energy_profile,
            "pillars": {
                "pv": pv_pillar_data,
                "generation": pv_pillar_data,
                "producer": pv_pillar_data,
                "grid": grid_pillar_data,
                "meter": grid_pillar_data,
                "battery": battery_pillar_data,
                "storage": battery_pillar_data,
                "load": load_pillar_data,
                "consumption": load_pillar_data,
                "timezone": timezone_pillar_data,
                "location": timezone_pillar_data,
                "settings": timezone_pillar_data,
            },
            "submeters": {
                "count": len(submeter_devices),
                "rooms_count": len(rooms_set),
                "rooms": list(rooms_set),
                "floors_count": len(floors_set),
                "floors": list(floors_set),
            },
            "recommendations": recommendations,
        }
    except Exception as exc:
        logger.exception("[SystemHealth] Fehler beim Ermitteln des Systemstatus: %s", exc)
        return {
            "score": 0,
            "status": "error",
            "home_name": getattr(home, "name", "Mein Zuhause") if home else "Mein Zuhause",
            "energy_profile": None,
            "pillars": {},
            "submeters": {"count": 0, "rooms_count": 0, "rooms": [], "floors_count": 0, "floors": []},
            "recommendations": [],
        }

