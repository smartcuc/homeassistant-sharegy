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
                "title_de": "Abrechnung, Tarife & PDF-Belege",
                "title_en": "Billing, Tariffs & Statements",
                "description_de": "Haushaltsabrechnungen, Reststrom- und Solartarife, PDF-Belege und DATEV-Exporte.",
                "description_en": "Household billing, grid tariffs, PDF statements, and DATEV exports.",
                "sort_order": 8,
            },
            {
                "key": "energy-sharing",
                "icon": "🏘️",
                "title_de": "Energy Sharing, Quartiere & Mieterstrom",
                "title_en": "Energy Sharing, Communities & Tenant Power",
                "description_de": "§ 42b EnWG Gemeinschaftliche Gebäudeversorgung, Liegenschafts-Verwaltung, 15m-Sharing-Matrix und Mieter-Abrechnungen.",
                "description_en": "§ 42b EnWG collective building supply, property management, 15-minute sharing matrix, and resident settlement.",
                "sort_order": 9,
            },
            {
                "key": "partners",
                "icon": "🔧",
                "title_de": "Partner, Solarteure & Flottenmanagement",
                "title_en": "Partners, Installers & Fleet Management",
                "description_de": "Kundenanlagen-Onboarding, Inbetriebnahme, 3-Sekunden-Diagnosetests, Health-Scores und Fachpartner-Service.",
                "description_en": "Customer onboarding, commissioning, 3-second diagnostic checks, health scores, and service workflows.",
                "sort_order": 10,
            },
            {
                "key": "admin-governance",
                "icon": "🛡️",
                "title_de": "Administration, Quartiere & VPP",
                "title_en": "Administration, Communities & VPP",
                "description_de": "Leitfäden für Portfoliomanager, Mieterstrom (§ 42a), GGV (§ 42b), Bürgerenergiegenossenschaften, VPP-Flexibilitätsaggregate & Partner-Flotten.",
                "description_en": "Comprehensive guides for portfolio managers, tenant power (§ 42a), collective supply (§ 42b), energy sharing cooperatives, VPP aggregators & partner fleets.",
                "sort_order": 12,
            },
            {
                "key": "devices-protocols",
                "icon": "🔌",
                "title_de": "Geräte, Schnittstellen & Protokolle",
                "title_en": "Devices, Interfaces & Protocols",
                "description_de": "Integration von OCPP 1.6-J CSMS, Home Assistant, Shelly WSS, wMSB Discovergy, Modbus TCP und Selbsttest.",
                "description_en": "Integration with OCPP 1.6-J CSMS, Home Assistant, Shelly WSS, wMSB Discovergy, Modbus TCP, and Self-Test.",
                "sort_order": 11,
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
| **Fronius** | GEN24 Plus, Symo, Primo, Tauro | `Solar.web E-Mail`, `Passwort` (oder lokale IP) |
| **SolarEdge** | SE-Serie, HD-Wave, StorEdge, Optimierer | `Standort-ID (site_id)`, `API-Schlüssel (api_key)` |
| **Kostal** | PLENTICORE plus, PIKO IQ, PIKO MP, BYD | `Anlagen-ID (plant_id)`, `API-Schlüssel (api_key)` |
| **Growatt** | MIN, MOD, MID, SPH, SPA, ARK-Speicher | `Benutzername / E-Mail`, `Passwort` (oder OpenAPI Token) |
| **Deye** | SUN 3–12k Hybrid, Mikrowechselrichter | `AppID`, `AppSecret`, `E-Mail`, `Passwort`, `Geräte-SN` |
| **Huawei** | SUN2000 3–30KTL, LUNA2000 Speicher | `SystemCode`, `SecretKey`, `Anlagencode (Plant Code)` |
| **GoodWe** | ET, EH, BH, ES Hybrid, Lynx Home | `SEMS Account (E-Mail)`, `Passwort`, `PowerStation-ID` |
| **Solis** | Solis RHI, S5, S6 Hybrid | `Key-ID`, `Key-Secret`, `Station-ID` |
| **Victron** | MultiPlus-II, Quattro, Cerbo GX, SmartSolar | `VRM Personal Access Token`, `Site-ID (Installation-ID)` |

---

## 2. Einrichtung je Hersteller

### ☀️ Fronius (Solar.web Cloud & Lokale Anbindung)
Fronius unterstützt zwei besonders komfortable Wege:
* **Weg 1 (Direkt-Cloud via Solar.web)**: Gib einfach deine gewohnten Solar.web Zugangsdaten (**E-Mail und Passwort**) ein. Sharegy synchronisiert deine Anlage automatisch.
* **Weg 2 (Lokal via Home Assistant oder ioBroker)**: Falls du Home Assistant oder ioBroker nutzt, binde Fronius direkt im LAN über die lokale Solar API v1 ein und leite die Sensoren per 1-Klick über die Sharegy Home Assistant / ioBroker Integration weiter.

### ☀️ Sungrow (iSolarCloud OpenAPI & OAuth)
1. Logge dich unter [isolarcloud.eu](https://www.isolarcloud.eu) ein.
2. In der Adresszeile deines Browsers findest du die **Power Station ID (`ps_id`)** (`...stationDetail?ps_id=1234567`).
3. Trage deine Zugangsdaten ein und klicke auf **„Verbindung testen“**.

### ☀️ Growatt (ShineServer & ShinePhone)
1. Gib deinen normalen ShineServer / ShinePhone Benutzernamen und dein Passwort ein.
2. Sharegy ermittelt automatisch deine Anlage und liest alle Hybrid-, PV- und Speicherdaten aus.

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
1. **Fronius** (Solar.web Direct & Local Solar API)
2. **Sungrow** (iSolarCloud OpenAPI & Web)
3. **Growatt** (ShineServer & OpenAPI)
4. **SolarEdge** (Monitoring Portal API)
5. **Kostal** (Solar Portal API)
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
            # ---------------------------------------------------------------------
            # 10. ENERGY SHARING, GGV & MIETERSTROM: DER GROSSE VERGLEICHS-LEITFADEN
            # ---------------------------------------------------------------------
            {
                "category": cats["energy-sharing"],
                "slug": "mieterstrom-ggv-und-energy-sharing-unterschiede",
                "context_key": "energy_sharing_guide",
                "title_de": "Mieterstrom (§ 42a), GGV (§ 42b) & Energy Sharing: Unterschiede, Rechte & Abrechnung",
                "title_en": "Tenant Electricity (§ 42a), Collective Building Supply (§ 42b) & Energy Sharing Explained",
                "summary_de": "Der vollständige Vergleich: Klassischer Mieterstrom vs. Gemeinschaftliche Gebäudeversorgung (GGV) vs. Regionales Energy Sharing mit Prosumern.",
                "summary_en": "The definitive guide explaining the differences between full-supply tenant power (§ 42a), collective building supply (§ 42b), and prosumer energy sharing.",
                "content_de": r"""# ⚡ Mieterstrom (§ 42a), GGV (§ 42b) & Energy Sharing im Vergleich

In der modernen Energiewirtschaft und im Sharegy-Ökosystem unterscheiden wir zwischen drei grundlegend verschiedenen Modellen für die gemeinsame Nutzung von Solarstrom:

---

## 📊 1. Die drei Modelle im tabellarischen Schnellvergleich

| Merkmal | 🏢 1. Mieterstrom (§ 42a EnWG) | 🏘️ 2. GGV / Quartier (§ 42b EnWG) | ⚡ 3. Energy Sharing (Bürgerenergie / RED II) |
| :--- | :--- | :--- | :--- |
| **Netznutzung** | **Keine** Durchleitung durch das öffentliche Netz (hinter dem Summenzähler). | **Keine** Durchleitung durch das öffentliche Netz (im selben Gebäude / Grundstück). | **MIT Durchleitung** durch das öffentliche Verteilnetz (bilanzielles Sharing). |
| **Teilnehmer-Rollen** | **Reine Consumer (Mieter)**. | **Wohnungseigentümer / Mieter** (nach MEA oder dynamisch). | **Prosumer** (Einspeiser) & **Consumer** (Abnehmer). |
| **Erzeugung** | Zentrale Dachanlage des Vermieters / Contractors. | Gemeinsame Anlage auf dem Gebäude (z. B. WEG). | **Viele dezentrale Anlagen** verschiedener Prosumer im Verteilnetz. |
| **Vertragsmodell** | **Vollversorgungsvertrag** (Vermieter liefert Solar- UND Reststrom aus einer Hand). | **Reine interne Aufteilung** (Jeder Bewohner behält seinen eigenen Reststromvertrag). | **Sharing-Gemeinschaftsvertrag** (Jeder behält eigenen Versorger + wMSB-Allokation). |
| **Finanzfluss** | Mieter zahlt monatliche Gesamtrechnung an Vermieter. | Interne Abrechnung des Solarstroms / Umlage der Anlagenkosten. | **Zweiseitig**: <br>• **Prosumer** erhält Sharing-Einspeisevergütung.<br>• **Consumer** zahlt reduzierten Sharing-Bezugspreis. |
| **Sharegy Cockpit** | `/app/tenant` (Liegenschafts-Dashboard) | `/app/tenant` (Gebäude-Wizard, MEA, Virtueller Summenzähler) | `/app/community` (Prosumer- & Consumer-Cockpit) |

---

## 🏢 Modell 1: Mieterstrom (§ 42a EnWG)

Beim klassischen Mieterstrom tritt der Vermieter oder ein beauftragter Energiedienstleister (Contractor) als **Vollversorger** auf.

* **Rechte & Pflichten**: Der Lieferant muss die Mieter zu 100 % mit Strom versorgen (auch wenn keine Sonne scheint). Er kauft Reststrom an der Strombörse oder beim Vorlieferanten zu.
* **Rechnungsstellung**: Der Mieter erhält eine einzige Gesamtrechnung für seinen kompletten Stromverbrauch.
* **Gesetzliche Vorgabe**: Der Mieterstrompreis darf maximal 90 % des örtlichen Grundversorgertarifs betragen.

---

## 🏘️ Modell 2: Gemeinschaftliche Gebäudeversorgung (GGV nach § 42b EnWG)

Mit dem Solarpaket I hat der Gesetzgeber die **Gemeinschaftliche Gebäudeversorgung** geschaffen, um die bürokratischen Hürden des Mieterstroms abzubauen:

* **Keine Lieferantenpflichten**: Die WEG oder der Vermieter wird **nicht** zum Vollversorger.
* **Eigener Reststromvertrag**: Jede Mietpartei / jeder Eigentümer behält weiterhin seinen bestehenden Vertrag mit einem frei gewählten Stromanbieter.
* **15-Minuten-Aufteilung**: Sharegy verteilt den erzeugten Solarstrom im 15-Minuten-Takt entweder **statisch nach Miteigentumsanteilen (MEA)** oder **dynamisch nach zeitgleichem Verbrauch**.
* **Abrechnung**: Sharegy generiert monatlich einen reinen **Solarstrom-Nachweis** für den im Haus genutzten Strom.

---

## ⚡ Modell 3: Regionales Energy Sharing (Bürgerenergie / EU RED II)

Energy Sharing ermöglicht es Bürgerinnen, Bürgern und Prosumern, Strom über das **öffentliche Mittel- und Niederspannungsnetz** hinweg miteinander zu teilen:

* **Dezentraler Erzeuger-Pool**: Prosumer mit PV-Anlagen, Heimspeichern oder Windkraftanlagen speisen ihren Überschussstrom ins Verteilnetz ein.
* **Doppelter wirtschaftlicher Hebel**:
  1. **Prosumer** erhalten für ihren geteilten Strom eine attraktive **Sharing-Einspeisevergütung** (z. B. 10 Ct/kWh), die über der gesetzlichen EEG-Einspeisevergütung liegt.
  2. **Consumer** im selben Verteilnetzgebiet beziehen diesen Ökostrom zu einem günstigen **Sharing-Tarif** (z. B. 12–15 Ct/kWh) und sparen gegenüber dem Netzstrom.
* **Bilanzieller Ausgleich**: Sharegy und der wettbewerbliche Messstellenbetreiber (wMSB) führen im 15-Minuten-Raster den bilanziellen Abgleich durch.

---

## 🧭 Wo finde ich was in Sharegy?

1. **Liegenschafts-Admins & WEG-Verwalter (GGV & Mieterstrom)**:
   * Gehe zu **`/app/tenant`**. Nutze den 3-Schritte-Gebäude-Wizard, pflege MEA-Anteile und verwalte den Virtuellen Summenzähler.
2. **Mitglieder einer regionalen Energiegemeinschaft (Energy Sharing)**:
   * Gehe zu **`/app/community`**. Sieh deine persönliche Einspeisung (als Prosumer) oder deinen Bezug (als Consumer) sowie deine monatlichen Nachweise und Gutschriften.
""",
                "content_en": r"""# ⚡ Tenant Electricity (§ 42a), Collective Building Supply (§ 42b) & Energy Sharing

Understanding the key differences between on-site building supply and regional prosumer energy sharing in the Sharegy platform.

## 📊 1. Quick Comparison Matrix

| Feature | 🏢 1. Tenant Power (§ 42a EnWG) | 🏘️ 2. Collective Supply / GGV (§ 42b EnWG) | ⚡ 3. Regional Energy Sharing (RED II) |
| :--- | :--- | :--- | :--- |
| **Grid Usage** | **No** public grid transit (behind local master meter). | **No** public grid transit (within the building/property). | **WITH transit** over the public distribution grid. |
| **Roles** | **Pure Consumers (Tenants)**. | **Apartment Owners / Tenants** (MEA or dynamic split). | **Prosumers** (Feeders) & **Consumers** (Offtakers). |
| **Generation** | Single central roof PV system. | Shared building PV system. | **Multiple distributed prosumer assets** in the region. |
| **Contract** | **Full supply contract** (Solar + grid residual from one source). | **On-site allocation only** (Each resident keeps their own residual grid provider). | **Sharing community membership** (15-min smart meter allocation). |
| **Dashboard** | `/app/tenant` | `/app/tenant` (Building Wizard, MEA, Master Meter) | `/app/community` (Prosumer & Consumer Cockpit) |
""",
                "tags": ["energy-sharing", "ggv", "mieterstrom", "enwg", "prosumer", "consumer", "abrechnung"],
                "is_featured": True,
                "sort_order": 1,
            },
            {
                "category": cats["energy-sharing"],
                "slug": "tenant-admin-leitfaden-mieterstrom-und-vpp",
                "context_key": "tenant_admin_guide",
                "title_de": "Tenant-Admin Leitfaden: Virtueller Summenzähler, § 42b GGV & PDF-Abrechnungen",
                "title_en": "Tenant-Admin Guide: Virtual Master Meter, § 42b Collective Supply & PDF Invoices",
                "summary_de": "Der vollständige Leitfaden für Liegenschafts-Admins, Vermieter und WEGs: 15m NAP-Saldierung, MEA-Aufteilungsschlüssel, PDF-Abrechnungen und VPP-Flexibilität.",
                "summary_en": "Comprehensive guide for property managers and communities: 15-minute grid settlement, allocation keys, automated PDF billing, and VPP flexibility.",
                "content_de": r"""# 🏢 Tenant-Admin Leitfaden: Liegenschafts-Dashboard, GGV & Mieterstrom

Als **Liegenschafts- oder Quartiers-Administrator (Tenant-Admin)** steuerst und überwachst du alle energiewirtschaftlichen, kaufmännischen und organisatorischen Prozesse deines Gebäudes oder deiner Nachbarschaftsgemeinschaft im zentralen Cockpit (`/app/tenant`).

---

## 🌟 1. Schnellaktionen im Header

Direkt unter dem Community-Namen stehen vier zentrale Werkzeuge bereit:

### 🎨 Whitelabel & Branding
* **Eigene Corporate Identity**: Passe Logo, Primär- und Akzentfarben für deine Hausverwaltung, Genossenschaft oder Stadtwerke an.
* **Eigene Domain / Subdomain**: Bereitstellung unter eigener Mandanten-Domain (z. B. `energie.mein-quartier.de`).
* **White-Label-Mieterbelege**: Alle generierten PDF-Abrechnungsnachweise und E-Mails tragen automatisch dein Branding.

### 📄 Marktkommunikation (AS4 / EDIFACT)
* **BNetzA-konforme Marktpartner-Kommunikation**: Anbindung an das 1:1-Marktkommunikationsnetz der Energiewirtschaft.
* **AS4-Zertifikate & MP-ID**: Sichere Verschlüsselung von Zählzeitreihen (MSCONS), Stammdaten (UTILMD) und Allokationsmeldungen.
* **Automatisierter Datenaustausch**: Schnittstelle zum Verteilnetzbetreiber (VNB) und Bilanzkreisverantwortlichen (BKV).

### ✨ Gebäude-Assistent (3 Schritte)
* **Geführte Erstinbetriebnahme** für neue Mehrfamilienhäuser und Quartiere:
  1. *Gebäudedaten & Adresse erfassen* (Flurstück, Wohneinheiten, PLZ).
  2. *Zählerstruktur definieren* (Netzanschlusspunkt + Unterzähler je Wohneinheit).
  3. *Tarif- und Verteilschlüssel wählen* (§ 42b EnWG Allokationsmodell).

### 📢 Erfolge teilen
* **Community-Erfolgs-Card**: Zeigt die gemeinsame Autarkiequote (%), geteilten Solarstrom (kWh) und CO₂-Ersparnis.
* Ideal zum Teilen auf Eigentümerversammlungen oder zur Kommunikation mit Mietern und Beiräten.

---

## 📑 2. Die 7 Funktionsbereiche im Detail

### ⚡ 1. Cockpit & Live-Sharing-Matrix (`Tab: Cockpit`)
* **15-Minuten-Saldierung in Echtzeit**: Visualisiert die viertelstündliche Erzeugung, den gemeinsamen Verbrauch und den Reststrombezug.
* **Autarkiegrad & Eigenverbrauchsquote**: Kennzahlen zur kontinuierlichen Optimierung der Eigenversorgung im Gebäude.
* **Quartiers-Energiefluss**: Verfolgung, wie viel PV-Strom aktuell im Haus verbleibt und wie viel ins Netz eingespeist wird.

### 🏢 2. Virtueller Summenzähler (`Tab: Virtueller Summenzähler`)
* **Differenzbilanzierung am NAP**: Errechnet den virtuellen Hauptzähler aus der Summe aller MID-konformen Unterzähler und Erzeuger.
* **3 gesetzliche Verteilschlüssel (§ 42b EnWG)**:
  1. *Dynamisch (zeitgleich)*: Aufteilung proportional zum tatsächlichen Verbrauch in derselben 15-Minuten-Viertelstunde (Maximale Fairness).
  2. *Statisch (nach MEA-Schlüssel)*: Feste Zuteilung nach Miteigentumsanteilen oder Wohnfläche.
  3. *Hybrid*: Vorrangige Eigenversorgung einzelner Wohnungen mit dynamischem Überschuss-Sharing.

### 🔌 3. VPP Kraftwerk & § 14a EnWG Flex-Pool (`Tab: VPP Kraftwerk`)
* **Virtuelles Kraftwerk (VPP)**: Aggregiert alle Heimspeicher, bidirektionalen Wallboxen und steuerbaren Lasten zu einem virtuellen Großkraftwerk.
* **Flexibilitäts-Bonus**: Ermöglicht Zusatzerlöse durch netzdienliche Schwarmsteuerung am Regelenergiemarkt.
* **§ 14a EnWG Modul**: Erfüllung der Dimmvorgaben (4,2 kW) für Wallboxen und Wärmepumpen zur Sicherung pauschaler Netzentgelt-Rabatte (~160 € / Jahr je Großverbraucher).

### 💰 4. Tarife & Monatsabrechnungen (`Tab: Tarife & Abrechnungen`)
* **Rechtssichere Tarifstruktur**: Getrennte Bepreisung von vor Ort erzeugtem Solarstrom (ct/kWh), Reststrombezug (ct/kWh) und Grundgebühr (€/Monat).
* **1-Klick Monatsabrechnung**: Generiert für jede Mietpartei einen eichrechtskonformen, übersichtlichen PDF-Abrechnungsnachweis mit detailliertem 15-Minuten-Einzelnachweis.
* **Multi-Format-Exporte**: Download aller Monatsdaten als **Excel (`.xlsx`)**, **DATEV-kompatible CSV** (mit Semikolon und UTF-8 BOM) und **XML** für Hausverwaltungssoftware (Haufe, DOMUS, Immoware24).

### 👥 5. Mitglieder- & Mieterverwaltung (`Tab: Mitglieder & Mieter`)
* **Einladungsdialog ohne IT-Jargon**: Erstellung sicherer Registrierungslinks für Sharing-Teilnehmer, Mieter und Hausverwaltungen.
* **Die 5 Rechte-Rollen im System**:
  1. ⚡ **Mitglied / Mieter (Sharing-Teilnehmer)**: Einsicht in den eigenen Solar-Anteil, Live-Verbrauch und persönliche Monatsabrechnungen.
  2. 👥 **Mitglieder- & Mieterbetreuung**: Darf Teilnehmer einladen, Links verwalten und Wohnungszuordnungen bei Mieterwechsel pflegen.
  3. 🛟 **Gemeinschafts- & Mieter-Support**: First-Level-Ansprechpartner vor Ort bei Fragen zu Zählern oder der App.
  4. 📊 **Kassenprüfer / Beirat**: Reiner Lesezugriff zur transparenten Einsicht in Quartiersbilanzen, Summenzähler und Abrechnungsberichte.
  5. 🏛️ **Gemeinschafts-Leitung / Energie-Verwalter**: Volle administrative Kontrolle über Tarife, Submetering und Verträge.
* **3 Ausgabemöglichkeiten**:
  * 📋 *1-Klick Link kopieren* (mit visuellem Checkmark-Feedback).
  * ✉️ *Vorbereitete E-Mail* (öffnet vorausgefüllte Einladungsmail an Bewohner).
  * 📱 / 🖨️ *QR-Code für Hausflur-Aushänge* (zum Ausdrucken für das Schwarze Brett im Treppenhaus).
* **Widerrufen & Löschen**: Veraltete oder versehentlich erstellte Links können mit 1 Klick dauerhaft deaktiviert werden.

### 📟 6. wMSB & Smart Meter Gateways (`Tab: wMSB & Zähler`)
* **Direkte SMGW-Kopplung**: Integration wettbewerblicher Messstellenbetreiber (wMSB) wie Discovergy, Solandeo und inexogy.
* **Zählerstatus & Latenz-Überwachung**: Kontinuierliche Prüfung der Zählerstände und Kommunikationsverbindungen.

### 🛡️ 7. Revisionssicheres Audit-Log (`Tab: Audit`)
* **GoBD- und DSGVO-konforme Protokollierung**: Lückenlose Aufzeichnung aller administrativen Änderungen (Tarifänderungen, Rollenzuweisungen, Einladungen, Mieterwechsel).
* Unveränderliche Nachvollziehbarkeit für Kassenprüfer, Beiräte und Steuerberater.
""",
                "content_en": r"""# 🏢 Tenant-Admin Guide: Property Dashboard, Multi-Tenant Power & Energy Sharing

As a **Property or Community Administrator (Tenant-Admin)**, you manage all energy, billing, and organizational workflows across your multi-family building or energy community via the central cockpit (`/app/tenant`).

---

## 🌟 1. Header Quick Actions

Located directly beneath the community title, four key tools provide instant access:

### 🎨 Whitelabel & Branding
* **Custom Brand Identity**: Configure logo, primary and accent colors for housing associations, utilities, or property managers.
* **Custom Subdomain**: Host under your dedicated domain (e.g. `energy.my-property.com`).
* **White-Label Invoices**: All generated PDF settlement statements and notification emails carry your custom branding.

### 📄 Market Communication (AS4 / EDIFACT)
* **BNetzA Energy Market Interface**: Connect to the regulated 1:1 German energy market communication network.
* **AS4 Certificates & MP-ID**: Secure encryption of metering time series (MSCONS), master data (UTILMD), and allocation clearing.
* **Automated Data Exchange**: Direct integration with distribution system operators (DSO) and balance responsible parties (BRP).

### ✨ Building Setup Wizard (3 Steps)
* **Guided Initial Commissioning**:
  1. *Property & Location Data* (Building address, apartment units, postal code).
  2. *Metering Hierarchy* (Grid connection NAP + sub-meters per apartment).
  3. *Tariff & Allocation Model* (§ 42b EnWG sharing key).

### 📢 Share Achievements
* **Community KPI Card**: Displays collective autarky (%), shared solar energy (kWh), and CO₂ savings for resident meetings and AGM reports.

---

## 📑 2. The 7 Main Features in Detail

### ⚡ 1. Cockpit & Live Sharing Matrix (`Tab: Cockpit`)
* **Real-Time 15-Minute Settlement**: Visualizes quarter-hourly generation, collective consumption, and grid imports.
* **Autarky & Self-Consumption KPIs**: Actionable metrics to maximize local solar self-reliance.

### 🏢 2. Virtual Master Meter (`Tab: Virtual Master Meter`)
* **Difference Settlement at Grid Connection (NAP)**: Aggregates MID-certified sub-meters into a virtual building meter.
* **3 Legal Allocation Keys (§ 42b EnWG)**:
  1. *Dynamic (Concurrent)*: Allocated proportional to real-time 15m consumption (Maximum fairness).
  2. *Static (Ownership Share / MEA)*: Fixed percentage per apartment.
  3. *Hybrid*: Priority self-consumption with dynamic excess sharing.

### 🔌 3. VPP Swarm & Grid Flexibility (`Tab: VPP Kraftwerk`)
* **Virtual Power Plant (VPP)**: Aggregates home batteries, smart wallboxes, and heat pumps into a synchronized virtual power asset.
* **Flexibility Bonus**: Monetize grid-supportive swarm dispatch on balancing markets.
* **§ 14a EnWG Compliance**: Automated 4.2 kW active power dimming securing annual grid fee rebates (~€160 / asset / year).

### 💰 4. Tariffs & Monthly Statements (`Tab: Tarife & Abrechnungen`)
* **Compliant Tariff Configuration**: Distinct rates for local solar power (ct/kWh), grid import (ct/kWh), and base fees (€/month).
* **1-Click Settlement**: Generates compliant, itemized PDF invoices for every resident with 15-minute billing breakdowns.
* **Multi-Format Exports**: Download monthly records in **Excel (`.xlsx`)**, **DATEV-compatible CSV** (semicolon + UTF-8 BOM), and **XML** for property ERP systems.

### 👥 5. Member & Resident Management (`Tab: Mitglieder & Mieter`)
* **Clear Role-Based Access Control**:
  1. ⚡ **Member / Resident (Sharing Participant)**: Views personal solar allocation, real-time consumption, and monthly statements.
  2. 👥 **Resident & Member Management**: Invites participants, manages links, and updates apartment assignments during tenant transitions.
  3. 🛟 **Local Community Support**: On-site point of contact for meter or app inquiries.
  4. 📊 **Auditor / Advisory Board**: Read-only oversight for quarter-hourly balances and financial audit reports.
  5. 🏛️ **Community Lead / Property Admin**: Full administrative control over contracts, tariffs, and sub-metering.
* **3 Invitation Channels**:
  * 📋 *1-Click Copy Link* (with instant checkmark feedback).
  * ✉️ *Pre-formatted Email* (opens welcoming invitation email template).
  * 📱 / 🖨️ *Bulletin Board QR Code* (for hallway flyers and community noticeboards).
* **Revoke & Delete**: Easily revoke outdated or unused invitation tokens with 1 click.

### 📟 6. wMSB & Smart Meter Gateways (`Tab: wMSB & Zähler`)
* **SMGW Integration**: Direct connectivity with competitive meter operators (Discovergy, Solandeo, inexogy).
* **Health & Latency Telemetry**: Real-time monitoring of meter readings and gateway communication.

### 🛡️ 7. Tamper-Proof Audit Log (`Tab: Audit`)
* **Audit-Proof Activity Protocol**: Complete chronological logging of all administrative actions (tariff adjustments, role changes, tenant transitions) for auditors and tax advisors.
""",
                "tags": ["tenant admin", "mieterstrom", "virtual master meter", "pdf abrechnung", "vpp", "§ 42b EnWG", "hausverwaltung"],
                "is_featured": True,
                "sort_order": 2,
            },
            # ---------------------------------------------------------------------
            # 11. VPP & FLEXIBILITÄTS-BONUS: DER LEITFADEN FÜR EMS-USER
            # ---------------------------------------------------------------------
            {
                "category": cats["optimizer"],
                "slug": "vpp-flexibilitaets-bonus-heimspeicher",
                "context_key": "vpp_ems_guide",
                "title_de": "VPP & Flexibilitäts-Bonus: Heimspeicher im Schwarm vernetzen & monetarisieren",
                "title_en": "VPP & Flexibility Bonus: Monetize Home Batteries in the Swarm Network",
                "summary_de": "Was ist ein Virtuelles Kraftwerk (VPP)? Wie private Heimspeicherbetreiber durch intelligente Schwarmsteuerung Zusatzerlöse erzielen, 80% Erlösbeteiligung erhalten und durch 20% Mindest-SoC-Reserven volle Eigenverbrauchs-Sicherheit behalten.",
                "summary_en": "What is a Virtual Power Plant (VPP)? How home battery owners generate extra income through intelligent swarm pooling, receive an 80/20 revenue share, and maintain 100% self-consumption reliability with a guaranteed 20% min-SoC reserve.",
                "content_de": r"""# 🔋 VPP & Flexibilitäts-Bonus: Dein Heimspeicher als Kraftwerk

Ein **Virtuelles Kraftwerk (Virtual Power Plant, VPP)** ist ein intelligenter, digital vernetzter Verbund tausender dezentraler Energieanlagen – wie deiner Photovoltaikanlage, deinem Batteriespeicher, deiner Wärmepumpe oder deiner Wallbox.

Durch die Vernetzung mit Sharegy wird dein privater Heimspeicher Teil eines leistungsstarken Schwarmspeichers, der das öffentliche Stromnetz stabilisiert und dir zusätzliche finanzielle Erträge einbringt.

---

## 🌟 Was ist der Flexibilitäts-Bonus und wie funktioniert er?

Stromnetze geraten durch schwankende Wind- und Sonnenenergie immer häufiger in Ungleichgewichte (Über- oder Unterdeckung). Übertragungsnetzbetreiber (ÜNB) zahlen hohe Prämien für sekundenschnelle Ausgleichsenergie (Regelleistung wie **aFRR/mFRR**) und Engpassmanagement (**Redispatch 2.0**).

Bislang konnten nur Großkraftwerke oder industrielle Megawatt-Batterien an diesen lukrativen Energiemärkten teilnehmen. **Sharegy demokratisiert diesen Markt:**
1. **Schwarm-Bündelung**: Sharegy bündelt die freie Speicherkapazität vieler privater Heimspeicher zu einem virtuellen Großspeicher.
2. **KI-gestützte Vermarktung**: Unser Algorithmus analysiert Wetterprognosen, Börsenstrompreise (Day-Ahead & Intraday) sowie deinen individuellen Haushaltsbedarf.
3. **Automatisierte Bereitstellung**: Wenn das Stromnetz Flexibilität anfordert, lädt oder entlädt der Speicher für wenige Minuten gezielt Strom – vollautomatisch und unbemerkt im Hintergrund.

---

## 💰 Deine Vorteile als EMS-Nutzer

### 1. 💶 80/20 Erlösaufteilung (Maximaler Gewinn für dich)
* **80 % der erwirtschafteten Markterlöse** fließen direkt als **Flexibilitäts-Bonus** auf dein Konto oder werden mit deiner Stromrechnung gutgeschrieben.
* **20 % Plattform- & Clearinggebühr** deckt die regulatorische Marktteilnahme, den Bilanzkreis und die automatisierte Abrechnung ab.
* In typischen Haushalten mit 10 kWh Speicher entspricht dies einem jährlichen Zusatzerlös von **120 € bis 350 €**, ohne zusätzliche Investition.

### 2. 🛡️ 100% Eigenverbrauchs-Sicherheit & 20% Mindest-SoC
* **Vorrang für deinen Haushalt**: Dein Eigenbedarf hat stets oberste Priorität. Sharegy greift niemals auf Energie zu, die du für deinen eigenen Abend- oder Nachtverbrauch benötigst.
* **Garantierte Mindest-Reserve**: Im EMS ist ein Mindestladezustand (Standard: **20 % min-SoC**) fest verankert. Diese Notstrom- und Basiskapazität bleibt für externe Abrufe gesperrt.
* Du kannst diesen Mindest-SoC im Einstellungsmenü jederzeit individuell nach deinen Wünschen anpassen (z. B. auf 30% im Winter).

### 3. 🔋 Schonung der Batterie-Lebensdauer
* **Sanfte C-Raten**: Lade- und Entladeimpulse werden auf schonende Raten limitiert (max. 0,5C), um thermischen Stress zu vermeiden.
* **Keine Tiefentladung**: Das Batteriemanagementsystem (BMS) deines Wechselrichters behält stets die physikalische Hoheit.
* **Zyklenschutz**: Das VPP führt maximal 0,3 bis 0,8 zusätzliche Teilzyklen pro Tag aus – weit innerhalb der Hersteller-Garantiegrenzen.

---

## 🚀 So aktivierst du das VPP in deinem Dashboard

1. Öffne im linken Menü den Bereich **Smart Energy Optimizer** (`/app/optimizer`).
2. Scrolle zum Bereich **VPP & Flexibilitäts-Vermarktung**.
3. Aktiviere den Schalter **"Am Schwarm-VPP teilnehmen (Flex-Bonus aktivieren)"**.
4. Wähle deinen gewünschten **Mindest-Reserve-SoC** (z. B. 20%).
5. Bestätige die Aktivierung. Ab der nächsten Viertelstunde optimiert Sharegy deinen Speicher automatisch für das Stromnetz!

Im Dashboard siehst du unter *Abrechnung & Erträge* live deine aufgelaufenen Boni und kannst monatliche Abrechnungsnachweise jederzeit als PDF herunterladen.
""",
                "content_en": r"""# 🔋 VPP & Flexibility Bonus: Turn Your Home Battery into a Virtual Power Plant

A **Virtual Power Plant (VPP)** is an intelligent, cloud-connected network of distributed energy resources – such as your rooftop solar system, home battery, heat pump, or EV charger.

By connecting to Sharegy, your home battery joins a high-performance swarm that helps balance the public power grid while generating passive income for you.

---

## 🌟 What is the Flexibility Bonus and How Does It Work?

As renewable energy expands, grid operators face frequent supply-demand imbalances. Transmission System Operators (TSOs) pay substantial premiums for fast balancing power (**aFRR / mFRR**) and congestion management (**Redispatch 2.0**).

Historically, only massive industrial power plants could participate. **Sharegy opens this revenue stream to homeowners:**
1. **Swarm Aggregation**: Sharegy pools idle capacity from thousands of residential batteries into a unified megawatt-scale battery swarm.
2. **AI-Driven Market Optimization**: Our algorithms evaluate solar forecasts, dynamic electricity prices, and your household consumption habits.
3. **Automated Grid Support**: When the grid needs balancing, your battery charges or discharges briefly and automatically without disturbing your routine.

---

## 💰 Key Benefits for EMS Owners

### 1. 💶 80/20 Revenue Share (Maximum Payout for You)
* **80% of all generated market earnings** are credited directly to you as a **Flexibility Bonus** (bank transfer or bill credit).
* **20% platform fee** covers market certification, balancing group management, and settlement.
* For a typical 10 kWh battery, this yields **€120 to €350 per year** in pure extra cash flow.

### 2. 🛡️ 100% Self-Consumption Priority & 20% Min-SoC Reserve
* **Your Household Comes First**: Local solar self-consumption always takes precedence over grid services.
* **Guaranteed Reserve**: A configurable minimum state of charge (default: **20% min-SoC**) is strictly locked for household and backup needs.
* You can adjust this threshold anytime in your optimizer settings (e.g. increase to 30% in winter).

### 3. 🔋 Battery Health & Longevity Protection
* **Gentle C-Rates**: Charge/discharge power is capped at conservative levels (max 0.5C) to minimize heat and cell wear.
* **BMS Safety**: Your inverter's physical Battery Management System maintains ultimate safety override.
* **Cycle Guard**: VPP operations typically add only 0.3 to 0.8 partial cycles per day, well within manufacturer warranty limits.

---

## 🚀 How to Enable VPP in Your Dashboard

1. Navigate to **Smart Energy Optimizer** (`/app/optimizer`).
2. Scroll to the **VPP & Flexibility Markets** section.
3. Toggle the switch **"Participate in Swarm VPP (Enable Flex Bonus)"**.
4. Set your preferred **Minimum Reserve SoC** (e.g. 20%).
5. Save changes. Starting with the next 15-minute interval, your storage actively participates in the balancing market!
""",
                "tags": ["vpp", "virtuelles kraftwerk", "flexibilitaets bonus", "heimspeicher", "schwarmbatterie", "aFRR", "redispatch 2.0", "optimizer", "ertrag"],
                "is_featured": True,
                "sort_order": 3,
            },
            # ---------------------------------------------------------------------
            # 12. ENERGY SHARING & COMMUNITY COCKPIT: ANLEITUNG FÜR NUTZER & ADMINS
            # ---------------------------------------------------------------------
            {
                "category": cats["energy-sharing"],
                "slug": "energy-sharing-und-community-cockpit",
                "context_key": "energy_sharing_guide",
                "title_de": "Energy Sharing & Community Cockpit: Strom im Quartier teilen & abrechnen",
                "title_en": "Energy Sharing & Community Cockpit: Local Energy Sharing & Administration",
                "summary_de": "Durchgängige Anleitung für Energy Sharing gem. § 42b EnWG: Gemeinschaftliche Gebäudeversorgung, 15-Minuten-Echtzeit-Clearing, Verteilschlüssel und das Community-Cockpit für Administratoren.",
                "summary_en": "End-to-end guide for Energy Sharing under § 42b EnWG: Local multi-party sharing, 15-minute real-time clearing, allocation keys, and community admin management.",
                "content_de": r"""# 🤝 Energy Sharing & Community Cockpit: Strom in der Nachbarschaft teilen

Mit dem **Sharegy Energy Sharing Modul** können Mehrfamilienhäuser, Eigentümergemeinschaften (WEGs), Gewerbeparks und Nachbarschaftsquartiere lokal erzeugten Solarstrom gemeinschaftlich nutzen und rechtssicher abrechnen (**Gemeinschaftliche Gebäudeversorgung gem. § 42b EnWG**).

---

## 👥 Teil 1: Anleitung für Teilnehmer & Bewohner (Community-Mitglieder)

### 1. Beitritt zu einer Energy Community
1. Du erhältst von deiner Hausverwaltung oder dem Quartiers-Admin einen **Einladungslink oder QR-Code**.
2. Registriere dich bei Sharegy oder verknüpfe deinen bestehenden Account.
3. Bestätige deine Wohneinheit (z. B. *Wohnung 4, 1. OG*) und trage bei Bedarf deine Zählernummer ein.

### 2. Das Bewohner-Dashboard (`/app/community`)
* **Live-Sharing-Matrix**: Sieh in Echtzeit, wie viel Solarstrom die Dachanlage gerade produziert, wie viel in deiner Wohnung ankommt und wer im Haus gerade versorgt wird.
* **Deine Ersparnis**: Jeder Kilowattstunde Solarstrom aus der Community ersetzt teuren Netzbezug (Ersparnis i. d. R. 10 bis 20 Cent pro kWh).
* **Monatliche Abrechnungsübersicht**: Lade deine persönlichen Monatsnachweise als transparente PDF-Rechnung herunter.

---

## 🏛️ Teil 2: Anleitung für Community-Administratoren & Hausverwaltungen

Als Community-Admin verwaltest du die energiewirtschaftlichen Parameter, die Zählerzuordnung und die monatliche Abrechnung.

### 1. Community anlegen & Zählerstruktur einrichten
* Navigiere im Menü zur **Administration → Community Cockpit** (`/app/tenant` bzw. `/app/admin`).
* Klicke auf **"Neue Community anlegen"** und definiere den Namen sowie die Postleitzahl.
* Hinterlege den **Netzanschlusspunkt (NAP)**: Wähle den Hauptzähler oder erstelle einen **Virtuellen Summenzähler**, der die Erzeugung und den Netzbezug aggregiert.

### 2. Verteilschlüssel (§ 42b EnWG) wählen
Sharegy unterstützt alle gesetzlich anerkannten Allokationsmodelle:
1. **Dynamisch (Zeitgleich nach 15-Minuten-Intervall - Empfohlen)**:
   * Der in einer Viertelstunde erzeugte Solarstrom wird exakt im Verhältnis des tatsächlichen gleichzeitigen Verbrauchs auf alle aktiven Wohnungen aufgeteilt.
   * *Vorteil*: Höchste Gerechtigkeit – wer Strom verbraucht wenn die Sonne scheint, profitiert am meisten.
2. **Statisch (nach Miteigentumsanteilen / MEA oder qm)**:
   * Jede Partei erhält einen festen prozentualen Anteil der Erzeugung.
3. **Hybrid (Prioritär + Überschuss)**:
   * Basis-Kontingent je Wohneinheit, Überschüsse werden dynamisch geteilt.

### 3. Mitglieder einladen & Zähler zuweisen
* Klicke auf **"Mitglied einladen"** und gib die E-Mail-Adresse sowie die Wohnungsnummer an.
* Weise der Wohneinheit den entsprechenden Unterzähler (Shelly Pro 3EM, Modbus Zähler, Discovergy wMSB oder Smart Meter Gateway) zu.

### 4. Tarife festlegen & 1-Klick Monatsabrechnung
* **Solarstrom-Tarif**: z. B. `18,50 ct/kWh` (brutto).
* **Reststrom-Tarif**: z. B. `32,00 ct/kWh` (vom Versorger durchgeleitet).
* **Grundgebühr / Messstellenbetrieb**: z. B. `4,50 € / Monat`.
* **Monatsabschluss ausführen**: Am Monatsende klickst du auf **"Abrechnungslauf starten"**. Sharegy saldiert alle 2.880 bis 2.976 Viertelstundenwerte, generiert eichrechtskonforme PDF-Abrechnungen für jedes Mitglied und stellt DATEV/CSV-Exporte für deine Buchhaltung bereit.
""",
                "content_en": r"""# 🤝 Energy Sharing & Community Cockpit: Local Power Sharing & Administration

With the **Sharegy Energy Sharing Module**, multi-family residences, homeowner associations (HOAs), commercial buildings, and local quarters share rooftop solar power compliant with **§ 42b EnWG (Collective Building Supply)**.

---

## 👥 Part 1: Guide for Residents & Community Members

### 1. Joining an Energy Community
1. Receive an **Invitation Link or QR Code** from your property manager.
2. Sign up or log into your Sharegy account.
3. Confirm your apartment unit (e.g. *Apt 4, 1st Floor*) and verify your sub-meter number.

### 2. Member Dashboard Features (`/app/community`)
* **Live Sharing Matrix**: View in real time how much solar power is produced on the roof, how much flows into your home, and how much is shared across neighbors.
* **Direct Cost Savings**: Every shared solar kWh replaces expensive grid electricity, typically saving 10 to 20 cents per kWh.
* **Monthly Invoices**: Download transparent, itemized PDF statements showing your exact solar vs. grid consumption.

---

## 🏛️ Part 2: Guide for Community Admins & Property Managers

As a Community Administrator, you manage meter topology, billing formulas, and automated settlement runs.

### 1. Setting Up Community & Meter Hierarchy
* Navigate to **Administration → Community Cockpit** (`/app/tenant`).
* Click **"Create Community"** and specify the site name and address.
* Connect the **Grid Connection Point (NAP)**: Bind your main utility meter or set up a **Virtual Master Meter**.

### 2. Selecting Allocation Schemes (§ 42b EnWG)
1. **Dynamic (Concurrent 15-Minute Intervals - Recommended)**:
   * Solar generation is allocated proportionally to residents consuming power in the exact same 15-minute window.
   * Maximizes fairness and economic utilization.
2. **Static (Ownership Shares / MEA / Area-based)**:
   * Fixed percentage of solar output assigned to each unit.
3. **Hybrid**:
   * Priority self-consumption quota plus dynamic surplus sharing.

### 3. Inviting Members & Mapping Sub-Meters
* Click **"Invite Member"** with the tenant email and apartment ID.
* Map the resident's physical sub-meter (Shelly Pro 3EM, Modbus meter, wMSB Discovergy, or Smart Meter Gateway).

### 4. Tariff Setup & 1-Click Monthly Billing Run
* Configure Community Solar Rate (e.g. `18.50 ct/kWh`), Grid Backup Rate (e.g. `32.00 ct/kWh`), and Base Fee.
* At the end of each billing cycle, trigger **"Run Settlement"**. Sharegy calculates all 2,900+ 15-minute intervals, renders audit-ready PDF invoices, and generates DATEV/CSV exports for ERP systems.
""",
                "tags": ["energy sharing", "community", "§ 42b EnWG", "gemeinschaftliche gebaeudeversorgung", "quartiersstrom", "admin", "abrechnung", "verteilschluessel"],
                "is_featured": True,
                "sort_order": 4,
            },
            # ---------------------------------------------------------------------
            # 13. PARTNER-LEITFADEN: FLOTTENMANAGEMENT & ONBOARDING FÜR INSTALLATEURE
            # ---------------------------------------------------------------------
            {
                "category": cats["partners"],
                "slug": "partner-cockpit-flottenmanagement-onboarding",
                "context_key": "partner_guide",
                "title_de": "Partner-Leitfaden: Flottenmanagement, Wechselrichter-Onboarding & Kundenservice",
                "title_en": "Partner & Installer Guide: Fleet Management, Inverter Onboarding & Service",
                "summary_de": "Die durchgängige Anleitung für Solarteure, Elektroinstallateure und Partnerbetriebe: Kundenanlagen per QR-Code anlegen, Wechselrichter & Speicher via Modbus/WSS koppeln, 3-Sekunden-Selbsttests durchführen und Kundenservice effizient managen.",
                "summary_en": "Complete guide for solar installers, electricians, and partner businesses: Onboarding customer systems via QR code, connecting inverters via Modbus/WSS, running 3-second self-tests, and managing fleet health.",
                "content_de": r"""# 🔧 Partner-Leitfaden: Flottenmanagement, Wechselrichter-Onboarding & Kundenservice

Das **Sharegy Partner Cockpit** (`/app/partner`) wurde speziell für Solarteure, Elektro-Fachbetriebe, Stadtwerke und Energieberater entwickelt, um Hunderte Kundenanlagen zentral zu überwachen, schnell in Betrieb zu nehmen und perfekten After-Sales-Service zu bieten.

---

## 📊 1. Flotten-Dashboard & Health-Monitoring

Im Partner-Cockpit behältst du den Überblick über dein gesamtes Kundenportfolio:
* **Flotten-Status**: Aktive Anlagen, Gesamterzeugung (kW / MWh), Speicher-Füllstände und Warnmeldungen.
* **Health-Score (0 - 100%)**: Erkennt sofort Leistungsabfälle, defekte Strings, Kommunikationsabbrüche oder Phasenasymmetrien.
* **Priorisierte Ticket- & Fehlerliste**: Sortiert Störungen nach Dringlichkeit (z. B. *Wechselrichter Offline > 2h*, *Isolationsfehler String 2*).

---

## ⚡ 2. Schritt-für-Schritt Onboarding einer neuen Kundenanlage

### Schritt 1: Kundenanlage im Partner-Portal anlegen
1. Klicke im Partner-Cockpit auf **"+ Neue Kundenanlage anlegen"**.
2. Gib den Kundennamen, die Adresse sowie die installierte PV-Leistung (kWp) und Speicherkapazität (kWh) ein.
3. Sharegy generiert automatisch einen **Kunden-Einladungslink und QR-Code** für die spätere Übergabe.

### Schritt 2: Wechselrichter & Smart Meter anbinden
Sharegy unterstützt alle marktführenden Hersteller ohne proprietäre Zusatzboxen:

| Hersteller / System | Schnittstelle | Standard-Port & Einstellungen |
| :--- | :--- | :--- |
| **Sungrow** (SHxxRT, SGxx) | Modbus TCP | Port `502`, Unit ID `1` |
| **Fronius** (Gen24, Symo) | SolarAPI / Modbus TCP | Port `502`, SolarAPI JSON aktiviert |
| **SMA** (Tripower, Sunny Boy) | Speedwire / Modbus TCP | Port `502`, Unit ID `3` |
| **SolarEdge** (SE-Serie) | Modbus TCP (SunSpec) | Port `1502` oder `502`, Unit ID `1` |
| **Deye / Growatt / Huawei** | Modbus TCP / RTU Bridge | Port `502`, Register-Map SunSpec |
| **Shelly Pro 3EM / Pro 4PM** | WebSocket (WSS) Outbound | Port `443` (Verschlüsseltes Push-Protokoll) |
| **Home Assistant** | Native HACS Bridge | 1-Klick Entity Picker |

*Tipp für Vor-Ort-Installateure*: Bei gesicherten Routern genügt die Installation eines **Shelly Pro 3EM** auf der Hutschiene mit Outbound-WSS oder die Aktivierung von Modbus TCP im Wechselrichter-Menü.

### Schritt 3: Wallboxen & Wärmepumpen einbinden
* **Wallbox (OCPP 1.6-J)**: Trage in der Wallbox (z. B. ABL, Mennekes, Alfen, go-e) einfach die WebSocket-URL `wss://sharegy.de/ocpp/<ANLAGEN_ID>` ein.
* **Wärmepumpe (SG Ready / Modbus)**: Verbinde das SG-Ready-Relais mit einem Shelly Plus 1 oder steuere modulierende Wärmepumpen via Modbus TCP.

---

## 🧪 3. Der 3-Sekunden-Selbsttest & Telemetrie-Validierung

Vor der Abreise von der Baustelle führst du den integrierten **Inbetriebnahmetest** durch:
1. Öffne die Anlagendetails im Partner-Cockpit und klicke auf **"3-Sekunden-Diagnosetest starten"**.
2. Sharegy prüft automatisiert:
   * ✅ **Phasenfolge & Vorzeichen**: Misst der Zähler Einspeisung positiv und Bezug negativ? (Verhindert verdrehte Stromwandler-Klemmen).
   * ✅ **Latenz & Update-Frequenz**: Treffen Telemetriewerte im 1-Sekunden- bis 5-Sekunden-Takt ein?
   * ✅ **Speicher-Ansprechbarkeit**: Reagiert das BMS auf Sollwert-Vorgaben?
3. Nach erfolgreichem Test wird ein **digitales Inbetriebnahmeprotokoll (PDF)** mit Zeitstempel erzeugt.

---

## 🤝 4. Übergabe an den Kunden (Owner Handover)

1. Lass den Kunden den **Übergabe-QR-Code** mit seinem Smartphone scannen.
2. Der Kunde erstellt sein persönliches Passwort und hat sofort Zugriff auf sein **Private EMS Dashboard**.
3. **Dauerhafter Wartungszugang**: Deine Firma bleibt als betreuender Fachpartner hinterlegt. Bei Fehlern wirst du automatisch benachrichtigt und kannst Ferndiagnosen ohne Anfahrt durchführen.
""",
                "content_en": r"""# 🔧 Partner & Installer Guide: Fleet Management, Inverter Onboarding & Service

The **Sharegy Partner Cockpit** (`/app/partner`) is engineered for solar installers, master electricians, and municipal utilities to manage hundreds of customer installations from a unified dashboard.

---

## 📊 1. Fleet Dashboard & Health Monitoring

Monitor your entire customer portfolio at a glance:
* **Fleet Overview**: Total live generation (kW / MWh), storage states, and active fleet capacity.
* **Health Score (0 - 100%)**: Automatically detects underperforming strings, reversed CT clamps, or communication losses.
* **Smart Alert Queue**: Prioritizes issues by severity (e.g. *Inverter Offline > 2h*, *Isolation Fault String 2*).

---

## ⚡ 2. Step-by-Step Customer Plant Onboarding

### Step 1: Create Plant in Partner Portal
1. Navigate to the Partner Cockpit and click **"+ Onboard New Plant"**.
2. Enter the customer details, installed solar capacity (kWp), and battery size (kWh).
3. Sharegy generates an instant **Handover QR Code & Activation Link**.

### Step 2: Connect Inverters & Smart Meters
Sharegy integrates with all major hardware protocols out of the box:

| Manufacturer | Interface | Default Port & Settings |
| :--- | :--- | :--- |
| **Sungrow** (SHxxRT, SGxx) | Modbus TCP | Port `502`, Unit ID `1` |
| **Fronius** (Gen24, Symo) | SolarAPI / Modbus TCP | Port `502`, SunSpec Enabled |
| **SMA** (Tripower, Sunny Boy) | Speedwire / Modbus TCP | Port `502`, Unit ID `3` |
| **SolarEdge** (SE Series) | Modbus TCP | Port `1502` / `502`, Unit ID `1` |
| **Deye / Growatt / Huawei** | Modbus TCP / RTU | Port `502`, SunSpec register map |
| **Shelly Pro 3EM / 4PM** | WebSocket (WSS) Outbound | Port `443` (Encrypted Push) |
| **Home Assistant** | Native HACS Bridge | 1-Click Entity Picker |

### Step 3: Add EV Wallboxes & Heat Pumps
* **OCPP 1.6-J Chargers**: Set the charger's Central System URL to `wss://sharegy.de/ocpp/<PLANT_ID>`.
* **SG-Ready Heat Pumps**: Trigger thermal storage boosts using dry contacts or Modbus TCP registers.

---

## 🧪 3. The 3-Second Diagnostics Test

Validate installations before leaving the site:
1. Open the plant view and click **"Run 3-Second Diagnostics"**.
2. Automated checks verify:
   * ✅ **Phase Direction & CT Orientation**: Verifies correct sign (+/-) on grid import and feed-in.
   * ✅ **Telemetry Stream Health**: Ensures sub-5-second update intervals.
   * ✅ **Inverter & Battery Control Loop**: Confirms remote setpoint response.
3. Automatically generates an **Audit-Ready Commissioning Certificate (PDF)**.

---

## 🤝 4. Seamless Customer Handover

1. Have the homeowner scan the **Handover QR Code**.
2. The customer activates their **Private EMS Dashboard**.
3. Your installer account retains remote maintenance access for proactive servicing and warranty support.
""",
                "tags": ["partner", "solarteur", "installateur", "flottenmanagement", "inbetriebnahme", "modbus tcp", "shelly", "ocpp", "health score", "selbsttest"],
                "is_featured": True,
                "sort_order": 5,
            },
            # ---------------------------------------------------------------------
            # 14. MIETERSTROM-LEITFADEN: ABRECHNUNG, UNTERZÄHLER & VERWALTUNG
            # ---------------------------------------------------------------------
            {
                "category": cats["energy-sharing"],
                "slug": "mieterstrom-abrechnung-und-zaehlerverwaltung",
                "context_key": "mieterstrom_guide",
                "title_de": "Mieterstrom & Unterzähler: Abrechnung, Transparenz & Mieterverwaltung",
                "title_en": "Tenant Power & Sub-Metering: Billing, Resident Transparency & Management",
                "summary_de": "Der umfassende Leitfaden für Mieter und Vermieter: Günstiger Vor-Ort-Solarstrom ohne Netzentgelte, eichrechtskonforme Unterzähler, automatisches Monats-Clearing und reibungslose Mieterwechsel.",
                "summary_en": "Comprehensive guide for tenants and landlords: Cost-effective local solar power without grid fees, certified sub-metering, automated monthly clearing, and effortless tenant transitions.",
                "content_de": r"""# 🏘️ Mieterstrom & Unterzähler: Transparente Solarstrom-Versorgung im Mehrfamilienhaus

**Mieterstrom** ermöglicht es Mieterinnen und Mietern in Mehrfamilienhäusern, sauberen Solarstrom direkt vom Dach ihres Wohnhauses zu beziehen – ohne Netzentgelte, Konzessionsabgaben und Stromsteuer auf den erzeugten Solaranteil.

Sharegy automatisiert die komplette Messung, 15-Minuten-Saldierung und Abrechnung zwischen Vermieter, Hausverwaltung und Mieter.

---

## 💡 Warum lohnt sich Mieterstrom für alle Beteiligten?

* **Für Mieter**:
  * **20 % bis 35 % Ersparnis** gegenüber dem örtlichen Grundversorger.
  * Reiner Ökostrom direkt vom eigenen Hausdach.
  * Volle Transparenz über das Smartphone-Dashboard (`/app/community`).
* **Für Vermieter & Eigentümer**:
  * Attraktive Rendite auf die PV-Investition (höhere Erlöse als die reine EEG-Einspeisevergütung).
  * Wertsteigerung der Immobilie und Erfüllung von ESG- und Effizienzhaus-Kriterien.
  * Vollautomatisierte Abrechnung ohne manuelles Zählerablesen.

---

## 📐 Die Zählerarchitektur im Mieterstrom-Modell

Um Mieterstrom rechtssicher abzurechnen, setzt Sharegy auf zwei bewährte Messkonzepte:

### Modell A: Virtueller Summenzähler mit Unterzählern (Hutschienen-Zähler)
* **Netzanschlusspunkt (NAP)**: Ein offizieller Zweirichtungszähler des Messstellenbetreibers misst den Gesamtbezug und die Gesamteinspeisung des Gebäudes.
* **Wohnungs-Unterzähler**: In jeder Wohnungsverteilung sitzt ein digitaler MID-konformer Zähler (z. B. Shelly Pro 3EM, Modbus TCP Drehstromzähler oder M-Bus Zähler).
* **Sharegy Cloud Engine**: Berechnet im 15-Minuten-Takt, wie viel Solarstrom in welcher Wohnung verbraucht wurde und wie viel Reststrom aus dem öffentlichen Netz zugekauft werden musste.

### Modell B: Intelligente Messsysteme (iMSys / wMSB)
* Jede Wohnung und die PV-Anlage verfügen über ein Smart Meter Gateway (SMGW).
* Sharegy ruft die 15-Minuten-Lastgänge über gesicherte Schnittstellen ab.

---

## 📱 1. Anleitung für Mieter

1. **Einladungs-Link annehmen**: Öffne die Einladung deines Vermieters und erstelle dein Sharegy-Profil.
2. **Dashboard-Überblick**:
   * Sieh live deinen aktuellen Stromverbrauch und die aktuelle Solar-Deckungsquote.
   * Historie: Wie viel Prozent deines Monatsstroms stammten vom Dach?
3. **Monatliche Abrechnung**: Du erhältst jeden Monat eine transparente PDF-Abrechnung mit genauer Trennung von:
   * *Verbrauchter Solarstrom (z. B. 20 ct/kWh)*
   * *Verbrauchter Netzstrom (z. B. 33 ct/kWh)*
   * *Monatliche Zähler- und Grundgebühr*

---

## 🏛️ 2. Anleitung für Vermieter & Hausverwaltungen

### Tarifstruktur konfigurieren
1. Gehe in der Navigation auf **Administration → Liegenschaften & Mieterstrom** (`/app/tenant`).
2. Lege die Tarife fest:
   * **Solarstrompreis**: Der günstige Vor-Ort-Preis für Mieter (muss mind. 10% unter dem Grundversorger liegen).
   * **Reststrom-Einkaufspreis**: Der Arbeitspreis deines gewählten Gewerbe-Stromliefervertrags für das Gesamtgebäude.
   * **Grundpreis je Wohneinheit**: Zur Deckung von Messstellenbetrieb und Verwaltung.

### Mieterwechsel & Zwischenabrechnung (Stichtagsgenau)
* Zieht ein Mieter aus, klickst du in der Wohnungsübersicht auf **"Mieterwechsel erfassen"**.
* Wähle das Auszugsdatum: Sharegy generiert sekundengenau eine **Schlussabrechnung** für den ausziehenden Mieter.
* Trage die E-Mail des Nachmieters ein – die Zählerhistorie bleibt für die Hausverwaltung lückenlos archiviert.

### Export für Hausverwaltungssoftware (Haufe, DOMUS, Winline, DATEV)
* Alle Monatsabschlüsse können mit einem Klick als strukturierte CSV-, Excel- oder XML-Datei exportiert werden, sodass Zählerstände und Beträge ohne Abtippen in die Betriebskostenabrechnung übernommen werden.
""",
                "content_en": r"""# 🏘️ Tenant Power & Sub-Metering: Multi-Family Solar Supply & Billing

**Tenant Power (Mieterstrom)** allows apartment residents to consume clean, low-cost solar electricity generated directly on their building's roof – exempt from grid fees, concession levies, and electricity taxes on the solar portion.

Sharegy automates interval metering, 15-minute grid settlement, and monthly tenant invoices for property managers and landlords.

---

## 💡 Win-Win for Tenants and Landlords

* **For Tenants**:
  * **20% to 35% cost savings** compared to standard utility default tariffs.
  * 100% green solar energy straight from the roof.
  * Real-time transparency on the mobile dashboard (`/app/community`).
* **For Landlords & Building Owners**:
  * Higher yield on solar investment compared to feed-in tariffs.
  * Enhanced ESG property value and modern tenant amenities.
  * Zero-touch automated billing without manual meter readings.

---

## 📐 Metering Topologies

### Model A: Virtual Master Meter with Sub-Meters
* **Grid Connection (NAP)**: Main bi-directional utility meter records aggregate import and export.
* **Sub-Meters**: Standard MID-compliant sub-meters (Shelly Pro 3EM, Modbus TCP, M-Bus) in each apartment sub-distribution box.
* **Sharegy Clearing Engine**: Reconciles every 15-minute interval to allocate solar self-consumption vs. grid import per apartment.

### Model B: Smart Meter Gateways (iMSys)
* Certified Smart Meter Gateways deliver synchronized 15-minute load profiles directly to the Sharegy clearing backend.

---

## 📱 1. Guide for Residents

1. **Accept Invitation**: Sign up via the property manager's link.
2. **Track Energy & Solar Share**: Check real-time rooftop solar coverage and historic monthly savings.
3. **Monthly PDF Statements**: Automated statements clearly break down solar power kWh, grid power kWh, and base fees.

---

## 🏛️ 2. Guide for Property Managers & Landlords

### Setting Up Tariffs
1. Open **Administration → Properties & Tenant Power** (`/app/tenant`).
2. Set your rates:
   * **Solar Tariff**: Affordable on-site rate.
   * **Grid Backup Rate**: Pass-through rate from building power contract.
   * **Base Fee**: Sub-metering and admin service fee.

### Tenant Move-In / Move-Out
* Click **"Log Tenant Change"** on any unit.
* Set effective date: Sharegy generates an instant final settlement PDF.
* Add the incoming tenant email to initialize new billing cycles.

### ERP & DATEV Exports
* Export monthly settlements directly to Excel, DATEV-ready CSV, or XML for property management suites (Haufe, DOMUS, etc.).
""",
                "tags": ["mieterstrom", "unterzaehler", "abrechnung", "vermieter", "hausverwaltung", "pdf abrechnung", "shelly pro 3em", "datev"],
                "is_featured": True,
                "sort_order": 6,
            },
            # ---------------------------------------------------------------------
            # 15. NETZBETREIBER & EVUS: § 14A ENWG, CLS-GATEWAY & REDISPATCH 2.0
            # ---------------------------------------------------------------------
            {
                "category": cats["grid-enwg"],
                "slug": "netzbetreiber-redispatch-cls-14a-enwg",
                "context_key": "grid_operator_guide",
                "title_de": "Netzbetreiber & EVUs: § 14a EnWG Steuerung, CLS-Gateway & Redispatch 2.0 Clearing",
                "title_en": "Grid Operators & Utilities: § 14a EnWG Control, CLS Gateway & Redispatch 2.0 Clearing",
                "summary_de": "Das Handbuch für Verteilnetzbetreiber (VNB), Übertragungsnetzbetreiber (ÜNB) und Stadtwerke: Dimmvorgaben gem. § 14a EnWG (4,2 kW SteuVE), CLS-Kanal über Smart Meter Gateway, 96-Viertelstunden-Fahrpläne und revisionssicherer Audit-Trail.",
                "summary_en": "Handbook for DSOs, TSOs, and municipal utilities: § 14a EnWG dimming controls (4.2 kW SteuVE), SMGW CLS channel integration, 96 quarter-hour day-ahead schedules, and audit trails.",
                "content_de": r"""# 🛡️ Netzbetreiber & EVUs: § 14a EnWG Steuerung, CLS-Gateway & Redispatch 2.0 Clearing

Als **Verteilnetzbetreiber (VNB)**, **Übertragungsnetzbetreiber (ÜNB)** oder **Energieversorger (EVU)** nutzen Sie Sharegy als Schnittstelle zur netzdienlichen Steuerung dezentraler Flexibilitäten und Erzeuger im Niederspannungsnetz.

Sharegy setzt die Vorgaben der **Bundesnetzagentur (BNetzA BK6-22-300 / BK8-22/010-A)** sowie die Standards für **Redispatch 2.0** und **Connect+** vollständig und automatisiert um.

---

## ⚡ 1. § 14a EnWG: Steuerbare Verbrauchseinrichtungen (SteuVE)

Seit dem 01.01.2024 müssen Neuanlagen mit steuerbaren Verbrauchseinrichtungen (> 4,2 kW elektrische Leistung) netzdienlich steuerbar sein:
* **Betroffene Geräte**: Private Wallboxen (Ladeeinrichtungen für E-Fahrzeuge), Wärmepumpen, Klimageräte und Heimspeicher (beim Laden aus dem Netz).
* **Mindestbezugsleistung**: Bei einer netzorientierten Steuerung (Dimmung) muss dem Haushalt stets eine Mindestleistung von **4,2 kW je SteuVE** (bzw. nach dem BNetzA-Gleichzeitigkeitsfaktor) zur Verfügung stehen. Ein vollständiges Abschalten ist unzulässig.

### Dimm-Modi in Sharegy:
1. **Statische Einzelsteuerung**: Direkte Drosselung der jeweiligen SteuVE auf 4,2 kW über Modbus / Relais / OCPP.
2. **Dynamische Summenleistungssteuerung (EMS-Modell)**:
   * Das Sharegy EMS überwacht den Netzanschlusspunkt (NAP).
   * Der Netzbetreiber gibt eine maximale Netzbezugsgrenze vor (z. B. `Max_Import = 4,2 kW + Hausgrundlast`).
   * Das EMS steuert Wallbox, Wärmepumpe und Speicher intelligent so aus, dass die Grenze exakt eingehalten wird – eigener Solarstrom kann weiterhin ungedrosselt genutzt werden!

---

## 🔌 2. Technische Anbindung: Smart Meter Gateway & CLS-Kanal

Sharegy unterstützt alle modernen Kommunikationspfade der FNN-Leitfäden:

```mermaid
graph LR
    VNB[Verteilnetzbetreiber VNB / Leitstelle] -->|Befehl: Dimmung 4.2 kW| SMGW[Smart Meter Gateway BSI-konform]
    SMGW -->|CLS-Kanal / EEBUS / IEC 61850| STEUERBOX[FNN-Steuerbox / Sharegy Bridge]
    STEUERBOX -->|Modbus TCP / REST / Relais| EMS[Sharegy Smart EMS Core]
    EMS --> WB[Wallbox OCPP 1.6-J]
    EMS --> WP[Wärmepumpe SG Ready]
    EMS --> BAT[Batteriespeicher Modbus]
```

* **CLS-Kanal (Controllable Local System)**: Sichere TLS-verschlüsselte Kommunikation über das Smart Meter Gateway (SMGW) nach BSI TR-03109-1.
* **EEBUS (SPINE / SHIP)**: Standardisiertes Datenmodell für netzdienliche Leistungsanforderungen (`LimitPowerConsumption`).
* **Fallback / Relais**: Unterstützung klassischer 4-Stufen-Relaiskontakte (0%, 30%, 60%, 100%) über FNN-konforme Steuerboxen.

---

## 📈 3. Redispatch 2.0 & 96-Viertelstunden-Fahrpläne (`PT15M`)

Zur Engpassvermeidung im Verteilnetz stellt Sharegy Netzbetreibern standardisierte Schnittstellen bereit:
* **Day-Ahead Prognose-Fahrpläne**: Automatische Übermittlung von 96 Viertelstundenwerten (`PT15M`) für Erzeugung, Grundlast und abrufbare Flexibilität (+kW / -kW) je Netzbezirk/Transformatorstation.
* **Revisionssicherer Audit-Trail**: Jeder Dimmbefehl, jede Steuerungshandlung und jede Sollwertänderung wird mit Zeitstempel (Millisekundengenau), Wirkleistungsvorher/-nachher und Netzspannung protokolliert.
* **Bilanzkreis-Clearing**: Automatische Bereitstellung von Abrechnungsdaten zur bilanziellen und energetischen Ausgleichsberechnung gem. BNetzA-Beschlüssen.

---

## 🧪 4. Netzbetreiber-Testschaltung & Diagnose im Dashboard

Im Netzbetreiber-Cockpit (`/app/grid-operator` bzw. via API):
1. **Verbindungstest ausführen**: Prüft die Latenz zum SMGW und der lokalen Steuerbox.
2. **Test-Dimmung anfordern**: Simuliert einen 15-minütigen Dimmbefehl zur Abnahme nach VDE-AR-N 4100 / 4105.
3. **Abnahmeprotokoll generieren**: Erstellt automatisch ein signiertes PDF-Prüfprotokoll für den Netzanschlussvertrag.
""",
                "content_en": r"""# 🛡️ Grid Operators & Utilities: § 14a EnWG Control, CLS Gateway & Redispatch 2.0

As a **Distribution System Operator (DSO)**, **Transmission System Operator (TSO)**, or **Energy Utility**, Sharegy provides your digital gateway to aggregate, schedule, and control distributed energy flexibility in the low-voltage grid.

Fully compliant with **German Federal Network Agency (BNetzA BK6-22-300 / BK8-22/010-A)** mandates, **§ 14a EnWG**, and **Redispatch 2.0** standards.

---

## ⚡ 1. § 14a EnWG: Controllable Consumer Units (SteuVE)

Controllable loads (> 4.2 kW) connected after Jan 1, 2024 must support grid-oriented dimming:
* **Applicable Assets**: EV Wallboxes, heat pumps, air conditioning systems, and stationary battery storage systems.
* **Guaranteed Minimum Import**: Under dimming commands, customers are legally guaranteed a minimum active power of **4.2 kW per SteuVE** (or adjusted by concurrency factors). Complete disconnects are strictly prohibited.

### Control Modes in Sharegy:
1. **Direct Device Dimming**: Throttles individual devices to 4.2 kW via Modbus, Relays, or OCPP.
2. **Dynamic Aggregate Grid-Limit (EMS Mode - Preferred)**:
   * Sharegy EMS manages the Grid Connection Point (NAP).
   * The DSO sends an active power ceiling.
   * The EMS dynamically throttles loads while allowing unrestricted local solar self-consumption.

---

## 🔌 2. Smart Meter Gateway & CLS Channel Integration

* **CLS (Controllable Local System)**: End-to-end encrypted TLS tunnel through the Smart Meter Gateway (SMGW) adhering to BSI TR-03109.
* **EEBUS Protocol**: Native SPINE/SHIP data model supporting standardized `LimitPowerConsumption` payloads.
* **Hardware Relays**: Compatibility with 4-contact FNN relay Steuerboxen.

---

## 📈 3. Redispatch 2.0 & 96 Quarter-Hour Day-Ahead Schedules

* **96 Quarter-Hour Forecasts (`PT15M`)**: Aggregated day-ahead generation, baseline load, and controllable flexibility (+kW / -kW) per feeder transformer.
* **Immutable Audit Trail**: Millisecond-accurate logging of all dispatch orders, actual power responses, and voltage telemetry.
* **Balancing Group Settlement**: Automated export for financial and physical energy compensation.

---

## 🧪 4. DSO Verification & Test Dispatching

1. **Ping & Latency Check**: Test communication to SMGW and on-site controller.
2. **Simulate Test Dimming**: Execute 15-minute compliance tests required under VDE-AR-N 4100 / 4105.
3. **Generate Compliance Certificate**: Instant PDF report documenting grid-compliance readiness.
""",
                "tags": ["netzbetreiber", "vnb", "uenb", "evu", "§ 14a EnWG", "steuve", "cls gateway", "smgw", "redispatch 2.0", "dimmung 4.2 kw", "eebus"],
                "is_featured": True,
                "sort_order": 7,
            },

            # ---------------------------------------------------------------------
            # 12. ADMIN & GOVERNANCE LEITFÄDEN (6 SPEZIFISCHE ADMINBEREICHE)
            # ---------------------------------------------------------------------
            {
                "category": cats["admin-governance"],
                "slug": "admin-communities-portfolio-guide",
                "context_key": "admin_communities",
                "title_de": "Quartiere & Gemeinschaften: Portfolio-Cockpit, Aggregierte Bilanzen & Liegenschaftsverwaltung",
                "title_en": "Communities & Portfolios: Aggregated Balances, Property Management & Simulation",
                "summary_de": "Umfassender Leitfaden zur Verwaltung mehrerer Liegenschaften, Quartiersbilanzen, Simulation von Erzeugungs- und Lastprofilen sowie Whitelabel-Rollen.",
                "summary_en": "Comprehensive guide for multi-property portfolio management, aggregated community balances, load simulation, and role-based access control.",
                "content_de": """# Quartiere & Gemeinschaften (Portfolio-Verwaltung)

Das **Community Portfolio Cockpit** (`/app/admin/communities`) ist die zentrale Steuerzentrale für Energieversorger, Stadtwerke, Quartiersentwickler, Wohnungsbaugesellschaften und Verwalter mit mehreren Liegenschaften. Es bündelt sämtliche dezentralen Erzeugungs- und Verbrauchsanlagen in einer ganzheitlichen Mandantenübersicht.

---

## 1. Portfolio-Übersicht & Aggregierte Live-Kennzahlen

Auf der obersten Portfolio-Ebene aggregiert Sharegy in Echtzeit:

| Kennzahl | Beschreibung & Relevanz |
| :--- | :--- |
| **🏘️ Aktive Liegenschaften** | Gesamtzahl aller verwalteten Quartiere, Mehrfamilienhäuser und Gewerbeparks |
| **☀️ Aggregierte Solarleistung** | Summe der installierten PV-Peakleistung (kWp) sowie momentane Echtzeit-Erzeugung (kW) |
| **⚡ Quartiers-Gesamtverbrauch** | Momentane Last aller Wohneinheiten, Gemeinschaftsflächen und Wärmepumpen/Wallboxen |
| **🔄 Lokaler Deckungsgrad** | Prozentualer Anteil des Gesamtverbrauchs, der zeitgleich aus lokaler PV-Erzeugung gedeckt wird |
| **🛡️ Lokale Autarkiequote** | Unabhängigkeit des gesamten Portfolios vom übergeordneten Verteilnetz |
| **🔋 Flexibilitätspotenzial** | Momentan verfügbare positive (+kW) und negative (-kW) Regelleistung aller Heimspeicher |

---

## 2. Liegenschaften anlegen & Stammdaten konfigurieren

Beim Anlegen eines neuen Quartiers über den Button **„+ Neues Quartier anlegen“** werden folgende Kernparameter erfasst:

1. **Stammdaten & Adresse**: Name der Liegenschaft, Anschrift, Bundesland und Geokoordinaten (für hochpräzise Solar- und Einstrahlungsprognosen).
2. **Netzanschlusspunkt (NAP)**: 
   * Zählpunktbezeichnung (MaLo-ID / 33-stelliger Zählpunktcode).
   * Verteilnetzbetreiber (VNB) und zuständiger Messstellenbetreiber (gMSB / wMSB).
   * Maximal zulässige Netzanschlussleistung (kVA).
3. **Erzeugungs- & Speicherzuweisung**:
   * Zuweisung von Zentral-Wechselrichtern, Dachanlagen und Batteriespeicher-Blöcken.
4. **Wohneinheiten & Zählerstruktur**:
   * Erfassung aller Parteien, Unterzähler (MID) oder Smart Meter Gateways (SMGW).

---

## 3. Mandanten- & Rollenberechtigungen (RBAC)

Sharegy unterstützt ein granulares rollenbasiertes Zugriffskonzept:

* **Super-Administrator**: Voller Zugriff auf das gesamte Portfolio, Globale Tarife, API-Keys und Whitelabel-Einstellungen.
* **Quartiersverwalter / Property Manager**: Verwaltung spezifischer Liegenschaften, Einsicht in Lastgänge, Einladung von Mietern und Initiierung von Monatsabrechnungen.
* **Hausverwaltung / Beirat (WEG)**: Lesender Zugriff auf Energiebilanzen, Quartiers-Zertifikate und Beschlussvorlagen.
* **Fachpartner / Installateur**: Technischer Zugriff auf Inverter, Modbus-Register und IBN-Protokolle.

---

## 4. Quartiers-Simulation & Lastprofiloptimierung

Im Bereich **Quartiers-Simulation** können Sie vor Investitionsentscheidungen virtuelle Szenarien berechnen:

* **Gleichzeitigkeitsfaktor-Analyse**: Wie verteilen sich die Spitzenlasten von 20, 50 oder 100 Wohnungen bei gleichzeitiger Nutzung von Elektroautos und Wärmepumpen?
* **Batteriespeicher-Dimensionierung**: Simulation von 30 kWh bis 200 kWh Quartiersspeichern zur Vermeidung teurer Netzausbauten (Peak Shaving).
* **Dynamische Preisszenarien**: Berechnung der Portfoliokosten bei Börsenstromtarifen im Vergleich zu klassischen Festverträgen.

---

## 5. Export, ESG-Reporting & Monatsberichte

Mit einem Klick generiert das Portfolio-Cockpit:
* **ESG- & Nachhaltigkeitsberichte (PDF/CSV)**: Nachweis der vermiedenen CO2-Emissionen gem. GHG Protocol (Scope 1 & 2).
* **DATEV-kompatible Buchungsstapel**: Vorkontierte Erlös- und Kostenstellen für die Buchhaltung.
* **BNetzA-Jahresmeldung**: Zusammenfassung aller erzeugten, vor Ort verbrauchten und eingespeisten Kilowattstunden.
""",
                "content_en": """# Communities & Portfolios (Multi-Property Management)

The **Community Portfolio Cockpit** (`/app/admin/communities`) is the mission control center for energy suppliers, municipal utilities, housing corporations, and property managers overseeing multiple assets. It consolidates all distributed energy resources and multi-unit loads into a unified tenant structure.

---

## 1. Portfolio Overview & Real-Time KPIs

At the portfolio level, Sharegy aggregates real-time metrics across all locations:

| Metric | Description & Strategic Value |
| :--- | :--- |
| **🏘️ Active Communities** | Total number of managed residential complexes, quarters, and commercial sites |
| **☀️ Aggregated Solar Power** | Total installed PV peak power (kWp) alongside instantaneous live generation (kW) |
| **⚡ Total Community Load** | Combined power demand across all apartments, common areas, and heat pumps / EVs |
| **🔄 Local Coverage Ratio** | Percentage of active demand supplied directly by on-site solar generation |
| **🛡️ Local Self-Sufficiency** | Grid independence percentage across the complete property portfolio |
| **🔋 Flexibility Potential** | Aggregated positive (+kW discharge) and negative (-kW charging) balancing reserves |

---

## 2. Setting Up & Configuring New Communities

Clicking **"+ Add New Community"** initiates the configuration workflow:

1. **Master Data & Geolocation**: Community name, address, federal state, and precise GPS coordinates for solar irradiance forecasting.
2. **Grid Connection Point (NAP)**:
   * 33-digit Market Location ID (MaLo-ID).
   * Distribution System Operator (DSO / VNB) and Metering Point Operator (MSB).
   * Maximum authorized grid connection capacity (kVA).
3. **Generation & Battery Assignment**: Linking central inverters, sub-inverters, and storage blocks.
4. **Units & Meter Hierarchy**: Mapping individual residential units, MID submeters, and Smart Meter Gateways (SMGW).

---

## 3. Role-Based Access Control (RBAC)

* **Super Admin**: Full multi-tenant governance, global tariff templates, API integrations, and whitelabeling.
* **Portfolio Manager**: Multi-site management, load curve inspection, resident onboarding, and settlement runs.
* **HOA / Building Board**: Read-only oversight of energy metrics, sustainability certificates, and meeting templates.
* **Certified Partner / Installer**: Engineering access for Modbus registers, telemetry diagnostic checks, and commissioning.

---

## 4. Community Simulation & Load Curve Optimization

* **Coincidence Factor Modeling**: Simulating peak demand across 20 to 200 units with concurrent heat pump and EV charging sessions.
* **Storage Sizing**: Sizing community storage systems (30–300 kWh) for optimal peak-shaving and self-consumption.
* **Dynamic Tariff Impact**: Simulating day-ahead spot market exposure versus fixed utility contracts.

---

## 5. Automated ESG Reporting & Export

* **ESG & Sustainability PDF Reports**: Audited GHG Protocol Scope 1 & 2 carbon reduction statements.
* **DATEV Accounting Export**: Standardized transaction ledgers for automated bookkeeping.
* **Regulatory Compliance**: Complete annual summaries for grid and market operators.
""",
                "tags": ["portfolio", "communities", "quartiere", "liegenschaften", "admin", "multi-tenant", "simulation", "esg", "kpi"],
                "is_featured": True,
                "sort_order": 1,
            },
            {
                "category": cats["admin-governance"],
                "slug": "admin-mieterstrom-enwg-guide",
                "context_key": "admin_mieterstrom",
                "title_de": "Mieterstrom gem. § 42a EnWG: Vollversorgung, Zählerkaskade, AS4-Marktkommunikation & Monatsabrechnung",
                "title_en": "Tenant Power (§ 42a EnWG): Full Supply, Submetering, AS4 Market Dispatch & Monthly Billing",
                "summary_de": "Praxisleitfaden für Vermieter & Betreiber: Solar- & Reststromtarife in einer Gesamtrechnung, 15m-MSCONS-Export, Mieterstromzuschlag und automatisiertes Onboarding.",
                "summary_en": "Operator guide for full-supply tenant electricity: combined solar & grid tariffs, 15m MSCONS export, statutory subsidies, and automated tenant onboarding.",
                "content_de": """# Mieterstrom-Vollversorgung gem. § 42a EnWG

Das Modul **Mieter- & Wohnungsverwaltung** (`/app/admin/mieterstrom`) bildet die rechtlichen und abrechnungstechnischen Anforderungen des klassischen Mieterstroms gem. **§ 42a Energiewirtschaftsgesetz (EnWG)** vollständig digital ab.

---

## 1. Gesetzliche Grundlagen & Das Vollversorgungs-Prinzip

Beim Mieterstrom nach § 42a EnWG tritt der Betreiber (z. B. Vermieter, Stadtwerk oder Contracting-Dienstleister) als **Vollversorger** auf. Das bedeutet:

* **Eine einzige Gesamtrechnung**: Der Mieter erhält eine einheitliche Rechnung, die sowohl den vor Ort erzeugten Solarstrom als auch den aus dem öffentlichen Netz bezogenen Reststrom umfasst.
* **Gesetzlicher Preisdeckel**: Der Mieterstromtarif darf **maximal 90 % des Grundversorgertarifs** im jeweiligen Netzgebiet betragen (§ 42a Abs. 4 EnWG).
* **Freie Versorgerwahl**: Mieter sind gesetzlich nicht verpflichtet, Mieterstrom zu beziehen; ein Kopplungsverbot mit dem Mietvertrag ist zwingend einzuhalten (§ 42a Abs. 2 EnWG).
* **Gesetzlicher Mieterstromzuschlag**: Für jede an Mieter gelieferte Kilowattstunde Solarstrom erhält der Anlagenbetreiber eine zusätzliche EEG-Förderung (Mieterstromzuschlag).

---

## 2. Tarifstruktur & Preisbausteine

Im Mieterstrom-Cockpit konfigurieren Sie folgende Kernparameter:

| Preisbaustein | Erläuterung | Typischer Bereich |
| :--- | :--- | :--- |
| **☀️ Solar-Arbeitspreis** | Preis je kWh für direkt vom Dach verbrauchten PV-Strom | 16,00 – 22,00 ct/kWh |
| **⚡ Reststrompreis** | Preis je kWh für aus dem Netz bezogenen Strom | 28,00 – 34,00 ct/kWh |
| **🏢 Grundpreis** | Monatliche Gebühr für Zählerbetrieb, Abrechnung & Grundkosten | 6,00 – 12,00 € / Monat |
| **💶 Mieterstromzuschlag** | Gesetzliche EEG-Förderung für den Betreiber | Gemäß Bundesnetzagentur-Satz |

---

## 3. Zählerkaskade & Messkonzepte

Sharegy unterstützt sowohl physische Kaskadenmessungen als auch moderne virtuelle Summenzähler mit Smart Meter Gateways:

```
                  [ Öffentliches Netz ]
                            |
                     [ Z1: Zweirichtungs-Summenzähler ]
                            |
      +---------------------+---------------------+
      |                                           |
[ PV-Anlage Z2 ]                        [ Mieter-Unterzähler ]
 (Erzeugung)                           /          |                                            [ Z_Wohnung 1 ] [ Z_Wohnung 2 ] [ Z_Wohnung 3 ]
```

* **Summenzähler (Z1)**: Misst den gesamten Netzbezug und die Netzeinspeisung des Gebäudes.
* **Erzeugungszähler (Z2)**: Misst die gesamte Brutto-PV-Erzeugung.
* **Unterzähler (Z3..Zn)**: MID-konforme Unterzähler oder intelligente Messsysteme je Wohneinheit.
* **Automatisches Clearing**: Sharegy berechnet im 15-Minuten-Intervall die exakte Aufteilung von Solar- und Reststrom je Partei.

---

## 4. BNetzA AS4 Marktkommunikations-Adapter

Für die automatische Übermittlung an Verteilnetzbetreiber (VNB) und Messstellenbetreiber (MSB) verfügt Sharegy über einen integrierten **AS4 / EDIFACT Konnektor**:

* **MSCONS Export**: Automatisierte Erstellung von 15-Minuten-Lastgangnachrichten (Viertelstundenwerte gem. BNetzA MaKo 2020 / 2024).
* **UTILMD Dispatch**: Stammdatenänderungen, Zählpunktanmeldungen und Abmeldungen bei Mieterwechsel.
* **Protokoll-Verschlüsselung**: BSI-konforme AS4-Webservice-Schnittstelle mit Zertifikatsvalidierung.

---

## 5. Monatsabrechnung auslösen ("Trigger Monthly Settlement")

Am Monatsende erfolgt die Abrechnung in 3 einfachen Schritten:

1. **Prüfung**: Klick auf *„Trigger Monthly Settlement“* öffnet den Monatsprüfbericht.
2. **Validierung**: Sharegy gleicht Zählerstände, Lastgänge und Mieterstammdaten automatisch auf Plausibilität ab.
3. **Generierung & Versand**: 
   * Erstellung rechtssicherer PDF-Abrechnungen für jeden Mieter.
   * Automatischer SEPA-Lastschriftexport (XML camt.053 / pain.008).
   * E-Mail-Versand an Mieter mit Link zum Mieter-Portal.
""",
                "content_en": """# Tenant Electricity Full-Supply (§ 42a EnWG)

The **Tenant & Apartment Management** module (`/app/admin/mieterstrom`) fully automates the regulatory and billing requirements of statutory German tenant power pursuant to **§ 42a EnWG**.

---

## 1. Statutory Framework & Full-Supply Principle

Under § 42a EnWG, the operator acts as a **full electricity supplier**. Key legal obligations:

* **Unified Monthly Invoice**: Tenants receive one combined invoice covering both on-site solar consumption and grid residual power.
* **Statutory Price Cap**: The tenant rate must **not exceed 90 % of the local default utility tariff** (§ 42a para. 4 EnWG).
* **Freedom of Choice**: Participation is strictly voluntary; bundling electricity contracts with tenancy agreements is prohibited by law.
* **Statutory Tenant Power Surcharge**: Operators receive an EEG subsidy per kWh of solar energy delivered directly to tenants.

---

## 2. Tariff Structure & Price Components

| Component | Definition | Typical Range |
| :--- | :--- | :--- |
| **☀️ Solar Energy Rate** | Price per kWh for locally consumed rooftop solar | 16.00 – 22.00 ct/kWh |
| **⚡ Residual Grid Rate** | Price per kWh for supplementary grid power | 28.00 – 34.00 ct/kWh |
| **🏢 Base Service Fee** | Monthly metering and billing maintenance fee | €6.00 – €12.00 / month |
| **💶 Operator Subsidy** | Official EEG tenant subsidy paid to the operator | Regulated BNetzA rate |

---

## 3. Submetering Cascades & Meter Hierarchy

Sharegy natively supports physical meter cascades as well as virtual balancing via Smart Meter Gateways:

* **Main Grid Meter (Z1)**: Dual-direction meter measuring total grid import and export.
* **Production Meter (Z2)**: Certified meter tracking gross solar generation.
* **Submeters (Z3..Zn)**: MID-approved submeters per apartment.
* **15-Minute Clearing Engine**: Sharegy calculates the exact 15-minute split between solar self-consumption and grid backup for each unit.

---

## 4. BNetzA AS4 Market Communication Adapter

* **EDIFACT MSCONS Dispatch**: Automated generation of 15-minute load curves for DSO and MSB balancing.
* **UTILMD Master Data Exchange**: Automated tenant moving-in/moving-out notifications.
* **AS4 BSI Security**: Encrypted communication using certified PKI market certificates.

---

## 5. Monthly Settlement Workflow ("Trigger Monthly Settlement")

1. **Review**: Launch *Trigger Monthly Settlement* to review aggregated consumption and revenue splits.
2. **Automated Audit**: Pre-flight validation checks for meter gaps or tariff anomalies.
3. **Dispatch & Invoicing**: Automated PDF generation, tenant email notifications, and SEPA direct debit XML export (pain.008).
""",
                "tags": ["mieterstrom", "enwg", "§ 42a", "abrechnung", "as4", "mscons", "utilmd", "submetering", "vollversorgung"],
                "is_featured": True,
                "sort_order": 2,
            },
            {
                "category": cats["admin-governance"],
                "slug": "admin-ggv-weg-guide",
                "context_key": "admin_ggv",
                "title_de": "WEG & Gebäudeverwaltung: Gemeinschaftliche Gebäudeversorgung (§ 42b EnWG / Solarpaket I)",
                "title_en": "HOA & Building Management: Collective Self-Supply (§ 42b EnWG / Solar Package I)",
                "summary_de": "Bürokratiearmer Solarstrom für Mehrparteienhäuser: Statische & dynamische 15m-Aufteilungsschlüssel (MEA), WEG-Beschlussvorlagen und AS4-Clearing ohne Versorgerpflichten.",
                "summary_en": "Streamlined solar for multi-family homes: Static & dynamic 15m allocation keys (MEA), HOA resolution templates, and AS4 grid clearing without full-supplier burdens.",
                "content_de": """# WEG & Gebäudeverwaltung: Gemeinschaftliche Gebäudeversorgung (§ 42b EnWG)

Mit dem **Solarpaket I** wurde die **Gemeinschaftliche Gebäudeversorgung (GGV)** gem. **§ 42b EnWG** eingeführt. Sie ermöglicht es Wohnungseigentümergemeinschaften (WEG), Vermietern und Mietergemeinschaften, Solarstrom vom eigenen Dach bürokratiearm im Gebäude aufzuteilen – **ohne Vollversorgerpflichten und ohne Gewerbeanmeldung**.

Das Modul **WEG & Gebäudeverwaltung** (`/app/admin/ggv`) führt Verwaltungen und Beiräte schrittweise durch Beschlüsse, Schlüsselaufteilung und Zählerabgleich.

---

## 1. Die Revolution des § 42b EnWG: GGV vs. Mieterstrom

| Kriterium | 🏢 Klassischer Mieterstrom (§ 42a EnWG) | ⚖️ Gemeinschaftliche Gebäudeversorgung (§ 42b EnWG) |
| :--- | :--- | :--- |
| **Versorgerpflicht** | **JA** (Vollversorgung mit Reststrom zwingend) | **NEIN** (Reine Solarstrom-Aufteilung; Reststrom bleibt frei) |
| **Reststromvertrag** | Betreiber muss Reststrom an der Strombörse einkaufen | Jeder Bewohner behält seinen eigenen Stromanbieter |
| **Bürokratieaufwand** | Hoch (EVU-Meldepflichten, Bilanzkreisabrechnung) | **Minimal** (Keine EVU-Registrierung notwendig) |
| **Messung** | Physische Kaskadenzähler oder Smart Meter | **Smart Meter (iMSys)** je Partei erforderlich |
| **Ideal für** | Große Wohnungsunternehmen & Contracting | **WEGs, Mehrfamilienhäuser, Vermieter ab 2 Einheiten** |

---

## 2. Die beiden 15-Minuten-Aufteilungsschlüssel

Gemäß § 42b Abs. 3 EnWG kann der erzeugte Solarstrom in jedem 15-Minuten-Intervall nach zwei Modellen aufgeteilt werden:

### A. Statischer Aufteilungsschlüssel (z. B. nach MEA oder Fläche)
* Jede Wohneinheit erhält einen festen prozentualen Anteil der jeweiligen Momentanerzeugung (z. B. 25 % bei 4 gleich großen Wohnungen oder gem. Miteigentumsanteil im Grundbuch).
* *Vorteil*: Maximale Einfachheit und absolute Planbarkeit für die Eigentümergemeinschaft.

### B. Dynamischer Aufteilungsschlüssel (Echtzeit-Optimierung)
* Der momentan erzeugte Solarstrom wird in jeder Viertelstunde **proportional zum tatsächlichen Momentanverbrauch** der teilnehmenden Parteien verteilt.
* *Vorteil*: Höchste solare Nutzungsquote im Gesamtgebäude; kein Strom wird ungenutzt eingespeist, wenn eine Partei gerade nicht zu Hause ist.

---

## 3. WEG-Beschlussvorlagen & Gebäudevertrag (§ 42b Abs. 2)

Im GGV-Cockpit stellt Sharegy rechtssichere Vorlagen für die Eigentümerversammlung bereit:

1. **Beschlussfassung in der WEG**:
   * Beschluss über die Errichtung / Nutzung der PV-Anlage auf dem Gemeinschaftseigentum.
   * Festlegung des Aufteilungsmodells (Statisch vs. Dynamisch).
2. **Gebäudevertrag (Vertrag zur gemeinschaftlichen Gebäudeversorgung)**:
   * Gesetzlich vorgeschriebener Vertrag zwischen Anlagenbetreiber/WEG und den teilnehmenden Parteien.
   * Regelt Solarpreis, Betriebskostenumlage, Instandhaltung und Kündigungsmöglichkeiten.

---

## 4. Messstellenbetrieb & BNetzA Marktkommunikation

Für die rechtskonforme Bilanzierung meldet Sharegy die 15-Minuten-Werte an den Netzbetreiber:

* **Smart Meter Gateway (SMGW)**: Auslesung über wMSB (z. B. Discovergy, Solandeo, inexogy) oder gMSB (CLS-Kanal).
* **AS4 MSCONS Dispatch**: Der Verteilnetzbetreiber zieht die solaren Bezugsmengen rechnerisch vom externen Netzbezug des jeweiligen Mieters ab. Der Mieter zahlt seinem externen Versorger automatisch nur noch den reduzierten Reststrom.
""",
                "content_en": """# HOA & Building Management: Collective Self-Supply (§ 42b EnWG)

Enacted under Germany's **Solar Package I (Solarpaket I)**, **Collective Building Supply (Gemeinschaftliche Gebäudeversorgung - GGV)** pursuant to **§ 42b EnWG** enables Homeowners Associations (HOA / WEG) and landlords to share rooftop solar energy across all building units **without supplier licensing or full-utility burdens**.

The **HOA & Building Management** module (`/app/admin/ggv`) guides property managers and boards through HOA resolutions, allocation key selection, and automated meter balancing.

---

## 1. § 42b EnWG vs. Classic Tenant Power

| Feature | 🏢 Classic Tenant Power (§ 42a EnWG) | ⚖️ Collective Self-Supply (§ 42b EnWG) |
| :--- | :--- | :--- |
| **Supplier Obligations** | **YES** (Must supply 100% residual grid electricity) | **NO** (Only allocates rooftop solar; grid power is independent) |
| **Grid Power Sourcing** | Operator must purchase grid electricity on spot markets | Each resident keeps their own individual grid provider |
| **Regulatory Burden** | High (Utility registration, balancing group audits) | **Minimal** (No energy utility registration required) |
| **Metering Setup** | Physical meter cascades or smart meters | **Smart Meter Gateways (iMSys)** per participating unit |
| **Best Suited For** | Large real estate developers & energy contractors | **HOAs, 2–30 unit apartment buildings, private landlords** |

---

## 2. 15-Minute Solar Allocation Models

Pursuant to § 42b para. 3 EnWG, rooftop solar is split in 15-minute settlement intervals:

### A. Static Allocation Key (e.g. Ownership Share / MEA)
* Each apartment receives a fixed percentage of momentary generation (e.g., 25% for 4 equal units or proportional to land registry co-ownership shares).
* *Benefit*: Predictable, transparent, and simple for HOA accounting.

### B. Dynamic Allocation Key (Real-Time Proportional)
* Momentary solar generation is distributed dynamically in every 15-minute window based on the **actual simultaneous consumption** of participating units.
* *Benefit*: Maximizes self-consumption; solar energy is not wasted when a resident is away.

---

## 3. HOA Resolutions & Statutory Building Agreement

The GGV cockpit generates ready-to-sign legal templates:

1. **HOA Assembly Resolution (WEG-Beschluss)**: Formal voting draft approving rooftop solar utilization and selected allocation key.
2. **Statutory Building Agreement (§ 42b para. 2 EnWG)**: Mandatory contract between building operator/HOA and participants detailing solar pricing, maintenance reserves, and exit clauses.

---

## 4. Metering & Automated Grid Operator Dispatch

* **Smart Meter Integration**: Data ingestion via independent metering operators (wMSB) or basic metering operators (gMSB CLS channel).
* **AS4 MSCONS Clearing**: Sharegy transmits 15-minute allocations to the local grid operator, automatically deducting on-site solar consumption from each resident's external utility bill.
""",
                "tags": ["ggv", "weg", "§ 42b", "solarpaket", "gemeinschaftliche gebaeudeversorgung", "mea", "aufteilungsschluessel", "eigentuemergemeinschaft"],
                "is_featured": True,
                "sort_order": 3,
            },
            {
                "category": cats["admin-governance"],
                "slug": "admin-energy-sharing-cooperative-guide",
                "context_key": "admin_sharing",
                "title_de": "Bürgerenergie & Genossenschaften: Energy Sharing, Mitgliederverwaltung & P2P-Strompool",
                "title_en": "Energy Cooperatives: Energy Sharing, Member Management & P2P Electricity Pool",
                "summary_de": "Bürgerstrom im virtuellen Bilanzkreis: 15-Minuten P2P-Sharing, Netzentgelt-Reduktion, Genossenschaftsanteile und transparente Mitgliederabrechnung.",
                "summary_en": "Local citizen energy pooling: 15-minute P2P sharing matrix, grid fee discounts, cooperative shares, and transparent member billing.",
                "content_de": """# Bürgerenergie & Genossenschaften (Energy Sharing)

Das Modul **Genossenschaft & Mitglieder** (`/app/admin/sharing`) ist die Steuerungsplattform für Bürgerenergiegenossenschaften (eG), Erneuerbare-Energien-Gemeinschaften (EEG) und regionale Energie-Sharing-Initiativen gem. der europäischen **Renewable Energy Directive II (EU RED II)** und dem **Genossenschaftsgesetz (GenG)**.

---

## 1. Das Sharegy Energy-Sharing-Konzept

Energy Sharing verbindet dezentrale Erzeuger (Solaranlagen, Bürger-Windparks, Biomasse) mit privaten und gewerblichen Verbrauchern in einem gemeinsamen virtuellen Strom-Pool:

```
[ Bürger-PV-Anlagen & Windparks ]
               |
    [ Virtueller Energy-Pool ] <---> [ Sharegy 15-Minuten P2P Matching Engine ]
               |
     +---------+---------+---------+
     |                   |         |
[ Mitglied A ]     [ Mitglied B ]  [ Mitglied C ]
 (Prosumer)         (Reiner Verbr.) (Gewerbe)
```

* **Viertelstündlicher P2P-Ausgleich**: In jedem 15-Minuten-Intervall matcht der Algorithmus Erzeugung und Verbrauch der Mitglieder.
* **Transparenter Bürgerstrom**: Mitglieder sehen in Echtzeit, aus welchen lokalen Anlagen ihr Strom stammt.
* **Finanzielle Vorteile**: Geringere Stromgestehungskosten, Netzentgeltreduktion bei regionalem Verbrauch und genossenschaftliche Rückvergütungen.

---

## 2. Mitgliederverwaltung & Onboarding-Workflow

Über das Genossenschafts-Cockpit verwalten Vorstände und Administratoren:

1. **Mitglieder-Einladungen**: Versenden personalisierter Registrierungslinks per E-Mail oder QR-Code.
2. **Anteilsverwaltung**: Erfassung der gezeichneten Genossenschaftsanteile gem. Satzung.
3. **Zähler- & Messstellen-Kopplung**: Verknüpfung von Smart Metern (iMSys) oder MID-Zählern der Mitglieder.
4. **Tarif- & Vergütungsmodelle**: Festlegung des internen Sharing-Arbeitspreises sowie der Einspeisevergütung für Überschusseinspeiser.

---

## 3. Das Transparenz-Cockpit (/app/admin/sharing)

Das Live-Dashboard visualisiert für das gesamte Kollektiv:

| Kennzahl | Bedeutung |
| :--- | :--- |
| **☀️ Kollektive Erzeugung** | Momentane Stromproduktion aller angeschlossenen Photovoltaik- und Erzeugungsanlagen |
| **⚡ Kollektiver Verbrauch** | Zeitgleiche Last aller privaten Haushalte und Gewerbemitglieder |
| **🔄 Geteilter Strom (Sharing)** | Menge an Strom, die im selben Zeitfenster innerhalb der Genossenschaft getauscht wurde |
| **🛡️ Autarkiegrad der Gemeinschaft** | Grad der Unabhängigkeit vom externen Großhandelsmarkt |
| **🌱 Vermiedenes CO2** | Einsparung an Treibhausgasen im Vergleich zum bundesweiten Strommix |

---

## 4. Abrechnung, Clearing & Dividenden-Ausschüttung

Sharegy automatisiert das genossenschaftliche Clearing:
* **Monatliche Abrechnungsbelege**: Aufschlüsselung über bezogenen Gemeinschaftsstrom, Reststrom und Einspeiseerlöse.
* **Gutschriften für Erzeuger**: Direkte Auszahlung der Erlöse an Mitglieder, die Solarstrom in den Pool einspeisen.
* **Jahresabschluss & Dividende**: Aggregierte Datenbasis für die Generalversammlung und Dividendenausschüttung.
""",
                "content_en": """# Citizen Energy Cooperatives (Energy Sharing)

The **Cooperative & Member Management** module (`/app/admin/sharing`) provides the core engine for Citizen Energy Cooperatives (eG), Renewable Energy Communities (REC), and local energy sharing pools under the EU **Renewable Energy Directive II (EU RED II)**.

---

## 1. The Sharegy Energy Sharing Architecture

Energy sharing dynamically links decentralized producers (community solar, wind farms, biomass) with local consumers in a shared virtual electricity pool:

* **15-Minute P2P Matching**: Advanced algorithms calculate quarter-hourly matching between local generation and consumption.
* **Source Transparency**: Members track in real time which local wind or solar system powers their home.
* **Economic Benefits**: Substantially lower levelized costs of electricity (LCOE), regional grid fee incentives, and cooperative patronage refunds.

---

## 2. Member Management & Onboarding

Cooperative boards and administrators manage workflows in one portal:

1. **Member Invitations**: Single-click invitation links via email or QR codes.
2. **Share Registry**: Audited tracking of subscribed cooperative equity shares.
3. **Meter Binding**: Linking Smart Meter Gateways (iMSys) or certified submeters.
4. **Internal Tariff Formulation**: Setting internal sharing tariffs and feed-in compensation for prosumers.

---

## 3. Community Transparency Cockpit (/app/admin/sharing)

| Metric | Meaning & Value |
| :--- | :--- |
| **☀️ Collective Generation** | Live power generation across all member solar and wind assets |
| **⚡ Collective Demand** | Simultaneous electricity demand of all participating homes and businesses |
| **🔄 Shared Energy** | Energy matched directly within the cooperative during the current interval |
| **🛡️ Community Autarky** | Collective independence percentage from external wholesale energy |
| **🌱 Carbon Offset** | Audited greenhouse gas abatement compared to national grid mix |

---

## 4. Clearing, Accounting & Dividend Payouts

* **Automated Monthly Invoices**: Detailed statements of shared energy, residual backup, and feed-in revenue.
* **Producer Credits**: Automated disbursements to members feeding solar into the collective pool.
* **Annual Assembly Export**: Audited accounting reports for the general assembly and statutory dividend distribution.
""",
                "tags": ["energy sharing", "genossenschaft", "buergerenergie", "red ii", "p2p", "strompool", "mitgliederverwaltung", "clearing"],
                "is_featured": True,
                "sort_order": 4,
            },
            {
                "category": cats["admin-governance"],
                "slug": "admin-vpp-flex-aggregator-guide",
                "context_key": "admin_vpp",
                "title_de": "VPP & Flex-Zentrale: Schwarm-Aggregation, § 14a EnWG, Eichrecht & 80/20 Clearing",
                "title_en": "VPP & Flex Control Center: Swarm Aggregation, § 14a EnWG, Legal Metrology & 80/20 Settlement",
                "summary_de": "Das Virtuelle Kraftwerk von Sharegy: Heimspeicher & SteuVE bündeln, § 14a Netzentgelt-Kalkulator, SMGW/CLS Inspector, PTB-A 50.7 Eichrecht und 80/20 Clearing Simulator.",
                "summary_en": "Sharegy Virtual Power Plant: Pooling home batteries & steerable loads, § 14a grid fee calculator, SMGW/CLS inspector, PTB-A 50.7 metrology verification, and 80/20 clearing simulator.",
                "content_de": """# VPP & Flex-Zentrale: Schwarm-Aggregation, § 14a EnWG, Eichrecht & 80/20 Clearing

Die **VPP & Flex-Zentrale** (`/app/admin/vpp`) vernetzt dezentrale Heimspeicher, steuerbare Verbrauchseinrichtungen (**§ 14a EnWG SteuVE**) wie Wallboxen und Wärmepumpen sowie Photovoltaikanlagen zu einem hochverfügbaren **Virtuellen Kraftwerk (Virtual Power Plant - VPP)**.

Betreiber monetarisieren Flexibilitäten an den Regelleistungsmärkten (aFRR / FCR), unterstützen Netzbetreiber bei **Redispatch 2.0 / Connect+**, prüfen eichrechtskonforme Messdaten nach **PTB-A 50.7** und schütten Erlöse automatisiert über ein faires **80/20-Clearing** an die Anlagenbesitzer aus.

---

## 1. Die Flexibilitäts-Säulen im Virtuellen Kraftwerk

Sharegy unterscheidet zwei fundamentale Steuerungsrichtungen:

| Flexibilitätsart | Technische Maßnahmen | Netzdienlicher Nutzen |
| :--- | :--- | :--- |
| **📈 Positive Flexibilität (+kW)** | * Entladung vernetzter Heimspeicher ins Haus/Netz<br>* § 14a Lastabwurf / Drosselung von Wallboxen & WP | Stützt das Netz bei Unterdeckung, Frequenzabfall und teuren Peak-Preisen |
| **📉 Negative Flexibilität (-kW)** | * Forciertes Laden von Speichern aus dem Netz<br>* Abregelung / Drosselung von PV-Einspeisung | Nimmt Überschussenergie bei Sturm/Sonnenspitzen auf und verhindert Netzüberlastungen |

---

## 2. § 14a EnWG Netzentgelt-Kalkulator & SteuVE-Flotte

Alle steuerbaren Verbrauchseinrichtungen mit einer Anschlussleistung ≥ 4,2 kW (Wallboxen, Wärmepumpen, Batteriespeicher) profitieren von reduzierten Netzentgelten gem. BNetzA-Beschluss:

1. **Modul 1 (Pauschale Vergütung)**:
   * Jährlicher Netzentgelt-Rabatt von ca. **130 € bis 190 € / Jahr** (bundesweiter Durchschnitt).
   * Kein separater Zähler erforderlich.
2. **Modul 2 (Prozentuale Reduktion)**:
   * **60 % Erlass auf den Arbeitspreis** des Netzentgelts (Ct/kWh).
   * Besonders rentabel für Wärmepumpen & Vielfahrer-Wallboxen ab ~3.500 kWh Jahresverbrauch.
   * Separater Unterzähler / Messlokation (MeLo) erforderlich.
3. **Modul 3 (Zeitvariable Netzentgelte)**:
   * Dynamische Netzentgelte in Hoch-, Standard- und Niedriglastzeiten ab 2025.

---

## 3. SMGW & CLS-Kanal Inspector (BSI TR-03109-1)

Der integrierte CLS-Inspector überwacht die hochsichere Steuerungsinfrastruktur:
* **TLS 1.3 & PKI-Status**: Gültigkeit der BSI-zertifizierten Sub-CA Zertifikate des Smart Meter Gateways.
* **Protokoll-Brücken**: Latenzüberwachung für **EEBUS (SPINE/SHIP)**, **OCPP 1.6-J / 2.0.1** und **Modbus TCP**.
* **4,2 kW Dimm-Garantie**: Strikte Einhaltung der BNetzA-Vorgabe (Mindestleistung 4,2 kW verbleibt immer beim Kunden).

---

## 4. Eichrechtskonforme Messwert-Prüfung (PTB-A 50.7)

Zur revisionssicheren Abrechnung von VPP-Dispatches und Mieterstrom validiert Sharegy Rohmesswerte:
* **Kryptographische Signatur-Prüfung**: SHA-256 Digest-Validierung und Public-Key-Abgleich der SML/OBIS-Zählerstände (1.8.0 Netzbezug, 2.8.0 Einspeisung).
* **Transparenzsoftware-Kompatibilität**: 100 % konform mit den Prüfregeln der Physikalisch-Technischen Bundesanstalt (PTB).
* **Automatisierter Audit-Eintrag**: Jede Prüfung wird unveränderlich im `AuditLog` protokolliert.

---

## 5. VPP Sandbox Clearing Simulator (80/20 Payout)

Im interaktiven Simulator können Betreiber Markt-Ausschreibungen und Spotmarkt-Arbitrage testen:
* **80 % Prosumer Pool Payout**: Direkte Ausschüttung an die beteiligten Heimspeicher- und Anlagenbesitzer.
* **20 % Sharegy Aggregator-Marge**: Deckung von Netzzugang, Prognosemodellen und Betrieb.
* **Ökologischer Nachweis**: Exakte Ausweisung der vermiedenen CO₂-Emissionen (Peak-Shaving).""",
                "content_en": """# VPP & Flex Control Center: Swarm Aggregation, § 14a EnWG, Legal Metrology & 80/20 Settlement

The **VPP & Flex Control Center** (`/app/admin/vpp`) aggregates residential battery storage, controllable loads pursuant to **§ 14a EnWG (SteuVE)** such as EV wallboxes and heat pumps, and solar assets into a high-availability **Virtual Power Plant (VPP)**.

Operators monetize flexible capacity across balancing markets (aFRR / FCR), support DSOs with **Redispatch 2.0 / Connect+**, verify metrology signatures pursuant to **PTB-A 50.7**, and disburse revenues automatically via a transparent **80/20 market clearing** model.

---

## 1. Flexibility Pillars in the Virtual Power Plant

| Flexibility Vector | Physical Execution | Grid & Economic Function |
| :--- | :--- | :--- |
| **📈 Positive Flexibility (+kW)** | * Coordinated home battery discharge<br>* § 14a load shedding / throttling of EV chargers & heat pumps | Supports the grid during supply deficits, under-frequency events, and peak prices |
| **📉 Negative Flexibility (-kW)** | * Forced grid-charging into batteries<br>* Curtailed / throttled PV feed-in | Absorbs wind and solar surpluses during negative pricing events, preventing transformer overload |

---

## 2. § 14a EnWG Grid Fee Calculator & SteuVE Fleet

All steerable loads ≥ 4.2 kW (EV chargers, heat pumps, batteries) benefit from statutory grid fee reductions:

1. **Module 1 (Flat Reimbursement)**:
   * Fixed annual discount of approx. **€130 to €190 / year**.
   * No separate dedicated smart meter required.
2. **Module 2 (Percentage Discount)**:
   * **60% reduction on the volumetric grid fee** (ct/kWh).
   * Maximum savings for high-consumption heat pumps & EV fleets (>3,500 kWh/yr).
   * Requires a dedicated meter point (MeLo).
3. **Module 3 (Time-Variable Grid Tariffs)**:
   * Dynamic grid fees across peak, standard, and off-peak hours.

---

## 3. SMGW & CLS Channel Inspector (BSI TR-03109-1)

The integrated CLS inspector monitors the secure communication pipeline:
* **TLS 1.3 & PKI Health**: Sub-CA certificate validity and encryption cipher suites.
* **Protocol Bridges**: Latency tracking for **EEBUS (SPINE/SHIP)**, **OCPP 1.6-J / 2.0.1**, and **Modbus TCP**.
* **4.2 kW Floor Guarantee**: Assures minimum guaranteed power for consumer emergency operation.

---

## 4. Legal Metrology Verification (PTB-A 50.7 / German Eichrecht)

For tamper-proof billing of flexibility dispatches and tenant energy:
* **Cryptographic Signature Verification**: SHA-256 digest validation and public-key verification of SML/OBIS meter telegrams.
* **Transparency Software Compliance**: 100% compliant with PTB-A 50.7 verification rules.
* **Immutable Audit Trail**: Every validation is permanently recorded in the system audit log.

---

## 5. VPP Sandbox Clearing Simulator (80/20 Payout)

Test balancing tenders and spot market arbitrage in an interactive simulation sandbox:
* **80% Prosumer Pool Payout**: Direct financial disbursement to home battery owners.
* **20% Sharegy Aggregator Margin**: Platform infrastructure and market access fee.
* **CO₂ Avoidance Telemetry**: Quantifies avoided greenhouse gas emissions through peak-shaving.""",
                "tags": ["vpp", "flexibilitaet", "regelleistung", "afrr", "redispatch 2.0", "clearing", "14a enwg", "steuve", "eichrecht", "ptb", "cls"],
                "is_featured": True,
                "sort_order": 5,
            },
            {
                "category": cats["admin-governance"],
                "slug": "admin-partner-fleet-installer-guide",
                "context_key": "admin_partner",
                "title_de": "Fachpartner & Flottenmanagement: 1-Klick IBN, 6-in-1 Fernwartungs-Konsole & Abnahmeprotokolle",
                "title_en": "Certified Installers & Fleet Management: 1-Click Commissioning, 6-in-1 Remote Console & Protocols",
                "summary_de": "Leitfaden für Solarteure & Fachbetriebe: Flottenüberwachung (/app/partner), 3-Sekunden Schnell-Inbetriebnahme, bidirektionale Fernwartung und digitale IBN-Protokolle.",
                "summary_en": "Installer handbook: fleet monitoring (/app/partner), 3-second rapid commissioning, bidirectional remote maintenance console, and digital handover protocols.",
                "content_de": """# Fachpartner & Flottenmanagement-Portal

Das **Fachpartner- und Installateurs-Portal** (`/app/partner`) wurde speziell für Solarteure, Elektrofachbetriebe, Servicetechniker und Systemhäuser entwickelt. Es minimiert den Zeitaufwand bei der Inbetriebnahme (IBN) vor Ort und ermöglicht eine lückenlose **6-in-1 Fernwartung** ohne zeitraubende Vor-Ort-Fahrten.

---

## 1. Das Flotten-Dashboard im Überblick

Im Partner-Cockpit haben Installateure alle betreuten Kundenanlagen im Blick:

| KPI & Status | Funktionsumfang |
| :--- | :--- |
| **🏢 Betreute Kundenanlagen** | Gesamtübersicht aller installierten Systeme mit Live-Online/Offline-Status |
| **☀️ Installierte Gesamtleistung** | Summe der installierten PV-Kapazität (kWp) und Echtzeit-Erzeugung |
| **🔋 Heimspeicher & Ø SoC** | Anzahl der Batteriesysteme und durchschnittlicher Ladezustand der Flotte |
| **🚗 § 14a SteuVE (Dimmbar)** | Registrierte Wallboxen und Wärmepumpen mit aktivem Dimmstatus |
| **🛡️ Flotten-Health-Score** | 0–100 % Qualitätsindex; automatische Erkennung von Störungen und Ertragsausfällen |
| **🚨 Offene Service-Tickets** | Priorisierte Liste von Kunden mit Handlungsbedarf |

---

## 2. 1-Klick Schnell-Inbetriebnahme (IBN in unter 3 Minuten)

Vor Ort beim Kunden ermöglicht der geführte IBN-Assistent:

1. **QR-Code / Seriennummern-Scan**: Automatisches Einlesen von Wechselrichter, Speicher und Zähler.
2. **Automatischer Modbus-TCP / Cloud-Scan**: Sharegy erkennt automatisch Wechselrichter-Hersteller (SMA, Sungrow, Fronius, SolarEdge, Kostal, Deye, Huawei, GoodWe etc.) und konfiguriert alle Register.
3. **3-Sekunden Hardware-Selbsttest**: 
   * Überprüfung von Phasendrehfeldern und Zählerpolarität (Verhinderung von Fehlverdrahtungen).
   * Test-Kommunikation mit Steuerbox (§ 14a EnWG) und Wallbox.
4. **Digitales IBN-Abnahmeprotokoll (PDF)**:
   * Rechtssicheres Protokoll nach **VDE-AR-N 4105** mit Zeitstempel, Seriennummern und Messwerten.
   * Direkter PDF-Export zur Vorlage beim Verteilnetzbetreiber und Kundenunterschrift auf dem Tablet.

---

## 3. Die 6-in-1 Fernwartungs-Konsole

Treten beim Kunden Fragen oder Störungen auf, öffnet der Partner mit einem Klick die **Fernwartungs-Konsole**:

```
[ 6-in-1 Fernwartungs-Konsole ]
  |-- 1. Register-Direktabfrage (Modbus/REST Live-Werte)
  |-- 2. Grid-Code & Wirkleistungsbegrenzung (Cos Phi / 70% / 4,2 kW)
  |-- 3. Firmware- & Konfigurations-Update (OTA Push)
  |-- 4. Steuerbox- & § 14a Relaistest (Schaltprüfung)
  |-- 5. Batteriezellen-Balancing & SoC-Kalibrierung
  `-- 6. Fehlerspeicher (DTC) & Diagnose-Ereignislog
```

---

## 4. Live-Ansicht (Kunden-EMS direkt spiegeln)

Über die Funktion **„Live-Ansicht (Kunden-EMS)“** kann der Support-Techniker das Kunden-Dashboard exakt so einsehen wie der Kunde selbst:
* Identifikation von Fehlkonfigurationen im Smart Energy Optimizer.
* Überprüfung von Prioritätsregeln für Wallbox-Überschussladen.
* Anpassung dynamischer Stromtarif-Schwellenwerte aus der Ferne.

---

## 5. Präventive Störungserkennung & Health-Scores

Sharegy analysiert kontinuierlich alle Telemetriedaten und schlägt Alarm bei:
* **String-Ausfällen**: Erkennung von Mismatch oder defekten Modulsträngen durch DC-Spannungsvergleich.
* **Batteriezellen-Drift**: Frühzeitige Warnung bei abweichenden Zellspannungen vor Tiefentladung.
* **Isolationsfehlern**: Erkennung von Feuchtigkeitseintritten vor Auslösen des FI-Schutzschalters.
""",
                "content_en": """# Certified Installers & Fleet Management Portal

The **Partner & Installer Portal** (`/app/partner`) is engineered specifically for solar EPCs, electrical contractors, and maintenance engineers. It drastically shortens on-site commissioning (IBN) time and delivers a comprehensive **6-in-1 remote maintenance console** to eliminate unnecessary truck rolls.

---

## 1. Fleet Dashboard Overview

The partner dashboard provides instantaneous visibility across all managed customer sites:

| KPI & Status | Core Capabilities |
| :--- | :--- |
| **🏢 Managed Customer Sites** | Complete registry of deployed systems with real-time online/offline heartbeat |
| **☀️ Total Installed Capacity** | Combined PV peak capacity (kWp) and instantaneous generation |
| **🔋 Battery Fleet & Avg. SoC** | Total connected battery systems and fleet-wide average state of charge |
| **🚗 § 14a SteuVE (Dimmable)** | Registered EV chargers and heat pumps with active grid dimming status |
| **🛡️ Fleet Health Score** | 0–100 % aggregate reliability score with automated anomaly detection |
| **🚨 Active Service Tickets** | Prioritized action items and diagnostic alerts |

---

## 2. 1-Click Rapid Commissioning (Under 3 Minutes)

The on-site commissioning wizard guides technicians through:

1. **QR Code / Serial Scan**: Instantaneous binding of inverters, batteries, and smart meters.
2. **Automated Modbus TCP / Cloud Discovery**: Auto-detects inverters (SMA, Sungrow, Fronius, SolarEdge, Kostal, Deye, Huawei, GoodWe etc.) and configures all register addresses.
3. **3-Second Diagnostic Self-Test**: Validates grid phase rotation, CT clamp polarity, and § 14a relay responses.
4. **Digital Handover Protocol (PDF)**:
   * Generates a compliant **VDE-AR-N 4105 handover protocol** with cryptographic timestamps, serial numbers, and live electrical telemetry.
   * Direct customer on-glass tablet signature for immediate submission to the grid operator.

---

## 3. The 6-in-1 Remote Maintenance Console

When customer anomalies arise, technicians launch the **Remote Console**:

1. **Live Register Query**: Raw Modbus/REST polling of electrical parameters.
2. **Grid-Code & Power Limits**: Adjusting Cos Phi, active power derating, or 4.2 kW ceilings.
3. **Firmware & Config Push**: Over-the-air parameter and firmware deployments.
4. **Steuerbox & § 14a Relay Test**: Actuating digital contacts to confirm VNB dimming readiness.
5. **Battery Balancing & SoC Calibration**: Forced top-balancing cycles for drifted battery packs.
6. **Diagnostic Trouble Codes (DTC)**: Inverter fault log inspection with clear actionable remedies.

---

## 4. Live EMS Mirror (Customer Dashboard View)

Using the **"Live View (Customer EMS)"** bridge, engineers mirror the exact customer dashboard to assist with optimizer scheduling, EV priority settings, or dynamic tariff thresholds without physical visits.

---

## 5. Predictive Maintenance & Anomaly Detection

* **String Degradation**: Identifies shaded, soiled, or disconnected PV strings via DC voltage comparison.
* **Cell Voltage Drift**: Early alerts for battery cell imbalance before degradation occurs.
* **Insulation Resistance Warnings**: Alerts on moisture ingress before ground fault trips occur.
""",
                "tags": ["partner", "solarteur", "installateur", "flottenmanagement", "inbetriebnahme", "ibn", "vde-ar-n 4105", "fernwartung", "modbus"],
                "is_featured": True,
                "sort_order": 6,
            },
            {
                "category": cats["admin-governance"],
                "slug": "admin-audit-trail-guide",
                "context_key": "admin_audit_logs",
                "title_de": "Enterprise Audit Trail, Revisionssicherheit & KRITIS-Nachweisführung",
                "title_en": "Enterprise Audit Trail, Compliance & KRITIS Event Logging",
                "summary_de": "Vollständige Dokumentation des revisionssicheren Audit-Loggings: SHA-256 Signaturen, Vorher/Nachher-Diffs, EnWG § 14a Nachweisführung, CSV-Export und ISO 27001 / SOC 2 Konformität.",
                "summary_en": "Complete guide to tamper-proof audit logging: SHA-256 signatures, before/after JSON diffs, EnWG § 14a proof of dispatch, CSV export, and ISO 27001 / SOC 2 compliance.",
                "content_de": """# Enterprise Audit Trail & Revisionsprotokoll

Das **Audit Trail & Revisions-Cockpit** (`/app/admin/audit-logs`) stellt die lückenlose, unveränderliche Aufzeichnung aller administrativen, steuerungs- und sicherheitsrelevanten Aktionen innerhalb der Sharegy-Plattform sicher.

Es erfüllt die strengen Anforderungen des **Energiewirtschaftsgesetzes (EnWG § 14a)**, des **BSI IT-Sicherheitsgesetzes 2.0 (KRITIS)**, der **DSGVO** sowie relevanter Compliance-Frameworks wie **ISO/IEC 27001** und **SOC 2 Type II**.

---

## 1. Architektur & Revisionssicherheit

Jeder schreibende oder steuernde Zugriff wird im System automatisch über das `core.services_audit` Subsystem erfasst:

| Parameter | Beschreibung & Revisionswert |
| :--- | :--- |
| **Zeitstempel (UTC)** | Mikrosekundengenauer Zeitstempel mit Zeitzonen-Offset |
| **Akteur & Identität** | Benutzer-ID, E-Mail-Adresse und Rollenberechtigung (Superuser, Staff, Partner) |
| **Netzwerk-Kontext** | Client-IP-Adresse (X-Forwarded-For bereinigt) und User-Agent |
| **Aktion & Ressourcentyp** | Eindeutiger Aktionscode (z.B. `VPP_DISPATCH_TRIGGERED`, `STEUVE_DIMMING_APPLIED`, `CONFIG_UPDATED`) |
| **Vorher/Nachher-Diff** | Vollständiger JSON-Snapshot der geänderten Attribute zur exakten Rekonstruktion |
| **Schweregrad** | Einstufung in `info`, `warning`, `critical` oder `security` |

---

## 2. KRITIS & § 14a EnWG Nachweisführung

Im Rahmen von Netzengpass-Drosselungen und Redispatch 2.0-Abrufen verlangen Verteilnetzbetreiber (VNB) und die Bundesnetzagentur (BNetzA) einen lückenlosen Konformitätsnachweis:

1. **Dimm-Befehle**: Jeder 4,2 kW Sollwert-Eingriff wird mit Ziel-Liegenschaft, Leistungswert und Quell-Signal (VNB Relais oder CLS) unveränderlich protokolliert.
2. **PTB-A 50.7 Eichrechts-Nachweis**: Prüfungsergebnisse kryptographischer Zählersignaturen werden mit SHA-256 Hash im Log abgelegt.
3. **80/20 Clearing-Transaktionen**: Auszahlungsberechnungen an Prosumer werden revisionssicher eingefroren.

---

## 3. Filterung, Suche & CSV-Audit-Export

Für interne und externe Wirtschaftsprüfungen (Audits) bietet das Cockpit:
* **Echtzeit-Filter**: Nach Schweregrad, Aktionstyp und Suchbegriffen (IP, E-Mail, Objekt-ID).
* **Detail-Inspektor**: Klick auf ein Ereignis öffnet das formatierte Vorher/Nachher-Diff.
* **1-Klick CSV-Export**: Exportiert gefilterte Prüfberichte im UTF-8 CSV-Format für Behörden und Auditoren.
""",
                "content_en": """# Enterprise Audit Trail & Compliance Logging

The **Enterprise Audit Trail Cockpit** (`/app/admin/audit-logs`) provides an immutable, tamper-proof record of all administrative, dispatch, and security events across the Sharegy energy management platform.

It is engineered to fulfill statutory requirements under the **German Energy Industry Act (EnWG § 14a)**, **BSI Critical Infrastructure Regulations (KRITIS)**, **GDPR / DSGVO**, and international enterprise compliance frameworks including **ISO/IEC 27001** and **SOC 2 Type II**.

---

## 1. Architecture & Immutability

Every modifying API call and control dispatch is automatically intercepted by the `core.services_audit` pipeline:

| Audit Parameter | Description & Compliance Value |
| :--- | :--- |
| **Timestamp (UTC)** | Microsecond-precise UTC timestamp with timezone awareness |
| **Actor & Identity** | User ID, email, and permission level (superuser, staff, partner admin) |
| **Network Context** | Client IP address and HTTP User-Agent string |
| **Action & Resource** | Unique action key (e.g. `VPP_DISPATCH_TRIGGERED`, `STEUVE_DIMMING_APPLIED`, `SETTLEMENT_PROCESSED`) |
| **Before / After Diff** | Full JSON snapshot of state changes for precise forensic reconstruction |
| **Severity Level** | Classified into `info`, `warning`, `critical`, or `security` |

---

## 2. KRITIS & § 14a EnWG Proof of Dispatch

Grid operators and the Federal Network Agency (BNetzA) mandate strict verifiable audit logs for grid flexibility interventions:

1. **Dimming Commands**: Every 4.2 kW ceiling intervention is logged with target home, duration, and triggering source.
2. **PTB-A 50.7 Metrology Proof**: Cryptographic validation digests are permanently tied to audit logs.
3. **Settlement Runs**: 80/20 prosumer payout distributions are frozen against retrospective alteration.

---

## 3. Filtering, Inspection & CSV Audit Export

* **Multi-Vector Filtering**: Filter by severity, action category, or search keywords.
* **Forensic Inspector**: Visualizes full JSON state differences.
* **1-Click CSV Export**: Exports filtered audit reports formatted for external compliance auditors.
""",
                "tags": ["audit", "revision", "compliance", "kritis", "enwg 14a", "iso 27001", "soc 2", "sicherheit", "dsgvo"],
                "is_featured": True,
                "sort_order": 7,
            },
            {
                "category": cats["admin-governance"],
                "slug": "admin-tracking-telemetry-guide",
                "context_key": "admin_tracking",
                "title_de": "Event-Tracking, Telemetrie-Analytics & Conversion-Funnel",
                "title_en": "Event Tracking, Telemetry Analytics & Conversion Funnel",
                "summary_de": "Leitfaden für Telemetrie-Analytics: Nutzerinteraktionen, 7-Tage Event-Trend, Onboarding-Funnel, Magic-Link Tracking und datenschutzkonforme Auswertungen.",
                "summary_en": "Guide to telemetry analytics: User interactions, 7-day event volume trends, onboarding conversion funnel, magic-link tracking, and GDPR-compliant metrics.",
                "content_de": """# Event-Tracking, Telemetrie-Analytics & Conversion-Funnel

Das **Event-Tracking & Telemetrie-Dashboard** (`/app/admin/tracking`) liefert tiefe Einblicke in die tatsächliche Nutzung der Sharegy-Plattform, die Effektivität des Registrierungstrichters und die Beliebtheit einzelner Features.

Alle Telemetriedaten werden **DSGVO-konform** erhoben, anonymisiert verarbeitet und ermöglichen datenbasierte Produktentscheidungen.

---

## 1. Der Onboarding- & Registrierungs-Funnel

Der Trichter visualisiert die User Journey vom Erstbesuch bis zum aktiven Dashboard-Nutzer:

1. **🌐 Landing Page Aufruf (`landing_view`)**: Impressionen der Startseite und Kampagnen-Seiten.
2. **📝 Registrierung geklickt (`signup_click`)**: Nutzer initiiert den Registrierungs- oder Login-Flow.
3. **✉️ Magic-Link angefordert (`magic_link_requested`)**: Versand der passwortlosen Authentifizierungs-E-Mail.
4. **📬 E-Mail geöffnet (`email_open`)**: Bestätigung der Zustellung im Postfach.
5. **🖱️ Link angeklickt (`magic_link_click`)**: Nutzer klickt den sicheren Token-Link.
6. **🔑 Erfolgreich eingeloggt (`magic_login_success`)**: Verifizierung des Tokens und Session-Start.
7. **🏠 Dashboard geöffnet (`dashboard_open`)**: Ankunft im Live-Energiemonitoring.

---

## 2. 7-Tage Timeline & Trend-Analyse

Das interaktive Flächendiagramm stellt das tägliche Eventvolumen der letzten 7 Tage dar:
* **Lastspitzen**: Identifikation von Nutzungspeaks nach Newslettern oder Preisänderungen.
* **Aktivitäts-Muster**: Erkennung von Wochenend- vs. Werktagsnutzung.

---

## 3. Detail-Tabelle & Häufigkeitsverteilung

Die aggregierte Ereignis-Tabelle schlüsselt alle Events nach Name, Icon, Gesamtzahl und prozentualem Anteil am Gesamtvolumen auf.
""",
                "content_en": """# Event Tracking, Telemetry Analytics & Conversion Funnel

The **Event Tracking & Telemetry Dashboard** (`/app/admin/tracking`) delivers product telemetry insights into user engagement, feature adoption, and onboarding funnel conversion rates.

All telemetry is collected strictly in compliance with **GDPR / DSGVO** standards without collecting unauthorized personal data.

---

## 1. The Onboarding & Registration Funnel

The conversion funnel tracks the user journey from landing page visit to active dashboard engagement:

1. **🌐 Landing Page View (`landing_view`)**: Public website visits and marketing landing pages.
2. **📝 Signup Clicked (`signup_click`)**: User starts the onboarding or login flow.
3. **✉️ Magic Link Requested (`magic_link_requested`)**: Passwordless email token dispatch.
4. **📬 Email Open (`email_open`)**: Delivery and inbox confirmation.
5. **🖱️ Link Clicked (`magic_link_click`)**: User clicks verification link.
6. **🔑 Login Success (`magic_login_success`)**: Session authentication established.
7. **🏠 Dashboard Opened (`dashboard_open`)**: First arrival in the live energy dashboard.

---

## 2. 7-Day Timeline & Trend Analysis

The interactive chart provides a rolling 7-day timeline of aggregate platform events to detect engagement spikes and marketing campaign resonance.

---

## 3. Event Breakdown & Relative Distribution

The breakdown table classifies every event type with total execution counts and relative share of total platform activity.
""",
                "tags": ["tracking", "telemetrie", "analytics", "funnel", "conversion", "magic link", "onboarding", "events"],
                "is_featured": False,
                "sort_order": 8,
            },
            {
                "category": cats["admin-governance"],
                "slug": "admin-support-desk-guide",
                "context_key": "admin_support",
                "title_de": "Support-Zentrale: Multi-Mandanten-Triage & Ticket-Management",
                "title_en": "Agent Support Hub: Multi-Tenant Triage & Ticket Management",
                "summary_de": "Leitfaden für die Support-Zentrale: Globale Triage von Sharegy EMS und Factofy Tickets, SLA-Überwachung, Status-Workflows und Fachpartner-Eskalation.",
                "summary_en": "Guide to the Agent Support Hub: Global triage across Sharegy EMS and Factofy tickets, SLA monitoring, status workflows, and installer escalation.",
                "content_de": """# Support-Zentrale: Multi-Mandanten-Triage & Ticket-Management

Die **Support-Zentrale** (`/app/support-hub` bzw. `/app/support`) dient als zentraler Helpdesk für Support-Mitarbeiter, Administratoren und Fachpartner.

Sie bündelt alle Kundenanfragen, Störungsmeldungen und Hardware-Diagnosen über das gesamte Ökosystem – inklusive **Sharegy EMS** (B2C Prosumer & Quartiere) und **Factofy** (B2B Gewerbe- und Industriemanagement).

---

## 1. Multi-Mandanten Projektfilter

Über die Schnellfilter in der Kopfzeile filtern Agenten den Arbeitsvorrat:
* **🌐 Alle Tickets**: Übergreifende Gesamtansicht für Hauptadministratoren.
* **☀️ Sharegy Tickets**: Private Haushalte, Mieterstrom-Teilnehmer und Heimspeicher-Besitzer.
* **🏙️ Factofy Tickets**: Gewerbliche Liegenschaften, Lastspitzenkappung (Peak-Shaving) und Industrie-Submeter.

---

## 2. Ticket-Status & Workflow

Jedes Support-Ticket durchläuft einen definierten Lifecycle:

| Status | Bedeutung & nächste Aktion |
| :--- | :--- |
| **🔵 Offen (`open`)** | Neues Ticket, wartet auf Zuweisung oder Erstprüfung |
| **🟡 In Bearbeitung (`in_progress`)** | Agent oder Fachpartner analysiert das Problem aktiv |
| **🟣 Wartet auf Kunde (`waiting_on_customer`)** | Rückfrage oder Messdatenanforderung an den Kunden gesendet |
| **🟢 Gelöst (`resolved`)** | Problem behoben, Kunde informiert |
| **⚪ Geschlossen (`closed`)** | Abgeschlossener Vorgang im Revisionsarchiv |

---

## 3. Schnelle Störungsbehebung & Diagnose-Verknüpfung

Support-Mitarbeiter können direkt aus dem Ticket heraus:
* **Geräte-Telemetrie einsehen**: Wechselrichter-Verbindungsstatus, Zählerstände und Fehlercodes.
* **Prioritäten anpassen**: Einstufung in `Niedrig`, `Normal`, `Hoch` oder `Kritisch (P1)`.
* **Fachpartner eskalieren**: Tickets an den zuständigen Installationsbetrieb weiterleiten.
""",
                "content_en": """# Agent Support Hub: Multi-Tenant Triage & Ticket Management

The **Agent Support Hub** (`/app/support-hub`) serves as the mission control center for support engineers, staff administrators, and certified installation partners.

It unifies incoming support requests, diagnostic alerts, and customer inquiries across the entire ecosystem – including **Sharegy EMS** (residential & community energy) and **Factofy** (industrial submetering & peak shaving).

---

## 1. Multi-Tenant Project Filter

Agents can quickly isolate their scope of work:
* **🌐 All Tickets**: Unified global queue for primary dispatchers.
* **☀️ Sharegy Tickets**: Residential households, tenant power participants, and home battery owners.
* **🏙️ Factofy Tickets**: Commercial properties, industrial loads, and enterprise microgrids.

---

## 2. Ticket Lifecycle & SLA Tracking

Every support ticket progresses through standard workflow states:
* **🔵 Open (`open`)**: Newly received, awaiting initial assessment.
* **🟡 In Progress (`in_progress`)**: Actively investigated by support or technical engineers.
* **🟣 Waiting on Customer (`waiting_on_customer`)**: Additional telemetry or customer clarification requested.
* **🟢 Resolved (`resolved`)**: Root cause rectified, customer notified.
* **⚪ Closed (`closed`)**: Archived in historical knowledge base.

---

## 3. Diagnostic Integration & Partner Escalation

* **Live Telemetry Inspect**: Direct bridge to inverter error codes and meter communication states.
* **Priority Escalation**: Triage severity from Low to Critical (P1 SLA).
* **Partner Dispatch**: Seamless assignment to the responsible installer contractor.
""",
                "tags": ["support", "helpdesk", "triage", "tickets", "sla", "sharegy", "factofy", "kundenservice"],
                "is_featured": True,
                "sort_order": 9,
            },
            # ---------------------------------------------------------------------
            # 11. ADMIN & GOVERNANCE: ENTERPRISE RBAC ROLLENMATRIX & RECHTEVERWALTUNG
            # ---------------------------------------------------------------------
            {
                "category": cats["admin-governance"],
                "slug": "enterprise-rbac-rollenmatrix-und-berechtigungen",
                "context_key": "admin_rbac_matrix",
                "title_de": "Enterprise Multi-Tenant RBAC: Benutzerrollen, Rechte & Berechtigungsmatrix",
                "title_en": "Enterprise Multi-Tenant RBAC: User Roles, Permissions & Access Control Matrix",
                "summary_de": "Vollständiger Leitfaden zur rollenbasierten Zugriffskontrolle (RBAC): SuperAdmin, Operations/Dispatcher, Billing Specialist, Field Technician, Auditor & Community-Rollen.",
                "summary_en": "Comprehensive guide to Role-Based Access Control (RBAC): SuperAdmin, Operations/Dispatcher, Billing Specialist, Field Technician, Auditor & Community roles.",
                "content_de": """# Enterprise Multi-Tenant RBAC: Benutzerrollen, Rechte & Berechtigungsmatrix

Sharegy implementiert eine **zweistufige Enterprise-Rollenarchitektur (Multi-Tenant RBAC)**, die strenge Funktionstrennung (Separation of Duties) für Stadtwerke, Wohnungsbaugesellschaften, Bürgerenergiegenossenschaften und Großkunden gewährleistet.

---

## 1. Die 2-Ebenen-Architektur im Überblick

```
┌────────────────────────────────────────────────────────────────────────┐
│ EBENE 1: Globale Sharegy Plattform (Global / Staff)                    │
│  - 👑 SuperAdmin (Vollzugriff)     - ⚡ Operations / Dispatcher (VPP)    │
│  - 💳 Billing Specialist (Finanzen)- 👥 Global User-Admin              │
│  - 🛟 Plattform Helpdesk                                               │
└───────────────────────────────────┬────────────────────────────────────┘
                                    │ hostet & delegiert
                                    ▼
┌────────────────────────────────────────────────────────────────────────┐
│ EBENE 2: Lokale Quartiere / Liegenschaften / Partner (Multi-Tenant)    │
│  - 🏛️ Quartiers-Admin (WEG/EVU)   - 🔧 Field Technician (Installateur) │
│  - 👥 Energy-Userverwaltung        - 📊 Kassenprüfer / Auditor (Read-Only)
│  - 🛟 Energy-Helpdesk (Support)    - ⚡ Community-Mitglied (Endkunde)   │
└────────────────────────────────────────────────────────────────────────┘
```

---

## 2. Detaillierte Rollenübersicht

### 👑 1. SuperAdmin (`system_admin` / `is_superuser`)
* **Zielgruppe**: Sharegy Betreiberteam & Hauptadministratoren von Stadtwerken.
* **Befugnisse**: Voller Systemzugriff auf alle Plattform-Module, Mandanten, API-Keys, Django Admin, Systemgesundheit und Datenbank-Migrationen.

### ⚡ 2. Operations / Dispatcher (VPP & Steuerung)
* **Zielgruppe**: Technische Leitwarten, Netzbetreiber-Dispatcher und VPP-Aggregatoren.
* **Befugnisse**:
  * Vollzugriff auf das Virtuelle Kraftwerk ([`/app/admin/vpp`](file:///app/admin/vpp)), Redispatch 2.0 / Connect+ Fahrpläne und aFRR-Abrufe.
  * Steuerung netzdienlicher Lastdrosselungen gem. § 14a EnWG ([`/app/control`](file:///app/control)).
  * **Datenschutz-Schutzregel**: Kein Zugriff auf Endkunden-Bankverbindungen oder personenbezogene Abrechnungsdetails.

### 💳 3. Billing Specialist (`finance`)
* **Zielgruppe**: Buchhaltung, Abrechnungsdienstleister und Finanzbeiräte.
* **Befugnisse**:
  * Verwaltung von Stripe-Zahlungsströmen, SEPA-Lastschriftläufen und Clearing-Abrechnungen.
  * Festschreibung monatlicher Abrechnungsbescheide gem. § 42b / § 42a EnWG.
  * Zählerstands-Export (DATEV CSV, MSCONS 2.2b, Excel).

### 🔧 4. Field Technician / Fachpartner (`installer` / `PartnerMembership`)
* **Zielgruppe**: Elektro-Installateure, Solarteure und Instandhaltungsteams.
* **Befugnisse**:
  * Flotten-Management ([`/app/partner`](file:///app/partner)), Asset-Onboarding und 3-Sekunden-Diagnosetests.
  * Erstellung digitaler Inbetriebsetzungs- & Übergabeprotokolle nach VDE-AR-N 4105.
  * Fernwartung und Firmware-Status bei Störungsmeldungen.

### 📊 5. Auditor / Kassenprüfer (`auditor` - Read-Only)
* **Zielgruppe**: Revisionsprüfer, WEG-Beiräte, Steuerberater und Aufsichtsräte.
* **Befugnisse**:
  * Vollständiger **Read-Only-Zugriff** auf Quartiersbilanzen, Verbrauchszeitreihen, Abrechnungsberichte und das Enterprise Audit-Log ([`/app/admin/audit-logs`](file:///app/admin/audit-logs)).
  * **Sicherheitsgarantie**: Keine Berechtigung zum Bearbeiten von Daten, Schalten von Geräten oder Ändern von Tarifen.

### 👥 6. Community-Userverwaltung (`user_admin`)
* **Zielgruppe**: Hausverwaltungen und Mieterbetreuer vor Ort.
* **Befugnisse**: Erstellung von Einladungslinks für Nachbarn/Mieter, Rollenzuweisung (`member`, `helpdesk`, `auditor`) und Stammdatenpflege.

### ⚡ 7. Community-Mitglied (`member`)
* **Zielgruppe**: Endnutzer, Mieter und Prosumer.
* **Befugnisse**: Einsicht in die persönlichen Live-Flüsse, 15m-Zuteilungen, Monatsabrechnungen und Ersparnisrechner.

---

## 3. Vollständige Berechtigungsmatrix

| Berechtigung | SuperAdmin | Operations / Dispatcher | Billing Specialist | Field Technician | Auditor (Read-Only) | Community Admin | Mitglied |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **System-Infrastruktur & API-Keys** | ✅ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ |
| **VPP Flexibilität & Dispatch-Abruf** | ✅ | ✅ | ❌ | ❌ | ❌ | ❌ | ❌ |
| **§ 14a SteuVE Lastdrosselung** | ✅ | ✅ | ❌ | ❌ | ❌ | ❌ | ❌ |
| **Monatsabrechnungen (§ 42b EnWG)** | ✅ | ❌ | ✅ | ❌ | 👁️ *(Lesen)* | ✅ | 👁️ *(Eigen)* |
| **Stripe & SEPA Finanzströme** | ✅ | ❌ | ✅ | ❌ | ❌ | ❌ | ❌ |
| **IBN-Protokolle (VDE-AR-N 4105)** | ✅ | ❌ | ❌ | ✅ | 👁️ *(Lesen)* | 👁️ *(Lesen)* | ❌ |
| **Fernwartung & Diagnostik** | ✅ | ❌ | ❌ | ✅ | ❌ | ❌ | ❌ |
| **Audit-Log Einsicht (ISO 27001)** | ✅ | 👁️ *(Lesen)* | 👁️ *(Lesen)* | ❌ | ✅ | 👁️ *(Tenant)* | ❌ |
| **Dokumenten-Manager (Download Hub)** | ✅ | ❌ | ✅ | ✅ | ✅ | ✅ | ✅ |

---

## 4. Rollenhierarchie & Schutzregeln

1. **Selbsterhöhungs-Schutz (Privilege Escalation Guard)**:
   * Ein `user_admin` kann nur Rollen bis zur eigenen Berechtigungsstufe vergeben. Er kann **keine neuen Admins ernennen** und bestehende Admins nicht herabstufen.
2. **Revisionssichere Protokollierung**:
   * Jede Zuweisung, Änderung oder Entziehung einer Rolle wird unveränderlich mit IP-Adresse, Timestamp und Akteur im [`core_auditlog`](file:///app/admin/audit-logs) festgehalten.
""",
                "content_en": """# Enterprise Multi-Tenant RBAC: User Roles, Permissions & Access Control Matrix

Sharegy enforces a **two-tier Enterprise Role-Based Access Control (RBAC) architecture**, providing strict Separation of Duties for utilities, housing corporations, energy sharing cooperatives, and enterprise customers.

---

## 1. Two-Tier Hierarchy Overview

```
┌────────────────────────────────────────────────────────────────────────┐
│ TIER 1: Global Sharegy Platform (Global / Staff)                       │
│  - 👑 SuperAdmin (Full Access)      - ⚡ Operations / Dispatcher (VPP)   │
│  - 💳 Billing Specialist (Finance)  - 👥 Global User-Admin             │
│  - 🛟 Platform Helpdesk                                                │
└───────────────────────────────────┬────────────────────────────────────┘
                                    │ hosts & delegates
                                    ▼
┌────────────────────────────────────────────────────────────────────────┐
│ TIER 2: Local Communities / Properties / Partners (Multi-Tenant)       │
│  - 🏛️ Community Admin (HOA/Utility) - 🔧 Field Technician (Installer)  │
│  - 👥 Member Administrator          - 📊 Auditor / Inspector (Read-Only)│
│  - 🛟 Community Helpdesk (Support)  - ⚡ Resident Member (Consumer)     │
└────────────────────────────────────────────────────────────────────────┘
```

---

## 2. Detailed Role Profiles

* **👑 SuperAdmin (`system_admin` / `is_superuser`)**: Complete root access across all platform modules, tenants, migration pipelines, and API integrations.
* **⚡ Operations / Dispatcher**: Full command over the Virtual Power Plant ([`/app/admin/vpp`](file:///app/admin/vpp)), Redispatch 2.0 schedules, and § 14a EnWG controllable load dimming ([`/app/control`](file:///app/control)), with no access to billing/banking data.
* **💳 Billing Specialist (`finance`)**: In charge of Stripe settlement runs, SEPA batches, § 42b EnWG monthly statement finalization, and DATEV/MSCONS exports.
* **🔧 Field Technician (`installer` / `PartnerMembership`)**: Partner fleet monitoring ([`/app/partner`](file:///app/partner)), VDE-AR-N 4105 digital commissioning protocols, and remote diagnostic testing.
* **📊 Auditor / Inspector (`auditor` - Read-Only)**: Zero write access; complete read-only review rights for community balances, settlement records, and the compliance audit log ([`/app/admin/audit-logs`](file:///app/admin/audit-logs)).
* **👥 Member Admin (`user_admin`)**: Local resident onboarding, invitation token management, and basic role provisioning.
* **⚡ Resident Member (`member`)**: Personal dashboard access to real-time power flows, 15-minute community allocation, and personal statements.

---

## 3. Comprehensive Permission Matrix

| Capability | SuperAdmin | Operations / Dispatcher | Billing Specialist | Field Technician | Auditor (Read-Only) | Community Admin | Resident Member |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **System Infrastructure & Keys** | ✅ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ |
| **VPP Flexibility & Dispatch** | ✅ | ✅ | ❌ | ❌ | ❌ | ❌ | ❌ |
| **§ 14a EnWG Curtailment** | ✅ | ✅ | ❌ | ❌ | ❌ | ❌ | ❌ |
| **Monthly Statements (§ 42b)** | ✅ | ❌ | ✅ | ❌ | 👁️ *(Read)* | ✅ | 👁️ *(Self)* |
| **Stripe & SEPA Financials** | ✅ | ❌ | ✅ | ❌ | ❌ | ❌ | ❌ |
| **Commissioning Protocols** | ✅ | ❌ | ❌ | ✅ | 👁️ *(Read)* | 👁️ *(Read)* | ❌ |
| **Remote Maintenance & Tests** | ✅ | ❌ | ❌ | ✅ | ❌ | ❌ | ❌ |
| **Audit Log (ISO 27001)** | ✅ | 👁️ *(Read)* | 👁️ *(Read)* | ❌ | ✅ | 👁️ *(Tenant)* | ❌ |
| **Document Hub Access** | ✅ | ❌ | ✅ | ✅ | ✅ | ✅ | ✅ |
""",
                "tags": ["rbac", "roles", "superadmin", "dispatcher", "billing", "installer", "auditor", "berechtigungen", "rollenmatrix", "governance"],
                "is_featured": True,
                "sort_order": 1,
            },
            # ---------------------------------------------------------------------
            # 12. ADMIN & GOVERNANCE: REVISIONSSICHERHEIT & AUDIT TRAIL (ISO 27001 / GoBD)
            # ---------------------------------------------------------------------
            {
                "category": cats["admin-governance"],
                "slug": "revisionssicherheit-audit-trail-und-gobd-compliance",
                "context_key": "admin_audit_gobd",
                "title_de": "Revisionssicherheit & Audit Trail: GoBD-, ISO 27001- und EnWG-Compliance",
                "title_en": "Audit Trail & Security Governance: GoBD, ISO 27001 and EnWG Compliance",
                "summary_de": "Revisionssichere Protokollierung aller administrativen Aktionen, § 14a EnWG Drosselungsnachweise, PTB-A 50.7 Eichrecht und GoBD-konforme Archivierung.",
                "summary_en": "Immutable activity logging of administrative events, § 14a EnWG dimming proofs, PTB-A 50.7 calibration crypto signatures, and GoBD compliance.",
                "content_de": """# Revisionssicherheit & Audit Trail: GoBD-, ISO 27001- und EnWG-Compliance

Für Stadtwerke, Wohnungsbaugesellschaften und Energiegemeinschaften gelten strenge gesetzliche Anforderungen an die **Nachvollziehbarkeit, Unveränderbarkeit und Revisionssicherheit** digitaler Prozesse (ISO 27001, SOC 2, GoBD, § 14a EnWG, MessEG).

Sharegy stellt hierfür eine integrierte Compliance- und Audit-Log-Architektur bereit.

---

## 1. Enterprise Audit Log (`core_auditlog`)

Jede sicherheitskritische Aktion im System wird **automatisch und unveränderbar** mit vollständigem Kontext protokolliert:

* **Echtzeit-Metadaten**:
  * Timestamp mit Zeitzone (`Europe/Berlin`)
  * Akteur (Benutzer-ID & E-Mail)
  * Quell-IP-Adresse (inkl. Reverse-Proxy Header `X-Forwarded-For`)
  * User-Agent & Client-Typ (Web / Native App / API)
* **Diff-Tracking**: Vorher/Nachher-Vergleich geänderter Parameter (z. B. Netzdienlichkeits-Grenzwerte oder Rollenzuweisungen).
* **Severity-Klassifizierung**: `info`, `warning`, `critical`.

```
Beispiel-Ereignisse im Audit-Log:
• ROLE_ASSIGNED: Akteur admin@stadtwerke.de weist user@quartier.de die Rolle 'auditor' zu.
• STEUVE_DIMMING_TRIGGERED: VNB-Befehl dimmt Wärmepumpe WP-102 auf 4,2 kW (gem. § 14a EnWG).
• STATEMENT_FINALIZED: Monatsabrechnung ABR-202609 für Liegenschaft Spreeblick festgeschrieben.
• EICHRECHT_VERIFY: Zählerstand 1EMH0012398471 kryptographisch gem. PTB-A 50.7 validiert.
```

Das Audit-Log kann von berechtigten Auditoren und Administratoren unter [`/app/admin/audit-logs`](file:///app/admin/audit-logs) eingesehen und im CSV-/Excel-Format exportiert werden.

---

## 2. § 14a EnWG Netzdrosselungs-Nachweisführung

Im Rahmen des § 14a EnWG müssen Netzbetreiber und Betreiber steuerbarer Verbrauchseinrichtungen (SteuVE) netzdienliche Dimm-Ereignisse revisionssicher nachweisen können:

* **Protokollierung im `EnWG14aDimmingAuditLog`**:
  * Signal-Empfang über den CLS-Kanal (BSI TR-03109-1)
  * Quittierungs-Latenz (in Millisekunden)
  * Leistungsreduktion auf maximal 4,2 kW je Großlast
  * Wiederherstellung des Normalbetriebs nach Entwarnung

---

## 3. Eichrechtskonforme Messwertsignaturen (PTB-A 50.7)

Alle 15-Minuten-Lastgänge und Zählerstände werden mit kryptographischen Signaturen (ECDSA Secp256r1) versehen und sind mit der offiziellen **Transparenzsoftware** der PTB prüfbar.

---

## 4. Zentraler Dokumenten- & Download-Hub (`/app/documents`)

Alle generierten PDF-Monatsabrechnungen, IBN-Übergabeprotokolle nach VDE-AR-N 4105 und Eichrechtsberichte werden im [Dokumenten-Manager](file:///app/documents) revisionssicher historisiert und stehen für Wirtschaftsprüfer und Kassenprüfer jederzeit zum 1-Klick-Download bereit.
""",
                "content_en": """# Audit Trail & Security Governance: GoBD, ISO 27001 and EnWG Compliance

Utilities, housing associations, and energy communities are subject to stringent regulatory requirements regarding **traceability, immutability, and auditability** (ISO 27001, SOC 2, GoBD, § 14a EnWG, MessEG).

Sharegy delivers an integrated compliance, audit logging, and cryptographic verification architecture.

---

## 1. Enterprise Audit Log (`core_auditlog`)

Every security-relevant operation is recorded in an immutable ledger with full contextual telemetry:
* **Real-time Telemetry**: UTC/Europe timezone timestamp, actor ID & email, origin IP address (`X-Forwarded-For`), and user-agent.
* **Diff Tracking**: Before/After state differences for modified parameters (e.g. curtailment limits, tariff modifications, role transitions).
* **Severity Levels**: `info`, `warning`, `critical`.

Review and export the live audit log at [`/app/admin/audit-logs`](file:///app/admin/audit-logs).

---

## 2. § 14a EnWG Curtailment Compliance Ledger

Complies with mandatory grid operator reporting:
* Logged in `EnWG14aDimmingAuditLog` with CLS channel ingest (BSI TR-03109-1).
* Sub-second acknowledgment timestamps and 4.2 kW power ceiling confirmation.

---

## 3. PTB-A 50.7 Cryptographic Verification & Document Hub

* 15-minute smart meter readings signed with ECDSA Secp256r1 / SHA-256 for PTB Transparency Software compatibility.
* Centralized historical access to all statements, commissioning protocols, and certificates via the [Download Hub](file:///app/documents).
""",
                "tags": ["audit", "compliance", "gobd", "iso27001", "revisionssicherheit", "enwg14a", "ptb", "eichrecht", "dokumente"],
                "is_featured": True,
                "sort_order": 2,
            },
            # ---------------------------------------------------------------------
            # 13. ADMIN & BILLING: ZENTRALER DOKUMENTEN- & EXPORT-MANAGER (DOWNLOAD HUB)
            # ---------------------------------------------------------------------
            {
                "category": cats["admin-governance"],
                "slug": "zentraler-dokumenten-und-export-manager-download-hub",
                "context_key": "document_download_hub",
                "title_de": "Zentraler Dokumenten- & Export-Manager: Monatsabrechnungen, Berichte & Download Hub",
                "title_en": "Central Document & Export Manager: Monthly Statements, Reports & Download Hub",
                "summary_de": "Vollständige Anleitung zum Dokumenten-Manager: Historisierte PDF-Abrechnungen (§ 42b EnWG), EMS-Jahresberichte, IBN-Protokolle, DATEV-Exporte und On-Demand Generator.",
                "summary_en": "Complete guide to the Document Hub: Historical PDF statements (§ 42b EnWG), EMS annual reports, commissioning protocols, DATEV exports, and On-Demand Generator.",
                "content_de": """# Zentraler Dokumenten- & Export-Manager: Monatsabrechnungen, Berichte & Download Hub

Der **Zentrale Dokumenten- & Export-Manager** ([`/app/documents`](file:///app/documents)) bündelt alle im System erzeugten Abrechnungen, Messzertifikate, Energieberichte und Inbetriebnahmeprotokolle an einer einzigen, revisionssicheren Stelle.

---

## 1. Übersicht & Kernfunktionen

Der Download Hub erfüllt wesentliche gesetzliche und betriebliche Anforderungen (GoBD, § 14 UStG, EnWG § 42b, ISO 27001):

* 📂 **Zentrale Historisierung**: Alle generierten Monatsabschlüsse, Zählerlisten und Prüfberichte bleiben dauerhaft archiviert und können jederzeit erneut heruntergeladen werden.
* ⚡ **On-Demand Sofort-Export Generator**: Erzeuge Ad-hoc-Berichte für beliebige Zeiträume (Heute, Monat, Vormonat, Gesamtjahr) in deinem Wunschformat (PDF, Excel, CSV, JSON).
* 🔍 **Live-Suche & Filterleiste**: Filtere nach Dokumentenkategorie oder suche direkt nach Rechnungsnummer, Zähler-Seriennummer oder Liegenschaft.
* ⚖️ **Kryptographisches Prüfsiegel**: Jedes Dokument besitzt eine eindeutige SHA-256 Prüfsumme zur revisionssicheren Verifikation gegenüber Wirtschaftsprüfern, Finanzamt und Steuerberatern.

---

## 2. Unterstützte Dokumenttypen & Exportformate

| Dokumenttyp | Kategorie | Rechtsgrundlage / Norm | Verfügbare Dateiformate |
| :--- | :--- | :--- | :--- |
| **Monatsabrechnungsbescheide** | 📄 Abrechnungen | § 42b / § 42a EnWG, § 14 UStG | 📄 PDF (Druckbescheid), 📊 Excel (.xlsx), 📝 CSV (DATEV), 💻 XML / ERP |
| **EMS Energie- & Autarkieberichte** | ⚡ Energiebilanzen | DIN EN ISO 50001, EnWG | 📄 PDF (Auswertungsbericht), 📊 Excel (.xlsx), 📝 CSV-Rohdaten, 💻 JSON |
| **Digitale IBN- & Übergabeprotokolle** | 🔧 IBN-Protokolle | VDE-AR-N 4105, § 14a EnWG, NAV | 📄 PDF (Rechtsverbindliches Übergabeprotokoll mit TREI-Zertifikat) |
| **Eichrechts- & Messzertifikate** | ⚖️ Eichrecht & Zähler | MessEG, PTB-A 50.7, BSI TR-03109-1 | 📄 PDF (Signaturprüfbericht), 📊 CSV (15m MSCONS EDIFACT Lastgang) |
| **DSGVO Datenabzug** | 🔒 Datenschutz | Art. 15 & Art. 20 EU-DSGVO | 💻 JSON (Vollständiges Maschinenlesbares Archiv) |

---

## 3. Der On-Demand Export-Generator

Über die obere Schnell-Aktionsleiste im Dokumenten-Manager können individuelle Berichte ohne vorherigen Monatsabschluss erzeugt werden:

1. **Berichtstyp wählen**: Energiebilanz & Autarkie, Digitales IBN-Protokoll oder PTB-A 50.7 Eichrechtsnachweis.
2. **Zeitraum wählen**:
   * *Heute (Live)*: Sub-Sekunden-Snapshot des aktuellen Tages.
   * *Laufender Monat*: Bisherige Monatssummen und Autarkiegrad.
   * *Letzter Monat*: Abgeschlossener Vormonat.
   * *Gesamtjahr (YTD)*: Jahresenergiefluss und CO₂-Einsparung.
3. **Format wählen**: PDF für Vorlagen und Druck, Excel `.xlsx` für Tabellenkalkulation, CSV für DATEV-Buchhaltung oder JSON für Entwickler.
4. Klick auf **„Download“**: Der Download startet sofort im Browser.

---

## 4. Revisions- & Prüfnachweis-Modal

Durch Klick auf **„Details & Prüfsiegel“** bei einem Dokument öffnet sich das Inspektions-Modal:
* Anzeige des kryptographischen SHA-256 Hashes
* Verknüpfte Zähler- und Asset-IDs
* Bestätigung des WORM-konformen Festschreibungsstatus (Write Once, Read Many)
""",
                "content_en": """# Central Document & Export Manager: Monthly Statements, Reports & Download Hub

The **Central Document & Export Manager** ([`/app/documents`](file:///app/documents)) consolidates all generated financial statements, calibration certificates, energy balances, and commissioning records in a single audit-ready workspace.

---

## 1. Overview & Key Capabilities

* 📂 **Centralized Archival**: Historical statements and meter reading logs remain persistently accessible.
* ⚡ **On-Demand Export Generator**: Generate custom reports for any time window (Today, Month, Last Month, Full Year) in PDF, Excel, CSV, or JSON.
* 🔍 **Smart Filter & Search**: Instantly locate records by invoice number, meter serial, or community name.
* ⚖️ **Cryptographic Verification**: Every document includes a SHA-256 checksum for audit compliance (GoBD, ISO 27001, § 14 UStG).

---

## 2. Document Types & Formats

* **Monthly Settlement Statements (§ 42b EnWG)**: Formats: PDF, Excel (.xlsx), DATEV CSV, XML ERP.
* **EMS Energy & Autarky Balances**: Formats: PDF report, Excel, raw CSV, JSON.
* **Digital Commissioning Protocols (VDE-AR-N 4105)**: Formats: Official PDF handover protocol with contractor certification.
* **Eichrecht & Meter Certificates (PTB-A 50.7)**: Formats: PDF proof, 15-minute MSCONS EDIFACT CSV.
* **GDPR Data Export (Art. 15 / 20)**: Formats: RFC 8259 JSON full archive.
""",
                "tags": ["dokumente", "export", "download", "pdf", "excel", "datev", "abrechnung", "ibn", "eichrecht", "download-hub"],
                "is_featured": True,
                "sort_order": 3,
            },
        ]

        valid_slugs = set()
        for adata in articles_data:
            valid_slugs.add(adata["slug"])
            HelpArticle.objects.update_or_create(
                slug=adata["slug"],
                defaults=adata,
            )

        # Bereinige veraltete / gelöschte Artikel (z.B. frühere Entwürfe wie Matter)
        deleted_matter, _ = HelpArticle.objects.filter(slug__icontains="matter").delete()
        if deleted_matter > 0:
            self.stdout.write(self.style.WARNING(f"[CLEANUP] {deleted_matter} veraltete Matter-Artikel aus der Datenbank entfernt."))

        deleted_obsolete, _ = HelpArticle.objects.exclude(slug__in=valid_slugs).delete()
        if deleted_obsolete > 0:
            self.stdout.write(self.style.WARNING(f"[CLEANUP] {deleted_obsolete} nicht mehr im Handbuch definierte Artikel entfernt."))

        self.stdout.write(self.style.SUCCESS(f"[OK] Erfolgreich {len(categories_data)} Kategorien und {len(articles_data)} Handbuch-Artikel in DE & EN initialisiert!"))


