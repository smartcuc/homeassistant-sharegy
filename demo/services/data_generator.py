##################################
# demo/services/data_generator.py
##################################

import math
import random
import logging
from datetime import datetime, timedelta, timezone as dt_timezone
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
    DeviceMetric1h,
    DeviceMetric5m,
    CloudDeviceIntegration,
)
from devices.models_ocpp import ChargingStation
from producer.models import (
    GeneratorType,
    Orientation,
    GeneratorSystem,
    GeneratorString,
    StorageSystem,
)
from energy.models import EMSSignalType
from energy.ems.models import EMSSignalSource
from devices.services.ingest import ingest_metric_payload
from forecast.services_weather import fetch_and_store_weather_for_group
from forecast.services_store import save_all_forecasts_for_generator_string

from demo.models import DemoDeviceMap, DemoDeviceSimulation

logger = logging.getLogger(__name__)
User = get_user_model()

DEMO_EMAIL = "demo@sharegy.de"
DEMO_USERNAME = "demo"


def setup_demo_household(target_user=None):
    """
    Erstellt ein eigenständiges, realistisches Prosumer-Demo-Zuhause
    inklusive Erzeuger-Konfiguration (GeneratorSystem/Strings) und 96h-Wetter/PV-Forecast.
    Kann für einen beliebigen Benutzer (oder standardmäßig den Demo-User) aufgerufen werden.
    """
    if target_user is None:
        target_user, _ = User.objects.get_or_create(
            email=DEMO_EMAIL,
            defaults={
                "username": DEMO_USERNAME,
                "is_active": True,
            },
        )

    # ⭐ 0. Demo-User standardmäßig mit aktivem Pro-Plan ausstatten (voller Funktionsumfang)
    from billing.models import EMSSubscription
    EMSSubscription.objects.update_or_create(
        user=target_user,
        defaults={
            "plan": "pro_yearly",
            "status": "active",
            "current_period_end": timezone.now() + timedelta(days=365),
            "payment_provider": "stripe",
        },
    )

    # 1. Altes Home und alte Mappings sauber bereinigen
    target_user.homes.all().delete()
    DemoDeviceMap.objects.all().delete()
    DemoDeviceSimulation.objects.all().delete()


    # 2. Neues Prosumer-Demo-Haus erstellen
    demo_home = Home.objects.create(
        user=target_user,
        name=f"Sharegy Smart Home ({target_user.username})",
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

    # Signal-Typen laden / erstellen (Standard-Keys: pv, grid, load, battery)
    sig_pv, _ = EMSSignalType.objects.get_or_create(key="pv", defaults={"label": "PV"})
    sig_load, _ = EMSSignalType.objects.get_or_create(key="load", defaults={"label": "Verbrauch"})
    sig_bat, _ = EMSSignalType.objects.get_or_create(key="battery", defaults={"label": "Batterie"})
    sig_grid, _ = EMSSignalType.objects.get_or_create(key="grid", defaults={"label": "Netz"})

    # Generator-Typen & Orientierungen
    gen_solar, _ = GeneratorType.objects.get_or_create(key="solar", defaults={"name": "Photovoltaik", "icon": "☀️"})
    GeneratorType.objects.get_or_create(key="pv", defaults={"name": "Photovoltaik", "icon": "☀️"})

    ori_south, _ = Orientation.objects.get_or_create(key="s", defaults={"name": "Süd", "azimuth_deg": 180, "sort_order": 1})
    Orientation.objects.get_or_create(key="sw", defaults={"name": "Süd-West", "azimuth_deg": 225, "sort_order": 2})
    Orientation.objects.get_or_create(key="so", defaults={"name": "Süd-Ost", "azimuth_deg": 135, "sort_order": 3})
    Orientation.objects.get_or_create(key="w", defaults={"name": "West", "azimuth_deg": 270, "sort_order": 4})
    Orientation.objects.get_or_create(key="o", defaults={"name": "Ost", "azimuth_deg": 90, "sort_order": 5})

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
        energy_signal_type=sig_pv,
        metric_definition=m_power,
        floor=floor_og,
        room=room_roof,
    )
    devices["pv"] = d_pv

    # Erzeuger-System & Generator-String für Erzeuger-Verwaltung und Forecast-Engine!
    gen_system = GeneratorSystem.objects.create(
        home=demo_home,
        device=d_pv,
        name="PV-Dachanlage 10 kWp",
        generator_type=gen_solar,
        peak_power_kw=10.0,
        inverter_power_kw=10.0,
        battery_capacity_kwh=10.0,
        active=True,
    )
    gen_string = GeneratorString.objects.create(
        generator=gen_system,
        name="Dach Süd (Hauptstring 10 kWp)",
        module_count=24,
        peak_power_kwp=10.0,
        orientation=ori_south,
        tilt_deg=35,
        shading_percent=0.0,
    )

    # Initialen Wetter- und PV-Forecast für das Demo-Haus berechnen
    try:
        fetch_and_store_weather_for_group([demo_home], hours=96)
        save_all_forecasts_for_generator_string(gen_string)
        logger.info("Wetter- und PV-Prognose für Demo-Haus initialisiert.")
    except Exception as e:
        logger.warning("Forecast-Initialisierung für Demo-Haus übersprungen: %s", e)

    # B. Batteriespeicher (10 kWh) & Sungrow Cloud Integration
    d_bat = Device.objects.create(home=demo_home, identifier="demo_battery_storage", configured=True, active=True)
    DeviceConfig.objects.create(
        device=d_bat,
        home=demo_home,
        name="Sungrow SBR100 Heimspeicher 10 kWh",
        role=role_battery,
        energy_signal_type=sig_bat,
        metric_definition=m_power,
        floor=floor_ug,
        room=room_tech,
    )
    devices["battery"] = d_bat

    # StorageSystem für Batterie-Arbitrage & EMS
    StorageSystem.objects.create(
        home=demo_home,
        primary_device=d_bat,
        name="Sungrow SBR100 Batteriespeicher",
        capacity_kwh=10.0,
        max_charge_power_kw=5.0,
        max_discharge_power_kw=5.0,
        ems_control_enabled=True,
        control_mode="price_optimized",
        price_threshold_ct=16.5,
        target_charge_power_kw=4.5,
    )

    # Sungrow iSolarCloud Integration
    CloudDeviceIntegration.objects.create(
        device=d_pv,
        profile_id="sungrow_isolarcloud",
        credentials={
            "appkey": "988713D7D057090474AEC9584CBA1AAD",
            "token": "sg_oauth_demo_123",
            "ps_id": "demo_plant_01",
        },
        is_active=True,
    )

    # C. Smart Meter / Netzzähler
    d_grid = Device.objects.create(home=demo_home, identifier="demo_smart_meter", configured=True, active=True)
    DeviceConfig.objects.create(
        device=d_grid,
        home=demo_home,
        name="Hauptzähler (Discovergy iMSys)",
        role=role_grid,
        energy_signal_type=sig_grid,
        metric_definition=m_power,
        floor=floor_ug,
        room=room_tech,
    )
    devices["grid"] = d_grid

    # D. Wärmepumpe
    d_hp = Device.objects.create(home=demo_home, identifier="demo_heatpump", configured=True, active=True)
    DeviceConfig.objects.create(
        device=d_hp,
        home=demo_home,
        name="Wärmepumpe Luft-Wasser",
        role=role_consumer,
        energy_signal_type=sig_load,
        metric_definition=m_power,
        floor=floor_ug,
        room=room_tech,
    )
    devices["heatpump"] = d_hp

    # E. Wallbox (OCPP 1.6-J EV Charger)
    d_wb = Device.objects.create(home=demo_home, identifier="demo_wallbox_ev", configured=True, active=True)
    DeviceConfig.objects.create(
        device=d_wb,
        home=demo_home,
        name="Easee Charge Wallbox 11 kW",
        role=role_consumer,
        energy_signal_type=sig_load,
        metric_definition=m_power,
        floor=floor_eg,
        room=room_garage,
    )
    devices["wallbox"] = d_wb

    # OCPP ChargingStation Instanz
    ChargingStation.objects.create(
        home=demo_home,
        charge_point_id="DEMO-WALLBOX-01",
        name="Easee Charge (Garage)",
        vendor="Easee",
        model="Easee Charge 11kW",
        serial_number="EAS-DEMO-98214",
        firmware_version="v2.4.1",
        status="Charging",
        is_online=True,
        last_heartbeat=timezone.now(),
        connectors_count=1,
        phases=3,
        max_current_a=16.0,
        min_current_a=6.0,
        smart_charging_mode="pv_surplus",
        active_power_w=4200.0,
        target_current_a=10.0,
        total_energy_kwh=1450.5,
    )

    # F. Haushalt Grundlast / Wohnbereich
    d_house = Device.objects.create(home=demo_home, identifier="demo_household_load", configured=True, active=True)
    DeviceConfig.objects.create(
        device=d_house,
        home=demo_home,
        name="Haushalt & Küche",
        role=role_consumer,
        energy_signal_type=sig_load,
        metric_definition=m_power,
        floor=floor_eg,
        room=room_living,
    )
    devices["household"] = d_house

    # 30 Tage konsistente Stunden-Historie für Energiebilanz & Sub-Metering generieren
    try:
        generate_demo_historical_metrics(demo_home=demo_home, days=30)
    except Exception as e:
        logger.warning("Historische Demodaten-Generierung übersprungen: %s", e)

    # Realistische Demo-Alarme für den Demo-User erzeugen
    try:
        seed_demo_home_alerts(demo_home=demo_home)
    except Exception as e:
        logger.warning("Demo-Alarm-Generierung übersprungen: %s", e)

    # Realistische Demo-Rechnungen im Profil/Billing erzeugen
    try:
        from billing.services_subscription import seed_demo_invoices
        seed_demo_invoices(target_user)
    except Exception as e:
        logger.warning("Demo-Rechnungs-Generierung übersprungen: %s", e)

    logger.info("Demo Smart Home erfolgreich mit %d Geräten initialisiert", len(devices))
    return demo_home


