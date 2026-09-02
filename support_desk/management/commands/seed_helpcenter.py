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
                "title_de": "Geräte, Schnittstellen & Protokolle",
                "title_en": "Devices, Interfaces & Protocols",
                "description_de": "Integration von Home Assistant, Shelly WSS, Tasmota, OpenDTU, Modbus TCP und MQTT Gateways.",
                "description_en": "Integration with Home Assistant, Shelly WSS, Tasmota, OpenDTU, Modbus TCP, and MQTT gateways.",
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
            # 2b. CLOUD INVERTER INTEGRATION GUIDE (SUNGROW, KOSTAL, SOLAREDGE, FRONIUS, GROWATT)
            # ---------------------------------------------------------------------
            {
                "category": cats["inverters-meters"],
                "slug": "wechselrichter-cloud-anbindung-anleitung",
                "context_key": "devices",
                "title_de": "Wechselrichter & Speicher Cloud-Kopplung (Sungrow, Kostal, SolarEdge, Fronius, Growatt)",
                "title_en": "Cloud Inverter & Battery Integration Guide (Sungrow, Kostal, SolarEdge, Fronius, Growatt)",
                "summary_de": "Schritt-für-Schritt-Anleitung zur direkten Server-zu-Server Anbindung von PV-Wechselrichtern und Batteriespeichern ohne Zusatzhardware.",
                "summary_en": "Step-by-step setup guide for connecting solar inverters and battery storage directly via cloud APIs without local hardware.",
                "content_de": """# Direkte Cloud-Kopplung für Wechselrichter & Speicher ☁️🔌

Mit der **Cloud-Kopplung** bindest du deinen Wechselrichter und Batteriespeicher direkt per Server-zu-Server API an Sharegy an – **ganz ohne zusätzliche Hardware vor Ort** (wie Raspberry Pi oder Smart Dongle).

---

## 1. Übersicht der unterstützten Hersteller

| Hersteller | Unterstützte Modelle | Benötigte Zugangsdaten |
| :--- | :--- | :--- |
| **Sungrow** | SH5.0–SH25T Hybrid, SG-Serie, SBR-Speicher | `Anlagen-ID (ps_id)`, `E-Mail / Benutzer`, `Passwort`, `AppKey` |
| **Kostal** | PLENTICORE plus, PIKO IQ, PIKO MP, BYD | `Anlagen-ID (plant_id)`, `API-Schlüssel (api_key)` |
| **SolarEdge** | SE-Serie, HD-Wave, StorEdge, Optimierer | `Standort-ID (site_id)`, `API-Schlüssel (api_key)` |
| **Fronius** | GEN24 Plus, Symo, Primo, Tauro | `PV-System-ID`, `AccessKeyId`, `AccessKeyValue` |
| **Growatt** | MIN, MOD, MID, SPH, SPA, ARK-Speicher | `Anlagen-ID (plant_id)`, `OpenAPI Token` |

---

## 2. Schritt-für-Schritt Anleitung je Hersteller

### ☀️ Sungrow (iSolarCloud)
1. Logge dich im Browser unter [isolarcloud.eu](https://www.isolarcloud.eu) ein.
2. Klicke auf deine PV-Anlage. In der Adresszeile deines Browsers findest du die **Power Station ID (`ps_id`)** (z. B. `https://isolarcloud.eu/.../stationDetail?ps_id=1234567`).
3. Trage in Sharegy deine normale iSolarCloud-E-Mail, dein Passwort, die `ps_id` und den Gateway AppKey ein.
4. Klicke auf **„Verbindung testen“** und anschließend auf **„Jetzt mit Sharegy verbinden“**.

### ☀️ Kostal (Kostal Solar Portal)
1. Melde dich im [Kostal Solar Portal](https://www.kostal-solar-portal.com) an.
2. Navigiere zu **Einstellungen ➔ API-Zugriffsverwaltung** und generiere einen neuen **API-Schlüssel**.
3. Deine **Anlagen-ID** findest du in deiner Anlagenübersicht im Portal.
4. Trage den API-Schlüssel und die Anlagen-ID in Sharegy ein und speichere die Verbindung.

### ☀️ SolarEdge (Monitoring Portal)
1. Logge dich im [SolarEdge Monitoring Portal](https://monitoring.solaredge.com) ein.
2. Gehe auf **Admin ➔ Standortzugriff (Site Access)**.
3. Scrolle nach unten zum Bereich **API-Zugriff**, aktiviere diesen und generiere einen **API-Schlüssel**.
4. Kopiere die **Standort-ID (Site ID)** und den **API-Schlüssel** in Sharegy.

### ☀️ Fronius (Solar.web)
1. Öffne [solarweb.com](https://www.solarweb.com) und melde dich an.
2. Gehe zu **Einstellungen ➔ Benutzer- & Zugriffsverwaltung ➔ API-Zugriffsverwaltung**.
3. Erstelle einen API-Zugangsschlüssel und notiere dir `AccessKeyId` und `AccessKeyValue`.
4. Die **PV-System-ID** findest du in der URL deiner Anlage.

### ☀️ Growatt (ShineServer / OpenAPI)
1. Öffne das [Growatt ShineServer Portal](https://server.growatt.com) oder [openapi.growatt.com](https://openapi.growatt.com).
2. Gehe zu **Benutzerzentrum ➔ API Management** und erzeuge einen **OpenAPI Token**.
3. Notiere dir deine **Anlagen-ID (Plant ID)** aus der Anlagenübersicht.
4. Trage den Token und die Anlagen-ID in Sharegy ein.

---

## 3. Häufige Fragen (FAQ)

### Was mache ich, wenn ich mehrere Wechselrichter habe?
Lege in Sharegy einfach für jeden Wechselrichter ein eigenes Gerät an (z. B. *„Sungrow Süddach“* und *„Sungrow Garage“*). Jedes Gerät pollt seine eigene Seriennummer oder Anlagen-ID. Sharegy aggregiert alle Erträge automatisch im EMS.

### Wie oft werden die Daten aktualisiert?
Standardmäßig pollt Sharegy die Hersteller-Clouds im 60-Sekunden-Takt.
""",
                "content_en": """# Direct Cloud Integration for Inverters & Battery Storage ☁️🔌

With **Cloud Integration**, you connect your solar inverter and battery storage directly to Sharegy via server-to-server APIs – **no local hardware (like a Raspberry Pi or smart dongle) required**.

---

## 1. Supported Inverter Manufacturers

| Manufacturer | Supported Models | Required Credentials |
| :--- | :--- | :--- |
| **Sungrow** | SH5.0–SH25T Hybrid, SG Series, SBR Battery | `Plant ID (ps_id)`, `Email/Username`, `Password`, `AppKey` |
| **Kostal** | PLENTICORE plus, PIKO IQ, PIKO MP, BYD | `Plant ID`, `API Key (api_key)` |
| **SolarEdge** | SE Series, HD-Wave, StorEdge, Optimizers | `Site ID`, `API Key (api_key)` |
| **Fronius** | GEN24 Plus, Symo, Primo, Tauro | `PV System ID`, `AccessKeyId`, `AccessKeyValue` |
| **Growatt** | MIN, MOD, MID, SPH, SPA, ARK Battery | `Plant ID`, `OpenAPI Token` |

---

## 2. Step-by-Step Setup Guides

### ☀️ Sungrow (iSolarCloud)
1. Log in at [isolarcloud.eu](https://www.isolarcloud.eu).
2. Open your solar plant. In the browser URL bar, copy your **Power Station ID (`ps_id`)**.
3. In Sharegy, enter your iSolarCloud email, password, `ps_id`, and AppKey.
4. Click **"Test Connection"** and then **"Connect with Sharegy"**.

### ☀️ Kostal (Kostal Solar Portal)
1. Log in at [Kostal Solar Portal](https://www.kostal-solar-portal.com).
2. Navigate to **Settings ➔ API Access Management** and generate a new **API Key**.
3. Locate your **Plant ID** in your plant overview.
4. Enter both credentials into Sharegy and save.

### ☀️ SolarEdge (Monitoring Portal)
1. Log into [SolarEdge Monitoring Portal](https://monitoring.solaredge.com).
2. Go to **Admin ➔ Site Access**.
3. Scroll down to **API Access**, enable it, and generate an **API Key**.
4. Copy your **Site ID** and **API Key** into Sharegy.

### ☀️ Fronius (Solar.web)
1. Open [solarweb.com](https://www.solarweb.com) and log in.
2. Go to **Settings ➔ API Access Management**.
3. Create an API key and copy `AccessKeyId` and `AccessKeyValue`.
4. Find your **PV System ID** in your plant URL.

### ☀️ Growatt (ShineServer / OpenAPI)
1. Open [server.growatt.com](https://server.growatt.com) or [openapi.growatt.com](https://openapi.growatt.com).
2. Go to **User Center ➔ API Management** and generate an **OpenAPI Token**.
3. Note your **Plant ID** from your plant dashboard.
4. Enter your token and Plant ID into Sharegy.
""",
                "tags": ["cloud", "sungrow", "kostal", "solaredge", "fronius", "growatt", "wechselrichter", "inverter", "api"],
                "is_featured": True,
                "sort_order": 3,
            },

            # ---------------------------------------------------------------------
            # 2c. VENDOR-NEUTRAL TELEMETRY & METRIC SPECIFICATION
            # ---------------------------------------------------------------------

            {
                "category": cats["inverters-meters"],
                "slug": "benoetigte-messwerte-und-geraetebindung",
                "context_key": "devices",
                "title_de": "Welche Messwerte benötigt Sharegy? (Herstellerunabhängige Übersicht)",
                "title_en": "Which Telemetry Metrics Does Sharegy Require? (Universal Guide)",
                "summary_de": "Vom reinen Verbraucher-Tracking bis zum Hybrid-System mit Speicher: Welche physikalischen Größen für Bilanzierung, Autarkie und Sub-Metering nötig sind.",
                "summary_en": "From dynamic tariff tracking without PV to complex solar storage hybrids: What physical metrics are required for energy balance and sub-metering.",
                "content_de": """# Welche Messwerte benötigt Sharegy? ⚡📊

Sharegy ist vollständig **hersteller- und hardwareunabhängig**. Egal ob du Daten über Home Assistant, MQTT, ioBroker, Shelly, REST-Webhooks oder Cloud-APIs (Sungrow, SolarEdge, Fronius) einspeist: Sharegy verarbeitet die physikalischen Standardgrößen.

---

## 1. Funktioniert Sharegy auch ohne PV oder Batteriespeicher?
**Ja, absolut!** Sharegy ist modular aufgebaut:
* **Reine Verbraucher- & Tarifoptimierung**: Auch ohne eigene Erzeugung nutzt Sharegy Börsenstrompreise (EPEX Spot), steuert schaltbare Steckdosen und berechnet den Verbrauch einzelner Geräte (Sub-Metering).
* **Balkonkraftwerk-Setup**: Erfasst bereits mit einem einfachen Zwischenstecker an der Balkon-PV deinen erzeugten Solarstrom und berechnet, wie viel davon deine Haushaltsgeräte direkt nutzen.
* **Vollständiges Hybrid-System**: Mit PV-Anlage, Batteriespeicher und Smart Meter schöpfst du das maximale Potenzial für Autarkie und Lastoptimierung aus.

---

## 2. Die physikalischen Messgrößen im Überblick

| Messgröße | Einheit | Datenpunkt-Beispiele | Wofür wird der Wert genutzt? |
| :--- | :---: | :--- | :--- |
| **Wirkleistung** | **Watt (W)** | `power`, `pv_power`, `battery_power`, `grid_power`, `load_power` | Live-Energieflüsse, Sankey-Diagramm, Leistungsspitzen |
| **Stromstärke** | **Ampere (A)** | `battery_current`, `current`, `phase_current` | Eindeutige **Flussrichtung** bei Speichern (negativ = Laden, positiv = Entladen) |
| **Spannung** | **Volt (V)** | `voltage`, `battery_voltage`, `phase_voltage` | Netzstabilität, $P = U \times I$ Ersatzberechnung |
| **Ladestand** | **%** | `soc`, `battery_soc`, `battery_level` | Speicherstand, EMS-Ladelimits und Entladepuffer |
| **Zählerstand** | **kWh** | `energy`, `energy_in`, `energy_out`, `total_yield` | Exakte Tages-, Monats- und Jahresbilanzierung |

---

## 3. Die mathematische Grundregel für das Gesamthaus: *„3 von 4 reichen aus!“*

Im Haushalt gilt physikalisch immer der Knotenpunktsatz:
$$\\text{Hausverbrauch } (P_{\\text{Load}}) = \\text{PV-Erzeugung } (P_{\\text{PV}}) + \\text{Batterieleistung } (P_{\\text{Bat}}) + \\text{Netzübergabe } (P_{\\text{Grid}})$$

* Wenn du **3 dieser 4 Werte** lieferst, errechnet Sharegy den 4. Wert automatisch zu 100 % fehlerfrei.
* Lieferst du alle 4 Werte (z. B. aus einem modernen Wechselrichter mit Smart Meter), gleicht Sharegy die Werte zusätzlich ab.

---

## 4. Häufige Frage: Warum habe ich 2 Datenpunkte für die Batterie (Strom in A und Leistung in W)?
Manche Wechselrichter (wie z. B. Sungrow) liefern die Batterieleistung immer als positive Zahl und die Richtung separat über den **Batteriestrom in Ampere (A)**:
* **Batteriestrom < 0 A**: Batterie lädt aus PV/Netz.
* **Batteriestrom > 0 A**: Batterie entlädt ins Haus.

In Sharegy wird hierfür **nur 1 virtueller Batteriespeicher** angelegt: In den Einstellungen des Speichers ordnest du die Wirkleistung (W) als *Ladeleistung* und den Strom (A) als *Batteriestrom* zu. Sharegy trennt Lade- und Entladezyklen daraufhin automatisch und physikalisch exakt!
""",
                "content_en": """# Telemetry Metrics & Universal Device Mapping ⚡📊

Sharegy is completely **vendor- and hardware-agnostic**. Whether you stream data via Home Assistant, MQTT, ioBroker, Shelly, REST webhooks, or Cloud APIs (Sungrow, SolarEdge, Fronius): Sharegy processes standardized physical electrical units.


---

## 1. Does Sharegy work without PV or Battery Storage?
**Yes, absolutely!** Sharegy is built modularly:
* **Consumer & Dynamic Tariff Tracking**: Even without generation assets, Sharegy tracks spot market prices (EPEX Spot), schedules smart plugs, and provides granular sub-metering.
* **Balcony PV (Plug-in Solar)**: Measure solar output with a simple plug and track direct consumption across household appliances.
* **Full Solar + Storage Hybrid**: Harness maximal self-sufficiency and automated energy optimization.

---

## 2. Core Physical Quantities

| Physical Quantity | Unit | Metric Key Examples | Primary Usage |
| :--- | :---: | :--- | :--- |
| **Active Power** | **Watt (W)** | `power`, `pv_power`, `battery_power`, `grid_power` | Real-time energy flow, Sankey diagrams, live load tracking |
| **Electric Current** | **Ampere (A)** | `battery_current`, `current` | Unambiguous **flow direction** (negative = charging, positive = discharging) |
| **Voltage** | **Volt (V)** | `voltage`, `battery_voltage` | Grid stability, backup $P = U \times I$ power calculations |
| **State of Charge** | **%** | `soc`, `battery_soc`, `battery_level` | Battery status, smart reserve thresholds, optimization |
| **Energy Totals** | **kWh** | `energy`, `energy_in`, `energy_out` | Daily, monthly, and yearly fiscal energy balances |
""",
                "tags": ["telemetry", "messwerte", "watt", "ampere", "volt", "soc", "kwh", "hardware"],
                "is_featured": True,
                "sort_order": 3,
            },

            # ---------------------------------------------------------------------
            # 3. INVERTERS VIA HOME ASSISTANT & IOBROKER BRIDGE
            # ---------------------------------------------------------------------
            {
                "category": cats["inverters-meters"],
                "slug": "sma-sungrow-modbus-tcp-einrichten",
                "context_key": "devices",
                "title_de": "Wechselrichter (SMA, Sungrow, Fronius, Deye) via Home Assistant anbinden",
                "title_en": "Connecting Inverters (SMA, Sungrow, Fronius, Deye) via Home Assistant",
                "summary_de": "Da Modbus TCP ein rein lokales Netzwerkprotokoll ist, liest Home Assistant oder ioBroker den Wechselrichter aus und streamt die Datenpunkte in die Sharegy Cloud.",
                "summary_en": "Since Modbus TCP operates locally within your LAN, Home Assistant or ioBroker reads the inverter and streams telemetry into Sharegy Cloud.",
                "content_de": """# Wechselrichter & Speicher via Home Assistant Bridge anbinden ☀️🏠

Klassische Solar-Wechselrichter und Batteriespeicher (wie **SMA Sunny Tripower**, **Sungrow SH**, **Fronius GEN24**, **Deye**, **Huawei SUN2000**) kommunizieren im lokalen Heimnetzwerk über das industrielle **Modbus TCP** Protokoll (Port 502).

## Warum erfolgt die Anbindung über Home Assistant oder ioBroker?
* 🔒 **Sicherheit & Router-Schutz**: Modbus TCP ist unverschlüsselt und darf niemals direkt ins Internet geöffnet werden.
* 🌐 **SaaS Cloud-Architektur**: Sharegy verbindet sich nicht invasiv in dein privates Heimnetzwerk, sondern empfängt die Datenpunkte verschlüsselt von deiner lokalen Zentrale.
* ⚡ **1-Klick Auswahl**: Dein lokaler **Home Assistant** (oder ioBroker) liest den Wechselrichter per lokaler Integration (z. B. SunSpec, SMA oder Sungrow) aus – und du wählst die Sensoren in der Sharegy Integration einfach per Klick aus!

---

## Einrichtung in 3 einfachen Schritten

### Schritt 1: Modbus TCP im Wechselrichter aktivieren
1. Rufe das lokale Webportal deines Wechselrichters auf (z. B. im Installateurs-Menü).
2. Aktiviere **Modbus TCP** (Standard-Port: `502`).

### Schritt 2: Wechselrichter in Home Assistant hinzufügen
Füge in Home Assistant die passende Hersteller-Integration hinzu (z. B. *SMA Solar*, *Sungrow*, *Fronius* oder *SunSpec*). Home Assistant erkennt sofort alle Live-Werte:
* PV-Erzeugung (W)
* Netzeinspeisung / Bezug (W)
* Batterie-Ladestand (SoC %) & Batterieleistung (W)

### Schritt 3: In der Sharegy Home Assistant Integration auswählen
1. Öffne in Home Assistant **Einstellungen → Geräte & Dienste → Sharegy → Konfigurieren**.
2. Wähle die vom Wechselrichter bereitgestellten Entitäten im **1-Klick Entity Picker** aus.
3. Fertig! Ab sofort fließen alle Erzeugungs- und Speicherdaten in Echtzeit und mit 48h Offline-Puffer in dein Sharegy Dashboard.
""",
                "content_en": """# Connecting Inverters & Storage via Home Assistant Bridge ☀️🏠

Solar inverters and battery systems (such as **SMA Sunny Tripower**, **Sungrow SH**, **Fronius GEN24**, **Deye**, **Huawei**) communicate locally via **Modbus TCP** (Port 502).

## Why bridge through Home Assistant or ioBroker?
* 🔒 **Network Security**: Raw Modbus TCP is unencrypted and should never be exposed to the public internet.
* 🌐 **Clean SaaS Architecture**: Sharegy receives outbound encrypted telemetry without requiring local network ingress.
* ⚡ **1-Click Entity Selection**: Home Assistant reads the inverter locally, and you simply map the entities to Sharegy in seconds.

## Setup Workflow
1. **Enable Modbus TCP** in your inverter's local web portal (Port 502).
2. **Add Inverter Integration** in Home Assistant (e.g. SMA, Sungrow, Fronius, SunSpec).
3. **Map Sensors in Sharegy Integration**: Select the discovered entities in the Sharegy configuration flow.
""",
                "tags": ["modbus", "inverter", "homeassistant", "sma", "sungrow", "fronius", "deye", "huawei"],
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
                "title_de": "MQTT, ioBroker, Node-RED & Smart-Home Gateways",
                "title_en": "Connecting MQTT, ioBroker, Node-RED & Gateways",
                "summary_de": "Integration von Smart-Home-Zentralen und Custom-Zählern über den integrierten MQTT-Broker und REST-APIs.",
                "summary_en": "Integrating smart home systems and custom telemetry via MQTT broker and REST APIs.",
                "content_de": """# MQTT & Smart Home Gateway Integration

Sharegy lässt sich nahtlos mit lokalen Smart-Home-Zentralen wie **ioBroker**, **Node-RED** oder **OpenHAB** verbinden.

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

> [!IMPORTANT]
> **Shelly-Geräte bitte NICHT über MQTT anbinden!**  
> Für alle Shelly-Geräte (Gen2 / Gen3 / Plus / Pro / Mini) steht die native **Outbound-WebSocket (WSS)** Schnittstelle zur Verfügung.  
> * **Warum kein MQTT bei Shelly?** MQTT erfordert komplexe Broker-Konfigurationen, scheitert an Routern/Firewalls und unterstützt keine zuverlässige bidirektionale Aktorik in Cloud-Umgebungen.  
> * **Empfohlener Weg:** Nutze für Shelly immer **Outbound WebSocket (Port 443)** (siehe Handbuch-Artikel *„Shelly Outbound WebSocket & Bidirektionale Relais-Steuerung“*). Dies funktioniert in 2 Minuten ohne Routerfreigaben und ermöglicht sekundenschnelle Relais-Schaltung direkt im Dashboard.
""",
                "content_en": """# MQTT & Smart Home Gateway Integration

Connect Sharegy to your smart home environment including **ioBroker**, **Node-RED**, or **OpenHAB**.

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

> [!IMPORTANT]
> **Do NOT use MQTT for Shelly devices!**  
> For all Shelly devices (Gen2 / Gen3 / Plus / Pro / Mini), always use the native **Outbound WebSocket (WSS)** interface over Port 443. It requires zero router configuration and enables low-latency bidirectional relay switching.
""",
                "tags": ["mqtt", "iobroker", "nodered", "openhab", "smart home", "protokolle"],
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
                "title_de": "Home Assistant Native Integration & 1-Klick Entity Bridge",
                "title_en": "Home Assistant Native Integration & 1-Click Entity Bridge",
                "summary_de": "Vollständige Anleitung für die offizielle Sharegy Home Assistant Integration mit 1-Klick Entity Picker, Outbound WSS und 48h Offline-Puffer.",
                "summary_en": "Complete guide for the official Sharegy Home Assistant integration with 1-click entity selector, outbound WSS, and 48h offline buffer.",
                "content_de": """# Sharegy Cloud Energy Bridge für Home Assistant ⚡🏠

Die offizielle **Sharegy Home Assistant Integration** überträgt alle deine lokalen Energiedaten ohne Portfreigaben und vollkommen verschlüsselt an die Sharegy Cloud.

## 🌟 Highlights der Integration
* **🎯 1-Klick Entity Picker**: Wähle deine Zähler (Netzbezug, PV-Erzeugung, Batteriespeicher, Wallbox, Wärmepumpe, Einzel-Zwischenstecker) direkt in der Home Assistant Benutzeroberfläche aus.
* **⚡ Outbound WebSocket (WSS)**: Direkte verschlüsselte Verbindung zu `wss://sharegy.de/ws/energy/<TOKEN>/` über Standard-Port 443 (funktioniert durch jede FRITZ!Box und Firewall ohne VPN oder Portweiterleitung).
* **💾 48h SQLite Store & Forward Puffer**: Bei Internet- oder Stromausfällen speichert Home Assistant alle Messdaten lokal in einer SQLite-Datenbank und sendet sie nach Wiederverbindung lückenlos nach.
* **🔄 Live-Anpassung (Options Flow)**: Konfigurierte Sensoren können jederzeit unter *Einstellungen → Geräte & Dienste → Sharegy → Konfigurieren* angepasst werden.

## 🚀 Installation & Einrichtung

### Methode 1: Über HACS (Empfohlen)
1. Öffne **HACS** in deinem Home Assistant.
2. Klicke oben rechts auf das Drei-Punkte-Menü → **Benutzerdefinierte Repositories**.
3. Trage die Repository-URL deines Sharegy-Projekts ein (Kategorie: *Integration*).
4. Klicke auf **Herunterladen** und starte Home Assistant neu.
5. Gehe zu **Einstellungen → Geräte & Dienste → Integration hinzufügen → Sharegy** und trage deinen persönlichen Haushalts-Token ein.

### Methode 2: Manuelle Installation
1. Kopiere den Ordner `custom_components/sharegy` in deinen HA-Ordner `config/custom_components/`.
2. Starte Home Assistant neu und füge Sharegy unter *Geräte & Dienste* hinzu.
""",
                "content_en": """# Sharegy Cloud Energy Bridge for Home Assistant ⚡🏠

The official **Sharegy Home Assistant Integration** streams all your local smart home and energy data securely to the Sharegy Cloud without firewall changes or open ports.

## 🌟 Key Features
* **🎯 1-Click Entity Picker**: Select your energy sensors (Grid, Solar PV, Battery Storage, EV Charger, Heat Pump, Smart Plugs) natively inside the HA UI.
* **⚡ Outbound WebSocket (WSS)**: Secure streaming directly to `wss://sharegy.de/ws/energy/<TOKEN>/` over standard Port 443.
* **💾 48h SQLite Store & Forward Buffer**: If your internet connection drops, telemetry is buffered locally and automatically synchronized once reconnected.
* **🔄 Live Options Flow**: Easily modify mapped sensors anytime under *Settings → Devices & Services → Sharegy → Configure*.
""",
                "tags": ["homeassistant", "custom component", "hacs", "websocket", "offline buffer", "entity picker", "shelly"],
                "is_featured": True,
                "sort_order": 13,
            },

            # ---------------------------------------------------------------------
            # 14. SHELLY OUTBOUND WEBSOCKET & AKTORIK
            # ---------------------------------------------------------------------
            {
                "category": cats["devices-protocols"],
                "slug": "shelly-wss-und-relais-steuerung",
                "context_key": "interfaces",
                "title_de": "Shelly Outbound WebSocket & Bidirektionale Relais-Steuerung",
                "title_en": "Shelly Outbound WebSocket & Bidirectional Relay Actuation",
                "summary_de": "Einrichtung von Shelly Gen2/Gen3/Pro Relais per Outbound WSS (Port 443) und Live-Schaltung von Verbrauchern direkt im Sharegy Dashboard.",
                "summary_en": "Setting up Shelly Gen2/Gen3/Pro devices via Outbound WSS (Port 443) and live consumer actuation directly from the Sharegy dashboard.",
                "content_de": """# Shelly Outbound WebSocket & Bidirektionale Relais-Steuerung 🔌⚡

Sharegy unterstützt die direkte, bidirektionale Steuerung von **Shelly-Geräten der 2. und 3. Generation** (Plus, Pro, Gen3, Mini) über verschlüsselte Outbound-WebSockets.

## 1. Vorteile der Outbound-WSS-Technologie
* 🔒 **Keine offenen Ports oder Portweiterleitungen**: Das Gerät baut von innen heraus eine sichere TLS-Verbindung zu Sharegy auf.
* ⚡ **Echtzeit-Latenz (< 10 ms)**: Messwerte (W, V, A, kWh) und Schaltbefehle (Relais AN / AUS) werden ohne Verzögerung übertragen.
* 💡 **Optimistisches Dashboard-Feedback**: Schalte smarte Zwischenstecker, Warmwasserstäbe oder Wallbox-Freigaben direkt per Klick im Dashboard.

## 2. Einrichtung im Shelly Webinterface (in 2 Minuten)
1. Öffne die IP-Adresse deines Shelly-Geräts im Webbrowser (oder in der Shelly Smart Control App).
2. Navigiere zu **Settings → Outbound WebSocket** (oder *Advanced - Developer Settings*).
3. Aktiviere den WebSocket-Schalter (**Enable**).
4. Wähle als Server-Typ: **`ws`** oder **`wss`**.
5. Trage deine persönliche Sharegy-URL ein:
   > `wss://sharegy.de/ws/energy/<DEIN_HAUSHALTS_TOKEN>/`
6. Klicke auf **Save Settings**.

Sobald der Shelly verbunden ist, wird er automatisch in deiner **Geräteliste** angelegt und der **Relais-Schalter** steht sofort bereit!

## 3. Unterstützte Geräte & Protokolle
* **Shelly Smart Plugs & Relais**: Shelly Plus 1PM, Shelly 1PM Gen3, Shelly Plus Plug S, Shelly Pro 1PM, Pro 4PM, Mini 1PM.
* **Dreiphasige Energiemesser**: Shelly Pro 3EM, Shelly 3EM.
* **Tasmota Smart Plugs**: Nous A1T, Gosund SP111, Sonoff POW Elite/Origin.
* **Balkonkraftwerk-Wechselrichter**: OpenDTU / AhoyDTU für Hoymiles (inkl. Nulleinspeisung/Leistungsbegrenzung).
* **Wallboxen**: OCPP 1.6-J über WSS für dynamisches PV-Überschussladen.
""",
                "content_en": """# Shelly Outbound WebSocket & Bidirectional Relay Actuation 🔌⚡

Sharegy provides native bidirectional control for **Shelly Gen2, Gen3, and Pro series** devices over encrypted Outbound WebSockets.

## 1. Outbound WSS Benefits
* 🔒 **Zero Port Forwarding**: The device initiates an outbound TLS connection over standard Port 443.
* ⚡ **Real-time Latency (< 10ms)**: High-speed telemetry and immediate relay actuation.
* 💡 **Interactive UI Switches**: Toggle relays and smart plugs directly from your Sharegy dashboard.

## 2. Configuration Steps
1. Open your Shelly's local web portal.
2. Navigate to **Settings → Outbound WebSocket**.
3. Enable WebSockets and enter your Sharegy connection URL:
   > `wss://sharegy.de/ws/energy/<YOUR_HOME_TOKEN>/`
4. Click **Save Settings**.
""",
                "tags": ["shelly", "wss", "relais", "aktorik", "schalten", "smart plug", "tasmota", "opendtu", "ocpp"],
                "is_featured": True,
                "sort_order": 14,
            },
            {
                "category": cats["alerts"],
                "slug": "mobile-push-notifications",
                "context_key": "alerts",
                "title_de": "Mobile Push-Benachrichtigungen & Ruhezeiten einrichten 📲🔔",
                "title_en": "Setting up Mobile Push Notifications & Quiet Hours 📲🔔",
                "summary_de": "So aktivierst du Echtzeit-Alarme auf dem Sperrbildschirm deines Smartphones (iOS & Android) oder PCs und konfigurierst intelligente Ruhezeiten.",
                "summary_en": "How to enable real-time lockscreen alerts on your smartphone (iOS & Android) or PC and configure intelligent quiet hours.",
                "content_de": """# Mobile Push-Benachrichtigungen & Ruhezeiten 📲🔔

Mit Sharegy verpasst du keine kritischen Ereignisse in deinem Heimnetzwerk mehr. Erhalte wichtige Alarme direkt als **native Push-Benachrichtigung auf den Sperrbildschirm deines Smartphones (Apple iPhone & Android) oder PCs** – auch wenn die App vollständig geschlossen ist.

---

## 1. Was kann die Push-Engine?
* 🔋 **Speicher-Notreserve**: Sofortige Warnung, wenn dein Batteriespeicher unter die kritische Notstrom-Schwelle (z. B. 10%) fällt.
* 💧 **1 kW Nachtdauerlast-Leckagen**: Erkennt vergessene Großverbraucher (wie Sauna, Heizlüfter, Poolpumpe) zwischen 01:00 und 05:00 Uhr.
* ☀️ **PV-Ertragsausfälle**: Alarmierung bei strahlendem Sonnenschein, wenn der Wechselrichter unerwartet 0 W liefert.
* 📉 **Börsenstrom-Negativpreise**: Chancen-Hinweise bei negativen EPEX-Spotpreisen (Geld verdienen beim Verbrauch).
* 🔌 **Geräte-Offline-Watchdog**: Erkennt ausgefallene Smart Plugs oder Ingest-Störungen.

---

## 2. In 1 Klick auf deinem Gerät aktivieren

### Auf dem Smartphone (Apple iOS & Android):
1. Öffne Sharegy im mobilen Browser (z. B. **Safari auf dem iPhone** oder **Chrome/Firefox auf Android**).
   > *Tipp für iPhone (iOS 16.4+)*: Tippe unten auf **Teilen (Viereck mit Pfeil nach oben)** und wähle **„Zum Home-Bildschirm“**. Öffne Sharegy danach über das Home-Icon.
2. Gehe in Sharegy auf **👤 Profil** oder **🚨 Alarme** → *„📲 Push-Alarme einrichten“*.
3. Klicke auf den lila Button **`🔔 Push auf diesem Gerät aktivieren`**.
4. Bestätige den Browser-Dialog mit **„Erlauben“**.
5. Klicke auf **`⚡ Test-Push`** – die Nachricht poppt sofort auf deinem Sperrbildschirm auf!

### Auf dem PC / Laptop (Firefox, Chrome, Edge, Safari):
1. Klicke unter **👤 Profil** oder **🚨 Alarme** auf **`🔔 Push auf diesem Gerät aktivieren`**.
2. Erlaube Benachrichtigungen oben links in der Adressleiste deines Browsers.
3. Klicke auf **`⚡ Test-Push`** – die Windows-/Mac-Benachrichtigung erscheint sofort unten bzw. oben rechts.

---

## 3. Intelligente Ruhezeiten (Quiet Hours) konfigurieren
Du möchtest nachts nicht durch normale Hinweise geweckt werden?
* **Ruhezeiten aktivieren**: Lege feste Zeitfenster fest (z. B. von **22:00 bis 07:00 Uhr**).
* **Notfall-Override für kritische Alarme**: Ist dieser Schalter aktiv, werden lebenswichtige Alarme (z. B. Speicher-Tiefentladung, Frostschutz, Fehler im Hauptstromnetz) auch während der Ruhezeit zugestellt.
* **Kategorie-Filter**: Schalte gezielt einzelne Alarmkategorien (Batterie, Leckagen, PV-Ertrag, Strompreise, Gerätestatus) ein oder aus.
""",
                "content_en": """# Mobile Push Notifications & Quiet Hours 📲🔔

Stay informed about critical events in your smart energy home. Receive **real-time lockscreen alerts on your smartphone (Apple iPhone & Android) and desktop PC** even when the app is completely closed.

---

## 1. Key Push Alerts
* 🔋 **Battery Critical Reserve**: Instant warning when battery SoC drops below safe emergency reserves.
* 💧 **Night Baseload Leakages**: Detects forgotten heavy loads (e.g. sauna, space heater) between 1 AM and 5 AM.
* ☀️ **PV Yield Losses**: Notifies you on sunny days if an inverter unexpectedly outputs 0 W.
* 📉 **Negative Price Opportunities**: Alerts when dynamic spot prices turn negative.

---

## 2. 1-Click Device Activation
1. Navigate to **👤 Profile** or **🚨 Alerts** → *\"Setup Push Notifications\"*.
2. Click **`🔔 Enable Push on this Device`**.
3. Confirm the browser permission prompt with **\"Allow\"**.
4. Click **`⚡ Test-Push`** to verify delivery.

---

## 3. Quiet Hours & Emergency Overrides
* Set nighttime quiet hours (e.g. **22:00 to 07:00**).
* Enable the **Critical Emergency Override** to ensure severe battery or power alerts still come through.
""",
                "tags": ["push", "benachrichtigung", "alarme", "sperrbildschirm", "quiet hours", "ruhezeiten", "iphone", "android", "firefox", "vapid", "web-push"],
                "is_featured": True,
                "sort_order": 15,
            },
        ]


        for adata in articles_data:
            HelpArticle.objects.update_or_create(
                slug=adata["slug"],
                defaults=adata,
            )

        self.stdout.write(self.style.SUCCESS(f"Erfolgreich {len(categories_data)} Kategorien und {len(articles_data)} Handbuch-Artikel in DE & EN initialisiert!"))


