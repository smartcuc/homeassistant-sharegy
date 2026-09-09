###################################
# energy/services/energy_profile.py
###################################

import logging
from typing import Dict, Any, List
from django.core.cache import cache
from devices.models import Device, Home
from producer.models import StorageSystem, GeneratorSystem

logger = logging.getLogger(__name__)

CACHE_KEY_PREFIX = "user_energy_profile:"


def calculate_energy_profile_data(
    solar_type: str = "none",  # "none", "bkw", "pv"
    has_battery: bool = False,
    has_ev: bool = False,
    has_heatpump: bool = False,
    tariff_type: str = "static",  # "static", "dynamic"
    lang: str = "de",
) -> Dict[str, Any]:
    """
    Klassifiziert die Hardware- und Tarif-Kombination präzise in die Profile
    A.1 bis F.1 der Feature-User-Matrix und berechnet Einsparpotenziale,
    verschiebbare Lasten sowie fundierte Tarif-Empfehlungen in DE & EN.
    """
    solar_type = (solar_type or "none").lower()
    tariff_type = (tariff_type or "static").lower()
    is_dynamic_tariff = tariff_type == "dynamic"
    is_en = (lang or "de").lower().startswith("en")

    # Standardwerte & Basisfall (Profil A.1)
    profile_code = "A.1"
    profile_name = "Household without Solar" if is_en else "Haushalt ohne Solar"
    profile_subtitle = (
        "Focus on standby reduction, transparency & price alerts"
        if is_en
        else "Fokus auf Standby-Reduktion, Transparenz & Strompreis-Alarm"
    )
    recommended_tariff = "static"
    tariff_verdict_title = (
        "Fixed electricity tariff recommended"
        if is_en
        else "Fester Stromtarif empfohlen"
    )
    tariff_verdict_reason = (
        "Without large flexible loads (such as an EV or heat pump), additional metering and base fees "
        "outweigh spot price advantages. A cost-effective fixed tariff provides optimal predictability."
        if is_en
        else "Ohne große verschiebbare Lasten (wie E-Auto oder Wärmepumpe) fressen "
        "zusätzliche Messstellen- und Grundgebühren den Börsenpreis-Vorteil auf. "
        "Ein günstiger fester Stromtarif bietet optimale Planbarkeit."
    )
    shiftable_kwh_year = 200  # Standby & Haushaltsgeräte
    base_savings_eur = 80  # Standby-Killer & Bewusstsein

    savings_breakdown = [
        {
            "title": "Standby elimination & consumption transparency" if is_en else "Standby-Killer & Verbrauchs-Transparenz",
            "amount_eur": 80,
            "icon": "🔌",
        }
    ]

    action_links = [
        {
            "title": "Check Electricity Tariffs" if is_en else "Strompreise & Tarife prüfen",
            "subtitle": "Configure a competitive fixed-rate tariff" if is_en else "Günstigen Festpreis-Tarif hinterlegen",
            "path": "/app/tariff",
            "icon": "💶",
            "color": "indigo",
        },
        {
            "title": "Connect Smart Plugs" if is_en else "Smarte Zwischenstecker anbinden",
            "subtitle": "Identify standby consumers in the home" if is_en else "Standby-Verbraucher im Haushalt aufspüren",
            "path": "/app/devices",
            "icon": "📟",
            "color": "blue",
        },
    ]

    # =========================================================================
    # ENTSCHEIDUNGSBAUM (MATRIX A.1 BIS F.1)
    # =========================================================================

    # 1. ARCHETYP F.1: ALL-IN (PV/BKW + SPEICHER + EV + WP)
    if (solar_type in ["pv", "bkw"]) and has_battery and has_ev and has_heatpump:
        profile_code = "F.1"
        profile_name = (
            "Fully Electrified: PV + Storage + EV + Heat Pump"
            if is_en
            else "Voll-Elektrifiziert: PV + Speicher + E-Auto + Wärmepumpe"
        )
        profile_subtitle = (
            "Maximum sector coupling & intelligent whole-home EMS"
            if is_en
            else "Maximale Sektorenkopplung & intelligentes Gesamthaus-EMS"
        )
        recommended_tariff = "dynamic"
        tariff_verdict_title = (
            "Dynamic spot tariff is essential!"
            if is_en
            else "Dynamischer Börsenstromtarif ist Pflicht!"
        )
        tariff_verdict_reason = (
            "With over 6,500 kWh of shiftable flexible loads (EV + heating + battery), "
            "savings potential from spot price dips and § 14a discounts is maximized."
            if is_en
            else "Mit über 6.500 kWh verschiebbarer Last (Fahrstrom + Wärme + Batterie) ist das "
            "Einsparpotenzial durch Börsenpreis-Tiefs und § 14a Rabatt maximal."
        )
        shiftable_kwh_year = 6500
        base_savings_eur = 1750
        savings_breakdown = [
            {"title": "PV self-consumption: home, car & heating" if is_en else "PV-Eigenverbrauch Haus, Auto & Wärme", "amount_eur": 1050, "icon": "☀️"},
            {"title": "§ 14a EnWG Module 1 grid fee discount" if is_en else "§ 14a EnWG Modul 1 Netzentgelt-Rabatt", "amount_eur": 160, "icon": "🛡️"},
            {"title": "Dynamic charging & heating during price lows" if is_en else "Dynamisches Laden & Heizen bei Preistiefs", "amount_eur": 420, "icon": "⚡"},
            {"title": "Battery arbitrage in winter" if is_en else "Batterie-Arbitrage im Winter", "amount_eur": 120, "icon": "🔋"},
        ]
        action_links.insert(0, {
            "title": "Smart Load Dispatch Hub",
            "subtitle": "Balance all sectors in real-time" if is_en else "Alle Sektoren in Echtzeit austarieren",
            "path": "/app/control",
            "icon": "🎛️",
            "color": "indigo",
        })

    # 2. ARCHETYP F.1 / E.3: PV + SPEICHER + WÄRMEPUMPE (OHNE EV)
    elif (solar_type in ["pv", "bkw"]) and has_battery and has_heatpump and not has_ev:
        profile_code = "F.1"
        profile_name = "PV System + Storage + Heat Pump" if is_en else "PV-Anlage + Speicher + Wärmepumpe"
        profile_subtitle = (
            "Sector coupling: Solar generation, home battery & heat pump"
            if is_en
            else "Sektorenkopplung: Solarerzeugung, Heimspeicher & Wärmepumpe"
        )
        recommended_tariff = "dynamic"
        tariff_verdict_title = (
            "Dynamic spot tariff recommended"
            if is_en
            else "Dynamischer Börsenstromtarif empfohlen"
        )
        tariff_verdict_reason = (
            "With a heat pump (high winter demand) and home battery, you profit maximally "
            "from dynamic winter price dips, battery arbitrage and § 14a grid fee discounts (~160 €/y)."
            if is_en
            else "Mit Wärmepumpe (hoher Winterstrombedarf) und Heimspeicher profitierst du ideal "
            "von dynamischen Winter-Tiefpreisen, Akku-Arbitrage und § 14a Netzentgelt-Rabatt (~160 €/a)."
        )
        shiftable_kwh_year = 5500
        base_savings_eur = 1450
        savings_breakdown = [
            {"title": "PV self-consumption for home & heat pump" if is_en else "PV-Eigenverbrauch Haus & Wärmepumpe", "amount_eur": 920, "icon": "☀️"},
            {"title": "§ 14a EnWG Module 1 grid fee discount" if is_en else "§ 14a EnWG Modul 1 Netzentgelt-Rabatt", "amount_eur": 160, "icon": "🛡️"},
            {"title": "Dynamic heating during spot price lows" if is_en else "Dynamisches Heizen bei Börsenpreis-Tiefs", "amount_eur": 250, "icon": "♨️"},
            {"title": "Battery arbitrage & winter recharge" if is_en else "Batterie-Arbitrage & Winter-Nachladung", "amount_eur": 120, "icon": "🔋"},
        ]
        action_links.insert(0, {
            "title": "Open Energy Control (HEMS)" if is_en else "Energiesteuerung (HEMS) öffnen",
            "subtitle": "Set priorities between heat pump, storage & home" if is_en else "Prioritäten zwischen Wärmepumpe, Speicher & Haus festlegen",
            "path": "/app/control",
            "icon": "🎛️",
            "color": "indigo",
        })

    # 3. ARCHETYP E.2: PROSUMER MULTI-SEKTOR (PV + SPEICHER + EV)
    elif solar_type == "pv" and has_battery and has_ev and not has_heatpump:
        profile_code = "E.2"
        profile_name = "PV System + Storage + EV" if is_en else "PV-Anlage + Speicher + E-Auto"
        profile_subtitle = (
            "Multi-Sector Prosumer: Solar power for home & mobility"
            if is_en
            else "Multi-Sektor Prosumer: Solarstrom für Haus & Mobilität"
        )
        recommended_tariff = "dynamic"
        tariff_verdict_title = (
            "Dynamic spot tariff recommended"
            if is_en
            else "Dynamischer Börsenstromtarif empfohlen"
        )
        tariff_verdict_reason = (
            "Maximum synergy: EV charges surplus solar during the day or spot price lows at night. "
            "Home storage covers the household."
            if is_en
            else "Maximales Zusammenspiel: E-Auto lädt tagsüber Solarüberschuss oder nachts Börsentiefs. "
            "Der Heimspeicher sichert das Haus ab."
        )
        shiftable_kwh_year = 4500
        base_savings_eur = 1350
        savings_breakdown = [
            {"title": "PV solar power for home & EV" if is_en else "PV-Eigenstrom für Haus & E-Auto", "amount_eur": 950, "icon": "☀️"},
            {"title": "Dynamic night charging in winter" if is_en else "Dynamisches Nachtladen im Winter", "amount_eur": 280, "icon": "🚗"},
            {"title": "Battery care & grid support" if is_en else "Batterie-Schonung & Netzdienlichkeit", "amount_eur": 120, "icon": "🔋"},
        ]
        action_links.insert(0, {
            "title": "Open Energy Control (HEMS)" if is_en else "Energiesteuerung (HEMS) öffnen",
            "subtitle": "Set priorities between car, battery & home" if is_en else "Prioritäten zwischen Auto, Speicher & Haus festlegen",
            "path": "/app/control",
            "icon": "🎛️",
            "color": "indigo",
        })

    # 4. ARCHETYP E.1: BASIS-PROSUMER (PV + SPEICHER)
    elif solar_type == "pv" and has_battery and not has_ev and not has_heatpump:
        profile_code = "E.1"
        profile_name = (
            "PV System with Home Battery (Basic Prosumer)"
            if is_en
            else "PV-Anlage mit Heimspeicher (Basis-Prosumer)"
        )
        profile_subtitle = (
            "High self-sufficiency (70–80%) & grid-friendly winter charging"
            if is_en
            else "Hohe Autarkie (70–80%) & netzdienliche Winterladung"
        )
        recommended_tariff = "dynamic" if is_dynamic_tariff else "static"
        tariff_verdict_title = (
            "Dynamic tariff (winter arbitrage) or fixed price"
            if is_en
            else "Dynamischer Tarif (Winter-Arbitrage) oder Festpreis"
        )
        tariff_verdict_reason = (
            "From March to October your solar covers 80% of demand. In winter you can "
            "recharge the battery at night during spot price lows (winter arbitrage)."
            if is_en
            else "Von März bis Oktober deckt deine PV 80% des Bedarfs. Im Winter kannst du "
            "deinen Speicher nachts günstig aus dem Netz beladen (Winter-Arbitrage)."
        )
        shiftable_kwh_year = 2000
        base_savings_eur = 950
        savings_breakdown = [
            {"title": "PV self-consumption & night-time battery use" if is_en else "PV-Eigenverbrauch & Nacht-Batteriebetrieb", "amount_eur": 820, "icon": "☀️"},
            {"title": "Winter grid recharge during spot price dips" if is_en else "Winter-Netzladung bei günstigen Börsenpreisen", "amount_eur": 130, "icon": "🔋"},
        ]
        action_links.insert(0, {
            "title": "Monitor Storage & Inverter" if is_en else "Speicher & Wechselrichter monitoren",
            "subtitle": "Activate battery arbitrage & SoC forecast" if is_en else "Batterie-Arbitrage & SoC-Prognose aktivieren",
            "path": "/app/producers",
            "icon": "🔋",
            "color": "emerald",
        })

    # 5. ARCHETYP D.2: WÄRMEPUMPE + PV (OHNE SPEICHER)
    elif (solar_type in ["pv", "bkw"]) and has_heatpump and not has_battery and not has_ev:
        profile_code = "D.2"
        profile_name = "Heat Pump + PV System" if is_en else "Wärmepumpe + PV-Anlage"
        profile_subtitle = (
            "Thermal storage in screed & domestic hot water"
            if is_en
            else "Thermische Speicherung im Estrich & Warmwasser"
        )
        recommended_tariff = "dynamic"
        tariff_verdict_title = (
            "Dynamic tariff with § 14a EnWG discount"
            if is_en
            else "Dynamischer Tarif mit § 14a EnWG Rabatt"
        )
        tariff_verdict_reason = (
            "Optimal combination: Store solar power during the day as heat in the floor, "
            "and utilize dynamic night prices plus § 14a grid fee discounts in winter."
            if is_en
            else "Perfekte Kombination: PV-Strom tagsüber als Wärme im Estrich speichern, "
            "im Winter dynamische Nachtpreise und § 14a Netzentgelt-Rabatt nutzen."
        )
        shiftable_kwh_year = 4200
        base_savings_eur = 780
        savings_breakdown = [
            {"title": "PV thermal boost for water & floor heating" if is_en else "PV-Solarüberhöhung Warmwasser & Estrich", "amount_eur": 420, "icon": "☀️"},
            {"title": "§ 14a EnWG flat-rate grid fee discount" if is_en else "§ 14a EnWG Netzentgelt-Pauschale", "amount_eur": 160, "icon": "🛡️"},
            {"title": "Dynamic winter heating" if is_en else "Dynamisches Winter-Heizen", "amount_eur": 200, "icon": "♨️"},
        ]
        action_links.insert(0, {
            "title": "Heating Load Management" if is_en else "Heizungs-Lastmanagement",
            "subtitle": "Optimize heat pump & floor heating" if is_en else "Wärmepumpe & Fußbodenheizung optimieren",
            "path": "/app/heating",
            "icon": "♨️",
            "color": "rose",
        })

    # 6. ARCHETYP D.1: WÄRMEPUMPE OHNE GROSSE PV
    elif has_heatpump and not has_ev and not has_battery:
        profile_code = "D.1"
        profile_name = "Heat Pump without large Solar" if is_en else "Wärmepumpe ohne große PV"
        profile_subtitle = (
            "§ 14a EnWG grid fee discount & heating shift"
            if is_en
            else "§ 14a EnWG Netzentgelt-Rabatt & Heizzeit-Verschiebung"
        )
        recommended_tariff = "dynamic"
        tariff_verdict_title = (
            "Dynamic tariff with § 14a EnWG Module 1"
            if is_en
            else "Dynamischer Tarif mit § 14a EnWG Modul 1"
        )
        tariff_verdict_reason = (
            "A heat pump qualifies for ~160 €/y grid fee discount (§ 14a Module 1). "
            "In addition, shifting heating to cheap spot market hours yields high savings."
            if is_en
            else "Mit einer Wärmepumpe hast du Anspruch auf ca. 160 € jährlichen Netzentgelt-Rabatt (§ 14a Modul 1). "
            "Zusätzlich sparst du durch Heizen in günstigen Börsenstunden."
        )
        shiftable_kwh_year = 3500
        base_savings_eur = 520
        savings_breakdown = [
            {"title": "§ 14a EnWG Module 1 grid fee discount" if is_en else "§ 14a EnWG Modul 1 Netzentgelt-Rabatt", "amount_eur": 160, "icon": "🛡️"},
            {"title": "Dynamic heating hours & spot price lows" if is_en else "Dynamische Heizzeiten & Preistiefs", "amount_eur": 310, "icon": "♨️"},
            {"title": "Transparency & efficiency" if is_en else "Transparenz & Effizienz", "amount_eur": 50, "icon": "🌡️"},
        ]
        action_links.insert(0, {
            "title": "Heat Pump Control (SG-Ready)" if is_en else "Wärmepumpen-Steuerung (SG-Ready)",
            "subtitle": "Align heating intervals with price signals" if is_en else "Heizzeiten an Preissignale anpassen",
            "path": "/app/heating",
            "icon": "♨️",
            "color": "rose",
        })

    # 7. ARCHETYP C.3: E-AUTO + PV (OHNE SPEICHER)
    elif solar_type == "pv" and has_ev and not has_battery and not has_heatpump:
        profile_code = "C.3"
        profile_name = "EV + PV System (without Home Battery)" if is_en else "E-Auto + PV-Anlage (ohne Heimspeicher)"
        profile_subtitle = (
            "Pure PV surplus charging & dynamic grid supplementation"
            if is_en
            else "Reines PV-Überschussladen & dynamische Ergänzung"
        )
        recommended_tariff = "dynamic"
        tariff_verdict_title = (
            "Dynamic spot tariff recommended"
            if is_en
            else "Dynamischer Börsenstromtarif empfohlen"
        )
        tariff_verdict_reason = (
            "In summer you charge for free with solar surplus; in winter you recharge inexpensively at night during spot market price dips."
            if is_en
            else "Im Sommer lädst du kostenlos mit Solar-Überschuss, im Winter "
            "lädst du mit dynamischen Börsentiefs nachts günstig nach."
        )
        shiftable_kwh_year = 3200
        base_savings_eur = 650
        savings_breakdown = [
            {"title": "PV surplus charging in summer" if is_en else "PV-Überschussladen im Sommer", "amount_eur": 380, "icon": "☀️"},
            {"title": "Cost-effective night charging in winter" if is_en else "Günstiges Nachtladen im Winter", "amount_eur": 180, "icon": "🚗"},
            {"title": "Feed-in tariff revenues" if is_en else "EEG-Einspeiseerlöse", "amount_eur": 90, "icon": "💶"},
        ]
        action_links.insert(0, {
            "title": "Set up PV Surplus Charging" if is_en else "PV-Überschuss-Laden einrichten",
            "subtitle": "Link wallbox with solar generation" if is_en else "Wallbox mit Solarerzeugung koppeln",
            "path": "/app/mobility",
            "icon": "🚗",
            "color": "emerald",
        })

    # 8. ARCHETYP C.2: E-AUTO + BKW
    elif solar_type == "bkw" and has_ev and not has_heatpump:
        profile_code = "C.2"
        profile_name = "EV + Balcony Solar" if is_en else "E-Auto + Balkonkraftwerk"
        profile_subtitle = (
            "Base load offset & dynamic charging"
            if is_en
            else "Grundlastkompensation & dynamisches Laden"
        )
        recommended_tariff = "dynamic"
        tariff_verdict_title = (
            "Dynamic spot tariff recommended"
            if is_en
            else "Dynamischer Börsenstromtarif empfohlen"
        )
        tariff_verdict_reason = (
            "The balcony solar offsets base load during the day, while the EV benefits from low spot prices at night."
            if is_en
            else "Das BKW entlastet das Haus am Tag, während das E-Auto nachts "
            "von extrem günstigen Börsenpreisen profitiert."
        )
        shiftable_kwh_year = 2700
        base_savings_eur = 480
        savings_breakdown = [
            {"title": "Dynamic night charging for EV" if is_en else "Dynamisches Nachtladen E-Auto", "amount_eur": 300, "icon": "🚗"},
            {"title": "Balcony solar yield" if is_en else "BKW-Solarstrom-Ertrag", "amount_eur": 140, "icon": "☀️"},
            {"title": "Standby reduction" if is_en else "Standby-Reduktion", "amount_eur": 40, "icon": "🔌"},
        ]
        action_links.insert(0, {
            "title": "Wallbox Smart-Charging",
            "subtitle": "Configure price signals & charging windows" if is_en else "Preissignale & Ladefenster konfigurieren",
            "path": "/app/mobility",
            "icon": "🚗",
            "color": "emerald",
        })

    # 9. ARCHETYP C.1: E-AUTO OHNE PV
    elif solar_type == "none" and has_ev and not has_heatpump:
        profile_code = "C.1"
        profile_name = "EV / Wallbox without Solar" if is_en else "E-Auto / Wallbox ohne PV"
        profile_subtitle = (
            "Dynamic charging & flexible load shifting"
            if is_en
            else "Dynamisches Laden & netzdienliche Lastverschiebung"
        )
        recommended_tariff = "dynamic"
        tariff_verdict_title = (
            "Dynamic spot tariff strongly recommended!"
            if is_en
            else "Dynamischer Börsenstromtarif dringend empfohlen!"
        )
        tariff_verdict_reason = (
            "With approx. 2,500 kWh EV driving electricity per year, your savings potential is high. "
            "Smart charging during low-price night hours saves significant money."
            if is_en
            else "Mit ca. 2.500 kWh Fahrstrom pro Jahr hast du ein riesiges Einsparpotenzial. "
            "Durch intelligentes Laden in günstigen Nachtstunden sparst du bares Geld."
        )
        shiftable_kwh_year = 2500
        base_savings_eur = 340
        savings_breakdown = [
            {"title": "Dynamic night charging (spot price lows)" if is_en else "Dynamisches Nachtladen (Börsenpreis-Tiefs)", "amount_eur": 300, "icon": "🚗"},
            {"title": "Household appliance optimization" if is_en else "Optimierung Haushaltsgeräte", "amount_eur": 40, "icon": "⚡"},
        ]
        action_links.insert(0, {
            "title": "Connect OCPP Wallbox" if is_en else "OCPP Wallbox verbinden",
            "subtitle": "Enable automated smart charging" if is_en else "Automatisches Smart-Charging aktivieren",
            "path": "/app/mobility",
            "icon": "🚗",
            "color": "emerald",
        })

    # 10. ARCHETYP B.2: BKW MIT SPEICHER
    elif solar_type == "bkw" and has_battery and not has_ev and not has_heatpump:
        profile_code = "B.2"
        profile_name = "Balcony Solar with Storage" if is_en else "Balkonkraftwerk mit Speicher"
        profile_subtitle = (
            "Night-time coverage with 1–2 kWh battery storage"
            if is_en
            else "Nachtabdeckung durch 1–2 kWh BKW-Akkuspeicher"
        )
        recommended_tariff = "dynamic" if is_dynamic_tariff else "static"
        tariff_verdict_title = (
            "Fixed tariff or entry-level dynamic"
            if is_en
            else "Fester Tarif oder Einstieg in Dynamisch"
        )
        tariff_verdict_reason = (
            "A balcony battery increases self-consumption up to 85%. "
            "Dynamic tariffs become beneficial especially when grid-recharging in winter."
            if is_en
            else "Mit BKW-Akku steigerst du deinen Eigenverbrauch auf bis zu 85%. "
            "Ein dynamischer Tarif lohnt sich vor allem bei winterlicher Netznachladung."
        )
        shiftable_kwh_year = 700
        base_savings_eur = 270
        savings_breakdown = [
            {"title": "Balcony solar yield & night discharge" if is_en else "BKW-Erzeugung & Nacht-Ausspeisung", "amount_eur": 230, "icon": "🔋"},
            {"title": "Standby killer" if is_en else "Standby-Killer", "amount_eur": 40, "icon": "🔌"},
        ]
        action_links.insert(0, {
            "title": "Integrate Balcony Storage" if is_en else "BKW-Speicher einbinden",
            "subtitle": "Control state of charge (SoC) & discharge" if is_en else "Speicherstand (SoC) & Entladung steuern",
            "path": "/app/producers",
            "icon": "🔋",
            "color": "emerald",
        })

    # 11. ARCHETYP B.1: BKW OHNE SPEICHER
    elif solar_type == "bkw" and not has_battery and not has_ev and not has_heatpump:
        profile_code = "B.1"
        profile_name = "Balcony Solar without Storage" if is_en else "Balkonkraftwerk ohne Speicher"
        profile_subtitle = (
            "Base load coverage with 800W plug-in solar"
            if is_en
            else "Grundlastdeckung durch 800W Stecker-Solar"
        )
        recommended_tariff = "static"
        tariff_verdict_title = (
            "Fixed electricity tariff optimal"
            if is_en
            else "Fester Stromtarif optimal"
        )
        tariff_verdict_reason = (
            "Your balcony solar covers daytime base load. Since flexible loads are small (< 300 kWh/y), "
            "a solid fixed-rate contract is more cost-effective than dynamic spot prices."
            if is_en
            else "Dein BKW deckt tagsüber deine Grundlast ab. Da die verschiebbare Last gering ist (< 300 kWh/a), "
            "ist ein solider Festpreis-Tarif wirtschaftlicher als ein dynamischer Börsentarif."
        )
        shiftable_kwh_year = 350
        base_savings_eur = 180
        savings_breakdown = [
            {"title": "Balcony solar yield (~450 kWh self-consumption)" if is_en else "BKW-Solarertrag (ca. 450 kWh Direktverbrauch)", "amount_eur": 150, "icon": "☀️"},
            {"title": "Standby optimization" if is_en else "Standby-Optimierung", "amount_eur": 30, "icon": "🔌"},
        ]
        action_links.insert(0, {
            "title": "Monitor Balcony Solar" if is_en else "BKW-Erzeugung monitoren",
            "subtitle": "Connect inverter or smart plug" if is_en else "Wechselrichter oder Steckdose verknüpfen",
            "path": "/app/devices",
            "icon": "☀️",
            "color": "amber",
        })

    # 12. SONSTIGE KOMBINATIONEN
    elif has_ev and has_heatpump:
        profile_code = "D.1"
        profile_name = "EV & Heat Pump (without Solar)" if is_en else "E-Auto & Wärmepumpe (ohne PV)"
        profile_subtitle = (
            "High flexible loads: Night charging & § 14a EnWG"
            if is_en
            else "Hohe flexible Lasten: Nachtladen & § 14a EnWG"
        )
        recommended_tariff = "dynamic"
        tariff_verdict_title = (
            "Dynamic spot tariff strongly recommended!"
            if is_en
            else "Dynamischer Börsenstromtarif dringend empfohlen!"
        )
        tariff_verdict_reason = (
            "Large flexible loads (> 5,500 kWh/y). Benefit substantially from dynamic charging and § 14a grid fee discounts."
            if is_en
            else "Große verschiebbare Lasten (> 5.500 kWh/a). Durch dynamisches Laden und "
            "§ 14a Netzentgelt-Rabatte sparst du erheblich."
        )
        shiftable_kwh_year = 5500
        base_savings_eur = 750
        savings_breakdown = [
            {"title": "Dynamic night charging for EV" if is_en else "Dynamisches Nachtladen E-Auto", "amount_eur": 300, "icon": "🚗"},
            {"title": "Dynamic heat pump heating" if is_en else "Dynamisches Heizen Wärmepumpe", "amount_eur": 290, "icon": "♨️"},
            {"title": "§ 14a EnWG flat-rate discount" if is_en else "§ 14a EnWG Netzentgelt-Pauschale", "amount_eur": 160, "icon": "🛡️"},
        ]

    elif solar_type == "pv":
        profile_code = "E.1"
        profile_name = "PV System" if is_en else "PV-Anlage"
        profile_subtitle = (
            "Solar generation & self-consumption optimization"
            if is_en
            else "Solarerzeugung & Eigenverbrauchsoptimierung"
        )
        recommended_tariff = "dynamic" if is_dynamic_tariff else "static"
        shiftable_kwh_year = 2000
        base_savings_eur = 650

    alternative_tariff_hint = (
        "Alternative with separate meter: A fixed household tariff combined with a discounted "
        "heating or EV charging tariff is possible, but requires a 2nd meter (cascade metering). "
        "This incurs additional fixed costs of approx. 80–120 €/year for metering and base fees. "
        "With a dynamic spot tariff, 1 smart meter is sufficient while maintaining full § 14a grid fee discounts (~160 €/year)."
        if is_en
        else "Alternative mit separatem Zähler: Ein fester Tarif kombiniert mit einem vergünstigten "
        "Wärmestrom- oder Autostromtarif ist möglich, erfordert jedoch einen 2. Zähler (Kaskadenschaltung). "
        "Dadurch entstehen Zusatzkosten von ca. 80–120 €/Jahr für Messstellenbetrieb und Grundgebühr. "
        "Bei einem dynamischen Börsenstromtarif genügt 1 Zähler bei vollem § 14a Rabatt (ca. 160 €/Jahr)."
    )

    return {
        "profile_code": profile_code,
        "profile_name": profile_name,
        "profile_subtitle": profile_subtitle,
        "solar_type": solar_type,
        "has_battery": has_battery,
        "has_ev": has_ev,
        "has_heatpump": has_heatpump,
        "tariff_type": tariff_type,
        "is_dynamic_tariff": is_dynamic_tariff,
        "recommended_tariff": recommended_tariff,
        "tariff_verdict_title": tariff_verdict_title,
        "tariff_verdict_reason": tariff_verdict_reason,
        "alternative_tariff_hint": alternative_tariff_hint,
        "shiftable_kwh_year": shiftable_kwh_year,
        "estimated_savings_eur_year": base_savings_eur,
        "savings_breakdown": savings_breakdown,
        "action_links": action_links,
        "help_article_slug": "tarif-und-ersparnis-kompass-matrix",
    }