def seed_demo_home_alerts(demo_home):
    """
    Erzeugt vorab erstellte, realistische Alarme für das Demo-Zuhause,
    damit Besucher in der Alarmzentrale sofort ein lebendiges Bild sehen.
    """
    from alerts.models import AlertEvent
    from alerts.services import evaluate_home_alerts

    # 1. Aktuelle Live-Regeln ausführen
    evaluate_home_alerts(demo_home)

    now = timezone.now()
    d_wb = demo_home.devices.filter(identifier="demo_wallbox_ev").first()
    d_bat = demo_home.devices.filter(identifier="demo_battery_storage").first()

    AlertEvent.objects.get_or_create(
        home=demo_home,
        alert_type="low_price_window",
        defaults={
            "severity": AlertEvent.SEVERITY_INFO,
            "title": "Günstiges Börsenstrom-Fenster erkannt",
            "message": "Heute zwischen 13:00 und 16:00 Uhr sinkt der Börsenstrompreis auf unter 12 ct/kWh. Perfekter Zeitpunkt zum Laden deines E-Autos oder für die Waschmaschine.",
            "action_hint": "Wallbox / Großverbraucher jetzt einplanen",
            "action_type": "optimize_consumption",
            "status": AlertEvent.STATUS_ACTIVE,
            "device": d_wb,
        },
    )

    AlertEvent.objects.get_or_create(
        home=demo_home,
        alert_type="battery_empty",
        defaults={
            "severity": AlertEvent.SEVERITY_WARNING,
            "title": "Hausspeicher unter 20 % Restkapazität",
            "message": "Der Batteriespeicher nähert sich der Reservegrenze (18 % SoC). Für die Abendstunden wird Netzbezug prognostiziert.",
            "action_hint": "Verbraucher auf PV-Überschuss ausrichten",
            "action_type": "charge_battery",
            "status": AlertEvent.STATUS_ACTIVE,
            "device": d_bat,
        },
    )

    AlertEvent.objects.get_or_create(
        home=demo_home,
        alert_type="negative_price",
        defaults={
            "severity": AlertEvent.SEVERITY_INFO,
            "title": "Negativer Strompreis am Wochenende",
            "message": "Am Sonntag traten zwischen 12:00 und 14:00 Uhr negative Strompreise (-3,4 ct/kWh) auf. Der Speicher wurde automatisch voll geladen.",
            "action_hint": "Historischen Zyklus ansehen",
            "action_type": "view_history",
            "status": AlertEvent.STATUS_RESOLVED,
            "resolved_at": now - timedelta(days=2),
        },
    )


