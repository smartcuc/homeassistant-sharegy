################################################
# support_desk/management/commands/seed_helpcenter.py
################################################

from django.core.management.base import BaseCommand
from support_desk.models import HelpCategory, HelpArticle


class Command(BaseCommand):
    help = "Befuellt das Hilfesystem und Wissensportal mit allen 9 Kategorien und vollstaendigen Handbuch-Artikeln auf Deutsch & Englisch."

    def handle(self, *args, **options):
        self.stdout.write("[INFO] Befuelle Hilfesystem & Wissensportal (DE & EN)...")

        # =========================================================================
        # 1. KATEGORIEN ANLEGEN / AKTUALISIEREN (9 KERNBEREICHE)
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
                "description_de": "Anbindung von Sungrow, Fronius, SolarEdge, Kostal, Growatt, Deye, Huawei, GoodWe, Solis, Victron und Speichern.",
                "description_en": "Setup guides for Sungrow, Fronius, SolarEdge, Kostal, Growatt, Deye, Huawei, GoodWe, Solis, Victron, and batteries.",
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
                "key": "grid-enwg",
                "icon": "🛡️",
                "title_de": "§ 14a EnWG, Steuerbox & Netzdienlichkeit",
                "title_en": "§ 14a EnWG Grid Regulation & SteuVE Control",
                "description_de": "Gesetzliche Pflichtdrosselung auf 4,2 kW, BNetzA-Summenleistungsmodell, Steuerbox-Kopplung (Relais/Modbus) und Netzentgelt-Reduktion.",
                "description_en": "Mandatory 4.2 kW grid dimming, BNetzA sum power formula, physical relay / Modbus connection, and grid fee discounts.",
                "sort_order": 5,
            },
            {
                "key": "tariffs",
                "icon": "⚡",
                "title_de": "Strompreise & Börsenstrom",
                "title_en": "Electricity Tariffs & Dynamic Pricing",
                "description_de": "Dynamische Tarife, Tibber API, Day-Ahead-Preise, Formeln und stichtagsgenaue Tarifhistorie.",
                "description_en": "Dynamic tariffs, Tibber API, spot market prices, pricing formulas, and historical rates.",
                "sort_order": 6,
            },
            {
                "key": "alerts",
                "icon": "🚨",
                "title_de": "Alarm- & Notifikationszentrale",
                "title_en": "Alert & Notification Center",
                "description_de": "Echtzeit-Regeln für Ertragsausfälle, Tiefentladeschutz, Dauerlasten und Spar-Chancen.",
                "description_en": "Real-time health rules for yield losses, battery protection, baseload alerts, and savings tips.",
                "sort_order": 7,
            },
            {
                "key": "billing",
                "icon": "🧾",
                "title_de": "Abrechnung, Mieterstrom & Energy Sharing",
                "title_en": "Billing, Sub-Metering & Energy Sharing",
                "description_de": "Virtuelle Zähler, § 42b EnWG 15m-Clearing, Kostenallokation für WEGs, PDF-Abrechnungen und EDIFACT MSCONS Export.",
                "description_en": "Virtual meters, § 42b EnWG 15-minute clearing, multi-tenant allocation, PDF invoices, and EDIFACT MSCONS export.",
                "sort_order": 8,
            },
            {
                "key": "devices-protocols",
                "icon": "🔌",
                "title_de": "Geräte, Schnittstellen & Protokolle",
                "title_en": "Devices, Interfaces & Protocols",
                "description_de": "Integration von OCPP 1.6-J CSMS, Home Assistant, Shelly WSS, wMSB Discovergy, Modbus TCP und Selbsttest.",
                "description_en": "Integration with OCPP 1.6-J CSMS, Home Assistant, Shelly WSS, wMSB Discovergy, Modbus TCP, and Self-Test.",
                "sort_order": 9,
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
            # 3. CLOUD INVERTER INTEGRATION GUIDE (10 HERSTELLER)
            # ---------------------------------------------------------------------
            {
                "category": cats["inverters-meters"],
                "slug": "wechselrichter-cloud-anbindung-anleitung",
                "context_key": "devices",
                "title_de": "Wechselrichter & Speicher Cloud-Kopplung (10 Hersteller im Direktvergleich)",
                "title_en": "Cloud Inverter & Battery Integration Guide (10 Manufacturers)",
                "summary_de": "Schritt-für-Schritt-Anleitung zur direkten Server-zu-Server Anbindung von Sungrow, Fronius, SolarEdge, Kostal, Growatt, Deye, Huawei, GoodWe, Solis und Victron.",
                "summary_en": "Step-by-step setup guide for connecting solar inverters and battery storage directly via cloud APIs without local hardware.",
                "content_de": """# Direkte Cloud-Kopplung für Wechselrichter & Speicher ☁️🔌

Mit der **Cloud-Kopplung** bindest du deinen Wechselrichter und Batteriespeicher direkt per Server-zu-Server API an Sharegy an – **ganz ohne zusätzliche Hardware vor Ort** (wie Raspberry Pi oder Smart Dongle).

---

## 1. Übersicht der 10 unterstützten Hersteller

| Hersteller | Unterstützte Modelle | Benötigte Zugangsdaten |
| :--- | :--- | :--- |
| **Sungrow** | SH5.0–SH25T Hybrid, SG-Serie, SBR-Speicher | `Anlagen-ID (ps_id)`, `E-Mail / Benutzer`, `Passwort`, `AppKey` |
| **Fronius** | GEN24 Plus, Symo, Primo, Tauro | `PV-System-ID`, `AccessKeyId`, `AccessKeyValue` |
| **SolarEdge** | SE-Serie, HD-Wave, StorEdge, Optimierer | `Standort-ID (site_id)`, `API-Schlüssel (api_key)` |
| **Kostal** | PLENTICORE plus, PIKO IQ, PIKO MP, BYD | `Anlagen-ID (plant_id)`, `API-Schlüssel (api_key)` |
| **Growatt** | MIN, MOD, MID, SPH, SPA, ARK-Speicher | `Anlagen-ID (plant_id)`, `OpenAPI Token` |
| **Deye** | SUN 3–12k Hybrid, Mikrowechselrichter | `AppID`, `AppSecret`, `E-Mail`, `Passwort`, `Geräte-SN` |
| **Huawei** | SUN2000 3–30KTL, LUNA2000 Speicher | `SystemCode`, `SecretKey`, `Anlagencode (Plant Code)` |
| **GoodWe** | ET, EH, BH, ES Hybrid, Lynx Home | `SEMS Account (E-Mail)`, `Passwort`, `PowerStation-ID` |
| **Solis** | Solis RHI, S5, S6 Hybrid | `Key-ID`, `Key-Secret`, `Station-ID` |
| **Victron** | MultiPlus-II, Quattro, Cerbo GX, SmartSolar | `VRM Personal Access Token`, `Site-ID (Installation-ID)` |

---

## 2. Einrichtung je Hersteller

### ☀️ Sungrow (iSolarCloud OpenAPI & OAuth)
1. Logge dich unter [isolarcloud.eu](https://www.isolarcloud.eu) ein.
2. In der Adresszeile deines Browsers findest du die **Power Station ID (`ps_id`)** (`...stationDetail?ps_id=1234567`).
3. Trage deine Zugangsdaten ein und klicke auf **„Verbindung testen“**.

### ☀️ Deye / SolarMAN Smart API
1. Registriere dich auf [open.solarmanpv.com](https://open.solarmanpv.com) oder nutze deinen SolarMAN Smart Account.
2. Trage `App ID`, `App Secret` und die Seriennummer (`Device SN`) deines Deye Wechselrichters ein.

### ☀️ Huawei FusionSolar OpenAPI
1. Öffne das [Huawei FusionSolar Portal](https://eu5.fusionsolar.huawei.com).
2. Erstelle unter *System ➔ Northbound API* einen Benutzer und trage deinen `Plant Code` ein.

### ☀️ Victron Energy VRM Portal
1. Öffne [vrm.victronenergy.com](https://vrm.victronenergy.com).
2. Erstelle unter *Preferences ➔ Personal Access Tokens* einen Token und kopiere deine *Site ID* aus der URL.
""",
                "content_en": """# Direct Cloud Integration for Inverters & Battery Storage ☁️🔌

Connect solar inverters and home batteries directly via server-to-server APIs – **no local hardware required**.

## Supported Manufacturers (10 Major Brands)
1. **Sungrow** (iSolarCloud OpenAPI)
2. **Fronius** (Solar.web API)
3. **SolarEdge** (Monitoring Portal API)
4. **Kostal** (Solar Portal API)
5. **Growatt** (ShineServer OpenAPI)
6. **Deye** (SolarMAN Smart API)
7. **Huawei** (FusionSolar OpenAPI)
8. **GoodWe** (SEMS Portal API)
9. **Solis** (SolisCloud OpenAPI)
10. **Victron Energy** (VRM Portal API)
""",
                "tags": ["cloud", "sungrow", "kostal", "solaredge", "fronius", "growatt", "deye", "huawei", "goodwe", "solis", "victron", "inverter"],
                "is_featured": True,
                "sort_order": 3,
            },

            # ---------------------------------------------------------------------
            # 4. § 14a EnWG: PFLICHTDIMMUNG & SUMMENLEISTUNGSMODELL
            # ---------------------------------------------------------------------
            {
                "category": cats["grid-enwg"],
                "slug": "paragraf-14a-enwg-pflichtdimmung-und-summenleistungsmodell",
                "context_key": "grid",
                "title_de": "§ 14a EnWG: Gesetzliche Drosselung auf 4,2 kW & das BNetzA-Summenleistungsmodell",
                "title_en": "§ 14a EnWG Grid Regulation: Mandatory 4.2 kW Dimming & Sum Power Model",
                "summary_de": "Vollständige Erklärung der BNetzA-Vorgabe (BK6-22-300) für steuerbare Verbraucher (Wallboxen, Wärmepumpen, Speicher) und wie Sharegy den Komfort durch Solar-Kompensation erhält.",
                "summary_en": "Complete guide to the German BNetzA § 14a EnWG regulation for controllable loads (EV chargers, heat pumps, batteries) and solar compensation.",
                "content_de": """# § 14a EnWG: Drosselung auf 4,2 kW & Summenleistungsmodell 🛡️⚡

Seit dem **1. Januar 2024** gilt in Deutschland die verbindliche Festlegung der Bundesnetzagentur (BNetzA BK6-22-300 / BK8-22/010-A) zur Integration steuerbarer Verbrauchseinrichtungen (**SteuVE**).

---

## 1. Welche Geräte fallen unter § 14a EnWG?
Alle neu installierten Großverbraucher mit einem netzwirksamen Leistungsbezug **über 4,2 kW**:
* 🚗 **Private Wallboxen / Ladesäulen** (11 kW oder 22 kW).
* ♨️ **Wärmepumpen** (inkl. Zusatzheizstab).
* 🔋 **Batteriespeicher mit Netzbezug** (z. B. netzgekoppeltes Laden).
* ❄️ **Klimageräte und Raumkühlung**.

---

## 2. Die Grundregel: *„Drosseln statt Abschalten!“*
Droht im lokalen Niederspannungsnetz eine Überlastung, darf der Verteilnetzbetreiber (VNB) die SteuVE temporär drosseln:
* 🛑 **Früher (Rundsteuerempfänger)**: Das Gerät wurde komplett hart abgeschaltet (0 kW).
* 🟢 **Heute (§ 14a EnWG)**: Jedem Haushalt steht ein **garantierter Mindestnetzbezug von 4,2 kW** zu.

---

## 3. Das dynamische BNetzA-Summenleistungsmodell in Sharegy

Sharegy implementiert das offizielle **Summenleistungs-Modell** der Bundesnetzagentur. Hierbei wird nicht jedes Einzelgerät starr abgeregelt, sondern die **Gesamtleistung am Netzübergabepunkt** bilanziert:

> 📐 **Formel für erlaubte SteuVE-Gesamtleistung:**  
> $$P_{\\text{Erlaubt}} = 4{,}2\\,\\text{kW (Netzkontingent)} + P_{\\text{PV}} + P_{\\text{Batt}} - P_{\\text{Grundlast}}$$

### 💡 Ein Praxis-Beispiel für maximalen Komfort:
1. Der Netzbetreiber aktiviert eine Drosselung auf **4,2 kW**.
2. Auf deinem Dach erzeugt die Solaranlage zeitgleich **5,0 kW** und dein Speicher liefert **2,0 kW**.
3. Deine Haushaltsgrundlast beträgt **0,5 kW**.
4. **Sharegy-Ergebnis**: Deine Wallbox darf mit **$4{,}2 + 5{,}0 + 2{,}0 - 0{,}5 = 10{,}7\\,\\text{kW}$** laden!
5. **Ergebnis**: Dein Elektroauto lädt mit voller Leistung weiter, ohne das öffentliche Stromnetz um auch nur 1 Watt zu überlasten.

---

## 4. Finanzielle Vorteile (Netzentgelt-Reduktion)
Für die Teilnahme an § 14a EnWG erhält der Anlagenbetreiber reduzierte Netzentgelte:
* **Modul 1 (Pauschaler Rabatt)**: Jährliche Gutschrift von ca. **120 bis 180 €** auf der Stromrechnung (bundeslandabhängig).
* **Modul 2 (Prozentualer Rabatt)**: Ca. 60 % Rabatt auf den Arbeitspreis der Netzentgelte für steuerbare Zähler.
* **Modul 3 (Zeitvariable Netzentgelte ab 2025/2026)**: Zusätzliche Einsparungen durch netzdienliches Laden in Schwachlastphasen.
""",
                "content_en": """# § 14a EnWG: Mandatory 4.2 kW Dimming & Sum Power Model 🛡️⚡

Since **January 1, 2024**, German energy law (BNetzA BK6-22-300) requires controllable consumer devices (**SteuVE > 4.2 kW**) to participate in dynamic grid dimming.

## 1. Affected Devices
* 🚗 **EV Wallboxes** (11 kW / 22 kW)
* ♨️ **Heat Pumps & Heating Rods**
* 🔋 **Home Batteries with Grid Charging**
* ❄️ **Air Conditioning Systems**

## 2. Dynamic Sum Power Model in Sharegy
Instead of shutting down devices, Sharegy calculates a dynamic power envelope:

> $$P_{\\text{Allowed}} = 4.2\\,\\text{kW (Grid Allowance)} + P_{\\text{PV}} + P_{\\text{Battery}} - P_{\\text{Baseload}}$$

If solar power is available, your EV charges at full 11 kW speed despite active grid dimming!
""",
                "tags": ["14a", "enwg", "steuve", "dimmung", "bnetza", "summenleistung", "steuerbox", "wallbox", "wärmepumpe", "netzentgelte"],
                "is_featured": True,
                "sort_order": 4,
            },

            # ---------------------------------------------------------------------
            # 5. STEUERBOX ANBINDUNG: RELAIS, MODBUS & CLOUD
            # ---------------------------------------------------------------------
            {
                "category": cats["grid-enwg"],
                "slug": "steuerbox-anbindung-relais-modbus-und-cloud",
                "context_key": "interfaces",
                "title_de": "VNB-Steuerbox Anbindung: Physische Relais (Shelly Pro / Modbus) vs. Cloud-API",
                "title_en": "Grid Operator Steuerbox: Physical Relays (Shelly Pro / Modbus) vs. Cloud API",
                "summary_de": "Wie das Signal des Netzbetreibers in den Zählerschrank gelangt und wie Sharegy Relais-Schaltungen oder REST-Webhooks verarbeitet.",
                "summary_en": "How grid operator dimming signals reach your meter cabinet via dry contacts (Shelly Pro/Modbus) or cloud REST APIs.",
                "content_de": """# VNB-Steuerbox Anbindung & Signalketten 🔌📟

Um ein Dimmsignal des Verteilnetzbetreibers (VNB) auszuführen, unterstützt Sharegy **zwei Übertragungswege**:

---

## Weg A: Digitaler Cloud-Webhook (Moderne SMGWs)
* Das Smart Meter Gateway (SMGW) oder der Messstellenbetreiber (z. B. Discovergy/inexogy) sendet den Dimmbefehl per verschlüsseltem HTTPS-Webhook direkt an Sharegy:
  > `POST https://sharegy.de/api/energy/grid/dimming/signal/`
* **Vorteil**: Keine zusätzliche Hardware im Zählerschrank erforderlich.

---

## Weg B: Physische FNN-Steuerbox mit Relais-Klemmen
Bei vielen Netzbetreibern wird neben dem Zähler eine physische **Steuerbox (CLS-Modul)** mit 4 potentialfreien Relais-Ausgängen (K1–K4) montiert:

### Schaltplan mit Shelly Pro auf der Hutschiene:
1. Montiere ein **Shelly Pro 4PM** oder **Shelly Plus 1** auf der DIN-Hutschiene im Zählerschrank.
2. Verbinde die Relais-Ausgänge der VNB-Steuerbox mit den Digitaleingängen (SW1–SW4) des Shellys.
3. Richte im Shelly den Outbound-WebSocket zu Sharegy ein:
   > `wss://sharegy.de/ws/energy/<DEIN_HAUSHALTS_TOKEN>/`
4. **Funktion**: Schließt der Netzbetreiber Relais K1 (Dimmung auf 4,2 kW), erkennt der Shelly die Flanke in unter 5 Millisekunden und Sharegy aktiviert das Dimm-Profil im EMS.
""",
                "content_en": """# Grid Operator Steuerbox Connection & Signals 🔌📟

Sharegy supports two pathways to ingest § 14a grid dimming signals:

## Pathway A: Cloud REST Webhooks
The Smart Meter Gateway (SMGW) posts directly to `POST /api/energy/grid/dimming/signal/`.

## Pathway B: Physical Dry Contact Relays (Shelly Pro / Modbus TCP)
Connect the dry contact relay outputs (K1-K4) of the VNB Steuerbox to the switch inputs of a DIN-rail **Shelly Pro 4PM** or Modbus TCP digital input module. Sharegy receives the state change over Outbound-WSS within 5 ms.
""",
                "tags": ["steuerbox", "cls", "relais", "shelly pro", "modbus", "fnn", "zählerschrank", "dimmsignal"],
                "is_featured": True,
                "sort_order": 5,
            },

            # ---------------------------------------------------------------------
            # 6. 1-KLICK HARDWARE SELBSTTEST & DIAGNOSE
            # ---------------------------------------------------------------------
            {
                "category": cats["devices-protocols"],
                "slug": "hardware-selbsttest-und-diagnose-assistent",
                "context_key": "devices",
                "title_de": "1-Klick Hardware-Selbsttest & Diagnose-Assistent (Onboarding)",
                "title_en": "1-Click Hardware Self-Test & Diagnostic Assistant",
                "summary_de": "Automatisierte 3-Phasen-Prüfung für Wechselrichter, Speicher und Wallboxen: Latenz-Check, Live-Telemetrie und Steuerkanal-Rücktest.",
                "summary_en": "Automated 3-phase verification for inverters, batteries, and wallboxes: Latency ping, live telemetry ingest, and control loop verification.",
                "content_de": """# 1-Klick Hardware-Selbsttest & Diagnose ⚡🩺

Der **1-Klick Hardware-Selbsttest** prüft neu gekoppelte oder bestehende Geräte in Sekundenschnelle auf Herz und Nieren.

---

## Die 3 Phasen der Diagnose

```
[ Phase 1: Verbindung & Latenz ] ➔ [ Phase 2: Live-Telemetrie ] ➔ [ Phase 3: Steuerkanal ] ➔ [ Diagnose-Zertifikat ]
```

1. **⚡ Phase 1: Verbindung & Latenz-Prüfung**
   - Prüft DNS-Auflösung, TLS-Handshake und Netzwerk-Roundtrip.
   - Ideal-Latenz: **< 100 ms** (grünes Badge).
2. **📊 Phase 2: Live-Telemetrie Ingestion**
   - Prüft, ob gültige Messwerte für Leistung (W), Netzspannung (V) und Ladestand (SoC %) ankommen.
   - Validiert die Plausibilität (z. B. keine negativen Hausverbräuche).
3. **🔄 Phase 3: Steuerungs-Rückkanal & Heartbeat**
   - Testet den bidirektionalen Steuerkanal (OCPP 1.6-J bei Wallboxen, OpenAPI bei Sungrow, WSS bei Shelly).

---

## Diagnose-Zertifikat & Health-Score
Nach Abschluss vergibt Sharegy einen **Health-Score (0–100 Punkte)** und empfiehlt bei Unregelmäßigkeiten konkrete Optimierungsschritte.
""",
                "content_en": """# 1-Click Hardware Self-Test & Diagnostics ⚡🩺

Run instant 3-phase diagnostics on any connected inverter, battery, wallbox, or smart plug:
1. **Connectivity & Latency**: Verifies TLS handshake and latency (< 100 ms).
2. **Telemetry Ingestion**: Validates real-time power (W), voltage (V), and SoC (%).
3. **Bidirectional Control**: Verifies OCPP and OpenAPI command dispatch.
""",
                "tags": ["selbsttest", "diagnose", "latenz", "health score", "telemetrie", "onboarding"],
                "is_featured": True,
                "sort_order": 6,
            },

            # ---------------------------------------------------------------------
            # 7. OCPP 1.6-J WALLBOX CSMS & SMART CHARGING
            # ---------------------------------------------------------------------
            {
                "category": cats["optimizer"],
                "slug": "ocpp-wallbox-anbindung-und-smart-charging",
                "context_key": "wallbox",
                "title_de": "OCPP 1.6-J CSMS Wallbox-Integration & Intelligente Lademodi",
                "title_en": "OCPP 1.6-J CSMS Wallbox Integration & Smart Charging Modes",
                "summary_de": "Anbindung jeder OCPP-konformen Wallbox (Easee, openWB, Webasto, Mennekes, Alfen) und Steuerung über die 5 intelligenten Lademodi.",
                "summary_en": "Connect any OCPP 1.6-J EV charger (Easee, openWB, Webasto, Mennekes, Alfen) with 5 automated smart charging algorithms.",
                "content_de": """# OCPP 1.6-J Wallbox-Integration & Smart Charging 🚗⚡

Sharegy verfügt über ein integriertes **OCPP 1.6-J Charging Station Management System (CSMS)**. Damit steuerst du jede standardkonforme Wallbox hardware-unabhängig.

---

## 1. Wallbox in 2 Minuten anbinden
1. Gehe in Sharegy auf **🔌 Geräte ➔ Wallbox hinzufügen**.
2. Vergib einen Namen und notiere dir die generierte **OCPP-Server-URL**:
   > `wss://sharegy.de/ocpp/<DEINE_CHARGE_POINT_ID>`
3. Öffne die Konfigurationsoberfläche deiner Wallbox (z. B. Easee, openWB, Webasto, Mennekes, Alfen, go-e) und trage diese URL als OCPP-Backend ein.
4. Sobald sich die Wallbox verbindet, erscheint sie sofort online mit Live-Ladeleistung!

---

## 2. Die 5 intelligenten Lademodi

* ☀️ **1. Nur Solarüberschuss (`pv_surplus`)**:
  - Lädt ausschließlich mit Strom vom eigenen Dach.
  - Pausiert automatisch bei Bewölkung und regelt den Ladestrom zwischen 6A und 16A/32A stufenlos nach.
* ⛅ **2. Min + PV-Überschuss (`min_pv`)**:
  - Garantiert eine Mindest-Ladeleistung (z. B. 6A 1-phasig) und schiebt jeden solaren Überschuss zusätzlich ins Auto.
* 💶 **3. Börsenpreisgeführt (`spot_price`)**:
  - Lädt nur, wenn der dynamische Börsenstrompreis (EPEX Spot) unter deiner eingestellten Preisschwelle (z. B. 15 ct/kWh) liegt.
* ⚡ **4. Sofortladen (`instant`)**:
  - Lädt sofort mit maximaler Ladeleistung (z. B. 11 kW oder 22 kW), unabhängig von Sonne oder Strompreis.
* 🛑 **5. Gesperrt (`off`)**:
  - Verriegelt die Wallbox gegen unbefugte Nutzung.
""",
                "content_en": """# OCPP 1.6-J EV Wallbox CSMS & Smart Charging 🚗⚡

Sharegy operates a built-in OCPP 1.6-J CSMS gateway compatible with any open wallbox (Easee, openWB, Webasto, Mennekes, Alfen, go-e).

## 5 Intelligent Charging Modes
1. ☀️ **Pure Solar Surplus** (`pv_surplus`)
2. ⛅ **Min + Solar Surplus** (`min_pv`)
3. 💶 **Dynamic Spot Price Guided** (`spot_price`)
4. ⚡ **Instant Fast Charge** (`instant`)
5. 🛑 **Locked / Paused** (`off`)
""",
                "tags": ["wallbox", "ocpp", "csms", "smart charging", "überschussladen", "eauto", "easee", "openwb"],
                "is_featured": True,
                "sort_order": 7,
            },

            # ---------------------------------------------------------------------
            # 8. wMSB SMART METER (DISCOVERGY / INEXOGY / SOLANDEO)
            # ---------------------------------------------------------------------
            {
                "category": cats["devices-protocols"],
                "slug": "discovergy-inexogy-solandeo-wmsb-smart-meter",
                "context_key": "devices",
                "title_de": "wMSB Smart Meter Gateway Anbindung (Discovergy, inexogy, Solandeo)",
                "title_en": "wMSB Smart Meter Gateway Integration (Discovergy, inexogy, Solandeo)",
                "summary_de": "Automatische Synchronisation von 15-Minuten RLM/SLP-Zählerzeitreihen (OBIS 1.8.0 / 2.8.0) für § 42b EnWG Energy Sharing.",
                "summary_en": "Automated synchronization of 15-minute interval readings (OBIS 1.8.0 / 2.8.0) for § 42b EnWG energy sharing.",
                "content_de": """# wMSB Smart Meter Gateway Anbindung 📟⚡

Wettbewerbliche Messstellenbetreiber (**wMSB**) wie **Discovergy, inexogy und Solandeo** erfassen Zählerdaten hochpräzise im 15-Minuten-Takt.

---

## 1. Warum ist ein wMSB ideal für Sharegy?
* 🎯 **15-Minuten-Intervallmessung**: Pflichtvoraussetzung für gesetzliches Energy Sharing nach § 42b EnWG.
* 🔄 **Zwei-Richtungs-Zählung**: Exakte Erfassung von Netzbezug (OBIS `1.8.0`) und Netzeinspeisung (OBIS `2.8.0`).
* ☁️ **Direkte REST-Schnittstelle**: Sharegy ruft Zählerstände und 15-Minuten-Lastgänge automatisch per API ab.

---

## 2. Einrichtung
1. Trage deine wMSB-Zugangsdaten (E-Mail, Passwort und Zähler-ID) in Sharegy ein.
2. Der Hintergrund-Worker synchronisiert alle 15 Minuten die validierten Lastprofile.
""",
                "content_en": """# wMSB Smart Meter Gateway Integration 📟⚡

Discovergy, inexogy, and Solandeo provide 15-minute certified smart meter data (OBIS 1.8.0 / 2.8.0) required for legal § 42b EnWG Energy Sharing.
""",
                "tags": ["discovergy", "inexogy", "solandeo", "wmsb", "smart meter", "15m", "obis"],
                "is_featured": True,
                "sort_order": 8,
            },

            # ---------------------------------------------------------------------
            # 9. ENERGY SHARING & CLEARING (§ 42b EnWG)
            # ---------------------------------------------------------------------
            {
                "category": cats["billing"],
                "slug": "energy-sharing-und-quartiers-clearing-nach-enwg-42b",
                "context_key": "billing",
                "title_de": "Energy Sharing & Quartiers-Clearing gem. § 42b EnWG",
                "title_en": "Energy Sharing & Neighborhood Clearing per § 42b EnWG",
                "summary_de": "Revisionssichere 15-Minuten-Bilanzierung zwischen Erzeugern und Verbrauchern in Quartieren, PDF-Rechnungslegung und BNetzA MSCONS EDIFACT.",
                "summary_en": "Compliant 15-minute interval energy sharing between producers and consumers in local communities with PDF & EDIFACT exports.",
                "content_de": """# Energy Sharing & Quartiers-Clearing (§ 42b EnWG) 🏘️⚡

Mit Sharegy können Nachbarschaften, Mehrfamilienhäuser (WEGs) und Gewerbequartiere ihren lokal erzeugten Solarstrom **gemeinsam nutzen, kilowattstundengenau aufteilen und abrechnen**.

---

## 1. Das 15-Minuten-Clearing-Verfahren
Alle 15 Minuten führt die Sharegy Clearing-Engine ein mathematisches Matching durch:
1. **Erzeugungsüberschuss**: Wie viel Solarstrom speisen die Prosumer des Quartiers in diesem 15m-Slot ein?
2. **Verbraucherbedarf**: Welche Nachbarn verbrauchen zeitgleich Strom?
3. **Quartierspreis**: Der geteilte Strom wird zum vereinbarten Community-Tarif (z. B. 16 ct/kWh) verrechnet – günstiger als Netzstrom, aber lukrativer als die EEG-Einspeisevergütung!

---

## 2. Revisionssichere Abrechnungen & Exporte
* 📄 **PDF-Monatsabrechnungen**: Aufgeschlüsselt nach Tagen und 15m-Slots.
* 📊 **Excel-Formate mit Formeln**: Transparente mathematische Nachvollziehbarkeit.
* 📁 **BNetzA MSCONS EDIFACT (D:04B)**: Offizielles Marktkommunikations-Format für Netzbetreiber und Energieversorger.
""",
                "content_en": """# Energy Sharing & Neighborhood Clearing (§ 42b EnWG) 🏘️⚡

Sharegy enables renewable energy communities and multi-tenant buildings to share local solar power with compliant 15-minute interval clearing, monthly PDF invoices, and BNetzA MSCONS EDIFACT exports.
""",
                "tags": ["energy sharing", "42b", "enwg", "clearing", "quartier", "mieterstrom", "edifact", "mscons"],
                "is_featured": True,
                "sort_order": 9,
            },

            # ---------------------------------------------------------------------
            # 10. HOME ASSISTANT CUSTOM COMPONENT
            # ---------------------------------------------------------------------
            {
                "category": cats["devices-protocols"],
                "slug": "home-assistant-integration-guide",
                "context_key": "devices",
                "title_de": "Offizielle Home Assistant Integration für Sharegy Cloud",
                "title_en": "Official Home Assistant Integration for Sharegy Cloud",
                "summary_de": "So bindest du Home Assistant über die offizielle Custom Component per verschlüsseltem Outbound-WebSocket (WSS) an.",
                "summary_en": "Step-by-step setup for streaming local smart home sensors to Sharegy Cloud using the official Home Assistant custom component.",
                "content_de": """# Sharegy Home Assistant Integration ⚡🏠

Die offizielle **Sharegy Home Assistant Integration** streamt alle Sensoren deines Haushalts verschlüsselt und in Echtzeit in die Sharegy Cloud.

## Highlights
* **Entity Picker**: Wähle deine Zähler, Wechselrichter, Wallboxen und Smart Plugs direkt in der Home Assistant UI aus.
* **Outbound-WSS**: Port 443, keine offenen Router-Ports erforderlich.
* **48h Offline-Puffer**: Bei Internetausfall werden Messdaten lokal zwischengespeichert.
""",
                "content_en": """# Sharegy Home Assistant Integration ⚡🏠

Stream your local smart home telemetry to Sharegy Cloud over secure Outbound WebSockets with zero firewall changes and 48h offline buffering.
""",
                "tags": ["homeassistant", "custom component", "hacs", "websocket", "shelly"],
                "is_featured": True,
                "sort_order": 10,
            },

            # ---------------------------------------------------------------------
            # 11. SHELLY WSS & RELAIS-AKTORIK
            # ---------------------------------------------------------------------
            {
                "category": cats["devices-protocols"],
                "slug": "shelly-wss-und-relais-steuerung",
                "context_key": "interfaces",
                "title_de": "Shelly Outbound WebSocket & Bidirektionale Relais-Steuerung",
                "title_en": "Shelly Outbound WebSocket & Bidirectional Relay Actuation",
                "summary_de": "Einrichtung von Shelly Gen2/Gen3/Pro Relais per Outbound WSS (Port 443) und Live-Schaltung von Verbrauchern direkt im Dashboard.",
                "summary_en": "Setting up Shelly Gen2/Gen3/Pro devices via Outbound WSS (Port 443) and live consumer actuation directly from the dashboard.",
                "content_de": """# Shelly Outbound WebSocket & Relais-Aktorik 🔌⚡

Sharegy unterstützt die direkte Steuerung von **Shelly Plus, Pro und Gen3** Geräten über Outbound-WebSockets.

## Einrichtung
1. Öffne das Webinterface deines Shelly.
2. Navigiere zu **Settings ➔ Outbound WebSocket**.
3. Trage deine Sharegy-URL ein: `wss://sharegy.de/ws/energy/<TOKEN>/`
4. Speichern – das Gerät schaltet ab sofort live im Dashboard!
""",
                "content_en": """# Shelly Outbound WebSocket & Bidirectional Relay Actuation 🔌⚡

Native bidirectional actuation for Shelly Gen2, Gen3, and Pro series devices over Outbound WebSockets.
""",
                "tags": ["shelly", "wss", "relais", "schalten", "smart plug"],
                "is_featured": True,
                "sort_order": 11,
            },

            # ---------------------------------------------------------------------
            # 12. PUSH NOTIFICATIONS & QUIET HOURS
            # ---------------------------------------------------------------------
            {
                "category": cats["alerts"],
                "slug": "mobile-push-notifications",
                "context_key": "alerts",
                "title_de": "Mobile Push-Benachrichtigungen & Ruhezeiten einrichten 📲🔔",
                "title_en": "Setting up Mobile Push Notifications & Quiet Hours 📲🔔",
                "summary_de": "So aktivierst du Echtzeit-Alarme auf dem Sperrbildschirm deines Smartphones (iOS & Android) oder PCs.",
                "summary_en": "How to enable real-time lockscreen alerts on your smartphone (iOS & Android) or PC and configure quiet hours.",
                "content_de": """# Mobile Push-Benachrichtigungen & Ruhezeiten 📲🔔

Erhalte wichtige Alarme direkt auf deinen Sperrbildschirm (iOS & Android) oder PC – auch bei geschlossener App.

## Features
* 🔋 **Batterie-Notreserve Warnung**
* 💧 **Nachtdauerlast-Leckagen (1 kW+)**
* ☀️ **PV-Ertragsausfall bei Sonnenschein**
* 🌙 **Konfigurierbare Ruhezeiten mit Notfall-Override**
""",
                "content_en": """# Mobile Push Notifications & Quiet Hours 📲🔔

Real-time lockscreen alerts for battery reserves, baseload leakages, and PV yields with configurable quiet hours.
""",
                "tags": ["push", "benachrichtigung", "alarme", "sperrbildschirm", "quiet hours"],
                "is_featured": True,
                "sort_order": 12,
            },

            # ---------------------------------------------------------------------
            # 13. SMART LOAD MANAGEMENT & DISPATCH HUB
            # ---------------------------------------------------------------------
            {
                "category": cats["optimizer"],
                "slug": "smart-load-management-und-dispatch-hub",
                "context_key": "control",
                "title_de": "Smart Load Management & Dispatch-Zentrale (/app/control) 🎛️⚡",
                "title_en": "Smart Load Management & Dispatch Hub (/app/control) 🎛️⚡",
                "summary_de": "Leitfaden für die Lastmanagement-Zentrale: Prioritäten-Kaskade (Merit-Order), Master-Modi (Autopilot, Nur Solar, Sparfuchs) und 24h-Fahrplan.",
                "summary_en": "Comprehensive guide for the Load Management Hub: Priority Cascade (Merit-Order), Master Autopilot modes, and 24h schedule preview.",
                "content_de": r"""# Smart Load Management & Dispatch Hub 🎛️⚡

Der **Smart Load Management & Dispatch Hub** auf `/app/control` ist die zentrale Steuerungszentrale für alle flexiblen Verbraucher und Speicher deines Haushalts.

---

## 1. Die 4 Master-Autopilot-Modi

Wähle in der Steuerungsleiste den gewünschten Betriebsmodus:
* 🤖 **Smart Autopilot**: Maximiert vollautomatisch die Eigenverbrauchsquote und optimiert Speicher und flexible Lasten basierend auf Solarprognose und stündlichen dynamischen Strompreisen (EPEX Spot).
* ☀️ **Nur PV-Überschuss**: Verbraucher und Heimspeicher werden ausschließlich aktiviert, wenn solarer Überschuss eingespeist werden würde ($P_\text{grid} < 0\,\text{W}$). Netzbezug für flexible Lasten wird strikt vermieden.
* 💰 **Preise-Optimiert**: Nutzt gezielt günstige und negative Strompreis-Phasen an der Strombörse zur Aufladung von Speicher und thermischen Speichern.
* 🛑 **Manuell**: Die automatische Zuteilung ist pausiert. Alle Verbraucher können direkt per Hand geschaltet werden.

---

## 2. Die Prioritäten-Kaskade (Merit-Order)

Wenn die Sonne scheint, reicht der Überschuss nicht immer für alle Verbraucher gleichzeitig. Über die **Prioritäten-Kaskade** legst du per Klick die Zuteilungs-Reihenfolge fest:

```
[ 1. 🔋 Heimspeicher ] ➔ [ 2. ♨️ BWWP ] ➔ [ 3. 🚗 Wallbox ] ➔ [ 4. 🏊 Poolpumpe ] ➔ [ 5. ❄️ Klima ] ➔ [ 6. 🧺 Haushalt ]
```

* **Beispiel**: Zuerst wird der Heimspeicher bis zur Reserve (z. B. 80%) geladen. Danach fließt der Überschuss in die Brauchwasserwärmepumpe (Boost auf 60°C). Reicht der Strom weiterhin, starten Wallbox und Poolfilterung.

---

## 3. Die 7 modularen Verbraucher-Kategorien

1. ♨️ **Brauchwasserwärmepumpe (BWWP) & Wärmepumpe**: SG-Ready Schaltung (State 2 / State 3 Boost bis 60°C) mit integriertem Verdichter- und Taktschutz.
2. 🚗 **Wallbox & E-Auto**: Überschussladen (Min+PV), Börsenpreis-Laden und 1-Klick-Schnellladung.
3. 🔋 **Heimspeicher**: Arbitrage & automatisches Grid-Charging bei negativen Strompreisen.
4. 🏊 **Poolpumpen & Filter**: Garantiert tägliche Mindestlaufzeit (z. B. 5 Stunden) exakt in den Sonnenstunden (Peak-Shaving).
5. ❄️ **Klimaanlagen (Pre-Cooling)**: Kühlt das Haus bei sommerlichen PV-Spitzenzeiten 1,5°C vor, um teuren Abendstrom einzusparen.
6. 🧺 **Haushaltsgeräte (Smart Plugs)**: „Ready-to-Start“ Scharfschaltung für Waschmaschine und Geschirrspüler.
7. ⚡ **Heizstäbe (Power-to-Heat)**: Stufenlose Pufferladung zur vollständigen Überschussverwertung vor der Netzeinspeisung.

---

## 4. Der 24h-Fahrplan (Dispatch-Timeline)

Die horizontale Fahrplan-Vorschau visualisiert für jede Stunde des Tages:
* Erwartete PV-Erzeugung (kW) und dynamischer Strompreis.
* Welche Geräte voraussichtlich mit kostenlosem Solarstrom oder Tiefstpreisen betrieben werden.
""",
                "content_en": r"""# Smart Load Management & Dispatch Hub 🎛️⚡

The **Smart Load Management & Dispatch Hub** on `/app/control` serves as the central orchestration engine for your home's flexible energy assets.

## Key Features
* 📊 **Live Power Budget & Master Autopilot Modes** (Autopilot, Solar Only, Price Saver, Manual)
* 🥇 **Interactive Priority Cascade (Merit-Order)** for solar surplus allocation.
* 📅 **24h Dispatch Schedule & Timeline** merging solar forecasts with dynamic spot prices.
* 🎛️ **Modular Load Controllers** for Heat Pumps/DHW, EV Chargers, Home Batteries, Pool Pumps, AC Pre-Cooling, Smart Plugs, and Heating Rods.
""",
                "tags": ["lastmanagement", "dispatch", "prioritäten", "merit order", "bwwp", "wallbox", "pool", "klima", "autopilot"],
                "is_featured": True,
                "sort_order": 13,
            },

            # ---------------------------------------------------------------------
            # 14. BWWP & SG-READY HEAT PUMP CONTROL
            # ---------------------------------------------------------------------
            {
                "category": cats["optimizer"],
                "slug": "brauchwasserwaermepumpe-bwwp-und-sg-ready",
                "context_key": "bwwp",
                "title_de": "BWWP & Wärmepumpen-Lastmanagement: SG-Ready & Verdichterschutz ♨️🛡️",
                "title_en": "DHW Heat Pump (BWWP) Load Management: SG-Ready & Compressor Safety ♨️🛡️",
                "summary_de": "Funktionsweise des BWWP-Lastmanagements mit SG-Ready Kontakt, Temperaturgrenzen, Solar-Boost und Verdichter-Schutzzeiten gegen Takten.",
                "summary_en": "Domestic Hot Water Heat Pump control with SG-Ready relays, temperature thresholds, solar boost, and anti-cycling compressor protection.",
                "content_de": r"""# BWWP & Wärmepumpen-Lastmanagement (SG-Ready) ♨️🛡️

Brauchwasserwärmepumpen (**BWWP**) und Heizungs-Wärmepumpen bieten durch ihren Wasserspeicher eine hervorragende thermische Speicherkapazität. Sharegy steuert diese Geräte vollautomatisch über SG-Ready Kontakte (Relais / Shelly / ioBroker / Home Assistant).

---

## 1. Die SG-Ready Betriebszustände

Sharegy bildet die genormten SG-Ready Stufen ab:
* ⚪ **Zustand 1 (Sperre / Standby)**: EVU-Sperre oder absoluter Überhitzungsschutz ($T \ge 65^\circ\text{C}$).
* 🟡 **Zustand 2 (Normalbetrieb)**: Standardbetrieb nach internem Thermostat der Wärmepumpe ($T_{soll} \approx 52^\circ\text{C}$).
* 🟢 **Zustand 3 (SG-Ready Boost / Verstärkter Betrieb)**: Relais schließt bei PV-Überschuss ($\ge 800\,\text{W}$) oder Börsen-Tiefstpreisen. Die Wärmepumpe heizt den Speicher auf **$60^\circ\text{C}$ (Boost-Temperatur)** als thermische Batterie auf.
* 🔥 **Zustand 4 (Zwangsanlauf / Komfort-Sicherung)**: Fällt die Wassertemperatur unter die Mindestgrenze ($T < 45^\circ\text{C}$), erzwingt Sharegy das Heizen zur Warmwasser- und Legionellengarantie.

---

## 2. Verdichter- & Taktschutz (Anti-Cycling)

Zum Schutz des Wärmepumpen-Verdichters vor vorzeitigem Verschleiß erzwingt Sharegy zwei essenzielle Schutzzeiten:
1. 🔒 **Mindestlaufzeit (Standard: 20 Minuten)**: Wurde die BWWP eingeschaltet, bleibt sie mindestens 20 Minuten aktiv – selbst wenn vorübergehend eine Wolke über die PV-Anlage zieht.
2. ⏳ **Mindestruhezeit (Standard: 15 Minuten)**: Nach dem Abschalten bleibt das Relais mindestens 15 Minuten geöffnet, um schädliches Takten zu verhindern.

---

## 3. Anbindung über ioBroker & Home Assistant

Verbinde dein BWWP-Schaltrelais (z. B. Shelly Plus 1 / Shelly Pro 1PM oder HomeMatic-Schaltaktor):
* **ioBroker**: Wähle im Sharegy-Adapter das zusammengestellte BWWP-Gerät aus (Leistung, Temperatur und SG-Schaltkontakt).
* **Home Assistant**: Nutze das integrierte **BWWP-Gerätebündel** im Setup Flow.
* **Geschlossener Regelkreis**: Sobald Sharegy den Boost-Befehl sendet, schaltet das Relais in Millisekunden per Outbound-WebSocket.
""",
                "content_en": r"""# DHW Heat Pump (BWWP) & SG-Ready Load Management ♨️🛡️

Domestic Hot Water (DHW) heat pumps represent ideal thermal batteries. Sharegy actuates SG-Ready relays via ioBroker, Home Assistant, and Shelly WSS.

## Core Mechanisms
* 🌡️ **Temperature Limits**: Min Comfort (45°C), Standard Target (52°C), Solar Boost (60°C), Safety Lock (65°C).
* 🔒 **Compressor Protection**: Minimum 20-minute runtime and 15-minute cooldown between cycles to eliminate short-cycling.
* 🔄 **Closed-Loop Actuation**: Real-time state synchronization over Outbound WebSockets.
""",
                "tags": ["bwwp", "wärmepumpe", "sg-ready", "verdichterschutz", "brauchwasser", "boost", "temperaturen"],
                "is_featured": True,
                "sort_order": 14,
            },

            # ---------------------------------------------------------------------
            # 15. IOBROKER ADAPTER INTEGRATION
            # ---------------------------------------------------------------------
            {
                "category": cats["devices-protocols"],
                "slug": "iobroker-sharegy-adapter-guide",
                "context_key": "interfaces",
                "title_de": "Offizieller ioBroker Adapter für Sharegy Cloud (ioBroker.sharegy) 📡🟢",
                "title_en": "Official ioBroker Adapter for Sharegy Cloud (ioBroker.sharegy) 📡🟢",
                "summary_de": "Einrichtung des nativen ioBroker-Adapters mit verschlüsseltem WebSocket-Stream, Telemetrie-Mapping, BWWP-Bündelung und bidirektionaler Relais-Schaltung.",
                "summary_en": "Step-by-step setup for ioBroker.sharegy with encrypted Outbound WebSocket streaming, multi-sensor bundling, and closed-loop relay control.",
                "content_de": r"""# Offizieller ioBroker Adapter (ioBroker.sharegy) 📡🟢

Der offizielle **ioBroker Adapter** verbindet deine lokale ioBroker-Installation verschlüsselt und in Echtzeit mit der Sharegy Cloud.

---

## 1. Installation & Konfiguration
1. Installiere den Adapter `iobroker.sharegy` aus dem offiziellen Repository.
2. Kopiere deine persönliche **WSS-Server-Adresse** aus Sharegy unter **⚙️ Einstellungen ➔ Schnittstellen**.
3. Füge die URL im ioBroker-Instanz-Setup ein (Token wird automatisch erkannt).
4. Speichern – der Adapter baut sofort eine sichere TLS-Verbindung über Port 443 auf.

---

## 2. Multi-Sensor Gerätebündelung (z. B. BWWP)
Im ioBroker-Adapter kannst du verschiedene Datenpunkte einem logischen Gerät zuordnen:
* **Leistungssensor**: Wirkleistung (W)
* **Temperatursensor**: Wassertemperatur (°C)
* **Schaltzustand & Aktorik**: SG-Ready Schalter / Shelly-Relais

---

## 3. Bidirektionaler Closed-Loop Rückkanal
Sobald Sharegy einen Steuerbefehl (z. B. BWWP-Boost oder Lastabwurf) an ioBroker sendet, wird das lokale Relais betätigt und der bestätigte Schaltzustand sofort an das Sharegy Dashboard zurückgemeldet.
""",
                "content_en": r"""# Official ioBroker Adapter (ioBroker.sharegy) 📡🟢

The official **ioBroker.sharegy** adapter streams local telemetry and accepts bidirectional actuation commands from Sharegy Cloud over secure WebSockets.
""",
                "tags": ["iobroker", "adapter", "websocket", "bwwp", "relais", "telemetrie"],
                "is_featured": True,
                "sort_order": 15,
            },
            # ---------------------------------------------------------------------
            # 16. SHELLY NON-CLOUD & LOKALE ANBINDUNG
            # ---------------------------------------------------------------------
            {
                "category": cats["devices-protocols"],
                "slug": "shelly-local-non-cloud-guide",
                "context_key": "interfaces",
                "title_de": "Shelly ohne Cloud einrichten: 100% lokal, kostenlos & datensparsam 🔌🛡️",
                "title_en": "Setup Shelly without Cloud: 100% local, free & privacy-first 🔌🛡️",
                "summary_de": "Schritt-für-Schritt-Anleitung zur Anbindung von Shelly Plus 1PM, Pro 3EM, Plugs und Gen3 über Outbound-WebSocket (WSS) oder lokales RPC ohne kostenpflichtiges Cloud-Abo.",
                "summary_en": "Step-by-step setup guide for connecting Shelly Gen2/Gen3/Pro devices via Outbound-WebSocket (WSS) or local RPC without any paid cloud subscription.",
                "content_de": r"""# Shelly ohne Cloud einrichten: 100% lokal, kostenlos & sicher 🔌🛡️

Du benötigst **kein kostenpflichtiges Shelly Cloud-Abo**. Sharegy unterstützt die direkte, verschlüsselte Outbound-WebSocket (WSS) Verbindung deiner Shelly-Geräte – **100% kostenlos und mit < 50 ms Live-Reaktionszeit**.

---

## 1. Vorteile der lokalen WSS-Verbindung
* **0,00 € dauerhaft**: Kein Cloud-Abonnement erforderlich.
* **Echtzeit-Telemetrie**: Live-Werte alle 1–2 Sekunden für exaktes Smart-Charging und SG-Ready Wärmepumpensteuerung.
* **Keine Portweiterleitung (NAT)**: Der Shelly baut die Verbindung verschlüsselt von innen nach außen über Port 443 auf.

---

## 2. In 3 Schritten einrichten (Shelly Plus 1PM, Pro 3EM, Gen3, Plugs)
1. **Shelly Weboberfläche öffnen**: Gib die IP-Adresse deines Shelly im Browser ein (z. B. `http://192.168.178.50`).
2. **Outbound WebSocket aktivieren**: Navigiere zu **Settings ➔ Outbound WebSocket** (oder *Network & Connectivity*).
3. **WSS-Server URL eintragen**:
   * Setze das Häkchen bei **Enable**.
   * Wähle **SSL/TLS (WSS)**.
   * Trage deine persönliche Sharegy WSS-Adresse ein:
     `wss://sharegy.de/ws/energy/<DEIN_HOME_TOKEN>/`
   * Klicke auf **Save Settings**.

---

## 3. Fertig!
Der Shelly verbindet sich sofort mit Sharegy und erscheint automatisch unter **Geräte** und im **Dashboard**.
""",
                "content_en": r"""# Setup Shelly without Cloud: 100% local, free & secure 🔌🛡️

You do not need a paid Shelly Cloud subscription. Sharegy supports direct, encrypted Outbound-WebSocket (WSS) connections with sub-50ms latency.

1. Open your Shelly device web interface by entering its IP address in your browser.
2. Navigate to **Settings ➔ Outbound WebSocket**.
3. Enable WebSocket, choose SSL/TLS, enter `wss://sharegy.de/ws/energy/<YOUR_TOKEN>/` and click Save.
""",
                "tags": ["shelly", "websocket", "local", "non-cloud", "pro3em", "plus1pm", "kostenlos"],
                "is_featured": True,
                "sort_order": 16,
            },
            # ---------------------------------------------------------------------
            # ALERTS & NOTIFICATIONS: SYSTEMBERICHTE & BENACHRICHTIGUNGEN
            # ---------------------------------------------------------------------
            {
                "category": cats["alerts"],
                "slug": "benachrichtigungen-und-systemberichte",
                "context_key": "notifications",
                "title_de": "E-Mail-Zusammenfassungen, Systemberichte & Push-Benachrichtigungen",
                "title_en": "Email Digests, System Reports & Push Notifications",
                "summary_de": "Wöchentlicher Energie- & Autarkie-Report (jeden Montag 08:00 Uhr lokaler Benutzerzeit), Echtzeit-Warnungen bei Hardwareausfall und Push-Ruhezeiten konfigurieren.",
                "summary_en": "Weekly energy & autarky digest (every Monday 08:00 user local time), real-time critical hardware failure alerts, and push quiet hours.",
                "content_de": """# E-Mail-Zusammenfassungen, Systemberichte & Benachrichtigungen 📧⚡

Sharegy hält dich über den Zustand deiner Energieanlagen, wöchentliche Einsparungen und kritische Hardware-Ereignisse auf dem Laufenden – wahlweise per **E-Mail**, **Browser-Push** oder **Mobile Notification**.

---

## 1. Wöchentlicher Energie- & Autarkie-Report 📊

Der wöchentliche Report fasst deine wichtigsten Energiekennzahlen der vergangenen 7 Tage übersichtlich zusammen:

* ☀️ **PV-Erzeugung (kWh)**: Wie viel Solarstrom hat deine PV-Anlage in der letzten Woche erzeugt?
* 🔄 **Eigenverbrauch (kWh)**: Wie viel deines Solarstroms wurde direkt im Haushalt, in der Batterie oder im E-Auto verbraucht?
* 🛡️ **Autarkiegrad (%)**: Wie unabhängig warst du vom öffentlichen Stromnetz?
* 💰 **Erzielte Ersparnis (€)**: Berechnete finanzielle Einsparung durch Eigenverbrauch und Netzeinspeisung.
* ⚡ **Netzeinspeisung & Netzbezug**: Genaue Zählerbilanz im Vergleich.

### ⏰ Versandzeitpunkt & Zeitzone
> **Versand jeden Montag um 08:00 Uhr:**  
> Der Versand erfolgt pünktlich zum Start der neuen Woche um **08:00 Uhr in deiner persönlichen Benutzer-Zeitzone** (standardmäßig deutsche Zeit `Europe/Berlin` bzw. MEZ/MESZ).  
> Hast du in deinen Profileinstellungen eine abweichende Zeitzone (z. B. `Europe/Warsaw` oder `UTC`) gewählt, richtet sich der Versand nach deiner eingestellten Ortszeit.

### 🌍 Mehrsprachigkeit
Die E-Mail wird automatisch in deiner im Profil eingestellten Sprache versendet (**Deutsch**, **Englisch** oder **Polnisch**).

---

## 2. Kritische Hardware-Warnungen (Sofort / Echtzeit) 🚨

Bei schwerwiegenden Störungen deiner Energiehardware erhältst du sofort eine Benachrichtigung per E-Mail und Push, um Ertragsausfälle oder Schäden abzuwenden:

* **Wechselrichter Offline / Ertragsausfall**: Die Sonne scheint, aber der Wechselrichter meldet keine Erzeugung (z. B. ausgelöster DC-Schalter oder FI-Sicherung).
* **Batterie-Tiefentladung**: Der Ladestand (SoC) ist unter das kritische Notfall-Limit gefallen.
* **Kommunikationsabbruch**: Smart Meter oder Wechselrichter senden seit mehr als 15 Minuten keine Telemetriedaten.

Jede Notfall-Meldung enthält den genauen Gerätenamen, die Fehlerursache und **konkrete Sofortmaßnahmen zur Behebung** sowie einen Direktlink ins System.

---

## 3. Push-Benachrichtigungen & Ruhezeiten (Quiet Hours) 🔔

Über die Push-Zentrale kannst du Desktop- und Smartphone-Benachrichtigungen aktivieren. Um in der Nacht nicht gestört zu werden, kannst du **Ruhezeiten** definieren (z. B. 22:00 bis 07:00 Uhr). In dieser Zeit werden unkritische Mitteilungen stummgeschaltet.

---

## 4. Wie aktiviere oder deaktiviere ich Benachrichtigungen?

1. Klicke oben rechts auf dein **Profilbild** und wähle den Tab **Benachrichtigungen & Alarme**.
2. Unter **„E-Mail-Zusammenfassungen & Systemberichte“** kannst du den wöchentlichen Report sowie kritische Hardware-Warnungen mit einem Klick aktivieren oder deaktivieren.
3. Deine Auswahl wird sofort sicher gespeichert.
""",
                "content_en": """# Email Digests, System Reports & Notifications 📧⚡

Sharegy keeps you informed about energy performance, weekly cost savings, and critical hardware health events via **Email**, **Browser Web Push**, and **Mobile Push**.

---

## 1. Weekly Energy & Autarky Digest 📊

The weekly digest provides a concise summary of your home's energy performance over the past 7 days:

* ☀️ **Solar Generation (kWh)**: Total PV generation achieved during the previous week.
* 🔄 **Self-Consumption (kWh)**: Solar energy utilized directly by appliances, storage, or EV charging.
* 🛡️ **Autarky Rate (%)**: Percentage of energy independence from the public grid.
* 💰 **Estimated Savings (€)**: Financial benefit calculated from avoided grid purchases and feed-in compensation.
* ⚡ **Grid Feed-In vs. Grid Purchase**: Comprehensive grid exchange balance.

### ⏰ Schedule & Timezone
> **Delivered every Monday at 08:00 AM:**  
> Reports are dispatched at **08:00 AM local user time** (defaulting to `Europe/Berlin` / CET/CEST).  
> If you configured a different timezone in your profile (e.g., `UTC` or `Europe/Warsaw`), the report is scheduled according to your configured local clock.

### 🌍 Multilingual Delivery
Emails are rendered in your selected interface language (**German**, **English**, or **Polish**).

---

## 2. Real-Time Critical Hardware Alerts 🚨

When a critical failure occurs, Sharegy immediately dispatches an urgent alert via email and push:

* **Inverter Offline / Zero-Yield**: High solar irradiance detected while solar inverter reports zero output (e.g., tripped breaker or DC switch).
* **Battery Deep Discharge**: Battery state of charge (SoC) drops below the safe reserve threshold.
* **Telemetry Timeout**: Smart meter or gateway communication lost for more than 15 minutes.

Each alert includes affected device identifiers, root-cause diagnostics, and actionable steps.

---

## 3. Web Push Notifications & Quiet Hours 🔔

Configure browser push notifications with customizable **Quiet Hours** (e.g., 22:00 to 07:00) to silence non-critical notifications during the night.

---

## 4. Managing Notification Settings

1. Open your **Profile** and navigate to the **Notifications & Alerts** tab.
2. Under **"Email Summaries & System Reports"**, toggle weekly reports and hardware alerts on or off.
3. Changes are saved automatically.
""",
                "tags": [
                    "benachrichtigungen",
                    "email",
                    "reports",
                    "wochenbericht",
                    "alarme",
                    "hardware",
                    "zeitzone",
                    "push",
                    "notifications",
                ],
                "is_featured": True,
                "sort_order": 1,
            },
        ]

        for adata in articles_data:
            HelpArticle.objects.update_or_create(
                slug=adata["slug"],
                defaults=adata,
            )

        self.stdout.write(self.style.SUCCESS(f"[OK] Erfolgreich {len(categories_data)} Kategorien und {len(articles_data)} Handbuch-Artikel in DE & EN initialisiert!"))

