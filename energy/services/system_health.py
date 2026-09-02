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
        )
        active_devices = [d for d in devices if d.active]

        # 2. Prüfen auf Säule 1: Solaranlage (PV)
        pv_devices = []
        for d in active_devices:
            cfg = getattr(d, "config", None)
            role = cfg.role.key if cfg and cfg.role else ""
            sig = cfg.energy_signal_type.key if cfg and cfg.energy_signal_type else ""
            if role in ["producer", "pv", "hybrid", "both"] or sig in ["pv", "solar", "producer"]:
                pv_devices.append(d)
            elif cache.get(f"device:{d.id}:latest_power") is not None and float(cache.get(f"device:{d.id}:latest_power") or 0) > 0:
                if role != "consumer":
                    pv_devices.append(d)

        # Auch DB-Generatoren prüfen
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
                role = cfg.role.key if cfg and cfg.role else ""
                sig = cfg.energy_signal_type.key if cfg and cfg.energy_signal_type else ""
                if role == "grid" or sig in ["grid", "grid_import", "grid_feed_in"]:
                    grid_devices.append(d)
                elif cache.get(f"device:{d.id}:grid_power") is not None:
                    grid_devices.append(d)
                elif DeviceLatestMetric.objects.filter(device=d, metric_key="grid_power").exists():
                    grid_devices.append(d)

        has_grid = len(grid_devices) > 0
        grid_device_name = grid_devices[0].name if grid_devices else None

        # 4. Prüfen auf Säule 3: Batteriespeicher (Battery)
        storages = list(StorageSystem.objects.filter(home=home, active=True))
        battery_devices = []
        for d in active_devices:
            cfg = getattr(d, "config", None)
            role = cfg.role.key if cfg and cfg.role else ""
            sig = cfg.energy_signal_type.key if cfg and cfg.energy_signal_type else ""
            if role in ["battery", "storage", "speicher"] or sig in ["battery", "storage", "speicher"]:
                battery_devices.append(d)
            elif cache.get(f"device:{d.id}:battery_power") is not None or cache.get(f"device:{d.id}:battery_soc") is not None:
                battery_devices.append(d)

        has_battery = len(storages) > 0 or len(battery_devices) > 0
        battery_name = storages[0].name if storages else (battery_devices[0].name if battery_devices else None)
        battery_capacity = float(storages[0].capacity_kwh) if storages else None

        # 5. Prüfen auf Säule 4: Gesamthauslast (Load)
        # Entweder direkt über gemessene load_power (z. B. Sungrow / Hybrid-WR)
        # oder rechnerisch über PV + Grid - Bat
        has_direct_load = False
        for d in active_devices:
            if cache.get(f"device:{d.id}:load_power") is not None or DeviceLatestMetric.objects.filter(device=d, metric_key="load_power").exists():
                has_direct_load = True
                break

        # Berechenbar ist die Hauslast, wenn entweder direkt gemessen ODER wenn PV und Netzzähler vorliegen!
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

        # 7. Readiness Score & Status-Ampel berechnen (0 .. 100%)
        score = 0
        if has_pv:
            score += 35
        if has_grid:
            score += 35
        if can_calculate_load:
            score += 30

        recommendations: List[Dict[str, Any]] = []

        # Recommendations für den Laien / Oma generieren
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

        return {
            "score": min(100, score),
            "status": "ready" if score >= 70 else ("partial" if score > 0 else "empty"),
            "home_name": home.name,
            "pillars": {
                "pv": {
                    "installed": has_pv,
                    "label": "Solarerzeugung",
                    "device_name": pv_device_name,
                    "status_text": "Aktiv und liefert Solarstrom" if has_pv else "Nicht verbunden",
                },
                "grid": {
                    "installed": has_grid,
                    "label": "Netzanschluss & Zähler",
                    "device_name": grid_device_name,
                    "status_text": "Zweirichtungszähler erfasst Bezug & Einspeisung" if has_grid else "Zähler fehlt noch",
                },
                "battery": {
                    "installed": has_battery,
                    "label": "Batteriespeicher",
                    "device_name": battery_name,
                    "capacity_kwh": battery_capacity,
                    "status_text": f"Speicher aktiv ({battery_capacity} kWh)" if has_battery and battery_capacity else ("Speicher aktiv" if has_battery else "Kein Speicher (Optional)"),
                },
                "load": {
                    "installed": can_calculate_load,
                    "label": "Hausverbrauch",
                    "is_direct": has_direct_load,
                    "status_text": "Vollständig in Echtzeit erfasst" if can_calculate_load else "Wird aus PV & Netz berechnet",
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