def generate_demo_historical_metrics(demo_home=None, days: int = 30):
    """
    Generiert vollständige stündliche DeviceMetric1h-Aggregate für alle Demo-Geräte
    über die vergangenen X Tage, damit alle Zeiträume (Heute, 7T, 30T, Jahr)
    mit physikalisch stimmigen, hochqualitativen Daten gefüllt sind.
    """
    if demo_home is None:
        demo_home = Home.objects.filter(user__email=DEMO_EMAIL).first()
        if not demo_home:
            return 0

    devices = {d.identifier: d for d in demo_home.devices.all()}
    if not devices:
        return 0

    now = timezone.now().replace(minute=0, second=0, microsecond=0)
    total_hours = days * 24

    records_to_create = []

    for h_offset in range(total_hours, -1, -1):
        bucket_time = now - timedelta(hours=h_offset)
        hour_float = bucket_time.hour + 0.5

        # 1. ☀️ PV Erzeugung
        pv_power = 0.0
        if 5.5 <= hour_float <= 21.0:
            sun_factor = math.sin((hour_float - 5.5) / (21.0 - 5.5) * math.pi)
            if sun_factor > 0:
                day_weather_factor = 0.85 + 0.25 * math.sin(bucket_time.day * 1.5)
                pv_power = round(7500.0 * (sun_factor ** 1.3) * max(0.2, day_weather_factor), 1)

        # 2. 🏠 Haushalt & Küche
        base_load = 230.0 + 15.0 * math.sin(hour_float * 0.5)
        morning_peak = 1100.0 * math.exp(-0.5 * ((hour_float - 7.5) / 0.8) ** 2) if 6.0 <= hour_float <= 9.5 else 0.0
        noon_peak = 1600.0 * math.exp(-0.5 * ((hour_float - 12.5) / 0.7) ** 2) if 11.5 <= hour_float <= 14.0 else 0.0
        evening_peak = 2100.0 * math.exp(-0.5 * ((hour_float - 19.5) / 1.5) ** 2) if 17.5 <= hour_float <= 23.0 else 0.0
        household_power = round(base_load + morning_peak + noon_peak + evening_peak, 1)

        # 3. ♨️ Wärmepumpe
        hp_active = (6.0 <= hour_float <= 8.5) or (17.5 <= hour_float <= 21.5)
        hp_power = 1600.0 if hp_active else 40.0

        # 4. 🚗 Wallbox (alle 2-3 Tage aktiv)
        wb_power = 0.0
        is_charging_day = (bucket_time.weekday() in [1, 3, 5, 6])
        if is_charging_day and (11.5 <= hour_float <= 15.0 and pv_power > 3500.0):
            wb_power = min(pv_power - 1500.0, 7200.0)
        elif is_charging_day and (18.5 <= hour_float <= 21.0):
            wb_power = 3700.0

        total_load = household_power + hp_power + wb_power

        # 5. 🔋 Speicher
        surplus = pv_power - total_load
        if surplus > 100.0:
            bat_power = -min(surplus, 3000.0)
        elif surplus < -100.0:
            bat_power = min(abs(surplus), 2800.0)
        else:
            bat_power = 0.0

        # 6. 🔌 Netz Saldo
        grid_power = round(total_load - pv_power - bat_power, 1)

        dev_values = {
            "demo_pv_inverter": (pv_power, pv_power),
            "demo_household_load": (household_power, household_power),
            "demo_heatpump": (hp_power, hp_power),
            "demo_wallbox_ev": (wb_power, wb_power),
            "demo_battery_storage": (bat_power, abs(bat_power)),
            "demo_smart_meter": (grid_power, abs(grid_power)),
        }

        for dev_key, (avg_val, wh_val) in dev_values.items():
            if dev_key in devices:
                records_to_create.append(
                    DeviceMetric1h(
                        device=devices[dev_key],
                        metric_key="power",
                        bucket=bucket_time,
                        avg=avg_val,
                        min=avg_val * 0.9,
                        max=avg_val * 1.1,
                        count=60,
                        energy_wh=wh_val,
                    )
                )

    DeviceMetric1h.objects.filter(
        device__in=devices.values(),
        bucket__gte=now - timedelta(days=days),
    ).delete()
    DeviceMetric1h.objects.bulk_create(records_to_create, batch_size=1000)
    logger.info("Demo-Historie für %d Tage mit %d Stunden-Einträgen erstellt.", days, len(records_to_create))
    return len(records_to_create)


