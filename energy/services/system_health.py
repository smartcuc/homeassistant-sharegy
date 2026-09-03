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
        home = user.homes.first() if hasattr(user, "homes") else None
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
            .select_related("config__role", "config__generator_type", "config__energy_signal_type", "config__room", "config__floor")
            .prefetch_related("latest_metrics")
        )
        active_devices = [d for d in devices if d.active]

        # 2. Prüfen auf Säule 1: Solaranlage (PV)
        pv_devices = []
        for d in active_devices:
            cfg = getattr(d, "config", None)
            role = (cfg.role.key if cfg and cfg.role else "").lower()
            sig = (cfg.energy_signal_type.key if cfg and cfg.energy_signal_type else "").lower()
            name_lower = (d.name or d.identifier or "").lower()

            metrics = {m.metric_key.lower(): m.value for m in d.latest_metrics.all()}
            has_pv_metric = any(k in metrics for k in ["pv_power", "solar_power", "power_pv", "pv", "solar", "yield_power", "production"])

            if role in ["producer", "pv", "hybrid", "both", "inverter", "generator"] or sig in ["pv", "solar", "producer"]:
                pv_devices.append(d)
            elif has_pv_metric:
                pv_devices.append(d)
            elif any(kw in name_lower for kw in ["pv", "solar", "wechselrichter", "inverter", "bkw", "balkon", "fronius", "sungrow", "solaredge", "kostal", "growatt", "deye", "huawei", "goodwe", "solis", "victron"]):
                pv_devices.append(d)
            elif cache.get(f"device:{d.id}:latest_power") is not None and float(cache.get(f"device:{d.id}:latest_power") or 0) > 0:
                if role != "consumer":
                    pv_devices.append(d)

        generators = list(GeneratorSystem.objects.filter(home=home))
        has_pv = len(pv_devices) > 0 or len(generators) > 0
        pv_device_name = pv_devices[0].name if pv_devices else (generators[0].name if generators else None)

        # 3. Prüfen auf Säule 2: Netzanschluss / Smart Meter (Grid)
        grid_sources = list(
            EMSSignalSource.objects.filter(
                home=home,
                signal_type__key__in=["grid", "grid_import", "grid_feed_in"],
            ).select_related("device")
        )
        grid_devices = [s.device for s in grid_sources if s.device and s.device.active]
        if not grid_devices:
            for d in active_devices:
                cfg = getattr(d, "config", None)
                role = (cfg.role.key if cfg and cfg.role else "").lower()
                sig = (cfg.energy_signal_type.key if cfg and cfg.energy_signal_type else "").lower()
                name_lower = (d.name or d.identifier or "").lower()

                metrics = {m.metric_key.lower(): m.value for m in d.latest_metrics.all()}
                has_grid_metric = any(k in metrics for k in ["grid_power", "power_grid", "grid", "power_import", "power_export", "obis_1_8_0", "obis_2_8_0", "energy_in", "energy_out", "1.8.0", "2.8.0"])

                if role in ["grid", "meter", "smart_meter", "zaehler", "main_meter"] or sig in ["grid", "grid_import", "grid_feed_in", "meter"]:
                    grid_devices.append(d)
                elif has_grid_metric:
                    grid_devices.append(d)
                elif any(kw in name_lower for kw in ["grid", "netz", "meter", "zähler", "tibber", "pulse", "powerfox", "shelly pro 3em", "shelly 3em", "em3", "pro3em", "smart meter", "hichi", "lesekopf"]):
                    grid_devices.append(d)
                elif cache.get(f"device:{d.id}:grid_power") is not None:
                    grid_devices.append(d)

        has_grid = len(grid_devices) > 0
        grid_device_name = grid_devices[0].name if grid_devices else None

        # 4. Prüfen auf Säule 3: Batteriespeicher (Battery)
        storages = list(StorageSystem.objects.filter(home=home, active=True))
        battery_devices = []
        for d in active_devices:
            cfg = getattr(d, "config", None)
            role = (cfg.role.key if cfg and cfg.role else "").lower()
            sig = (cfg.energy_signal_type.key if cfg and cfg.energy_signal_type else "").lower()
            name_lower = (d.name or d.identifier or "").lower()

            metrics = {m.metric_key.lower(): m.value for m in d.latest_metrics.all()}
            has_batt_metric = any(k in metrics for k in ["battery_power", "power_battery", "battery_soc", "soc", "battery_level", "battery_current"])

            if role in ["battery", "storage", "speicher", "akku"] or sig in ["battery", "storage", "speicher"]:
                battery_devices.append(d)
            elif has_batt_metric:
                battery_devices.append(d)
            elif any(kw in name_lower for kw in ["batterie", "battery", "speicher", "akku", "luna", "byd", "pylontech", "sbr"]):
                battery_devices.append(d)
            elif cache.get(f"device:{d.id}:battery_power") is not None or cache.get(f"device:{d.id}:battery_soc") is not None:
                battery_devices.append(d)

        has_battery = len(storages) > 0 or len(battery_devices) > 0
        battery_name = storages[0].name if storages else (battery_devices[0].name if battery_devices else None)
        battery_capacity = float(storages[0].capacity_kwh) if storages else None

        # 5. Prüfen auf Säule 4: Gesamthauslast (Load)
        has_direct_load = False
        load_device_name = None
        for d in active_devices:
            cfg = getattr(d, "config", None)
            role = (cfg.role.key if cfg and cfg.role else "").lower()
            sig = (cfg.energy_signal_type.key if cfg and cfg.energy_signal_type else "").lower()
            name_lower = (d.name or d.identifier or "").lower()

            metrics = {m.metric_key.lower(): m.value for m in d.latest_metrics.all()}
            has_load_metric = any(k in metrics for k in ["load_power", "consumption", "house_power", "power_load", "load", "total_load"])

            if role in ["consumer", "load", "house", "hauslast"] or sig in ["load", "consumption", "house"] or has_load_metric or cache.get(f"device:{d.id}:load_power") is not None:
                has_direct_load = True
                load_device_name = d.name
                break

        can_calculate_load = has_direct_load or (has_pv and has_grid)

        # 6. Submeter (Geräte, Räume, Etagen)
        submeter_devices = [
            d for d in active_devices
            if d not in pv_devices and d not in grid_devices and d not in battery_devices
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

        # 7. Aktive Alarme & Störungen (z. B. via Sungrow Webhook oder Modbus/MQTT)
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

        # 8. Readiness Score & Status-Ampel berechnen (0 .. 100%)
        score = 0
        if has_pv:
            score += 35
        if has_grid:
            score += 35
        if can_calculate_load:
            score += 30

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

        # Pillar-Status anpassen bei Störungen
        pv_status = "ok" if has_pv else "missing"
        pv_status_text = "Aktiv und liefert Solarstrom" if has_pv else "Nicht verbunden"
        for alarm in active_alarms:
            if any(p.id == alarm.get("device_id") for p in pv_devices):
                pv_status = "fault"
                pv_status_text = f"🚨 Störung: {alarm.get('name')} (Code {alarm.get('code')})"

        return {
            "score": min(100, score),
            "status": "fault" if active_alarms else ("ready" if score >= 70 else ("partial" if score > 0 else "empty")),
            "alarms": active_alarms,
            "home_name": home.name,
            "pillars": {
                "pv": {
                    "installed": has_pv,
                    "configured": has_pv,
                    "status": pv_status,
                    "method": "direct" if has_pv else "none",
                    "label": "Solarerzeugung",
                    "device_name": pv_device_name,
                    "status_text": pv_status_text,
                },
                "grid": {
                    "installed": has_grid,
                    "configured": has_grid,
                    "status": "ok" if has_grid else "missing",
                    "method": "direct" if has_grid else "none",
                    "label": "Netzanschluss & Zähler",
                    "device_name": grid_device_name,
                    "status_text": "Zweirichtungszähler erfasst Bezug & Einspeisung" if has_grid else "Zähler fehlt noch",
                },
                "battery": {
                    "installed": has_battery,
                    "configured": has_battery,
                    "status": "ok" if has_battery else "optional",
                    "method": "direct" if has_battery else "none",
                    "label": "Batteriespeicher",
                    "device_name": battery_name,
                    "capacity_kwh": battery_capacity,
                    "status_text": f"Speicher aktiv ({battery_capacity} kWh)" if has_battery and battery_capacity else ("Speicher aktiv" if has_battery else "Kein Speicher (Optional)"),
                },
                "load": {
                    "installed": can_calculate_load,
                    "configured": can_calculate_load,
                    "status": "ok" if can_calculate_load else "missing",
                    "method": "direct" if has_direct_load else ("calculated" if can_calculate_load else "none"),
                    "label": "Hausverbrauch",
                    "device_name": load_device_name or ("Berechnet (PV + Netz ± Speicher)" if can_calculate_load else None),
                    "is_direct": has_direct_load,
                    "status_text": "Vollständig in Echtzeit erfasst" if has_direct_load else ("Wird aus PV & Netz berechnet" if can_calculate_load else "Nicht berechenbar"),
                },
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
            "pillars": {},
            "submeters": {"count": 0, "rooms_count": 0, "rooms": [], "floors_count": 0, "floors": []},
            "recommendations": [],
        }
