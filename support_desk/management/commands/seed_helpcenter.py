################################################
# helpcenter/management/commands/seed_helpcenter.py
################################################

from django.core.management.base import BaseCommand
from support_desk.models import HelpCategory, HelpArticle


class Command(BaseCommand):
    help = "Befüllt das Hilfesystem und Wissensportal mit allen Kategorien und Handbuch-Artikeln auf Deutsch & Englisch."

    def handle(self, *args, **options):
        self.stdout.write("Befülle Hilfesystem & Wissensportal (DE & EN)...")

        # =========================================================================
        # 1. KATEGORIEN ANLEGEN / AKTUALISIEREN
        # =========================================================================
        categories_data = [
            {
                "key": "getting-started",
                "icon": "🚀",
                "title_de": "Erste Schritte & Grundlagen",
                "title_en": "Getting Started & Basics",
                "description_de": "Schnelleinstieg, Onboarding, Dashboard-Navigation und Kennzahlen im Überblick.",
                "description_en": "Quickstart guides, onboarding, dashboard navigation, and core energy KPIs.",
                "sort_order": 1,
            },
            {
                "key": "inverters-meters",
                "icon": "☀️",
                "title_de": "Erzeuger, Speicher & Wechselrichter",
                "title_en": "Inverters, Storage & PV",
                "description_de": "Anbindung von SMA, Sungrow, Fronius, Deye, Huawei, Batteriespeichern und Zählern.",
                "description_en": "Setup guides for SMA, Sungrow, Fronius, Deye, Huawei, home batteries, and meters.",
                "sort_order": 2,
            },
            {
                "key": "forecast",
                "icon": "📈",
                "title_de": "Solar- & Lastprognose",
                "title_en": "Solar & Load Forecast",
                "description_de": "Hybrid-Prognosen, Wettermodelle, Güte-Score (%-Genauigkeit) und Ist-vs-Soll-Vergleich.",
                "description_en": "Hybrid forecasting, weather models, accuracy score (%), and actual vs. forecast tracking.",
                "sort_order": 3,
            },
            {
                "key": "optimizer",
                "icon": "🤖",
                "title_de": "Smart Energy Optimizer & EMS",
                "title_en": "Smart Energy Optimizer & EMS",
                "description_de": "Automatisierte Fahrpläne für E-Auto (Wallbox), Hausspeicher, Wärmepumpen & Haushaltsgeräte.",
                "description_en": "Automated schedules for EV wallboxes, home batteries, heat pumps, and appliances.",
                "sort_order": 4,
            },
            {
                "key": "tariffs",
                "icon": "⚡",
                "title_de": "Strompreise & Börsenstrom",
                "title_en": "Electricity Tariffs & Dynamic Pricing",
                "description_de": "Dynamische Tarife, Tibber API, Day-Ahead-Preise, Formeln und stichtagsgenaue Tarifhistorie.",
                "description_en": "Dynamic tariffs, Tibber API, spot market prices, pricing formulas, and historical rates.",
                "sort_order": 5,
            },
            {
                "key": "alerts",
                "icon": "🚨",
                "title_de": "Alarm- & Notifikationszentrale",
                "title_en": "Alert & Notification Center",
                "description_de": "Echtzeit-Regeln für Ertragsausfälle, Tiefentladeschutz, Dauerlasten und Spar-Chancen.",
                "description_en": "Real-time health rules for yield losses, battery protection, baseload alerts, and savings tips.",
                "sort_order": 6,
            },
            {
                "key": "billing",
                "icon": "🧾",
                "title_de": "Abrechnung & Mieterstrom",
                "title_en": "Billing & Sub-Metering",
                "description_de": "Virtuelle Zähler, Sub-Metering, Kostenallokation für WEGs und monatliche PDF-Reports.",
                "description_en": "Virtual meters, sub-metering, multi-tenant cost allocation, and monthly PDF exports.",
                "sort_order": 7,
            },
            {
                "key": "devices-protocols",
                "icon": "🔌",
                "title_de": "Geräte, MQTT & Protokolle",
                "title_en": "Devices, MQTT & Protocols",
                "description_de": "Integration von Home Assistant, ioBroker, Shelly, Tasmota, Modbus RTU/TCP und REST APIs.",
                "description_en": "Integration with Home Assistant, ioBroker, Shelly, Tasmota, Modbus, and REST APIs.",
                "sort_order": 8,
            },
        ]

        cats = {}
        for cdata in categories_data:
            cat, _ = HelpCategory.objects.update_or_create(
                key=cdata["key"],
                defaults=cdata,
            )
            cats[cat.key] = cat

        # =========================================================================
        # 2. ARTIKEL ANLEGEN / AKTUALISIEREN (VOLLSTÄNDIG DE & EN)
        # =========================================================================
        articles_data = [
            # ---------------------------------------------------------------------
            # 1. GETTING STARTED: ENERGIEBILANZ & AUTARKIE
            # ---------------------------------------------------------------------
            {
                "category": cats["getting-started"],
                "slug": "energiebilanz-und-autarkiegrad",
                "context_key": "energy_dashboard",
                "title_de": "Energiebilanz, Autarkiegrad & Eigenverbrauchsquote",
                "title_en": "Energy Balance, Autarky Rate & Self-Consumption",
                "summary_de": "Erklärung aller zentralen Kennzahlen im Energie-Dashboard (Autarkie, Eigenverbrauch, Solardeckung).",
                "summary_en": "Explanation of core metrics on the Energy Dashboard (autarky rate, self-consumption ratio, solar share).",
                "content_de": """# Energiebilanz & Kennzahlen verstehen

Das **Energie-Dashboard** bietet einen ganzheitlichen Überblick über deine Erzeugung, Batteriespeicher, Verbräuche und Netzflüsse.

## Die wichtigsten Kennzahlen

### 1. Autarkiegrad (%)
Gibt an, zu welchem prozentualen Anteil der gesamte Haushaltsstrombedarf durch deine eigene Solaranlage und den Batteriespeicher gedeckt werden konnte:

> 📐 **Formel:**  
> **Autarkiegrad (%)** = `(1 - Netzbezug / Gesamtverbrauch) × 100`  
> *(Vereinfacht: Anteil des Eigenstroms am gesamten Hausverbrauch)*

* 🟢 **≥ 75 %**: Sehr hohe Unabhängigkeit vom öffentlichen Stromnetz.
* 🟡 **40 bis 74 %**: Solide Grunddeckung, typisch für Übergangsmonate (Frühjahr/Herbst).
* 🔵 **Unter 40 %**: Typischer Winterwert oder Ausbaupotenzial bei Speicher/PV.

---

### 2. Eigenverbrauchsquote (%)
Zeigt, wie viel Prozent des von deiner Photovoltaikanlage erzeugten Stroms direkt im Haus verbraucht oder in den Akku geladen wurde (statt ins Netz eingespeist zu werden):

> 📐 **Formel:**  
> **Eigenverbrauchsquote (%)** = `(Direktverbrauch + Batterieladung) / Gesamte PV-Erzeugung × 100`

> [!TIP]
> Um die Eigenverbrauchsquote zu maximieren, nutze den **Smart Energy Optimizer**, um Großverbraucher (z. B. Wallbox, Wärmepumpe, Spülmaschine) automatisch in Phasen mit hohem Solarüberschuss zu starten.
""",
                "content_en": """# Energy Balance & Key Performance Indicators

The **Energy Dashboard** provides a unified view of your solar generation, battery storage, household load, and grid interactions.

## Core Metrics Overview

### 1. Autarky / Self-Sufficiency Rate (%)
Represents the percentage of your total energy consumption covered directly by solar generation and your home battery:

> 📐 **Formula:**  
> **Autarky Rate (%)** = `(1 - Grid Import / Total Load) × 100`  
> *(Simplified: Share of self-generated clean power over total consumption)*

* 🟢 **≥ 75 %**: High grid independence.
* 🟡 **40 to 74 %**: Solid baseline coverage typical for spring and autumn.
* 🔵 **Under 40 %**: Typical winter performance or room for battery/solar expansion.

---

### 2. Self-Consumption Ratio (%)
Shows the percentage of generated solar energy consumed directly or stored in your home battery rather than being fed into the grid:

> 📐 **Formula:**  
> **Self-Consumption (%)** = `(Direct Consumption + Battery Charging) / Total PV Generation × 100`

> [!TIP]
> Use the **Smart Energy Optimizer** to align heavy loads (EV charging, heat pump heating cycles) with peak solar production hours.
""",
                "tags": ["energy", "autarkie", "eigenverbrauch", "bilanz", "kpis", "dashboard"],
                "is_featured": True,
                "sort_order": 1,
            },

            # ---------------------------------------------------------------------
            # 2. INVERTERS & STORAGE: ERZEUGER & SPEICHERANLAGEN
            # ---------------------------------------------------------------------
            {
                "category": cats["inverters-meters"],
                "slug": "erzeuger-und-batteriespeicher-konfiguration",
                "context_key": "producers",
                "title_de": "Erzeuger- & Speicheranlagen: Konfiguration & Messstellen-Zusammenführung",
                "title_en": "Producers & Storage: Setup & Metric Mapping",
                "summary_de": "So führst du PV-Strings, Hybrid-Wechselrichter und Batteriespeicher mit ihren Live-Messpunkten zusammen.",
                "summary_en": "How to configure PV strings, hybrid inverters, and battery systems with their live telemetry metrics.",
                "content_de": """# Erzeuger- & Speicheranlagen verwalten

Unter **Erzeuger- & Speicheranlagen** konfigurierst du deine PV-Module, Generator-Strings und Batteriesysteme, damit Sharegy Erträge und Speicherzustände exakt abbilden kann.

## 1. Photovoltaik-Erzeugungsanlagen & Strings
* **Leistung (kWp)**: Installierte Nennleistung deiner PV-Module (z. B. `10.5 kWp`).
* **Ausrichtung (Azimut)**: `0°` = Süden, `-90°` = Osten, `+90°` = Westen.
* **Neigungswinkel**: z. B. `35°` für klassische Schrägdächer oder `10°` für Flachdach-Ost-West-Systeme.
* **Messstellen-Zuweisung**: Wähle das Gerät (z. B. Wechselrichter) und den passenden Datenpunkt (z. B. `pv_power` oder `power`).

## 2. Batteriespeicher anlegen
Wenn ein Gerät die Rolle *Batteriespeicher* erhält, wird automatisch ein Eintrag angelegt. Hier kannst du einstellen:
* **Nennkapazität (kWh)**: z. B. `10.0 kWh` oder `20.0 kWh`.
* **Max. Lade-/Entladeleistung (kW)**: z. B. `5.0 kW`.
* **Notstromreserve / Mindest-SoC (%)**: z. B. `10 %` zur Schonung der Batteriezellen und für Netzausfälle.
* **Messpunkte**: Verknüpfe den Datenpunkt für den Ladestand (`soc` in %) sowie die Lade-/Entladeleistung (`battery_power` in W).

> [!NOTE]
> Werden mehrere Batteriespeicher aktiv geschaltet, aggregiert Sharegy diese automatisch zu einer Gesamtkapazität und berechnet einen kapazitätsgewichteten Gesamt-SoC.
""",
                "content_en": """# Managing Producers & Battery Storage Systems

Under **Producers & Storage**, configure your solar panel arrays, generator strings, and battery systems.

## 1. PV Arrays & Strings Configuration
* **Peak Power (kWp)**: Total nominal PV capacity (e.g., `10.5 kWp`).
* **Azimuth Orientation**: `0°` = South, `-90°` = East, `+90°` = West.
* **Tilt Angle**: e.g., `35°` for pitched roofs or `10°` for east-west flat roofs.
* **Metric Mapping**: Select the telemetry device and metric key (e.g., `pv_power` or `power`).

## 2. Battery Storage Setup
* **Usable Capacity (kWh)**: e.g., `10.0 kWh` or `20.0 kWh`.
* **Max. Charge / Discharge Power (kW)**: e.g., `5.0 kW`.
* **Backup Reserve / Min. SoC (%)**: e.g., `10 %` for cell protection and emergency backup.
* **Metric Binding**: Map the State of Charge (`soc` in %) and active power (`battery_power` in W).
""",
                "tags": ["producers", "storage", "batterie", "wechselrichter", "strings", "azimut"],
                "is_featured": True,
                "sort_order": 2,
            },

            # ---------------------------------------------------------------------
            # 3. INVERTERS & MODBUS TCP
            # ---------------------------------------------------------------------
            {
                "category": cats["inverters-meters"],
                "slug": "sma-sungrow-modbus-tcp-einrichten",
                "context_key": "devices",
                "title_de": "Modbus TCP für SMA, Sungrow, Fronius & Deye freischalten",
                "title_en": "Enabling Modbus TCP for SMA, Sungrow, Fronius & Deye",
                "summary_de": "Schritt-für-Schritt-Anleitung zur Aktivierung der lokalen Modbus-TCP-Schnittstelle im Wechselrichter-Webinterface.",
                "summary_en": "Step-by-step instructions to enable local Modbus TCP in your inverter's web portal.",
                "content_de": """# Modbus TCP für Wechselrichter aktivieren

Modbus TCP ermöglicht die verzögerungsfreie Direktabfrage aller Leistungswerte im lokalen Netzwerk ohne Umweg über Hersteller-Clouds.

## 1. SMA Sunny Tripower / Hybrid
1. Im Browser die IP-Adresse des SMA-Wechselrichters aufrufen.
2. Als **Installateur** einloggen.
3. Zu **Gerätekonfiguration → Externe Kommunikation → Modbus** navigieren.
4. **TCP-Server aktivieren** (Port: `502`, Unit-ID: `126` oder `3`).
5. Speichern.

## 2. Sungrow SH5.0 / SH10RT
1. In der **iSolarCloud**-App oder im lokalen Webportal einloggen.
2. In den **Erweiterten Einstellungen → Modbus TCP** auf **Aktiviert** setzen.
3. Standard-Port: `502`.

## 3. Fronius Symo / Primo GEN24
1. Webinterface des Fronius Datamanager aufrufen.
2. Unter **Einstellungen → Modbus** das Protokoll **Modbus TCP** auswählen.
3. Datenausgabeformat auf **Float** einstellen.

> [!TIP]
> Reserviere im WLAN-Router (z. B. FRITZ!Box) eine feste IP-Adresse für den Wechselrichter (*„Diesem Netzwerkgerät immer die gleiche IPv4-Adresse zuweisen“*).
""",
                "content_en": """# Enabling Modbus TCP on Inverters

Modbus TCP provides low-latency local telemetry without reliance on external cloud APIs.

## 1. SMA Sunny Tripower
1. Open the inverter's IP address in your browser and sign in as **Installer**.
2. Navigate to **Device Configuration → External Communication → Modbus**.
3. Enable the **TCP Server** (Port: `502`, Unit ID: `126` or `3`).

## 2. Sungrow SH Series
1. Sign in to the local web interface or iSolarCloud.
2. In **Advanced Settings → Modbus TCP**, toggle to **Enabled** (Port: `502`).

## 3. Fronius GEN24 / Symo
1. Open the Fronius Datamanager interface.
2. Under **Settings → Modbus**, select **Modbus TCP** and choose **Float** as data format.
""",
                "tags": ["modbus", "inverter", "sma", "sungrow", "fronius", "deye", "tcp"],
                "is_featured": True,
                "sort_order": 3,
            },

            # ---------------------------------------------------------------------
            # 4. FORECAST: SOLAR PROGNOSE & GÜTEABGLEICH
            # ---------------------------------------------------------------------
            {
                "category": cats["forecast"],
                "slug": "solar-prognose-und-genauigkeit",
                "context_key": "forecast",
                "title_de": "Solar-Prognose, Wettermodelle & Genauigkeitsabgleich (%-Score)",
                "title_en": "Solar Forecasting, Weather Models & Accuracy Score",
                "summary_de": "Wie die Hybrid-Prognose aus Wetterdaten, Sensor.Community und ML berechnet wird und wie der Güte-Score funktioniert.",
                "summary_en": "How the hybrid solar forecast combines numerical weather predictions with local observations and ML.",
                "content_de": """# Solar-Prognose & Genauigkeitsabgleich

Die Solar-Prognose berechnet auf Basis hochauflösender Wetterdaten (Globalstrahlung in W/m², Bewölkung, Temperatur) und deiner Anlagenausrichtung die stündliche PV-Erzeugung für die nächsten 24 bis 48 Stunden.

## Wie wird der Genauigkeits-Score berechnet?

Der stündliche Abgleich vergleicht die tatsächliche Wechselrichter-Leistung mit der Modellvorhersage:

> 📐 **Formel:**  
> **Prognosegüte (%)** = `100 % - prozentuale Abweichung zwischen Ist-Ertrag und Modellvorhersage`

* 🟢 **Hervorragend (≥ 90 %)**: Optimale Übereinstimmung mit realen Messwerten.
* 🟡 **Gut (75 bis 89 %)**: Normale wetterbedingte Schwankungen (z. B. wechselnde Wolkenfelder).
* 🔵 **In Kalibrierung (unter 75 %)**: Das System lernt standortspezifische Abschattungen oder Horizontverläufe ein.

## Selbstlernende Korrekturfaktoren
Stellt das System über mehrere Tage systematische Abweichungen fest (z. B. Nachmittagsschatten durch Bäume), passt ein adaptiver Korrekturfaktor zukünftige Vorhersagen automatisch an.
""",
                "content_en": """# Solar Forecasting & Accuracy Scoring

The solar forecast combines physical irradiation models (Global Horizontal Irradiance in W/m², cloud cover, ambient temperature) with machine learning adjustments.

## Accuracy Score Calculation

> 📐 **Formula:**  
> **Accuracy Score (%)** = `100% - percentage deviation between actual yield and forecast model`

* 🟢 **Excellent (≥ 90%)**: High model fidelity and clear sky tracking.
* 🟡 **Good (75 to 89%)**: Typical cloud drift and transient weather.
* 🔵 **Calibrating (under 75%)**: Continuous horizon and local shading adaptation.
""",
                "tags": ["forecast", "solar", "prognose", "wetter", "ml", "genauigkeit"],
                "is_featured": True,
                "sort_order": 4,
            },

            # ---------------------------------------------------------------------
            # 5. FORECAST: LASTPROGNOSE
            # ---------------------------------------------------------------------
            {
                "category": cats["forecast"],
                "slug": "lastprognose-und-haushaltsverbrauch",
                "context_key": "forecast",
                "title_de": "Haushalts-Lastprognose & Wochentags-Profile",
                "title_en": "Household Load Forecasting & Weekly Profiles",
                "summary_de": "So prognostiziert Sharegy den Haushaltsverbrauch anhand historischer Wochentags- und Stundenmuster.",
                "summary_en": "How Sharegy predicts domestic consumption using historical weekday and hourly load profiles.",
                "content_de": """# Haushalts-Lastprognose & Verbrauchsmuster

Die Lastprognose ermittelt für jede Stunde der kommenden 24 bis 48 Stunden den erwarteten Strombedarf deines Haushalts.

## Berechnungsmethode
* **Wochentags-Cluster**: Das System unterscheidet automatisch zwischen Werktagen (Montag bis Freitag) und Wochenenden (Samstag/Sonntag).
* **Gleitender Durchschnitt**: Verbräuche der letzten 4 bis 8 Wochen fließen gewichtet ein, um saisonale Veränderungen (z. B. Heizperiode) abzubilden.
* **Grundlast-Erkennung**: Konstante Ruhelasten in der Nacht werden isoliert, um Peaks von Standard-Verbräuchen zu trennen.

> [!NOTE]
> Zusammen mit der Solar-Prognose bildet die Lastprognose die mathematische Grundlage für die **Batterie-SoC-Simulation** und den **Smart Energy Optimizer**.
""",
                "content_en": """# Household Load Forecasting & Daily Profiles

The load forecasting engine estimates household demand for every hour of the upcoming 24 to 48 hours.

## Methodology
* **Weekday vs. Weekend Clustering**: Differentiates working days from weekends.
* **Rolling Historical Averages**: Weighted 4- to 8-week consumption patterns adapt to seasonal shifts.
* **Baseload Isolation**: Distinguishes continuous standby loads from active peaks.
""",
                "tags": ["lastprognose", "verbrauch", "profile", "grundlast", "wochentage"],
                "is_featured": False,
                "sort_order": 5,
            },

            # ---------------------------------------------------------------------
            # 6. OPTIMIZER: SMART ENERGY OPTIMIZER & EMS
            # ---------------------------------------------------------------------
            {
                "category": cats["optimizer"],
                "slug": "smart-energy-optimizer-funktionsweise",
                "context_key": "optimizer",
                "title_de": "Smart Energy Optimizer: Zeitfenster (1h/2h/4h) & Fahrplan optimal nutzen",
                "title_en": "Smart Energy Optimizer: 1h/2h/4h Time Windows & Smart Scheduling",
                "summary_de": "So ermittelt der Optimizer die günstigsten Zeitfenster für Wallbox, Wärmepumpe und Haushaltsgeräte.",
                "summary_en": "How the optimizer identifies the best time slots for EV charging, heat pump heating, and home appliances.",
                "content_de": """# Smart Energy Optimizer & EMS

Der **Smart Energy Optimizer** verknüpft Solar-Ertragsprognose, dynamische Börsenstrompreise (Day-Ahead) und deinen Grundverbrauch zu einem optimalen Fahrplan.

## Die drei Standard-Zeitfenster

1. **1-Stunden-Fenster (1h)**:
   * Perfekt für Waschmaschine, Wäschetrockner oder Geschirrspüler.
2. **2-Stunden-Fenster (2h)**:
   * Ideal für Wärmepumpen (Warmwasserbereitung oder thermische Pufferüberhöhung).
3. **4-Stunden-Fenster (4h)**:
   * Optimiert für das Laden von Elektrofahrzeugen an der Wallbox (11 kW oder 22 kW).

## Optimierungs-Strategie
* **Priorität 1 (Solarüberschuss)**: Nutzung von 100 % kostenlosem PV-Strom vor der Einspeisung ins Netz.
* **Priorität 2 (Günstigste Börsenstunden)**: Netzbezug gezielt in Phasen mit negativen oder extrem niedrigen Strompreisen.
* **Priorität 3 (Akkuschutz)**: Vermeidung von unnötiger Batterie-Zyklisierung, wenn zeitnah Sonne ansteht.
""",
                "content_en": """# Smart Energy Optimizer & EMS

The **Smart Energy Optimizer** merges solar generation forecasts with dynamic spot market electricity prices to compute cost-minimal operating schedules.

## Optimized Time Windows
1. **1-Hour Window (1h)**: Ideal for washing machines, dryers, or dishwashers.
2. **2-Hour Window (2h)**: Optimal for heat pump domestic hot water cycles.
3. **4-Hour Window (4h)**: Designed for Electric Vehicle (EV) charging via 11 kW / 22 kW wallboxes.

## Dispatch Strategy
* **Priority 1**: 100% free solar surplus utilization before grid export.
* **Priority 2**: Grid import during lowest or negative dynamic price periods.
* **Priority 3**: Battery preservation when solar generation is imminent.
""",
                "tags": ["optimizer", "ems", "fahrplan", "wallbox", "wärmepumpe", "ladefenster", "börsenstrom"],
                "is_featured": True,
                "sort_order": 6,
            },

            # ---------------------------------------------------------------------
            # 7. TARIFFS: STROMTARIFE & STICHTAGE
            # ---------------------------------------------------------------------
            {
                "category": cats["tariffs"],
                "slug": "stromtarife-und-stichtagsberechnung",
                "context_key": "tariffs",
                "title_de": "Strompreise, Stichtage & Tarifhistorie verwalten",
                "title_en": "Managing Electricity Tariffs, Effective Dates & Price History",
                "summary_de": "Wie Tarifänderungen mit Stichtag (valid_from) erfasst werden, damit historische Energiebilanzen stimmig bleiben.",
                "summary_en": "How to record tariff changes with a valid-from date to preserve accurate historical billing.",
                "content_de": """# Strompreise & Tarifhistorie

Damit deine monatlichen und jährlichen Energiekosten mathematisch exakt bleiben, unterstützt Sharegy **stichtagsgenaue Tarifhistorien**.

## Tarifwechsel erfassen (z. B. Preisanpassung zum 01.09.)

1. Navigiere zu **Strompreise & Tarife**.
2. Wähle das Datum **Gültig ab** (z. B. `01.09.2026`).
3. Trage den neuen Arbeitspreis (ct/kWh), Grundpreis (€/Monat) oder Einspeisevergütung ein.
4. Klicke auf **Speichern**.

### Automatische Verrechnung:
* Tage und Monate **vor dem Stichtag** werden mit dem damals gültigen Alttarif abgerechnet.
* Verbräuche **ab dem Stichtag** fließen sofort mit den neuen Konditionen in alle Berechnungen ein.
""",
                "content_en": """# Tariffs & Historical Precision

Sharegy uses date-effective tariffs (`valid_from`) to guarantee exact retroactive energy accounting.

## Setting Up a Tariff Change
1. Go to **Electricity Tariffs & Prices**.
2. Set the **Valid from** date (e.g., `2026-09-01`).
3. Enter the new energy rate (ct/kWh), base fee (€/month), or feed-in tariff.
4. Click **Save**.
""",
                "tags": ["tariffs", "strompreis", "stichtag", "historie", "einspeisung", "arbeitspreis"],
                "is_featured": False,
                "sort_order": 7,
            },

            # ---------------------------------------------------------------------
            # 8. TARIFFS: DYNAMISCHE TARIFE & TIBBER
            # ---------------------------------------------------------------------
            {
                "category": cats["tariffs"],
                "slug": "dynamische-stromtarife-und-tibber",
                "context_key": "tariffs",
                "title_de": "Dynamische Börsenstrompreise & Tibber API Anbindung",
                "title_en": "Dynamic Spot Tariffs & Tibber API Integration",
                "summary_de": "Anbindung von Day-Ahead-Börsenpreisen via Energy-Charts, SMARD und Tibber API.",
                "summary_en": "Connecting day-ahead spot market prices via Energy-Charts, SMARD, and Tibber API.",
                "content_de": """# Dynamische Stromtarife & Börsenpreise

Dynamische Stromtarife ermöglichen es dir, Strom genau dann aus dem Netz zu beziehen, wenn er an der europäischen Strombörse (EPEX Spot DE-LU) am günstigsten ist.

## Unterstützte Preisquellen
1. **Energy-Charts (Fraunhofer ISE)**: Primäre Echtzeit- und Day-Ahead-Schnittstelle.
2. **SMARD (Bundesnetzagentur)**: Automatischer Hochverfügbarkeits-Fallback.
3. **Tibber API**: Direkte Synchronisation deiner kundenspezifischen Endkundenpreise inklusive Netzgebühren und Umlagen.

## Preis-Formel
Für eigene dynamische Tarife kannst du flexible Formeln hinterlegen (z. B. `spot * 1.19 + 0.15` für Mehrwertsteuer und 15 ct/kWh fixe Netzentgelte).
""",
                "content_en": """# Dynamic Electricity Tariffs & Spot Market Integration

Dynamic tariffs allow you to consume grid electricity when spot market prices on the European Power Exchange (EPEX Spot) are lowest.

## Supported Data Providers
1. **Energy-Charts (Fraunhofer ISE)**: Primary day-ahead spot price source.
2. **SMARD (German Federal Network Agency)**: Automatic high-availability fallback.
3. **Tibber API**: Direct synchronization of your real retail electricity price.
""",
                "tags": ["tibber", "börsenstrom", "epex", "smard", "dynamisch", "dayahead"],
                "is_featured": True,
                "sort_order": 8,
            },

            # ---------------------------------------------------------------------
            # 9. ALERTS: ALARMZENTRALE & ANOMALIEERKENNUNG
            # ---------------------------------------------------------------------
            {
                "category": cats["alerts"],
                "slug": "alarmzentrale-und-anomalieerkennung",
                "context_key": "alerts",
                "title_de": "Alarm- & Notifikationszentrale: Echtzeit-Regeln & Anomalieerkennung",
                "title_en": "Alert & Notification Center: Live Rules & Anomaly Detection",
                "summary_de": "Übersicht aller 8 automatisierten Überwachungsregeln für Ertragsausfälle, Tiefentladeschutz und Dauerlasten.",
                "summary_en": "Overview of the 8 automated health checks for solar yield drops, battery protection, and baseload alarms.",
                "content_de": """# Alarm- & Notifikationszentrale

Die Alarmzentrale überwacht rund um die Uhr deine Erzeugung, Speicher und Verbräuche auf Unregelmäßigkeiten.

## Die 8 Live-Überwachungsregeln

1. 🔴 **Keine PV-Erzeugung (Ertragsausfall)**:
   * Löst aus, wenn die Globalstrahlung > 400 W/m² beträgt, der Wechselrichter aber 0 W meldet (z. B. DC-Freischalter aus oder Sicherung gefallen).
2. 🟡 **Batterie leer / Ungewöhnliche Entladung**:
   * Warnung bei Absinken des SoC unter die Notstromreserve (< 10 %).
3. 🟡 **Unerwarteter Nachtverbrauch (Dauerlast-Alarm)**:
   * Benachrichtigung bei konstantem Verbrauch > 1.500 W zwischen 01:00 und 05:00 Uhr.
4. 🔴 **Gerät offline / Signal-Verlust**:
   * Alarm bei Ausbleiben von Zähler- oder Wechselrichter-Telemetrie seit mehr als 15 Minuten.
5. 🟢 **Börsentief- & Negativpreis-Chance**:
   * Spar-Tipp bei anstehenden Negativpreisen an der Strombörse.
6. 🔴 **Netzbezug trotz Solarüberschuss**:
   * Erkennt Phasenasymmetrien oder fehlerhafte Zählerkonfigurationen.
7. 🟡 **Extremer Preis-Peak**:
   * Warnung vor teuren Verbrauchsspitzen bei Dunkelflauten.
8. 🔵 **Frostschutz & Wärmepumpen-Vorlauf**:
   * Hinweis bei extremen Außentemperaturen.

## Alarme quittieren & Historie
* **✓ Erledigt**: Schließt den Alarm ab und verschiebt ihn in die Historie.
* **Gesehen**: Bestätigt die Kenntnisnahme, lässt den Alarm aber aktiv.
""",
                "content_en": """# Alert & Notification Center

The Alert Center continuously scans energy flows and device telemetry to proactively flag equipment faults and cost-saving opportunities.

## The 8 Core Health Checks
1. 🔴 **PV Yield Loss**: Solar radiation > 400 W/m² but inverter power is 0 W.
2. 🟡 **Battery Depleted**: SoC falls below configured emergency reserve (< 10%).
3. 🟡 **Unexpected Night Baseload**: Sustained load > 1500 W between 01:00 and 05:00.
4. 🔴 **Device Offline**: Missing telemetry for > 15 minutes.
5. 🟢 **Negative Spot Price Opportunity**: Alerts to scheduled negative electricity price hours.
6. 🔴 **Grid Import During Solar Surplus**: Detects phase imbalance or meter misconfiguration.
7. 🟡 **Extreme Price Peak**: Warns before expensive peak hours.
8. 🔵 **Freeze Protection & Heat Pump Guard**: Temperature monitoring for heating systems.
""",
                "tags": ["alerts", "alarm", "benachrichtigung", "ertragsausfall", "überwachung", "notifikation"],
                "is_featured": True,
                "sort_order": 9,
            },

            # ---------------------------------------------------------------------
            # 10. BILLING: VIRTUELLE ZÄHLER & SUB-METERING
            # ---------------------------------------------------------------------
            {
                "category": cats["billing"],
                "slug": "virtuelle-zaehler-und-submetering",
                "context_key": "billing",
                "title_de": "Virtuelle Zähler, Sub-Metering & Mieterstrom-Abrechnung",
                "title_en": "Virtual Meters, Sub-Metering & Multi-Tenant Billing",
                "summary_de": "Aufteilung des Gesamtstroms auf einzelne Verbraucher (Wallbox, Wärmepumpe, Einliegerwohnung) und PDF-Abrechnung.",
                "summary_en": "Allocating total electricity across submeters (EV charger, heat pump, rental unit) with PDF reports.",
                "content_de": """# Virtuelle Zähler & Sub-Metering

Mit dem Sub-Metering-Modul kannst du deinen Gesamtverbrauch mathematisch auf einzelne Stromkreise oder Mieter aufteilen.

## Funktionsweise der Zählerhierarchie
1. **Hauptzähler (Grid Meter)**: Misst den gesamten Netzbezug und die Einspeisung am Hausanschluss.
2. **Sub-Zähler (Unterzähler)**: Messen dedizierte Verbraucher wie Wallbox, Wärmepumpe oder Einliegerwohnung.
3. **Restverbrauch (Virtueller Zähler)**:
   > 📐 **Formel:**  
   > `Restverbrauch = Gesamtverbrauch - Summe aller Unterzähler`

## Solare Deckungsquote je Verbraucher
Sharegy berechnet für jeden Unterzähler sekundengenau, zu wie viel Prozent der Verbrauch durch die Solaranlage gedeckt wurde und welcher Anteil Netzstrom war.
""",
                "content_en": """# Virtual Meters & Sub-Metering

The sub-metering engine enables precise breakdown of total household consumption into individual consumer circuits or multi-tenant parties.

## Meter Hierarchy
1. **Main Grid Meter**: Measures total import and export at the grid connection point.
2. **Sub-Meters**: Dedicated meters for EV chargers, heat pumps, or rental units.
3. **Residual Load (Virtual Meter)**:
   > 📐 **Formula:**  
   > `Residual Load = Total Consumption - Sum of all Submeters`
""",
                "tags": ["billing", "submetering", "mieterstrom", "virtuelle zähler", "abrechnung", "pdf"],
                "is_featured": False,
                "sort_order": 10,
            },

            # ---------------------------------------------------------------------
            # 11. DEVICES & PROTOCOLS: MQTT & SMART HOME
            # ---------------------------------------------------------------------
            {
                "category": cats["devices-protocols"],
                "slug": "mqtt-und-smart-home-integration",
                "context_key": "devices",
                "title_de": "MQTT, ioBroker & Shelly Zähler anbinden",
                "title_en": "Connecting MQTT, ioBroker & Shelly Meters",
                "summary_de": "Integration von Smart-Home-Zählern und Relais über den integrierten MQTT-Broker und REST-APIs.",
                "summary_en": "Integrating smart home meters and relays via MQTT broker and REST APIs.",
                "content_de": """# MQTT & Smart Home Integration

Sharegy lässt sich nahtlos mit bestehenden Smart-Home-Systemen wie **ioBroker**, **OpenHAB** oder **Shelly** verbinden.

## Anbindung via MQTT
* **Broker-Host**: IP deines Sharegy-Servers (oder externer Mosquitto Broker).
* **Port**: `1883` (bzw. `8883` für TLS).
* **Topic-Struktur**: `h/<token>/<device_id>/telemetry`
* **JSON-Payload**:
```json
{
  "power_w": 2450.5,
  "voltage_v": 230.2,
  "energy_kwh": 1420.8
}
```

## Shelly 3EM & Pro 3EM Direkt-Integration
Trage im Webinterface des Shelly unter **Advanced - Developer Settings → MQTT** einfach die Broker-Zugangsdaten ein. Die Messdaten werden automatisch erkannt.
""",
                "content_en": """# MQTT & Smart Home Integration

Connect Sharegy to your smart home environment including **ioBroker**, **OpenHAB**, or **Shelly** meters.

## MQTT Configuration
* **Broker Host**: IP address of your server.
* **Port**: `1883` (or `8883` for TLS).
* **Topic**: `h/<token>/<device_id>/telemetry`
* **Sample Payload**:
```json
{
  "power_w": 2450.5,
  "energy_kwh": 1420.8
}
```
""",
                "tags": ["mqtt", "iobroker", "shelly", "smart home", "protokolle"],
                "is_featured": False,
                "sort_order": 11,
            },

            # ---------------------------------------------------------------------
            # 12. GRAFANA INTEGRATION & COCKPIT DASHBOARDS
            # ---------------------------------------------------------------------
            {
                "category": cats["devices-protocols"],
                "slug": "grafana-integration-und-cockpit-dashboards",
                "context_key": "interfaces",
                "title_de": "Grafana Integration & Energy Cockpit Dashboards",
                "title_en": "Grafana Integration & Energy Cockpit Dashboards",
                "summary_de": "Einrichtung der Grafana JSON/Infinity Datasource, Token-Authentifizierung und Nutzung des fertigen Sharegy Cockpit Dashboards.",
                "summary_en": "Setting up Grafana JSON/Infinity datasource, token authentication, and importing the Sharegy Energy Cockpit dashboard.",
                "content_de": """# Grafana Integration & Energy Cockpit

Mit der integrierten Grafana-Schnittstelle kannst du hochentwickelte Dashboards und Zeitreihenanalysen in Grafana erstellen.

## 1. REST-Bridge Endpoints
Sharegy stellt standardisierte Endpunkte für Grafana (JSON / Infinity Datasource) bereit:
* `GET /api/grafana/`: Healthcheck & Ping.
* `POST /api/grafana/search`: Dynamische Metrikenliste (`pv_power_w`, `load_power_w`, `battery_soc_pct`, `autarky_rate_pct`, `spot_price_ct_per_kwh`, `submeter_*`).
* `POST /api/grafana/query`: Zeitreihen-Stream im Grafana Datapoint-Format `[[value, timestamp_ms], ...]`.
* `POST /api/grafana/annotations`: Überträgt Live-System-Warnungen und Optimizer-Ereignisse als Markierungen in den Zeitstrahl.

## 2. Authentifizierung in Grafana
Trage in den Grafana Datasource-Einstellungen unter **Custom HTTP Headers** einen der folgenden Header ein:
* `X-API-Key: <DEIN_MQTT_PASSWORT_ODER_TOKEN>`
* oder `Authorization: Bearer <DEIN_MQTT_PASSWORT_ODER_TOKEN>`

## 3. Fertiges Cockpit-Dashboard
Im Verzeichnis `plugins/grafana/dashboards/sharegy_energy_cockpit.json` findest du ein sofort importierbares Dashboard mit Gauges für PV/Last/SoC/Autarkie, 24h-Verläufen, dynamischen Strompreisen und gestapelten Sub-Metering-Kacheln.
""",
                "content_en": """# Grafana Integration & Energy Cockpit

Build professional dashboards and time-series analytics in Grafana powered by live Sharegy telemetry.

## 1. REST-Bridge Endpoints
Sharegy offers dedicated endpoints compatible with Grafana JSON / Infinity Datasources:
* `GET /api/grafana/`: Healthcheck & Ping.
* `POST /api/grafana/search`: Metrics list (`pv_power_w`, `load_power_w`, `battery_soc_pct`, `autarky_rate_pct`, `spot_price_ct_per_kwh`, `submeter_*`).
* `POST /api/grafana/query`: Time series data stream in `[[value, timestamp_ms], ...]` format.
* `POST /api/grafana/annotations`: System alerts and optimizer events.

## 2. Authentication
In Grafana Datasource settings, configure **Custom HTTP Headers**:
* `X-API-Key: <YOUR_MQTT_PASSWORD_OR_TOKEN>`
* or `Authorization: Bearer <YOUR_MQTT_PASSWORD_OR_TOKEN>`
""",
                "tags": ["grafana", "visualisierung", "dashboards", "json datasource", "infinity", "api"],
                "is_featured": True,
                "sort_order": 12,
            },

            # ---------------------------------------------------------------------
            # 13. HOME ASSISTANT CUSTOM INTEGRATION & TELEMETRY PUSH
            # ---------------------------------------------------------------------
            {
                "category": cats["devices-protocols"],
                "slug": "home-assistant-integration-und-telemetrie-push",
                "context_key": "interfaces",
                "title_de": "Home Assistant Custom Integration & Telemetrie-Push",
                "title_en": "Home Assistant Custom Integration & Telemetry Push",
                "summary_de": "Einrichtung der nativen Home Assistant Integration (9 Sensoren, Ladefenster) und verschlüsselter Messwerte-Push (sharegy.push_telemetry).",
                "summary_en": "Setting up the native Home Assistant integration (9 sensors, charging windows) and secure telemetry push (sharegy.push_telemetry).",
                "content_de": """# Home Assistant Integration & Telemetrie-Push

Die Sharegy Custom Component verbindet dein Smart Home bidirektional mit Sharegy HEMS.

## 1. Die 9 Home Assistant Live-Sensoren
Nach der Einrichtung im HA Config Flow stehen folgende Sensoren für Dashboards und Automationen bereit:
1. `sensor.sharegy_solar_erzeugung` (W)
2. `sensor.sharegy_hausverbrauch` (W)
3. `sensor.sharegy_netzleistung` (W)
4. `sensor.sharegy_batterieleistung` (W)
5. `sensor.sharegy_batterie_ladestand_soc` (%)
6. `sensor.sharegy_autarkiegrad` (%)
7. `sensor.sharegy_eigenverbrauchsquote` (%)
8. `sensor.sharegy_borsenstrompreis` (ct/kWh)
9. `sensor.sharegy_optimizer_best_zeitfenster` (z. B. `13:00 - 15:00` für smarte Aktorik)

## 2. Lokale Messwerte an Sharegy senden (`sharegy.push_telemetry`)
Mit dem Service `sharegy.push_telemetry` kann Home Assistant Messwerte lokaler Zähler (Shelly 3EM, Zigbee-Steckdosen, Wallbox, Wärmepumpe) gebündelt an Sharegy senden:

```yaml
alias: "Sharegy: Zählerdaten übertragen"
trigger:
  - platform: time_pattern
    seconds: "/10"
action:
  - service: sharegy.push_telemetry
    data:
      devices:
        - identifier: "ha_grid_meter"
          name: "Hausanschluss"
          power_w: "{{ states('sensor.shelly_3em_total_power') | float(0) }}"
          energy_kwh: "{{ states('sensor.shelly_3em_total_energy') | float(0) }}"
          role: "grid"
        - identifier: "ha_wallbox"
          name: "Wallbox"
          power_w: "{{ states('sensor.wallbox_power') | float(0) }}"
          role: "consumer"
```
""",
                "content_en": """# Home Assistant Integration & Telemetry Push

The Sharegy custom component bridges Home Assistant bidirectionally with Sharegy HEMS.

## 1. Live Sensors
1. `sensor.sharegy_solar_erzeugung` (W)
2. `sensor.sharegy_hausverbrauch` (W)
3. `sensor.sharegy_netzleistung` (W)
4. `sensor.sharegy_batterie_ladestand_soc` (%)
5. `sensor.sharegy_autarkiegrad` (%)
6. `sensor.sharegy_borsenstrompreis` (ct/kWh)
7. `sensor.sharegy_optimizer_best_zeitfenster` (e.g. `13:00 - 15:00`)

## 2. Sending Local Telemetry (`sharegy.push_telemetry`)
Push local energy meters (Shelly 3EM, Smart Plugs, Wallbox) automatically via Home Assistant automations.
""",
                "tags": ["homeassistant", "custom component", "push_telemetry", "aktoren", "wallbox", "shelly"],
                "is_featured": True,
                "sort_order": 13,
            },

            # ---------------------------------------------------------------------
            # 14. MATTER 1.3 ENERGY MANAGEMENT & HUB
            # ---------------------------------------------------------------------
            {
                "category": cats["devices-protocols"],
                "slug": "matter-1-3-energy-management-und-hub",
                "context_key": "interfaces",
                "title_de": "Matter 1.3 Energy Hub (Smart Plugs, EVSE & Inverter)",
                "title_en": "Matter 1.3 Energy Hub (Smart Plugs, EVSE & Inverters)",
                "summary_de": "Kopplung und Steuerung moderner Matter-Geräte via Thread/Wi-Fi/IP unter Nutzung des CSA Matter 1.3 Energy Management Standards.",
                "summary_en": "Commissioning and controlling Matter devices via Thread/Wi-Fi/IP utilizing the CSA Matter 1.3 Energy Management standard.",
                "content_de": """# Matter 1.3 Energy Management Hub

Sharegy verfügt über einen nativen **Matter Hub** mit voller Unterstützung des **CSA Matter 1.3 Energy Management Standards**.

## 1. Unterstützte Matter-Cluster
* **`0x0090` (Electrical Power Measurement)**: Misst Live-Leistung (`ActivePower` in W/mW), Spannung (`RMSVoltage` in mV), Stromstärke (`ActiveCurrent` in mA) und Power Factor.
* **`0x0091` (Electrical Energy Measurement)**: Erfasst kumulierte Zählerstände (`CumulativeEnergyImported`) in kWh.
* **`0x0006` (On/Off Cluster)**: Schaltet Relais und Zwischenstecker ein, aus oder toggelt ihren Zustand.
* **`0x0098` / `0x0099` (Device Energy Management & EVSE)**: Dynamische Leistungsbegrenzung (`power_adjustment_limit_w`) und Ladestromsteuerung (`max_charge_current_a`) für Wallboxen und Wärmepumpen.

## 2. Gerät per QR-Code oder Pairing-Code koppeln
1. Gehe in Sharegy auf **Schnittstellen & MQTT → Matter 1.3 Energy Hub**.
2. Klicke auf **+ Neues Matter-Gerät koppeln**.
3. Wähle die Kopplungsmethode:
   * **📷 QR-Code Payload**: z. B. `MT:Y.K9042C00KA0648G00`
   * **🔢 Manueller Code**: 11-stellig (z. B. `34970112332`) oder 21-stellig
   * **🔑 Setup-PIN**: 8-stelliger Geräte-PIN (z. B. `20202021`)
4. Nach dem Klick auf **Gerät verbinden** wird das Gerät automatisch in der Matter Fabric registriert und in die Sharegy-Zählerhierarchie eingebunden.
""",
                "content_en": """# Matter 1.3 Energy Management Hub

Sharegy provides a native **Matter Hub** fully compliant with the **CSA Matter 1.3 Energy Management standard**.

## 1. Supported Matter Clusters
* **`0x0090` (Electrical Power Measurement)**: Real-time active power (W), RMS voltage, active current, and power factor.
* **`0x0091` (Electrical Energy Measurement)**: Cumulative imported energy (kWh).
* **`0x0006` (On/Off Cluster)**: Smart plug relay toggling and switching.
* **`0x0098` / `0x0099` (Device Energy Management & EVSE)**: Dynamic EV charging limits and heat pump modulation.

## 2. Commissioning Devices
Pair devices in seconds via QR-Code (`MT:...`), 11-/21-digit manual pairing codes, or setup PINs directly from the **Matter 1.3 Energy Hub** card.
""",
                "tags": ["matter", "matter 1.3", "csa", "thread", "smart plug", "evse", "energy management"],
                "is_featured": True,
                "sort_order": 14,
            },
        ]

        for adata in articles_data:
            HelpArticle.objects.update_or_create(
                slug=adata["slug"],
                defaults=adata,
            )

        self.stdout.write(self.style.SUCCESS(f"Erfolgreich {len(categories_data)} Kategorien und {len(articles_data)} Handbuch-Artikel in DE & EN initialisiert!"))