def get_user_energy_profile(user, lang: str = "de") -> Dict[str, Any]:
    """
    Ermittelt das Energie-Profil des Nutzers aus Cache / Settings / angebundenen Geräten.
    """
    cache_key = f"{CACHE_KEY_PREFIX}{getattr(user, 'id', 'anonymous')}"
    cached_data = cache.get(cache_key)

    if cached_data and isinstance(cached_data, dict):
        return calculate_energy_profile_data(
            solar_type=cached_data.get("solar_type", "none"),
            has_battery=cached_data.get("has_battery", False),
            has_ev=cached_data.get("has_ev", False),
            has_heatpump=cached_data.get("has_heatpump", False),
            tariff_type=cached_data.get("tariff_type", "static"),
            lang=lang,
        )

    # Automatische Erkennung anhand existierender Hardware im Haushalt
    home = None
    if user and hasattr(user, "homes"):
        home = user.homes.first()
    if not home and user:
        home = Home.objects.filter(user=user).first()

    solar_type = "none"
    has_battery = False
    has_ev = False
    has_heatpump = False
    tariff_type = "static"

    if home:
        # 1. Solar prüfen
        generators = list(GeneratorSystem.objects.filter(home=home))
        if generators:
            max_kw = max([float(getattr(g, "peak_power_kw", 0) or 0) for g in generators] or [0])
            solar_type = "bkw" if 0 < max_kw <= 1.0 else ("pv" if max_kw > 1.0 else "pv")
        else:
            pv_devices = Device.objects.filter(
                home=home,
                active=True,
                config__role__key__in=["producer", "pv", "inverter", "hybrid"]
            )
            if pv_devices.exists():
                solar_type = "pv"

        # 2. Speicher prüfen
        has_battery = StorageSystem.objects.filter(home=home).exists() or Device.objects.filter(
            home=home, active=True, config__role__key__in=["battery", "storage"]
        ).exists()

        # 3. E-Auto / Wallbox prüfen
        try:
            from devices.models_ocpp import ChargingStation
            has_ev = ChargingStation.objects.filter(home=home, is_active=True).exists()
        except Exception:
            has_ev = False

        if not has_ev:
            from django.db.models import Q
            has_ev = Device.objects.filter(
                home=home, active=True
            ).filter(
                Q(identifier__icontains="wallbox") | Q(config__name__icontains="wallbox")
            ).exists()

        # 4. Wärmepumpe prüfen
        try:
            from energy.models import FloorHeatingConfig, BWWPConfig
            from django.db.models import Q
            has_heatpump = (
                FloorHeatingConfig.objects.filter(home=home, is_enabled=True).exists()
                or BWWPConfig.objects.filter(home=home, is_enabled=True).exists()
                or Device.objects.filter(home=home, active=True).filter(
                    Q(identifier__icontains="wärmepumpe") | Q(config__name__icontains="wärmepumpe") |
                    Q(identifier__icontains="heatpump") | Q(config__name__icontains="heatpump")
                ).exists()
            )
        except Exception:
            has_heatpump = False

        # 5. Tarif prüfen
        try:
            from market.models_tariff import HomeTariff
            home_tariff = HomeTariff.objects.filter(home=home).order_by("-valid_from").first()
            if home_tariff:
                tariff_type = home_tariff.tariff_type
        except Exception:
            tariff_type = "static"

    calculated = calculate_energy_profile_data(
        solar_type=solar_type,
        has_battery=has_battery,
        has_ev=has_ev,
        has_heatpump=has_heatpump,
        tariff_type=tariff_type,
        lang=lang,
    )

    # In Cache sichern
    cache.set(cache_key, {
        "solar_type": solar_type,
        "has_battery": has_battery,
        "has_ev": has_ev,
        "has_heatpump": has_heatpump,
        "tariff_type": tariff_type,
    }, timeout=86400)

    return calculated