def generate_demo_telemetry(now: datetime = None, target_user=None) -> dict:
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

    if target_user is not None:
        demo_home = Home.objects.filter(user=target_user).first()
        if not demo_home:
            demo_home = setup_demo_household(target_user=target_user)
    else:
        demo_home = Home.objects.filter(user__email=DEMO_EMAIL).first()
        if not demo_home:
            demo_home = setup_demo_household()

    devices = {d.identifier: d for d in demo_home.devices.all()}
    if not devices:
        demo_home = setup_demo_household(target_user=target_user)
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

    total_load = round(household_power + hp_power + wb_power, 1)

    # 5. 🔋 Batterie-Berechnung (Laden bei Überschuss, Entladen bei Last)
    # EMS-Standard:
    # Entladen (Strom fließt ins Haus): positiv (> 0)
    # Laden (Strom fließt in den Speicher): negativ (< 0)
    net_pv_surplus = pv_power - total_load

    # Letzten SoC laden oder Standard 65%
    last_soc_record = DeviceLatestMetric.objects.filter(
        device=devices.get("demo_battery_storage"),
        metric_key="battery_soc",
    ).first()
    current_soc = float(last_soc_record.value) if last_soc_record and last_soc_record.value is not None else 65.0

    battery_power = 0.0
    if net_pv_surplus > 100.0:
        # PV-Überschuss: Akku lädt (Ladung = negatives Signal im EMS)
        charge_rate = min(net_pv_surplus, 3000.0)
        if current_soc < 98.0:
            battery_power = round(-charge_rate, 1)
            current_soc = min(100.0, current_soc + (charge_rate / 10000.0) * 0.25)
    elif net_pv_surplus < -100.0:
        # Defizit: Akku entlädt (Entladung = positives Signal im EMS)
        discharge_rate = min(abs(net_pv_surplus), 3000.0)
        if current_soc > 10.0:
            battery_power = round(discharge_rate, 1)
            current_soc = max(5.0, current_soc - (discharge_rate / 10000.0) * 0.25)

    current_soc = round(current_soc, 1)

    # 6. 🔌 Netz-Saldo
    # EMS-Standard:
    # Netzbezug (Import): positiv (> 0)
    # Netzeinspeisung (Export): negativ (< 0)
    # Formel: Netzbezug = Last - PV - Batterieentladung (battery_power)
    grid_power = round(total_load - pv_power - battery_power, 1)

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

