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
            # 0. GETTING STARTED: TARIF- & ERSPARNIS-KOMPASS (KERN-LEITFADEN)
            # ---------------------------------------------------------------------
            {
                "category": cats["getting-started"],
                "slug": "tarif-und-ersparnis-kompass-matrix",
                "context_key": "tariffs_savings_compass",
                "title_de": "Tarif- & Ersparnis-Kompass: Welches Setup und welcher Stromtarif passt zu mir?",
                "title_en": "Tariff & Savings Compass: Which Setup and Electricity Tariff Fits My Home?",
                "summary_de": "Der große Ratgeber: Fester vs. Dynamischer Stromtarif, Balkonkraftwerk, Wärmepumpe, Wallbox und Ersparnis-Potenziale für alle 12 Haushalts-Profile.",
                "summary_en": "The definitive guide: Fixed vs. Dynamic electricity tariffs, balcony solar, heat pumps, EV charging, and savings potential across all home profiles.",
                "content_de": """# Tarif- & Ersparnis-Kompass: Welches Setup und welcher Stromtarif passt zu mir?

Nicht jeder Haushalt besitzt eine große Dach-Photovoltaikanlage, einen 10-kWh-Batteriespeicher oder ein Elektroauto. Sharegy ist modular aufgebaut und bietet für **jede Wohnsituation und Geräte-Ausstattung** konkrete finanzielle und ökologische Hebel.

---

## 1. Die goldene Grundregel der Tarif-Entscheidung

| Kriterium | 🔒 Fester Stromtarif (z. B. 28–32 ct/kWh) | ⚡ Dynamischer Börsentarif (Tibber, Awattar, Ostrom etc.) |
| :--- | :--- | :--- |
| **Zusatzkosten** | Keine / Standard-Grundgebühr (~10 €/Mt.) | Zusätzliche Monatsgebühr (~4–6 €/Mt.) + Smart-Meter-Messentgelt |
| **Preisrisiko** | 0 % Preisrisiko, feste Planbarkeit | Preisschwankungen; Risiko bei ungesteuertem Abend-Peak |
| **Voraussetzung** | Keine Steuerung notwendig | **Verschiebbare Großlast (≥ 2.000 kWh/a)** (z. B. E-Auto, modulierbare WP, Heimspeicher) |
| **Wann optimal?** | Reiner Haushaltsstrom, Mietwohnung, BKW ohne Speicher | E-Auto vorhanden, Speicher mit Winter-Netzladung, Wärmepumpe |

> [!IMPORTANT]
> **Warum lohnt sich ein dynamischer Tarif ohne Großverbraucher NICHT?**  
> Bei normalem Haushaltsstrom fällt der Verbrauch unverschiebbar in die Morgen- (07–09 Uhr) und Abendstunden (18–22 Uhr) – genau dann, wenn Strom an der Börse am teuersten ist. Zusammen mit den Zusatzgebühren zahlt ein Mieter im Börsentarif oft mehr als bei einem günstigen Festvertrag.

---

## 2. Die 6 Profile & 12 Hardware-Kombinationen

### 🏠 Kategorie A: Basishaushalt (Nur Haushaltsstrom)
* **Profil A.1 (Nur Stromzähler)**: 🔒 **FESTER TARIF**.  
  * *Hebel*: Standby-Killer (senkt 50–100 W Grundlast = **140–280 €/a**), Stromfresser-Alarme (**40–80 €/a**), P2P-Mieterstrom (**~120 €/a**).  
  * *Gesamtersparnis*: **180 € bis 360 € / Jahr**.

---

### ☀️ Kategorie B: Balkonkraftwerk (Stecker-Solar 600–800 W)
* **Profil B.1 (BKW ohne Speicher)**: 🔒 **FESTER TARIF**.  
  * *Hebel*: BKW deckt günstige Sonnenstunden gratis ab. Einschalttipps zur Mittagszeit steigern Eigenverbrauch von 45 % auf 80 % (**+80 €/a Zusatznutzen**). Amortisation in ~2,5 Jahren. Gesamtertrag: **200–260 € / a**.
* **Profil B.2 (BKW mit 1–2 kWh Minispeicher)**: 🔒 **FESTER TARIF**.  
  * *Hebel*: Nulleinspeisung / bedarfsgeführte Grundlast-Abgabe nachts. Gesamtertrag: **260–340 € / a**.

---

### 🚗 Kategorie C: Elektromobilität (Wallbox + E-Auto)
* **Profil C.1 (EV + Wallbox ohne PV)**: ⚡ **DYNAMISCHER TARIF + § 14a EnWG**.  
  * *Hebel*: 3.000 kWh Fahrstrom nachts zu Tiefpreisen (15–18 ct statt 32 ct) laden (**~420 €/a**) + **160 € § 14a Netzentgeltbonus**. Gesamtersparnis: **580–680 € / Jahr**.
* **Profil C.2 (EV + Wallbox + BKW)**: ⚡ **DYNAMISCHER TARIF** (ab 8.000 km/a). Gesamtersparnis: **720–850 € / Jahr**.
* **Profil C.3 (EV + Wallbox + Dach-PV ohne Speicher)**: ⚡ **DYNAMISCHER TARIF**. Sommer = 100 % Solarüberschuss; Winter = Windstrom-Nachtladen. Gesamtersparnis: **730–920 € / Jahr**.
* **Profil C.4 (EV + Dach-PV + Heimspeicher)**: ⚡ **DYNAMISCHER TARIF**. Sommer-Autarkie + Winter-Arbitrage + V2G/V2H. Gesamtersparnis: **1.400–1.900 € / Jahr**.

---

### 🏡 Kategorie D: Klassische Dach-PV (ohne EV/WP)
* **Profil D.1 (Dach-PV ohne Speicher)**: 🔒 **FESTER TARIF**. Eigenverbrauchssteuerung (WaMa, Heizstab) bringt **330–480 € / Jahr**.
* **Profil D.2 (Dach-PV mit Heimspeicher)**: 🔒 **FEST / DYN**. Festtarif für Standardbetrieb; Dynamisch nur bei aktiver Winter-Netzladung (**950–1.250 € / Jahr**).

---

### ♨️ Kategorie E: Wärmepumpen-Haushalt
* **Profil E.1 (Wärmepumpe ohne PV)**: ⚡ **DYN. TARIF oder § 14a WP-TARIF**. Smart Thermal Storage (Estrich-Vorlaufüberhöhung) + § 14a Rabatt (**300–420 € / Jahr**).
* **Profil E.2 (Wärmepumpe + Dach-PV)**: ⚡ **DYNAMISCHER TARIF**. Gesamtersparnis: **510–680 € / Jahr**.
* **Profil E.3 (Wärmepumpe + PV + Speicher)**: ⚡ **DYNAMISCHER TARIF**. Gesamtersparnis: **1.200–1.650 € / Jahr**.

---

### ⚡ Kategorie F: Voll-Prosumer (All-in-One)
* **Profil F.1 (PV + Speicher + EV + WP + V2G)**: 🚀 **DYNAMISCHER TARIF (Absolute Pflicht!)**.  
  * *Hebel*: Maximale Sektorenkopplung, Doppelter § 14a Vorteil (Wallbox + WP = **+320 €/a**), Netzarbitrage und V2G-Lastspitzenkappung.  
  * *Gesamtersparnis*: **1.950 € bis 2.600 € / Jahr**.

---

## 3. Übersichtstabelle aller Profile

| Profil | Hardware-Ausstattung | Tarif-Empfehlung | Realistisches Sparpotenzial |
| :--- | :--- | :---: | :---: |
| **A.1** | Nur Stromzähler | 🔒 **Fest** | **180 – 360 € / a** |
| **B.1** | BKW ohne Speicher | 🔒 **Fest** | **200 – 260 € / a** |
| **B.2** | BKW + Minispeicher | 🔒 **Fest** | **260 – 340 € / a** |
| **C.1** | EV + Wallbox (ohne PV) | ⚡ **Dynamisch** | **580 – 680 € / a** |
| **C.2** | EV + Wallbox + BKW | ⚡ **Dynamisch** | **720 – 850 € / a** |
| **C.3** | EV + Wallbox + Dach-PV | ⚡ **Dynamisch** | **730 – 920 € / a** |
| **C.4** | EV + PV + Heimspeicher | ⚡ **Dynamisch** | **1.400 – 1.900 € / a** |
| **D.1** | Dach-PV ohne Speicher | 🔒 **Fest** | **330 – 480 € / a** |
| **D.2** | Dach-PV + Heimspeicher | 🔒 **Fest / Dyn.** | **950 – 1.250 € / a** |
| **E.1** | Wärmepumpe (ohne PV) | ⚡ **Dyn. / WP** | **300 – 420 € / a** |
| **E.2** | Wärmepumpe + Dach-PV | ⚡ **Dynamisch** | **510 – 680 € / a** |
| **F.1** | PV + Speicher + EV + WP | 🚀 **Dynamisch** | **1.950 – 2.600 € / a** |
""",
                "content_en": """# Tariff & Savings Compass: Which Setup and Electricity Tariff Fits My Home?

Not every household owns a massive rooftop solar array, a 10 kWh battery, or an electric vehicle. Sharegy is built modularly to deliver **measurable financial and environmental savings** for every residential setup.

---

## 1. The Golden Rule of Electricity Tariffs

| Criterion | 🔒 Fixed Tariff (e.g. 28–32 ct/kWh) | ⚡ Dynamic Tariff (Tibber, Awattar, Ostrom etc.) |
| :--- | :--- | :--- |
| **Extra Costs** | None / standard base fee (~10 €/mo) | Monthly service fee (~4–6 €/mo) + smart metering costs |
| **Price Risk** | 0 % risk, full predictability | Price fluctuations; exposure to expensive evening peaks |
| **Prerequisite** | No automation required | **Shiftable heavy load (≥ 2,000 kWh/yr)** (EV, heat pump, battery) |
| **Best Choice** | Pure household load, rental flats, balcony solar | EV owners, winter grid battery charging, controllable heat pumps |

---

## 2. All 6 Profiles & 12 Hardware Combinations

### 🏠 Category A: Standard Household (No PV / EV / Heat Pump)
* **Profile A.1 (Smart Meter Only)**: 🔒 **FIXED TARIFF**.  
  * *Lever*: Standby killer (cuts 50–100 W continuous waste = **140–280 €/yr**), appliance anomaly alerts (**40–80 €/yr**), tenant sharing (**~120 €/yr**).  
  * *Total Savings*: **180 € to 360 € / year**.

### ☀️ Category B: Balcony Solar (Plug-in Solar 600–800 W)
* **Profile B.1 (Balcony Solar without Battery)**: 🔒 **FIXED TARIFF**. Midday appliance triggers boost self-consumption to 80 % (**+80 €/yr bonus**). Total output benefit: **200–260 € / yr**.
* **Profile B.2 (Balcony Solar with 1–2 kWh Battery)**: 🔒 **FIXED TARIFF**. Zero-feed-in baseload coverage at night (**260–340 € / yr**).

### 🚗 Category C: Electric Mobility (Wallbox + EV)
* **Profile C.1 (EV + Wallbox without Solar)**: ⚡ **DYNAMIC TARIFF + § 14a EnWG**. Night charging at 15–18 ct instead of 32 ct (**~420 €/yr**) + **160 € § 14a grid discount**. Total savings: **580–680 € / year**.
* **Profile C.2 (EV + Wallbox + Balcony Solar)**: ⚡ **DYNAMIC TARIFF**. Total savings: **720–850 € / year**.
* **Profile C.3 (EV + Wallbox + Rooftop Solar)**: ⚡ **DYNAMIC TARIFF**. Summer = free solar; Winter = cheap wind power. Total savings: **730–920 € / year**.
* **Profile C.4 (EV + Rooftop Solar + Battery)**: ⚡ **DYNAMIC TARIFF**. Full autarky + winter arbitrage + V2G/V2H (**1,400–1,900 € / year**).

### 🏡 Category D: Classic Rooftop Solar (No EV / Heat Pump)
* **Profile D.1 (Rooftop Solar without Battery)**: 🔒 **FIXED TARIFF**. Self-consumption optimization delivers **330–480 € / year**.
* **Profile D.2 (Rooftop Solar with Battery)**: 🔒 **FIXED / DYN**. Fixed for standard use; dynamic if winter grid charging is used (**950–1,250 € / year**).

### ♨️ Category E: Heat Pump Households
* **Profile E.1 (Heat Pump without Solar)**: ⚡ **DYNAMIC / HEAT PUMP TARIFF**. Smart thermal preheating + § 14a rebate (**300–420 € / year**).
* **Profile E.2 (Heat Pump + Rooftop Solar)**: ⚡ **DYNAMIC TARIFF** (**510–680 € / year**).
* **Profile E.3 (Heat Pump + Solar + Battery)**: ⚡ **DYNAMIC TARIFF** (**1,200–1,650 € / year**).

### ⚡ Category F: Full Prosumer (All-in-One)
* **Profile F.1 (Solar + Battery + EV + Heat Pump + V2G)**: 🚀 **DYNAMIC TARIFF (Mandatory!)**. Dual § 14a bonus (**+320 €/yr**), grid arbitrage, and V2G peak shaving (**1,950–2,600 € / year**).
""",
                "tags": ["tarif", "stromtarif", "ersparnis", "matrix", "balkonkraftwerk", "wallbox", "waermepumpe", "prosumer", "mieter", "savings", "tariffs"],
                "is_featured": True,
                "sort_order": 1,
            },
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
            # ---------------------------------------------------------------------
            # 16. WÄRME & HEIZUNG: FUSSBODENHEIZUNG & ESTRICH-SPEICHER (THERMAL BATTERY)
            # ---------------------------------------------------------------------
            {
                "category": cats["optimizer"],
                "slug": "fussbodenheizung-und-estrich-speicher",
                "context_key": "floor_heating",
                "title_de": "Fußbodenheizung & Estrich-Speicher: Regelungskonzept, Mess- & Steuerwerte",
                "title_en": "Underfloor Heating & Screed Thermal Battery: Control Logic, Metrics & Setpoints",
                "summary_de": "Vollständige Anleitung zur wettergeführten Fußbodenheizung (DIN EN 12831), thermischen Estrich-Vorladung (MPC) und allen Schaltsignalen.",
                "summary_en": "Complete guide to weather-guided underfloor heating (DIN EN 12831), predictive screed preheating (MPC), and control setpoints.",
                "content_de": r"""# Intelligente Fußbodenheizung & Thermischer Estrich-Speicher

Die **Fußbodenheizungs- & Estrich-Engine** von Sharegy verwandelt den Betonestrich deines Gebäudes in einen hocheffizienten thermischen Energiespeicher (*Thermal Battery Dispatch*).

---

## 1. Das physikalische Prinzip (Warum Estrich?)

Ein typisches Einfamilienhaus mit ca. $120\,\text{m}^2$ Fußbodenheizungsfläche besitzt rund **16,8 Tonnen Betonestrich** (Dicke $7\,\text{cm}$, Rohdichte $2.000\,\text{kg/m}^3$). 

* **Thermische Speicherkapazität:** ca. **4,67 kWh pro Kelvin** Temperaturerhöhung.
* **Vorladepotenzial (+1,0 K bis +1,5 K):** ca. **7 bis 14 kWh thermische Energie** (entspricht bei einer Wärmepumpe mit COP 3,5 ca. **2 bis 4 kWh elektrischer Energie**).
* **Phasenverschiebung:** Der Estrich nimmt Wärme tagsüber bei kostenlosem Solarüberschuss oder günstigen Börsenpreisen auf und gibt sie abends **über 3 bis 5 Stunden passiv an die Räume ab** – ganz ohne teuren Netzbezug in der Abendspitze!

---

## 2. Wo und wie wird geschaltet? (Aktorik)

Sharegy steuert den Heizkreis digital über einen der folgenden Wege:
1. **SG-Ready Eingang der Wärmepumpe:** Ein Relais (z. B. Shelly Plus 1 / Pro 1) schaltet den SG-Ready-Kontakt 2 (Betriebszustand 3 = *„Empfohlene Überhöhung / Speicherladung“*).
2. **Heizkreispumpe / FBH-Verteiler:** Ein Schaltaktor schaltet die Zirkulationspumpe des Niedertemperatur-Heizkreises direkt ein oder aus.
3. **Smart Home Integration:** Steuerung über Home Assistant, ioBroker oder Homematic IP via MQTT / WebSocket.

> [!TIP]
> In den Einstellungen der Karte (⚙️ Zahnrad) wählst du unter **„Verknüpftes Gerät / Aktor“** einfach deinen Schalter aus.

---

## 3. Benötigte Messwerte (Inputs) & Steuerwerte (Outputs)

### A. Benötigte Messwerte (Sensorik):
* **Raumtemperatur ($T_\text{ist}$):** Raumthermostat oder Temperatursensor (z. B. Shelly H&T, Zigbee, Homematic).
* **PV-Überschuss ($P_\text{surplus}$ in W):** Smart Meter am Netzübergabepunkt (z. B. Shelly 3EM / Pro 3EM, Wechselrichter).
* **Börsenstrompreis (EPEX Spot):** Automatisch via Sharegy Live-Schnittstelle.
* **Wetterdaten & Globalstrahlung (DWD / Open-Meteo):** Außentemperatur und Strahlung ($W/m^2$) der nächsten 24 Stunden.

### B. Berechnete Steuerwerte (Aktorik & MPC):
* **Relais-Schaltzustand:** `ON` (Vorheizen / Normalbetrieb) oder `OFF` (Passives Entladen / Standby).
* **Dynamische Vorlauftemperatur ($T_\text{flow}$):** Berechnet nach DIN EN 12831:
  $$\text{Vorlauf} = \text{Basis-Heizkurve} + \text{Vorladeboost}\,(+1{,}5\,\text{K}) - \text{Solares Absenken}\,(-1{,}5\,\text{K})$$
* **Thermischer Ladezustand (SoC in % & kWh):** Exakte Füllstandsanzeige des Estrich-Speichers.

---

## 4. Die 5 Betriebsmodi

1. **🤖 Autopilot (Empfohlen):** Kombiniert Solarüberschuss und Börsenpreise mit 24h-Wetterprognose.
2. **☀️ Nur PV-Überschuss:** Lädt den Estrich ausschließlich dann vor, wenn Solarstrom ins Netz fließen würde.
3. **💰 Sparfuchs:** Nutzt die günstigsten Börsenstromstunden der Nacht zur Vorladung.
4. **🛋️ Komfortbetrieb:** Hält konstant die eingestellte Wunschtemperatur (keine Vorladung).
5. **🛑 Manuell:** Automatik pausiert, Steuerung ausschließlich von Hand.

---

## 5. Sicherheit & Schutzfunktionen

* **🛡️ Überhitzungsschutz:** Bei Überschreiten der Maximaltemperatur (z. B. $24{,}5^\circ\text{C}$) schaltet Sharegy den Heizkreis sofort ab.
* **❄️ Untertemperaturschutz:** Sinkt die Temperatur unter $20{,}5^\circ\text{C}$, heizt Sharegy sofort auf, um Wohnkomfort zu garantieren.
* **⏳ Verdichter- & Pumpenschutz:** Anti-Cycling-Sperre (Mindestlaufzeit & Mindestruhezeit von je 10 Minuten) verhindert häufiges Takten.
""",
                "content_en": r"""# Smart Underfloor Heating & Screed Thermal Battery

Sharegy's **Underfloor Heating & Screed Thermal Battery Engine** turns your building's concrete floor into an intelligent thermal energy storage system (*Thermal Battery Dispatch*).

---

## 1. Physical Principle (Why Screed?)

A typical single-family home with $120\,\text{m}^2$ of underfloor heating contains roughly **16.8 tons of screed concrete** ($7\,\text{cm}$ thickness, density $2,000\,\text{kg/m}^3$).

* **Thermal Capacity:** approx. **4.67 kWh per Kelvin** of temperature rise.
* **Preheating Potential (+1.0 K to +1.5 K):** approx. **7 to 14 kWh of thermal energy** (approx. **2 to 4 kWh electrical** with a heat pump COP of 3.5).
* **Load Shifting:** The screed absorbs surplus solar energy or cheap dynamic power during the day and passively releases heat over **3 to 5 hours in the evening**, completely avoiding expensive peak grid hours.

---

## 2. Where and How is it Switched? (Actuators)

1. **Heat Pump SG-Ready Contacts:** An actuator relay switches state 3 (recommended preheating boost).
2. **Heating Circuit Pump:** An actuator switches the circulation pump directly.
3. **Smart Home Integration:** Controlled via Home Assistant or ioBroker via MQTT / WebSocket RPC.

---

## 3. Required Metrics & Output Setpoints

* **Inputs:** Room temperature, live solar surplus, EPEX Spot price, 24h weather forecast.
* **Outputs:** Relay on/off state, dynamic flow temperature (DIN EN 12831), solar gain compensation, thermal SoC (%).
""",
                "tags": [
                    "fussbodenheizung",
                    "estrich",
                    "thermal battery",
                    "wärmepumpe",
                    "heizkurve",
                    "mpc",
                    "solarüberschuss",
                    "sg ready",
                    "heating",
                ],
                "is_featured": True,
                "sort_order": 2,
            },
            # ---------------------------------------------------------------------
            # 17. SCHNITTSTELLEN: IOBROKER & HOME ASSISTANT (MESSEN & STEUERN)
            # ---------------------------------------------------------------------
            {
                "category": cats["devices-protocols"],
                "slug": "smart-home-iobroker-home-assistant-messen-steuern",
                "context_key": "interfaces_smarthome",
                "title_de": "ioBroker & Home Assistant Integration: Bidirektionales Messen & Steuern",
                "title_en": "ioBroker & Home Assistant Integration: Bidirectional Monitoring & Control",
                "summary_de": "Erklärung der bidirektionalen Schnittstelle für Home Assistant und ioBroker (Sensordaten erfassen, Thermostate und Aktoren schalten).",
                "summary_en": "Guide to the bidirectional interface for Home Assistant and ioBroker (sensor telemetry and actuator control).",
                "content_de": r"""# ioBroker & Home Assistant: Bidirektionales Messen & Steuern

Sharegy bietet eine universelle **MQTT- & WebSocket-Schnittstelle**, mit der du deine bestehende Smart-Home-Zentrale (**Home Assistant**, **ioBroker**, **Node-RED**, **OpenHAB**, **Homematic IP**) nahtlos einbinden kannst.

---

## 1. Das Konzept: Messen vs. Steuern

Die Schnittstelle arbeitet **bidirektional**:

```mermaid
flowchart LR
    subgraph HA["🏠 Home Assistant / ioBroker"]
        S["🌡️ Sensoren<br>(Temperatur, Smart Meter, PV)"]
        A["🔌 Aktoren<br>(Thermostate, Relais, Wallbox)"]
    end

    subgraph Sharegy["⚡ Sharegy Cloud & HEMS Optimizer"]
        O["🧠 MPC-Optimierung<br>& Börsenstrom-Algorithmus"]
    end

    S -- "1. Messen (Inbound Telemetrie)" --> O
    O -- "2. Steuern (Outbound Setpoints / Schaltsignale)" --> A
```

---

## 2. Messen (Sensordaten an Sharegy senden)

Home Assistant oder ioBroker übermitteln Sensorwerte per MQTT an Sharegy (`h/<home_token>/...`):
* `power_production` (PV-Leistung in W)
* `power_grid` (Netzbezug/Einspeisung in W)
* `battery_soc` (Batterieladezustand in %)
* `temperature_room` (Ist-Temperatur des Wohnzimmers)

---

## 3. Steuern (Schaltbefehle & Sollwerte von Sharegy empfangen)

Wenn die Option **„Bidirektionale Steuerung aktivieren“** eingeschaltet ist, publiziert Sharegy optimierte Sollwerte:
* `heating_relay` (`ON` / `OFF` für Wärmepumpe / Relais)
* `target_temperature` ($21{,}0^\circ\text{C}$ bzw. $22{,}0^\circ\text{C}$ bei Vorlade-Boost)
* `flow_temperature_target` (Berechnete Vorlauftemperatur nach DIN EN 12831)
* `wallbox_max_current` (Ladefreigabe 6 bis 16 A)

---

## 4. Konfiguration & Ein/Aus-Schalter

1. Öffne im Menü **„⚙️ Schnittstellen“** (`/app/interfaces`).
2. Wähle den Tab **„Home Assistant“** oder **„ioBroker“**.
3. Aktiviere den Schalter **„Bidirektionale Steuerung (Messen & Steuern)“**.
""",
                "content_en": """# ioBroker & Home Assistant: Bidirectional Monitoring & Control

Sharegy provides a universal **MQTT and WebSocket interface** to connect **Home Assistant**, **ioBroker**, **Node-RED**, and other smart home platforms.

---

## 1. Bidirectional Concept: Monitoring vs. Control

* **1. Monitoring (Inbound):** HA/ioB sends live sensors (PV power, grid meter, room temperatures) to Sharegy.
* **2. Control (Outbound):** Sharegy computes the optimal dispatch schedule and sends setpoints (`target_temperature`, `relay_state`, `wallbox_current`) back to your actuators.

---

## 2. Configuration & Activation

1. Navigate to **Interfaces** (`/app/interfaces`).
2. Select the **Home Assistant** or **ioBroker** tab.
3. Toggle **"Bidirectional Control (Monitor & Actuate)"** on.
""",
                "tags": [
                    "home assistant",
                    "iobroker",
                    "mqtt",
                    "smart home",
                    "messen",
                    "steuern",
                    "aktoren",
                    "sensoren",
                    "schnittstellen",
                ],
                "is_featured": True,
                "sort_order": 3,
            },

            # ---------------------------------------------------------------------
            # 18. ENERGIEPROFIL & HAUSHALTS-BASELINE-ASSISTENT
            # ---------------------------------------------------------------------
            {
                "category": cats["getting-started"],
                "slug": "energieprofil-und-baseline-assistent",
                "context_key": "energy_profile",
                "title_de": "Energieprofil & Haushalts-Baseline: Grundlast, Effizienz-Benchmarking & Einsparpotenziale",
                "title_en": "Energy Profile & Home Baseline: Baseload, Efficiency Benchmarking & Savings",
                "summary_de": "Konfiguration deines Haushalts-Energieprofils (/app/energy-profile): Haushaltsgröße, Wohnfläche, Heizungstyp, theoretische Grundlast-Berechnung und Identifikation versteckter Standby-Stromfresser.",
                "summary_en": "Configuring your household Energy Profile (/app/energy-profile): household size, floor area, heating type, theoretical baseload calculation, and eliminating standby power leakages.",
                "content_de": r"""# Energieprofil & Haushalts-Baseline: Grundlast & Effizienz 🏠📊

Das **Energieprofil** unter `/app/energy-profile` ist das Herzstück zur individuellen Modellierung deines Haushalts in Sharegy. Es liefert dem Smart Energy Optimizer (EMS) und der KI-Lastprognose die mathematische Basis für präzise Berechnungen.

---

## 1. Warum ist das Energieprofil unverzichtbar?

Jeder Haushalt ist einzigartig: Ein Single in einer Altbauwohnung hat völlig andere Verbrauchsmuster als eine 4-köpfige Familie im KfW-40-Neubau mit Wärmepumpe und Elektrofahrzeug.

Durch das Ausfüllen des Energieprofils erzielst du:
* 🎯 **Präzise 24h-Lastprognosen**: Das System weiß exakt, wie viel Strom dein Haushalt zu welcher Tageszeit benötigt.
* 🔍 **Aufdecken von Standby-Leckagen**: Automatischer Abgleich deiner echten nächtlichen Grundlast mit dem theoretischen Soll-Wert.
* 💰 **Gezielte Optimierungsempfehlungen**: Individuelle Spartipps für Heizung, Warmwasser, Mobilität und Haushaltsgeräte.

---

## 2. Die Eingabeparameter im Baseline-Assistenten

Im Assistenten erfasst du in wenigen Schritten deine Eckdaten:

| Parameter | Beschreibung | Auswirkung auf die Optimierung |
| :--- | :--- | :--- |
| **Haushaltsgröße** | Anzahl der ständig im Haushalt lebenden Personen | Skaliert den personenbezogenen Grund- und Kochstrom |
| **Wohnfläche ($m^2$)** | Beheizte Wohnfläche | Berechnet den spezifischen Heizwärmebedarf ($kWh/m^2a$) |
| **Gebäudestandard** | Baujahr / Sanierungsstufe (z. B. KfW 40, KfW 55, Altbau) | Bestimmt die thermische Gebäudeträgheit und Vorlauftemperaturen |
| **Heizungssystem** | Wärmepumpe, Fernwärme, Gas/Öl, Pelletheizung | Definiert flexible thermische Lastverschiebungs-Potenziale |
| **Warmwasserbereitung** | BWWP, Durchlauferhitzer, zentral über Heizung, Boiler | Modelliert Warmwasser-Peaks am Morgen und Abend |
| **E-Mobilität** | Anzahl Elektrofahrzeuge & jährliche Fahrleistung (km/a) | Plant Ladefenster und Akkukapazitäten im Fahrplan ein |
| **Sonderverbraucher** | Klimaanlage, Poolpumpe, Sauna, Home-Server, Teichfilter | Erkennt planbare Großverbraucher für Solar-Dispatching |

---

## 3. Die theoretische Grundlast-Berechnung (Benchmark)

Sharegy errechnet aus deinen Profildaten eine **theoretische Referenz-Grundlast** ($P_\text{theoretisch}$):

$$P_\text{theoretisch} = P_\text{Basis} + (\text{Personen} \times P_\text{Person}) + P_\text{Dauerverbraucher}$$

### Typische Richtwerte für die normale Haushaltsgrundlast:
* 👤 **1-Personen-Haushalt**: ca. **60 bis 90 W**
* 👥 **2-Personen-Haushalt**: ca. **90 bis 140 W**
* 👨‍👩‍👧‍👦 **3–4-Personen-Haushalt**: ca. **130 bis 200 W**
* 🏡 **Einfamilienhaus mit Komfortausstattung**: ca. **180 bis 250 W**

---

## 4. Standby-Leckage-Erkennung & Kostenfalle

Die automatische Analyse prüft kontinuierlich deine gemessene Dauerlast in der tiefen Nacht (**02:00 bis 05:00 Uhr**):

> ⚠️ **Beispiel für teure Dauerlasten:**  
> Liegt deine gemessene Nachtlast bei **280 W**, während dein theoretischer Soll-Wert nur **120 W** beträgt, verlierst du **160 W als reine Standby-Leckage**!  
> $$160\,\text{W} \times 8.760\,\text{h} = 1.401{,}6\,\text{kWh/Jahr} \approx \mathbf{420\text{ bis }490\text{ €/Jahr}}$$

### Typische versteckte Stromfresser:
1. 🔄 **Alte ungesteuerte Heizungspumpen**: Laufen oft ganzjährig mit 60–90 W durch (**~180–270 €/a**).
2. 📺 **Media-Receiver & HiFi-Verstärker**: Viele Altgeräte ziehen im Standby 15–30 W.
3. ❄️ **Zweit-Kühlschrank im Keller**: Defekte Dichtungen oder Vereisung führen zu dauerhaftem Kompressorlauf.
4. 🌐 **Ungesteuerte Netzwerk-Switches & Dauer-Netzteile**: Sammeln sich unbemerkt an.

---

## 5. Integration mit dem Smart Energy Optimizer

Sobald dein Profil vollständig konfiguriert ist:
* Berechnet das EMS die täglichen Lade- und Entladezyklen deines Batteriespeichers millimetergenau.
* Werden flexible Lasten (Wallbox, BWWP, Klimaanlage) so eingetaktet, dass die Grundlast nie zu ungeplantem Netzbezug führt.
""",
                "content_en": r"""# Energy Profile & Home Baseline: Baseload & Efficiency 🏠📊

The **Energy Profile** at `/app/energy-profile` provides the foundational blueprint for your home in Sharegy. It equips the Smart Energy Optimizer (EMS) and AI load forecasting engine with accurate parameters for simulation and dispatch.

---

## 1. Why is the Energy Profile essential?

Every household exhibits distinct consumption dynamics. A single occupant in a well-insulated apartment has completely different needs than a family of four in a single-family home with a heat pump and EV.

Completing your Energy Profile delivers:
* 🎯 **Precise 24h Load Forecasts**: Tailored expected hourly consumption patterns.
* 🔍 **Standby Leakage Detection**: Automated benchmarking of measured nighttime baseload against theoretical targets.
* 💰 **Targeted Savings Recommendations**: Tailored guidance for HVAC, hot water, EV charging, and smart appliances.

---

## 2. Input Parameters

| Parameter | Description | Optimization Impact |
| :--- | :--- | :--- |
| **Household Size** | Number of permanent residents | Scales occupancy-driven baseload and appliance usage |
| **Living Area ($m^2$)** | Heated floor area | Calculates specific thermal demand ($kWh/m^2a$) |
| **Building Standard** | Year of construction / insulation rating | Determines thermal inertia and heating curve parameters |
| **Heating System** | Heat pump, district heating, gas/oil, biomass | Defines flexible thermal shift capacity |
| **Hot Water (DHW)** | DHW heat pump, instantaneous heater, boiler | Schedules morning and evening peak demands |
| **EV Mobility** | Electric vehicle count and annual mileage (km/y) | Reserves charging slots in the 24h dispatch plan |
| **Special Loads** | Air conditioning, pool pump, sauna, home servers | Pinpoints schedulable heavy loads for solar dispatch |

---

## 3. Theoretical Baseload Calculation

Sharegy computes a **theoretical benchmark baseload** ($P_\text{theoretical}$):

$$P_\text{theoretical} = P_\text{base} + (\text{Occupants} \times P_\text{person}) + P_\text{constant\_loads}$$

### Typical Industry Benchmarks:
* 👤 **1-Person Household**: approx. **60 to 90 W**
* 👥 **2-Person Household**: approx. **90 to 140 W**
* 👨‍👩‍👧‍👦 **3–4-Person Household**: approx. **130 to 200 W**
* 🏡 **Single-Family Home with Smart Equipment**: approx. **180 to 250 W**

---

## 4. Standby Leakage Alert & Cost Impact

The analytics engine continually verifies your nighttime minimum power draw (**02:00 to 05:00 AM**):

> ⚠️ **Cost Example:**  
> If measured baseload is **280 W** against a target of **120 W**, the unexplained **160 W excess standby** costs:  
> $$160\,\text{W} \times 8,760\,\text{h} = 1,401.6\,\text{kWh/year} \approx \mathbf{420\text{ to }490\text{ €/year}}$$
""",
                "tags": ["energieprofil", "baseline", "grundlast", "standby", "stromfresser", "effizienz", "haushalt", "benchmark"],
                "is_featured": True,
                "sort_order": 3,
            },

            # ---------------------------------------------------------------------
            # 19. DC-DC LADEN, SPEICHER-ZU-SPEICHER & V2H / V2G
            # ---------------------------------------------------------------------
            {
                "category": cats["inverters-meters"],
                "slug": "dc-dc-laden-und-speicher-zu-speicher-v2g",
                "context_key": "dcdc_v2g",
                "title_de": "DC-DC Laden, Speicher-zu-Speicher & Bidirektionales Laden (V2H / V2G)",
                "title_en": "DC-DC Charging, Storage-to-Storage & Bidirectional Charging (V2H / V2G)",
                "summary_de": "Verlustfreies DC-Koppeln (bis 95 % Wirkungsgrad), Umladung von Heimspeicher ins E-Auto und Fahrzeug-Rückspeisung (Vehicle-to-Home / Vehicle-to-Grid) bei Spitzenlasten.",
                "summary_en": "Lossless DC-coupling (up to 95% efficiency), home battery to EV transfer, and Vehicle-to-Home / Vehicle-to-Grid (V2H / V2G) peak-shaving strategies.",
                "content_de": r"""# DC-DC Laden, Speicher-zu-Speicher & Bidirektionales Laden (V2H / V2G) 🔋⚡🚗

Moderne PV- und Speicher-Architekturen ermöglichen direkten Gleichstrom-Transfer (**DC-DC**) sowie bidirektionale Energieflüsse zwischen Heimspeicher, Solarmodulen und Elektrofahrzeug.

---

## 1. DC-Kopplung vs. AC-Kopplung: Die Physik der Wirkungsgrade

Klassische Wallboxen und Batteriespeicher arbeiten wechselstromseitig (AC). Dabei muss der Strom mehrfach umgewandelt werden:

```
[ Klassische AC-Kette ]
PV (DC) ➔ Wechselrichter (AC) ➔ Hausnetz (AC) ➔ Onboard-Lader (DC) ➔ Autobatterie (DC)
Gesamtwirkungsgrad: ca. 80 % bis 85 % (15–20 % Wandlungsverlust!)

[ Direkte DC-DC-Kette ]
PV (DC) ➔ DC/DC-Zwischenkreis ➔ Fahrzeugakku (DC)
Gesamtwirkungsgrad: ca. 94 % bis 97 % (Nur 3–6 % Verlust!)
```

### Warum ist DC-DC Laden so überlegen?
* **Minimaler Wandlungsverlust**: Keine doppelte Gleich- und Wechselrichtung ($DC \rightarrow AC \rightarrow DC$).
* **Geringere Wärmeentwicklung**: Schont Elektronik, Ladeinfrastruktur und Akkuzellen.
* **Höhere Ladeleistungen bei Schwachlicht**: Schnelleres Ansprechverhalten bereits ab geringen Solarströmen.

---

## 2. Speicher-zu-Speicher Umladung (Heimspeicher ➔ Elektroauto)

Im Sharegy EMS kannst du definieren, ob und unter welchen Bedingungen das Elektroauto aus dem stationären Heimspeicher geladen werden darf.

### Wann ist das Umladen wirtschaftlich sinnvoll?
* ☀️ **Sommer / Hohe Solarprognose**:  
  Wenn die Wetterprognose für den nächsten Vormittag $100\,\%$ Sonnenschein vorhersagt, kann der Heimspeicher abends bedenkenlos ins E-Auto entleert werden – am nächsten Morgen wird der Speicher ohnehin sofort wieder voll.
* 🍂 **Übergangszeit / Winter**:  
  Hier sollte die Heimspeicher-Energie primär für die nächtliche Haushaltsgrundlast und Wärmepumpe reserviert werden. Ein Umladen ins Auto würde doppelten Zyklenverschleiß bedeuten und nachts teuren Netzbezug (30+ ct/kWh) provozieren.

### Zyklenkosten-Formel im Sharegy Optimizer:
$$C_\text{Zyklus} = \frac{\text{Anschaffungskosten Speicher (€)}}{\text{Garantierte Vollzyklen} \times \text{Kapazität (kWh)}} \approx 0{,}08\text{ bis }0{,}12\text{ €/kWh}$$
Das EMS gibt das Umladen nur frei, wenn:
$$\text{Netzstrompreis} > \text{Einspeisevergütung} + C_\text{Zyklus} + \text{Wandlungsverlust}$$

---

## 3. Bidirektionales Laden: V2H (Vehicle-to-Home) & V2G (Vehicle-to-Grid)

Ein modernes Elektroauto besitzt eine Batteriekapazität von **50 bis 100 kWh** – das entspricht der **5- bis 10-fachen Kapazität** eines typischen Heimspeichers!

| Modus | Beschreibung | Typischer Einsatzbereich |
| :--- | :--- | :--- |
| **V2H (Vehicle-to-Home)** | Das E-Auto speist Energie in das private Hausnetz ein. | Versorgt Haus und Wärmepumpe über mehrere trübe Tage hinweg; Notstromversorgung bei Stromausfall. |
| **V2G (Vehicle-to-Grid)** | Das E-Auto speist geregelt ins öffentliche Stromnetz ein. | Teilnahme am Regelenergiemarkt; Spitzenlastkappung (Peak Shaving); Arbitrage bei Börsenpreis-Spitzen. |

---

## 4. Schutzfunktionen & Mindest-SoC-Garantie

Um sicherzustellen, dass dein Auto jederzeit abfahrbereit bleibt, setzt Sharegy strikte Sicherheitsgrenzen:
1. 🚗 **Mobilitäts-Reserve (Fahrzeug-Mindest-SoC)**: z. B. $60\,\%$ oder $150\,\text{km}$ Restreichweite werden niemals für V2H entladen.
2. 🔋 **Heimspeicher-Tiefentladeschutz**: Stationäre Speicher werden nie unter die Notstrom-Schwelle (z. B. $10\,\%$) entladen.
3. 🌡️ **Temperatur- und Zellüberwachung**: Reduktion der Lade-/Entladeleistung bei extremen Akkutemperaturen.
""",
                "content_en": r"""# DC-DC Charging, Storage-to-Storage & Bidirectional Charging (V2H / V2G) 🔋⚡🚗

Modern solar and storage topologies enable direct DC power transfer (**DC-DC**) and bidirectional energy exchange between stationary batteries, solar arrays, and electric vehicles.

---

## 1. DC vs. AC Coupling: Efficiency & Power Flow

Traditional EV chargers operate on alternating current (AC), necessitating dual conversion stages:

```
[ Traditional AC Topology ]
PV (DC) ➔ Inverter (AC) ➔ Home Grid (AC) ➔ Onboard Charger (DC) ➔ EV Battery (DC)
Overall Efficiency: approx. 80 % to 85 %

[ Direct DC-DC Coupling ]
PV (DC) ➔ DC Bus ➔ EV Battery (DC)
Overall Efficiency: approx. 94 % to 97 %
```

---

## 2. Storage-to-Storage Energy Transfer (Home Battery ➔ EV)

Sharegy EMS orchestrates whether stationary battery capacity should discharge into your electric vehicle based on dynamic economics and weather forecasting:

* ☀️ **High Solar Forecast**: Evening discharge into the EV is permitted if the home battery will reach full capacity early the next day.
* ❄️ **Winter / Low Solar**: Home battery capacity is strictly prioritized for household baseload and heat pumps to avoid costly peak grid purchases.

$$\text{Cycle Cost} \approx \frac{\text{Battery Investment Cost}}{\text{Guaranteed Cycles} \times \text{Capacity}} \approx 0.08\text{ to }0.12\text{ €/kWh}$$

---

## 3. Bidirectional Charging: V2H & V2G

With EV capacities ranging from **50 to 100 kWh**, vehicles represent massive distributed energy reservoirs:
* **V2H (Vehicle-to-Home)**: Powers domestic loads, shaving grid peaks and supplying multi-day resilience.
* **V2G (Vehicle-to-Grid)**: Injects power into the public distribution grid during extreme price events and grid stress.

---

## 4. Guardrails & Minimum SoC Protection

* 🚗 **Vehicle Mobility Reserve**: Guaranteed minimum EV SoC (e.g., $60\,\%$) is never discharged to home loads.
* 🔋 **Stationary Battery Deep Discharge Lock**: Reserves emergency backup margins.
""",
                "tags": ["dc-dc", "v2g", "v2h", "bidirektional", "speicher-zu-speicher", "wirkungsgrad", "peak shaving", "batterie"],
                "is_featured": True,
                "sort_order": 4,
            },

            # ---------------------------------------------------------------------
            # 20. OCPP 1.6 / 2.0.1 / 2.1 SMART CHARGING & PHASENUMSCHALTUNG
            # ---------------------------------------------------------------------
            {
                "category": cats["devices-protocols"],
                "slug": "ocpp-2-0-1-smart-charging-phasenumschaltung",
                "context_key": "ocpp",
                "title_de": "OCPP 1.6 / 2.0.1 / 2.1 Experte: Dynamisches PV-Laden, Phasenumschaltung & Departure Ready",
                "title_en": "OCPP 1.6 / 2.0.1 / 2.1 Expert: Dynamic PV Charging, Phase Switching & Departure Ready",
                "summary_de": "OCPP-Protokoll-Generationen (1.6-J, 2.0.1, 2.1), automatische 1p/3p Phasenumschaltung (1,4 kW – 11/22 kW), Abfahrtszeit-Zielladen (Departure Ready) und CSMS-Konfiguration.",
                "summary_en": "OCPP protocol generations (1.6-J, 2.0.1, 2.1), automatic 1p/3p phase switching (1.4 kW – 11/22 kW), Departure Ready schedule optimization, and CSMS setup.",
                "content_de": r"""# OCPP 1.6 / 2.0.1 / 2.1 Experte: Smart Charging & Phasenumschaltung 🚗🔌

Das integrierte **Sharegy OCPP Charging Station Management System (CSMS)** unterstützt alle maßgeblichen offenen Ladeprotokolle für professionelles intelligentes Laden.

---

## 1. Die OCPP-Protokoll-Generationen im Vergleich

| Feature | OCPP 1.6-J (JSON) | OCPP 2.0.1 | OCPP 2.1 |
| :--- | :--- | :--- | :--- |
| **Sicherheit & Verschlüsselung** | HTTP Basic Auth / TLS (WSS) | mTLS mit Client-Zertifikaten | Fortgeschrittene Zero-Trust mTLS |
| **Smart Charging Profiles** | `SetChargingProfile` (Composite Schedule) | Granulares Device Model & Constraints | Erweiterte dynamische Stromrampen (0,1 A) |
| **ISO 15118 Integration** | Eingeschränkt | Vollständig (Plug & Charge) | Nativ inkl. V2G Bidirektionalität |
| **Phasenumschaltung** | Vendor-spezifisch / Relay Trigger | Standardisierte Variablen | Nativer Phasenumschaltungs-Befehl |

---

## 2. Automatische 1-Phasen / 3-Phasen-Umschaltung (1p / 3p)

Nach der internationalen Ladungsnorm **IEC 61851** beträgt der minimale Ladestrom für Elektrofahrzeuge **6 Ampere pro Phase**.

### Das Problem bei reiner 3-Phasen-Ladung:
* $6\,\text{A} \times 3\,\text{Phasen} \times 230\,\text{V} = \mathbf{4{,}14\,\text{kW Mindestleistung}}$.
* Erzeugt deine PV-Anlage an bewölkten Tagen z. B. nur $2{,}0\,\text{kW}$ Überschuss, müsste bei 3 Phasen entweder $2{,}14\,\text{kW}$ teurer Netzstrom zugekauft werden – oder das Laden pausiert komplett!

### Die Lösung: Automatische Phasenumschaltung
* **1-phasiger Modus**: Lädt stufenlos von **$1{,}38\,\text{kW}$** ($6\,\text{A}$) bis **$3{,}68\,\text{kW}$** ($16\,\text{A}$) bzw. $7{,}36\,\text{kW}$ ($32\,\text{A}$).
* **3-phasiger Modus**: Lädt bei starkem Sonnenschein von **$4{,}14\,\text{kW}$** bis **$11{,}0\,\text{kW}$** (oder $22{,}0\,\text{kW}$).

```
[ PV-Überschuss < 4,2 kW ] ➔ 1-phasig aktiv (Laden startet bereits ab 1,4 kW!)
[ PV-Überschuss >= 4,4 kW (für > 120 s) ] ➔ Umschaltung auf 3-phasig (Volle Power bis 11 kW)
```

> [!IMPORTANT]
> **Schütz-Schonzeit (Totzeit)**:  
> Sharegy hält bei der Umschaltung zwischen 1 und 3 Phasen eine Sicherheits-Pause von **60 bis 120 Sekunden** ein. Dies schützt das Bordladegerät (OBC) deines Autos vor zerstörerischen Phasen-Lichtbögen.

---

## 3. Departure Ready (Zielladen nach Abfahrtszeit)

Mit **Departure Ready** stellst du sicher, dass dein Auto pünktlich zur Abfahrt den gewünschten Ladestand erreicht – zu den absolut geringsten Stromkosten:

1. ⏰ **Abfahrtszeit festlegen**: z. B. morgen früh um `07:30 Uhr`.
2. 🎯 **Ziel-SoC wählen**: z. B. `80 %` (oder gewünschte Reichweite in kWh).
3. 🧠 **Sharegy Optimierungs-Algorithmus**:
   - Lädt tagsüber priorisiert mit solarem Überschuss.
   - Ermittelt die verbleibende Restenergiemenge.
   - Berechnet anhand der Day-Ahead-Börsenstrompreise (EPEX Spot) die **günstigsten Stunden der Nacht** (z. B. 02:00 bis 04:30 Uhr) und schaltet die Wallbox exakt in diesem Preisfenster ein.

---

## 4. OCPP Server-Konfiguration & Einbindung

Trage in der Weboberfläche deiner Wallbox (Easee, openWB, Webasto, Mennekes, Alfen, go-e, DaheimLaden, cFos, ABB etc.) folgende Verbindungsdaten ein:

* **Backend-URL**: `wss://sharegy.de/ocpp/<DEINE_CHARGE_POINT_ID>`
* **Port**: `443` (Verschlüsseltes TLS/WSS)
* **Heartbeat-Intervall**: `60 Sekunden`
* **MeterValues SampleInterval**: `10 bis 30 Sekunden`
""",
                "content_en": r"""# OCPP 1.6 / 2.0.1 / 2.1 Expert: Smart Charging & Phase Switching 🚗🔌

Sharegy's built-in **OCPP Charging Station Management System (CSMS)** complies with universal open EV charging standards.

---

## 1. OCPP Protocol Generations Compared

| Feature | OCPP 1.6-J (JSON) | OCPP 2.0.1 | OCPP 2.1 |
| :--- | :--- | :--- | :--- |
| **Security** | HTTP Basic / TLS (WSS) | mTLS with Client Certificates | Advanced Zero-Trust mTLS |
| **Smart Charging Profiles** | Composite Schedules (`SetChargingProfile`) | Granular Device Variables | Dynamic current ramps in 0.1 A steps |
| **ISO 15118** | Basic | Native Plug & Charge | Bidirectional V2G & V2X |
| **Phase Switching** | Vendor-specific extensions | Standardized device model | Native phase control commands |

---

## 2. Automatic 1-Phase / 3-Phase Switching (1p / 3p)

Under standard **IEC 61851**, EV onboard chargers require a minimum current of **6 A per phase**.

* **3-Phase Minimum**: $6\,\text{A} \times 3 \times 230\,\text{V} = \mathbf{4.14\,\text{kW}}$.
* **1-Phase Minimum**: $6\,\text{A} \times 1 \times 230\,\text{V} = \mathbf{1.38\,\text{kW}}$.

Automatic phase switching dynamically shifts between 1-phase mode (1.4 kW to 3.7 kW) during cloudy periods and 3-phase mode (4.1 kW to 11/22 kW) under peak sunshine, incorporating a mandatory 60–120s safety dead-time to protect vehicle contactors.

---

## 3. Departure Ready (Target-Based Charging)

Specify departure time (e.g., `07:30 AM`) and target battery SoC (e.g., `80 %`). Sharegy maximizes solar surplus during the day and schedules remaining required kilowatt-hours into the lowest-priced nighttime spot market hours.

---

## 4. CSMS Connection Parameters

* **CSMS Endpoint**: `wss://sharegy.de/ocpp/<CHARGE_POINT_ID>`
* **Port**: `443` (TLS)
* **Heartbeat Interval**: `60 seconds`
""",
                "tags": ["ocpp", "ocpp 2.0.1", "ocpp 2.1", "phasenumschaltung", "smart charging", "1p3p", "departure ready", "wallbox"],
                "is_featured": True,
                "sort_order": 4,
            },

            # ---------------------------------------------------------------------
            # 21. WÄRME, ESTRICH-SPEICHER & SOLARES PRE-COOLING
            # ---------------------------------------------------------------------
            {
                "category": cats["optimizer"],
                "slug": "waerme-mpc-estrich-speicher-und-pre-cooling",
                "context_key": "heating",
                "title_de": "Wärme, Estrich-Speicher & Solares Pre-Cooling: Thermische Bauteilaktivierung & MPC",
                "title_en": "Heating, Screed Storage & Solar Pre-Cooling: Thermal Mass Activation & MPC",
                "summary_de": "Prädiktives Lastmanagement für Heizung und Kühlung: Estrich als 10–25 kWh thermischer Speicher (DIN EN 12831), wettergeführte Vorlauftemperatur und solare Raumvorkühlung (Pre-Cooling).",
                "summary_en": "Predictive HVAC load management: Building screed as 10–25 kWh thermal storage (DIN EN 12831), weather-guided flow temperature, and solar AC pre-cooling.",
                "content_de": r"""# Wärme, Estrich-Speicher & Solares Pre-Cooling ♨️❄️🏠

Das Heizungs- und Kühlungs-Modul auf `/app/heating` nutzt die thermische Trägheit deines Gebäudes als virtuellen Großspeicher (**Thermische Bauteilaktivierung**).

---

## 1. Das Konzept: Gebäude als 10–25 kWh Thermobatterie

Ein massiver Betonestrich besitzt enorme Wärmekapazität:
* Durch eine gezielte Vorladung um nur **$+1{,}0\,\text{K}$ bis $+1{,}5\,\text{K}$** nimmt der Baukörper **8 bis 18 kWh thermische Energie** auf.
* Bei einer Wärmepumpe mit Leistungszahl (COP) von 3,5 entspricht dies einer flexiblen Stromaufnahme von **2,5 bis 5,0 kWh**.
* **Der Effekt**: Das Haus bleibt den gesamten Abend über warm, ohne dass die Wärmepumpe in den teuren Spitzenlastzeiten Strom beziehen muss.

---

## 2. Wettergeführte Vorlauftemperatur & Prädiktives MPC (DIN EN 12831)

Sharegy passt die Heizkurve vorausschauend an:
* 📉 **Solares Absenken**: Erkennt die Wetterprognose intensive Sonneneinstrahlung auf Fensterflächen, senkt Sharegy die Vorlauftemperatur rechtzeitig ab, um ein Überhitzen der Wohnräume zu verhindern.
* 📈 **Surplus-Boost (SG-Ready State 3)**: Bei PV-Überschuss wird die Vorlauftemperatur um $+2$ bis $+4\,\text{K}$ angehoben, um kostenlose Wärme im Estrich einzulagern.

---

## 3. Solares Pre-Cooling (Raumkühlung & Klimaanlage im Sommer)

Im Sommer tritt häufig folgendes Dilemma auf:
* Die stärkste Hitze staut sich in den späten Nachmittags- und Abendstunden (17:00–21:00 Uhr) im Gebäude.
* Zu diesem Zeitpunkt sinkt die PV-Erzeugung bereits ab, und Strom an der Börse wird teuer.

### Die Lösung mit Sharegy Pre-Cooling:
1. ☀️ **Mittags-Kältepuffer**: Bei maximalem Solar-Peak (**12:00 bis 15:00 Uhr**) kühlt Sharegy die Räume automatisch um **$1{,}5\,\text{K}$ unter die Solltemperatur** vor (z. B. von $23{,}5^\circ\text{C}$ auf $22{,}0^\circ\text{C}$).
2. 🛡️ **Abend-Entlastung**: Die abgekühlten Wände und Böden halten den Raum bis in die Nacht kühl – die Klimaanlage bleibt in der teuren Abendspitze ausgeschaltet!

---

## 4. Brauchwasserwärmepumpe (BWWP) & Verdichterschutz

* **Solarer Heißwasser-Boost**: Aufheizung des Warmwasserspeichers auf bis zu **$60\text{–}65^\circ\text{C}$** bei PV-Überschuss.
* **Verdichterschutz (Anti-Cycling)**: Mindestlaufzeit von $20\,\text{Minuten}$ und Mindestruhezeit von $15\,\text{Minuten}$ schützen den Wärmepumpen-Kompressor vor vorzeitigem Verschleiß.
""",
                "content_en": r"""# Heating, Screed Storage & Solar Pre-Cooling ♨️❄️🏠

The HVAC module on `/app/heating` leverages the building's thermal mass as a distributed virtual battery (**Thermal Mass Activation**).

---

## 1. The Building as a 10–25 kWh Thermal Battery

Concrete floor screed holds massive thermal capacity:
* A slight pre-charge of **$+1.0\,\text{K}$ to $+1.5\,\text{K}$** stores **8 to 18 kWh of thermal energy**.
* With a heat pump COP of 3.5, this shifts **2.5 to 5.0 kWh of electrical load**.
* **Benefit**: The building maintains comfort throughout the evening without requiring grid power during expensive peak hours.

---

## 2. Model Predictive Control (MPC) & DIN EN 12831 Flow Temperature

* 📉 **Anticipatory Curtailment**: Lowers heating curve hours before solar window irradiance warms the living spaces.
* 📈 **Surplus Boost (SG-Ready State 3)**: Raises flow setpoint by $+2$ to $+4\,\text{K}$ when free solar power is available.

---

## 3. Solar Pre-Cooling (Summer Air Conditioning)

* ☀️ **Midday Cold Storage**: Pre-cools rooms by **$1.5\,\text{K}$ below setpoint** during peak solar production (12:00 to 15:00).
* 🛡️ **Evening Peak Shaving**: Cooled thermal mass keeps interior temperatures comfortable into the night, preventing expensive AC grid consumption.

---

## 4. DHW Heat Pump & Compressor Safeguards

* **Solar Thermal Boost**: Heats domestic hot water tanks up to $60\text{–}65^\circ\text{C}$.
* **Anti-Cycling Locks**: Enforces 20-minute minimum runtime and 15-minute resting intervals.
""",
                "tags": ["wärme", "heizung", "estrich", "pre-cooling", "klimaanlage", "thermische bauteilaktivierung", "mpc", "vorlauftemperatur"],
                "is_featured": True,
                "sort_order": 5,
            },

            # ---------------------------------------------------------------------
            # 22. SEKUNDÄRE AC-ERZEUGER & BALKONKRAFTWERK-BILANZERKENNUNG
            # ---------------------------------------------------------------------
            {
                "category": cats["inverters-meters"],
                "slug": "sekundaere-ac-erzeuger-und-balkonkraftwerk-erkennung",
                "context_key": "producers",
                "title_de": "Sekundäre AC-Erzeuger: Balkonkraftwerke & 2. Wechselrichter sauber bilanzieren",
                "title_en": "Secondary AC Generation: Accurate Balancing for Balcony Solar & 2nd Inverters",
                "summary_de": "Automatische Erkennung und mathematisch saubere Bilanzierung ungebundener AC-Erzeuger (Balkonkraftwerke, Mikrowechselrichter, 2. Dachanlage) zur Vermeidung von Fehlberechnungen im Hausverbrauch.",
                "summary_en": "Automated detection and accurate mathematical balancing of independent AC generators (balcony solar, microinverters, 2nd rooftop arrays) to prevent house load distortion.",
                "content_de": r"""# Sekundäre AC-Erzeuger & Balkonkraftwerke sauber bilanzieren ☀️🔌

Viele Haushalte erweitern ihre Photovoltaik um zusätzliche AC-Erzeuger: ein **Balkonkraftwerk (600 W / 800 W)** an der Steckdose, ein zweiter Garagen-Wechselrichter oder Mikrowechselrichter (Hoymiles, Enphase, Deye).

---

## 1. Das Problem ungebundener AC-Erzeuger im Hausnetz

Klassische Wechselrichter-Systeme messen die Solarerzeugung nur an den eigenen DC-Strings. Speist nun ein separates Balkonkraftwerk Strom auf einer Phase ins Hausnetz ein, passiert Folgendes:

* ❌ **Falsche Hausverbrauchsanzeige**: Der Smart Meter am Netzübergabepunkt sieht weniger Netzbezug und interpretiert dies fälschlicherweise als gesunkenen Hausverbrauch (oder sogar als negativen Hausverbrauch).
* ❌ **Fehlerhafte Solarstatistik**: Die tatsächliche Gesamterzeugung der Solaranlagen wird um Hunderte Kilowattstunden pro Jahr zu niedrig ausgewiesen.
* ❌ **Verfälschter Autarkiegrad**: Die Autarkie- und Eigenverbrauchsquoten stimmen mathematisch nicht mehr.

---

## 2. Die physikalische Bilanzkorrektur in Sharegy

Sharegy löst dieses Problem durch eine entkoppelte Energiebilanzierung:

$$P_\text{Solar, Gesamt} = P_\text{PV, Haupt-WR} + \sum P_\text{Sekundär, AC}$$

$$P_\text{Haus, Real} = P_\text{Netzbezug} + P_\text{Solar, Gesamt} + P_\text{Batterie, Entladung} - P_\text{Netzeinspeisung} - P_\text{Batterie, Ladung}$$

Dadurch wird der erzeugte Strom des Balkonkraftwerks physikalisch exakt als **Solarerzeugung** bilanziert und der echte Verbrauch aller Haushaltsgeräte transparent dargestellt.

---

## 3. Anbindungsmöglichkeiten in Sharegy

Unter `/app/producers` im Bereich **„Sekundäre AC-Erzeuger“** kannst du beliebig viele zusätzliche Erzeuger anlegen:

### Methode A: Smart Plug / Zwischenstecker (Empfohlen)
* Stecke das Balkonkraftwerk an eine smarte Steckdose mit Energiemessung (z. B. **Shelly Plus 1PM**, **Shelly Plug S**, **Tasmota**, **Zigbee**).
* Wähle das Gerät im Dropdown-Menü als Messpunkt aus.
* Sharegy addiert die Live-Wattwerte sekundengenau zur Gesamterzeugung hinzu.

### Methode B: Direkte Cloud- / API-Kopplung
* Binde die Monitoring-Cloud des Mikrowechselrichters an (z. B. Hoymiles DTU, Enphase Envoy, SolarMAN Deye).

### Methode C: Automatische Bilanzerkennung
* Erkennt Sharegy anhand des Netzübergabepunkts und der regionalen Einstrahlungsdaten ein Einspeisemuster ohne registrierte PV-Erzeugung, schlägt das System automatisch das Anlegen eines sekundären Erzeugers vor.

---

## 4. Schritt-für-Schritt Einrichtung

1. Öffne **Erzeuger & Speicher** (`/app/producers`).
2. Scrolle zu **„Automatische Erkennung sekundärer AC-Erzeuger (2. Wechselrichter / BKW)“**.
3. Klicke auf **„2. Anlage benennen & hinzufügen“**.
4. Vergib einen Namen (z. B. *„Balkonkraftwerk Süd 800 W“*) und verknüpfe den Leistungssensor.
5. Speichern – ab sofort stimmt deine Energiebilanz auf das Watt genau!
""",
                "content_en": r"""# Secondary AC Generation: Accurate Balancing for Balcony Solar & 2nd Inverters ☀️🔌

Many homes expand their solar capacity with secondary generators: **plug-in balcony solar (600 W / 800 W)**, garage inverters, or microinverter arrays (Hoymiles, Enphase, Deye).

---

## 1. The Challenge of Unbound AC Generation

Standard hybrid inverters only measure generation on their own DC strings. When a secondary AC inverter feeds power directly into a household circuit:

* ❌ **Distorted Home Consumption**: Main grid meters observe lower grid import and misinterpret generation as reduced household load (or even negative consumption).
* ❌ **Underreported Solar Yield**: Solar statistics miss hundreds of kilowatt-hours annually.
* ❌ **Skewed Autarky Metrics**: Self-consumption and energy independence ratios become mathematically invalid.

---

## 2. Physical Energy Balance Correction in Sharegy

Sharegy applies decoupled power-flow equations:

$$P_\text{Solar, Total} = P_\text{PV, Main Inverter} + \sum P_\text{Secondary, AC}$$

$$P_\text{Home, Actual} = P_\text{Grid Import} + P_\text{Solar, Total} + P_\text{Battery Discharge} - P_\text{Grid Export} - P_\text{Battery Charge}$$

Every watt from balcony solar is correctly categorized as clean solar generation.

---

## 3. Integration Methods

1. **Smart Plug / Relay (Recommended)**: Connect balcony inverters via a power-measuring smart switch (e.g., Shelly Plus 1PM, Shelly Plug S, Tasmota).
2. **Direct Cloud / Gateway Ingestion**: Link manufacturer monitoring gateways (Hoymiles DTU, Enphase Envoy).
3. **Automated Signature Detection**: Matches unmetered daytime export signatures with regional solar irradiance telemetry.
""",
                "tags": ["balkonkraftwerk", "bkw", "sekundärerzeuger", "wechselrichter", "bilanzierung", "autarkie", "ac-erzeugung", "mikrowechselrichter"],
                "is_featured": True,
                "sort_order": 5,
            },

            {
                "category": cats["inverters-meters"],
                "slug": "benoetigte-messwerte-und-geraetebindung",
                "context_key": "devices",
                "title_de": "Welche Messwerte benötigt Sharegy? (Herstellerunabhängige Übersicht)",
                "title_en": "Which Telemetry Metrics Does Sharegy Require? (Universal Guide)",
                "summary_de": "Vom reinen Verbraucher-Tracking bis zum Hybrid-System mit Speicher: Welche physikalischen Größen für Bilanzierung, Autarkie und Sub-Metering nötig sind.",
                "summary_en": "From dynamic tariff tracking without PV to complex solar storage hybrids: What physical metrics are required for energy balance and sub-metering.",
                "content_de": r"""# Welche Messwerte benötigt Sharegy? ⚡📊

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
| **Spannung** | **Volt (V)** | `voltage`, `battery_voltage`, `phase_voltage` | Netzstabilität, $P = U 	imes I$ Ersatzberechnung |
| **Ladestand** | **%** | `soc`, `battery_soc`, `battery_level` | Speicherstand, EMS-Ladelimits und Entladepuffer |
| **Zählerstand** | **kWh** | `energy`, `energy_in`, `energy_out`, `total_yield` | Exakte Tages-, Monats- und Jahresbilanzierung |

---

## 3. Die mathematische Grundregel für das Gesamthaus: *„3 von 4 reichen aus!“*

Im Haushalt gilt physikalisch immer der Knotenpunktsatz:
$$\text{Hausverbrauch } (P_{\text{Load}}) = \text{PV-Erzeugung } (P_{\text{PV}}) + \text{Batterieleistung } (P_{\text{Bat}}) + \text{Netzübergabe } (P_{\text{Grid}})$$

* Wenn du **3 dieser 4 Werte** lieferst, errechnet Sharegy den 4. Wert automatisch zu 100 % fehlerfrei.
* Lieferst du alle 4 Werte (z. B. aus einem modernen Wechselrichter mit Smart Meter), gleicht Sharegy die Werte zusätzlich ab.

---

## 4. Häufige Frage: Warum habe ich 2 Datenpunkte für die Batterie (Strom in A und Leistung in W)?
Manche Wechselrichter (wie z. B. Sungrow) liefern die Batterieleistung immer als positive Zahl und die Richtung separat über den **Batteriestrom in Ampere (A)**:
* **Batteriestrom < 0 A**: Batterie lädt aus PV/Netz.
* **Batteriestrom > 0 A**: Batterie entlädt ins Haus.

In Sharegy wird hierfür **nur 1 virtueller Batteriespeicher** angelegt: In den Einstellungen des Speichers ordnest du die Wirkleistung (W) als *Ladeleistung* und den Strom (A) als *Batteriestrom* zu. Sharegy trennt Lade- und Entladezyklen daraufhin automatisch und physikalisch exakt!
""",
                "content_en": r"""# Telemetry Metrics & Universal Device Mapping ⚡📊

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
| **Voltage** | **Volt (V)** | `voltage`, `battery_voltage` | Grid stability, backup $P = U 	imes I$ power calculations |
| **State of Charge** | **%** | `soc`, `battery_soc`, `battery_level` | Battery status, smart reserve thresholds, optimization |
| **Energy Totals** | **kWh** | `energy`, `energy_in`, `energy_out` | Daily, monthly, and yearly fiscal energy balances |
""",
                "tags": ["telemetry", "messwerte", "watt", "ampere", "volt", "soc", "kwh", "hardware"],
                "is_featured": True,
                "sort_order": 1,
            },
            {
                "category": cats["inverters-meters"],
                "slug": "sma-sungrow-modbus-tcp-einrichten",
                "context_key": "devices",
                "title_de": "Wechselrichter (SMA, Sungrow, Fronius, Deye) via Home Assistant anbinden",
                "title_en": "Connecting Inverters (SMA, Sungrow, Fronius, Deye) via Home Assistant",
                "summary_de": "Da Modbus TCP ein rein lokales Netzwerkprotokoll ist, liest Home Assistant oder ioBroker den Wechselrichter aus und streamt die Datenpunkte in die Sharegy Cloud.",
                "summary_en": "Since Modbus TCP operates locally within your LAN, Home Assistant or ioBroker reads the inverter and streams telemetry into Sharegy Cloud.",
                "content_de": r"""# Wechselrichter & Speicher via Home Assistant Bridge anbinden ☀️🏠

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
                "content_en": r"""# Connecting Inverters & Storage via Home Assistant Bridge ☀️🏠

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
                "sort_order": 1,
            },
            {
                "category": cats["forecast"],
                "slug": "solar-prognose-und-genauigkeit",
                "context_key": "forecast",
                "title_de": "Solar-Prognose, Wettermodelle & Genauigkeitsabgleich (%-Score)",
                "title_en": "Solar Forecasting, Weather Models & Accuracy Score",
                "summary_de": "Wie die Hybrid-Prognose aus Wetterdaten, Sensor.Community und ML berechnet wird und wie der Güte-Score funktioniert.",
                "summary_en": "How the hybrid solar forecast combines numerical weather predictions with local observations and ML.",
                "content_de": r"""# Solar-Prognose & Genauigkeitsabgleich

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
                "content_en": r"""# Solar Forecasting & Accuracy Scoring

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
                "sort_order": 1,
            },
            {
                "category": cats["forecast"],
                "slug": "lastprognose-und-haushaltsverbrauch",
                "context_key": "forecast",
                "title_de": "Haushalts-Lastprognose & Wochentags-Profile",
                "title_en": "Household Load Forecasting & Weekly Profiles",
                "summary_de": "So prognostiziert Sharegy den Haushaltsverbrauch anhand historischer Wochentags- und Stundenmuster.",
                "summary_en": "How Sharegy predicts domestic consumption using historical weekday and hourly load profiles.",
                "content_de": r"""# Haushalts-Lastprognose & Verbrauchsmuster

Die Lastprognose ermittelt für jede Stunde der kommenden 24 bis 48 Stunden den erwarteten Strombedarf deines Haushalts.

## Berechnungsmethode
* **Wochentags-Cluster**: Das System unterscheidet automatisch zwischen Werktagen (Montag bis Freitag) und Wochenenden (Samstag/Sonntag).
* **Gleitender Durchschnitt**: Verbräuche der letzten 4 bis 8 Wochen fließen gewichtet ein, um saisonale Veränderungen (z. B. Heizperiode) abzubilden.
* **Grundlast-Erkennung**: Konstante Ruhelasten in der Nacht werden isoliert, um Peaks von Standard-Verbräuchen zu trennen.

> [!NOTE]
> Zusammen mit der Solar-Prognose bildet die Lastprognose die mathematische Grundlage für die **Batterie-SoC-Simulation** und den **Smart Energy Optimizer**.
""",
                "content_en": r"""# Household Load Forecasting & Daily Profiles

The load forecasting engine estimates household demand for every hour of the upcoming 24 to 48 hours.

## Methodology
* **Weekday vs. Weekend Clustering**: Differentiates working days from weekends.
* **Rolling Historical Averages**: Weighted 4- to 8-week consumption patterns adapt to seasonal shifts.
* **Baseload Isolation**: Distinguishes continuous standby loads from active peaks.
""",
                "tags": ["lastprognose", "verbrauch", "profile", "grundlast", "wochentage"],
                "is_featured": False,
                "sort_order": 1,
            },
            {
                "category": cats["optimizer"],
                "slug": "smart-energy-optimizer-funktionsweise",
                "context_key": "optimizer",
                "title_de": "Smart Energy Optimizer: Zeitfenster (1h/2h/4h) & Fahrplan optimal nutzen",
                "title_en": "Smart Energy Optimizer: 1h/2h/4h Time Windows & Smart Scheduling",
                "summary_de": "So ermittelt der Optimizer die günstigsten Zeitfenster für Wallbox, Wärmepumpe und Haushaltsgeräte.",
                "summary_en": "How the optimizer identifies the best time slots for EV charging, heat pump heating, and home appliances.",
                "content_de": r"""# Smart Energy Optimizer & EMS

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
                "content_en": r"""# Smart Energy Optimizer & EMS

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
                "sort_order": 1,
            },
            {
                "category": cats["tariffs"],
                "slug": "stromtarife-und-stichtagsberechnung",
                "context_key": "tariffs",
                "title_de": "Strompreise, Stichtage & Tarifhistorie verwalten",
                "title_en": "Managing Electricity Tariffs, Effective Dates & Price History",
                "summary_de": "Wie Tarifänderungen mit Stichtag (valid_from) erfasst werden, damit historische Energiebilanzen stimmig bleiben.",
                "summary_en": "How to record tariff changes with a valid-from date to preserve accurate historical billing.",
                "content_de": r"""# Strompreise & Tarifhistorie

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
                "content_en": r"""# Tariffs & Historical Precision

Sharegy uses date-effective tariffs (`valid_from`) to guarantee exact retroactive energy accounting.

## Setting Up a Tariff Change
1. Go to **Electricity Tariffs & Prices**.
2. Set the **Valid from** date (e.g., `2026-09-01`).
3. Enter the new energy rate (ct/kWh), base fee (€/month), or feed-in tariff.
4. Click **Save**.
""",
                "tags": ["tariffs", "strompreis", "stichtag", "historie", "einspeisung", "arbeitspreis"],
                "is_featured": False,
                "sort_order": 1,
            },
            {
                "category": cats["tariffs"],
                "slug": "dynamische-stromtarife-und-tibber",
                "context_key": "tariffs",
                "title_de": "Dynamische Börsenstrompreise & Tibber API Anbindung",
                "title_en": "Dynamic Spot Tariffs & Tibber API Integration",
                "summary_de": "Anbindung von Day-Ahead-Börsenpreisen via Energy-Charts, SMARD und Tibber API.",
                "summary_en": "Connecting day-ahead spot market prices via Energy-Charts, SMARD, and Tibber API.",
                "content_de": r"""# Dynamische Stromtarife & Börsenpreise

Dynamische Stromtarife ermöglichen es dir, Strom genau dann aus dem Netz zu beziehen, wenn er an der europäischen Strombörse (EPEX Spot DE-LU) am günstigsten ist.

## Unterstützte Preisquellen
1. **Energy-Charts (Fraunhofer ISE)**: Primäre Echtzeit- und Day-Ahead-Schnittstelle.
2. **SMARD (Bundesnetzagentur)**: Automatischer Hochverfügbarkeits-Fallback.
3. **Tibber API**: Direkte Synchronisation deiner kundenspezifischen Endkundenpreise inklusive Netzgebühren und Umlagen.

## Preis-Formel
Für eigene dynamische Tarife kannst du flexible Formeln hinterlegen (z. B. `spot * 1.19 + 0.15` für Mehrwertsteuer und 15 ct/kWh fixe Netzentgelte).
""",
                "content_en": r"""# Dynamic Electricity Tariffs & Spot Market Integration

Dynamic tariffs allow you to consume grid electricity when spot market prices on the European Power Exchange (EPEX Spot) are lowest.

## Supported Data Providers
1. **Energy-Charts (Fraunhofer ISE)**: Primary day-ahead spot price source.
2. **SMARD (German Federal Network Agency)**: Automatic high-availability fallback.
3. **Tibber API**: Direct synchronization of your real retail electricity price.
""",
                "tags": ["tibber", "börsenstrom", "epex", "smard", "dynamisch", "dayahead"],
                "is_featured": True,
                "sort_order": 1,
            },
            {
                "category": cats["alerts"],
                "slug": "alarmzentrale-und-anomalieerkennung",
                "context_key": "alerts",
                "title_de": "Alarm- & Notifikationszentrale: Echtzeit-Regeln & Anomalieerkennung",
                "title_en": "Alert & Notification Center: Live Rules & Anomaly Detection",
                "summary_de": "Übersicht aller 8 automatisierten Überwachungsregeln für Ertragsausfälle, Tiefentladeschutz und Dauerlasten.",
                "summary_en": "Overview of the 8 automated health checks for solar yield drops, battery protection, and baseload alarms.",
                "content_de": r"""# Alarm- & Notifikationszentrale

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
                "content_en": r"""# Alert & Notification Center

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
                "sort_order": 1,
            },
            {
                "category": cats["billing"],
                "slug": "virtuelle-zaehler-und-submetering",
                "context_key": "billing",
                "title_de": "Virtuelle Zähler, Sub-Metering & Mieterstrom-Abrechnung",
                "title_en": "Virtual Meters, Sub-Metering & Multi-Tenant Billing",
                "summary_de": "Aufteilung des Gesamtstroms auf einzelne Verbraucher (Wallbox, Wärmepumpe, Einliegerwohnung) und PDF-Abrechnung.",
                "summary_en": "Allocating total electricity across submeters (EV charger, heat pump, rental unit) with PDF reports.",
                "content_de": r"""# Virtuelle Zähler & Sub-Metering

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
                "content_en": r"""# Virtual Meters & Sub-Metering

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
                "sort_order": 1,
            },
            {
                "category": cats["devices-protocols"],
                "slug": "mqtt-und-smart-home-integration",
                "context_key": "devices",
                "title_de": "MQTT, ioBroker, Node-RED & Smart-Home Gateways",
                "title_en": "Connecting MQTT, ioBroker, Node-RED & Gateways",
                "summary_de": "Integration von Smart-Home-Zentralen und Custom-Zählern über den integrierten MQTT-Broker und REST-APIs.",
                "summary_en": "Integrating smart home systems and custom telemetry via MQTT broker and REST APIs.",
                "content_de": r"""# MQTT & Smart Home Gateway Integration

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
                "content_en": r"""# MQTT & Smart Home Gateway Integration

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
                "sort_order": 1,
            },
            {
                "category": cats["devices-protocols"],
                "slug": "grafana-integration-und-cockpit-dashboards",
                "context_key": "interfaces",
                "title_de": "Grafana Integration & Energy Cockpit Dashboards",
                "title_en": "Grafana Integration & Energy Cockpit Dashboards",
                "summary_de": "Einrichtung der Grafana JSON/Infinity Datasource, Token-Authentifizierung und Nutzung des fertigen Sharegy Cockpit Dashboards.",
                "summary_en": "Setting up Grafana JSON/Infinity datasource, token authentication, and importing the Sharegy Energy Cockpit dashboard.",
                "content_de": r"""# Grafana Integration & Energy Cockpit

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
                "content_en": r"""# Grafana Integration & Energy Cockpit

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
                "sort_order": 1,
            },
            {
                "category": cats["devices-protocols"],
                "slug": "home-assistant-integration-und-telemetrie-push",
                "context_key": "interfaces",
                "title_de": "Home Assistant Native Integration & 1-Klick Entity Bridge",
                "title_en": "Home Assistant Native Integration & 1-Click Entity Bridge",
                "summary_de": "Vollständige Anleitung für die offizielle Sharegy Home Assistant Integration mit 1-Klick Entity Picker, Outbound WSS und 48h Offline-Puffer.",
                "summary_en": "Complete guide for the official Sharegy Home Assistant integration with 1-click entity selector, outbound WSS, and 48h offline buffer.",
                "content_de": r"""# Sharegy Cloud Energy Bridge für Home Assistant ⚡🏠

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
                "content_en": r"""# Sharegy Cloud Energy Bridge for Home Assistant ⚡🏠

The official **Sharegy Home Assistant Integration** streams all your local smart home and energy data securely to the Sharegy Cloud without firewall changes or open ports.

## 🌟 Key Features
* **🎯 1-Click Entity Picker**: Select your energy sensors (Grid, Solar PV, Battery Storage, EV Charger, Heat Pump, Smart Plugs) natively inside the HA UI.
* **⚡ Outbound WebSocket (WSS)**: Secure streaming directly to `wss://sharegy.de/ws/energy/<TOKEN>/` over standard Port 443.
* **💾 48h SQLite Store & Forward Buffer**: If your internet connection drops, telemetry is buffered locally and automatically synchronized once reconnected.
* **🔄 Live Options Flow**: Easily modify mapped sensors anytime under *Settings → Devices & Services → Sharegy → Configure*.
""",
                "tags": ["homeassistant", "custom component", "hacs", "websocket", "offline buffer", "entity picker", "shelly"],
                "is_featured": True,
                "sort_order": 1,
            },
            {
                "category": cats["devices-protocols"],
                "slug": "matter-1-3-energy-management-und-hub",
                "context_key": "interfaces",
                "title_de": "Matter 1.3 Energy Hub (Smart Plugs, EVSE & Inverter)",
                "title_en": "Matter 1.3 Energy Hub (Smart Plugs, EVSE & Inverters)",
                "summary_de": "Kopplung und Steuerung moderner Matter-Geräte via Thread/Wi-Fi/IP unter Nutzung des CSA Matter 1.3 Energy Management Standards.",
                "summary_en": "Commissioning and controlling Matter devices via Thread/Wi-Fi/IP utilizing the CSA Matter 1.3 Energy Management standard.",
                "content_de": r"""# Matter 1.3 Energy Management Hub

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
                "content_en": r"""# Matter 1.3 Energy Management Hub

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
                "sort_order": 1,
            },
        ]
        for adata in articles_data:
            HelpArticle.objects.update_or_create(
                slug=adata["slug"],
                defaults=adata,
            )

        self.stdout.write(self.style.SUCCESS(f"[OK] Erfolgreich {len(categories_data)} Kategorien und {len(articles_data)} Handbuch-Artikel in DE & EN initialisiert!"))