def save_user_energy_profile(user, data: Dict[str, Any], lang: str = "de") -> Dict[str, Any]:
    """
    Speichert das vom Nutzer manuell gesetzte Hardware- & Tarifprofil ab.
    """
    cache_key = f"{CACHE_KEY_PREFIX}{getattr(user, 'id', 'anonymous')}"

    solar_type = data.get("solar_type", "none")
    has_battery = bool(data.get("has_battery", False))
    has_ev = bool(data.get("has_ev", False))
    has_heatpump = bool(data.get("has_heatpump", False))
    tariff_type = data.get("tariff_type", "static")

    stored = {
        "solar_type": solar_type,
        "has_battery": has_battery,
        "has_ev": has_ev,
        "has_heatpump": has_heatpump,
        "tariff_type": tariff_type,
    }
    cache.set(cache_key, stored, timeout=86400 * 30)

    home = None
    if user and hasattr(user, "homes"):
        home = user.homes.first()
    if not home and user:
        home = Home.objects.filter(user=user).first()

    if home and "tariff_type" in data:
        try:
            from decimal import Decimal
            from market.models_tariff import HomeTariff
            from django.utils import timezone
            defaults = {
                "tariff_type": tariff_type,
                "static_price_eur_per_kwh": Decimal("0.3200") if tariff_type == "static" else None,
                "feed_in_tariff_eur_per_kwh": Decimal("0.0820"),
            }
            HomeTariff.objects.update_or_create(
                home=home,
                valid_from=timezone.now().date(),
                defaults=defaults,
            )
        except Exception as e:
            logger.warning("[EnergyProfile] Konnte HomeTariff nicht aktualisieren: %s", e)

    return calculate_energy_profile_data(
        solar_type=solar_type,
        has_battery=has_battery,
        has_ev=has_ev,
        has_heatpump=has_heatpump,
        tariff_type=tariff_type,
        lang=lang,
    )
