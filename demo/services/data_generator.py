##################################
# demo/services/data_generator.py
##################################

import math
import random
import logging
from datetime import datetime, timezone as dt_timezone
from django.utils import timezone
from django.contrib.auth import get_user_model

from devices.models import (
    Home,
    Device,
    DeviceConfig,
    DeviceRole,
    Room,
    Floor,
    MetricDefinition,
    DeviceLatestMetric,
)
from producer.models import GeneratorType
from energy.models import EMSSignalType
from energy.ems.models import EMSSignalSource
from devices.services.ingest import ingest_metric_payload

logger = logging.getLogger(__name__)
User = get_user_model()

DEMO_EMAIL = "demo@sharegy.de"
DEMO_USERNAME = "demo"


def setup_demo_household():
    """
    Erstellt ein eigenständiges, realistisches Prosumer-Demo-Zuhause
    völlig unabhängig von privaten Nutzerkonten.
    """
    demo_user, _ = User.objects.get_or_create(
        email=DEMO_EMAIL,
        defaults={
            "username": DEMO_USERNAME,
            "is_active": True,
        },
    )

    # 1. Altes Demo-Home sauber bereinigen
    demo_user.homes.all().delete()

    # 2. Neues Prosumer-Demo-Haus erstellen
    demo_home = Home.objects.create(
        user=demo_user,
        name="Sharegy Demo Smart Home",
        city="Köln",
        postal_code="50667",
        latitude=50.9375,
        longitude=6.9603,
        timezone="Europe/Berlin",
    )

    # Rollen laden / erstellen
    role_producer, _ = DeviceRole.objects.get_or_create(key="producer", defaults={"label": "Erzeuger"})
    role_consumer, _ = DeviceRole.objects.get_or_create(key="consumer", defaults={"label": "Verbraucher"})
    role_battery, _ = DeviceRole.objects.get_or_create(key="battery", defaults={"label": "Speicher"})
    role_grid, _ = DeviceRole.objects.get_or_create(key="grid", defaults={"label": "Netzzähler"})

    # Signal-Typen laden / erstellen
    sig_pv, _ = EMSSignalType.objects.get_or_create(key="pv_production", defaults={"label": "PV-Erzeugung"})
    sig_load, _ = EMSSignalType.objects.get_or_create(key="home_load", defaults={"label": "Hausverbrauch"})
    sig_bat, _ = EMSSignalType.objects.get_or_create(key="battery_power", defaults={"label": "Batterieleistung"})
    sig_grid, _ = EMSSignalType.objects.get_or_create(key="grid_feed", defaults={"label": "Netzeinspeisung / Bezug"})

    # Generator-Typ
    gen_solar, _ = GeneratorType.objects.get_or_create(key="solar", defaults={"name": "Photovoltaik"})

    # Räume & Etagen
    floor_eg, _ = Floor.objects.get_or_create(name="Erdgeschoss")
    floor_og, _ = Floor.objects.get_or_create(name="Obergeschoss")
    floor_ug, _ = Floor.objects.get_or_create(name="Keller / Technik")

    room_roof, _ = Room.objects.get_or_create(name="Dach")
    room_tech, _ = Room.objects.get_or_create(name="Technikraum")
    room_living, _ = Room.objects.get_or_create(name="Wohnbereich")
    room_garage, _ = Room.objects.get_or_create(name="Garage")

    # Metrik-Definitionen
    m_power, _ = MetricDefinition.objects.get_or_create(key="power", defaults={"name": "Wirkleistung", "unit": "W"})
    MetricDefinition.objects.get_or_create(key="voltage_l1", defaults={"name": "Spannung L1", "unit": "V"})
    MetricDefinition.objects.get_or_create(key="current_l1", defaults={"name": "Strom L1", "unit": "A"})
    MetricDefinition.objects.get_or_create(key="battery_soc", defaults={"name": "Batterieladestand", "unit": "%"})

    devices = {}

    # A. PV-Dachanlage (10 kWp)
    d_pv = Device.objects.create(home=demo_home, identifier="demo_pv_inverter", configured=True, active=True)
    DeviceConfig.objects.create(
        device=d_pv,
        home=demo_home,
        name="PV Dachanlage 10 kWp",
        role=role_producer,
        generator_type=gen_solar,
        metric_definition=m_power,
        floor=floor_og,
        room=room_roof,
    )
    EMSSignalSource.objects.create(home=demo_home, device=d_pv, signal_type=sig_pv)
    devices["pv"] = d_pv

    # B. Batteriespeicher (10 kWh)
    d_bat = Device.objects.create(home=demo_home, identifier="demo_battery_storage", configured=True, active=True)
    DeviceConfig.objects.create(
        device=d_bat,
        home=demo_home,
        name="Heimspeicher 10 kWh",
        role=role_battery,
        metric_definition=m_power,
        floor=floor_ug,
        room=room_tech,
    )
    EMSSignalSource.objects.create(home=demo_home, device=d_bat, signal_type=sig_bat)
    devices["battery"] = d_bat

    # C. Smart Meter / Netzzähler
    d_grid = Device.objects.create(home=demo_home, identifier="demo_smart_meter", configured=True, active=True)
    DeviceConfig.objects.create(
        device=d_grid,
        home=demo_home,
        name="Hauptzähler (iMSys)",
        role=role_grid,
        metric_definition=m_power,
        floor=floor_ug,
        room=room_tech,
    )
    EMSSignalSource.objects.create(home=demo_home, device=d_grid, signal_type=sig_grid)
    devices["grid"] = d_grid

    # D. Wärmepumpe
    d_hp = Device.objects.create(home=demo_home, identifier="demo_heatpump", configured=True, active=True)
    DeviceConfig.objects.create(
        device=d_hp,
        home=demo_home,
        name="Wärmepumpe Luft-Wasser",
        role=role_consumer,
        metric_definition=m_power,
        floor=floor_ug,
        room=room_tech,
    )
    devices["heatpump"] = d_hp

    # E. Wallbox (EV Charger)
    d_wb = Device.objects.create(home=demo_home, identifier="demo_wallbox_ev", configured=True, active=True)
    DeviceConfig.objects.create(
        device=d_wb,
        home=demo_home,
        name="Wallbox 11 kW (Garage)",
        role=role_consumer,
        metric_definition=m_power,
        floor=floor_eg,
        room=room_garage,
    )
    devices["wallbox"] = d_wb

    # F. Haushalt Grundlast / Wohnbereich
    d_house = Device.objects.create(home=demo_home, identifier="demo_household_load", configured=True, active=True)
    DeviceConfig.objects.create(
        device=d_house,
        home=demo_home,
        name="Haushalt & Küche",
        role=role_consumer,
        metric_definition=m_power,
        floor=floor_eg,
        room=room_living,
    )
    devices["household"] = d_house

    logger.info("Demo Smart Home erfolgreich mit %d Geräten initialisiert", len(devices))
    return demo_home


def generate_demo_telemetry(now: datetime = None) -> dict:
    """
    Erzeugt physikalisch realistische, dynamische Messwerte für das Demo-Haus:
    - Sonnengang & PV-Erzeugung (0 W nachts, Sinus-Glockenkurve tagsüber)
    - Tageszeitabhängiger Haushaltsverbrauch (Morgen-, Mittag- und Abendpeaks)
    - Dynamische Batterieladung / -entladung mit SoC-Berechnung
    - Netzbezug / Netzeinspeisung als Saldo
    - Multi-Channel Werte: Wirkleistung, Spannung, Strom, SoC
    """
    if now is None:
        now = timezone.now()

    demo_home = Home.objects.filter(user__email=DEMO_EMAIL).first()
    if not demo_home:
        demo_home = setup_demo_household()

    devices = {d.identifier: d for d in demo_home.devices.all()}
    if not devices:
        demo_home = setup_demo_household()
        devices = {d.identifier: d for d in demo_home.devices.all()}

    # Lokale Stunde (0.00 bis 23.99)
    hour_float = now.hour + (now.minute / 60.0) + (now.second / 3600.0)

    # 1. ☀️ PV-Erzeugung berechnen (Peak um 13:00 Uhr mit max 7.500 W)
    pv_power = 0.0
    if 5.5 <= hour_float <= 21.0:
        # Sonnenwinkel-Faktor (Sinuskurve)
        sun_factor = math.sin((hour_float - 5.5) / (21.0 - 5.5) * math.pi)
        if sun_factor > 0:
            noise = random.uniform(0.92, 1.05)
            pv_power = round(7500.0 * (sun_factor ** 1.3) * noise, 1)

    # 2. 🏠 Haushalt-Verbrauch berechnen
    base_load = 220.0 + random.uniform(-15.0, 25.0)
    morning_peak = 1200.0 * math.exp(-0.5 * ((hour_float - 7.5) / 0.8) ** 2) if 6.0 <= hour_float <= 9.5 else 0.0
    noon_peak = 1800.0 * math.exp(-0.5 * ((hour_float - 12.5) / 0.7) ** 2) if 11.5 <= hour_float <= 14.0 else 0.0
    evening_peak = 2200.0 * math.exp(-0.5 * ((hour_float - 19.5) / 1.5) ** 2) if 17.5 <= hour_float <= 23.0 else 0.0

    household_power = round(base_load + morning_peak + noon_peak + evening_peak, 1)

    # 3. ♨️ Wärmepumpe (zyklischer Betrieb, morgens & abends aktiv)
    hp_active = (6.0 <= hour_float <= 9.0) or (17.0 <= hour_float <= 22.0)
    hp_power = round(1650.0 + random.uniform(-50.0, 70.0), 1) if hp_active else round(35.0 + random.uniform(0, 10), 1)

    # 4. 🚗 Wallbox (lädt tagsüber bei PV-Überschuss oder abends ab 18 Uhr)
    wb_power = 0.0
    if (11.0 <= hour_float <= 15.0 and pv_power > 4000.0):
        wb_power = round(min(pv_power - 2000.0, 7400.0), 1)
    elif (18.5 <= hour_float <= 21.0):
        wb_power = 3700.0

    total_load = household_power + hp_power + wb_power

    # 5. 🔋 Batterie-Berechnung (Laden bei Überschuss, Entladen bei Last)
    net_pv_surplus = pv_power - total_load

    # Letzten SoC laden oder Standard 65%
    last_soc_record = DeviceLatestMetric.objects.filter(
        device=devices.get("demo_battery_storage"),
        metric_key="battery_soc",
    ).first()
    current_soc = float(last_soc_record.value) if last_soc_record and last_soc_record.value is not None else 65.0

    battery_power = 0.0
    if net_pv_surplus > 100.0:
        # PV-Überschuss: Akku lädt (positiver Wert)
        charge_rate = min(net_pv_surplus, 3000.0)
        if current_soc < 98.0:
            battery_power = round(charge_rate, 1)
            current_soc = min(100.0, current_soc + (battery_power / 10000.0) * 0.25)
    elif net_pv_surplus < -100.0:
        # Defizit: Akku entlädt (negativer Wert)
        discharge_rate = min(abs(net_pv_surplus), 3000.0)
        if current_soc > 10.0:
            battery_power = round(-discharge_rate, 1)
            current_soc = max(5.0, current_soc - (abs(battery_power) / 10000.0) * 0.25)

    current_soc = round(current_soc, 1)

    # 6. 🔌 Netz-Saldo
    # Netzbezug / Einspeisung = Last - (PV + Batterieentladung)
    effective_generation = pv_power + (-battery_power if battery_power < 0 else 0.0)
    effective_load = total_load + (battery_power if battery_power > 0 else 0.0)
    grid_power = round(effective_load - pv_power, 1)

    # 7. Ingestion über die zentrale Ingestion-Pipeline ausführen!
    results = {}

    # PV Inverter Ingestion
    if "demo_pv_inverter" in devices:
        results["pv"] = ingest_metric_payload(
            device=devices["demo_pv_inverter"],
            metrics={
                "power": pv_power,
                "voltage_l1": round(231.2 + random.uniform(-1.5, 1.5), 1),
                "voltage_l2": round(230.8 + random.uniform(-1.5, 1.5), 1),
                "voltage_l3": round(231.5 + random.uniform(-1.5, 1.5), 1),
                "current_l1": round(pv_power / 690.0, 2) if pv_power > 0 else 0.0,
            },
            timestamp=now,
            source="simulator",
            unit_map={"power": "W", "voltage_l1": "V", "voltage_l2": "V", "voltage_l3": "V", "current_l1": "A"},
        )

    # Battery Storage Ingestion
    if "demo_battery_storage" in devices:
        results["battery"] = ingest_metric_payload(
            device=devices["demo_battery_storage"],
            metrics={
                "power": battery_power,
                "battery_soc": current_soc,
                "soc": current_soc,
                "temperature": round(22.5 + (abs(battery_power) / 1000.0) * 1.2, 1),
            },
            timestamp=now,
            source="simulator",
            unit_map={"power": "W", "battery_soc": "%", "soc": "%", "temperature": "°C"},
        )

    # Smart Meter Ingestion
    if "demo_smart_meter" in devices:
        results["grid"] = ingest_metric_payload(
            device=devices["demo_smart_meter"],
            metrics={
                "power": grid_power,
                "voltage_l1": round(230.5 + random.uniform(-1.0, 1.0), 1),
                "voltage_l2": round(231.0 + random.uniform(-1.0, 1.0), 1),
                "voltage_l3": round(229.8 + random.uniform(-1.0, 1.0), 1),
            },
            timestamp=now,
            source="simulator",
            unit_map={"power": "W", "voltage_l1": "V", "voltage_l2": "V", "voltage_l3": "V"},
        )

    # Heatpump Ingestion
    if "demo_heatpump" in devices:
        results["heatpump"] = ingest_metric_payload(
            device=devices["demo_heatpump"],
            metrics={"power": hp_power},
            timestamp=now,
            source="simulator",
            unit_map={"power": "W"},
        )

    # Wallbox Ingestion
    if "demo_wallbox_ev" in devices:
        results["wallbox"] = ingest_metric_payload(
            device=devices["demo_wallbox_ev"],
            metrics={"power": wb_power},
            timestamp=now,
            source="simulator",
            unit_map={"power": "W"},
        )

    # Household Load Ingestion
    if "demo_household_load" in devices:
        results["household"] = ingest_metric_payload(
            device=devices["demo_household_load"],
            metrics={"power": household_power},
            timestamp=now,
            source="simulator",
            unit_map={"power": "W"},
        )

    logger.debug("Demo telemetry generated at %s: PV=%.1fW, Load=%.1fW, Bat=%.1fW (SoC=%.1f%%), Grid=%.1fW",
                 now.isoformat(), pv_power, total_load, battery_power, current_soc, grid_power)

    return {
        "status": "ok",
        "timestamp": now.isoformat(),
        "pv_w": pv_power,
        "load_w": total_load,
        "battery_w": battery_power,
        "battery_soc": current_soc,
        "grid_w": grid_power,
        "devices": list(results.keys()),
    }

