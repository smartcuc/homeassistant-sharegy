# Walkthrough: Bereitstellung des Help-Systems & Handbuchs (DE & EN)

Alle Kategorien, Handbuch-Artikel, FAQ-Texte und Kontext-Verknüpfungen für das **Help-System & Wissensportal** wurden vollständig auf **Deutsch (DE)** und **Englisch (EN)** ausgearbeitet und als Live-Import bereitgestellt.

---

### 📦 Enthaltene Kategorien & Themen (8 Hauptkategorien)

1. 🚀 **Erste Schritte & Grundlagen (`getting-started`)**
   * *DE*: Schnelleinstieg, Onboarding, Dashboard-Navigation und Kennzahlen im Überblick.
   * *EN*: Quickstart guides, onboarding, dashboard navigation, and core energy KPIs.
2. ☀️ **Erzeuger, Speicher & Wechselrichter (`inverters-meters`)**
   * *DE*: Anbindung von SMA, Sungrow, Fronius, Deye, Huawei, Batteriespeichern und Zählern.
   * *EN*: Setup guides for SMA, Sungrow, Fronius, Deye, Huawei, home batteries, and meters.
3. 📈 **Solar- & Lastprognose (`forecast`)**
   * *DE*: Hybrid-Prognosen, Wettermodelle, Güte-Score (%-Genauigkeit) und Ist-vs-Soll-Vergleich.
   * *EN*: Hybrid forecasting, weather models, accuracy score (%), and actual vs. forecast tracking.
4. 🤖 **Smart Energy Optimizer & EMS (`optimizer`)**
   * *DE*: Automatisierte Fahrpläne für E-Auto (Wallbox), Hausspeicher, Wärmepumpen & Haushaltsgeräte.
   * *EN*: Automated schedules for EV wallboxes, home batteries, heat pumps, and appliances.
5. ⚡ **Strompreise & Börsenstrom (`tariffs`)**
   * *DE*: Dynamische Tarife, Tibber API, Day-Ahead-Preise, Formeln und stichtagsgenaue Tarifhistorie.
   * *EN*: Dynamic tariffs, Tibber API, spot market prices, pricing formulas, and historical rates.
6. 🚨 **Alarm- & Notifikationszentrale (`alerts`)**
   * *DE*: Echtzeit-Regeln für Ertragsausfälle, Tiefentladeschutz, Dauerlasten und Spar-Chancen.
   * *EN*: Real-time health rules for yield losses, battery protection, baseload alerts, and savings tips.
7. 🧾 **Abrechnung & Mieterstrom (`billing`)**
   * *DE*: Virtuelle Zähler, Sub-Metering, Kostenallokation für WEGs und monatliche PDF-Reports.
   * *EN*: Virtual meters, sub-metering, multi-tenant cost allocation, and monthly PDF exports.
8. 🔌 **Geräte, MQTT & Protokolle (`devices-protocols`)**
   * *DE*: Integration von Home Assistant, ioBroker, Shelly, Tasmota, Modbus RTU/TCP und REST APIs.
   * *EN*: Integration with Home Assistant, ioBroker, Shelly, Tasmota, Modbus, and REST APIs.

---

### 📄 Ausgearbeitete Handbuch-Artikel (Vollständige Markdown-Texte)

| Slug / ID | Kategorie | Context-Key | Titel (DE) | Title (EN) |
|---|---|---|---|---|
| `energiebilanz-und-autarkiegrad` | `getting-started` | `energy_dashboard` | Energiebilanz, Autarkiegrad & Eigenverbrauchsquote | Energy Balance, Autarky Rate & Self-Consumption |
| `erzeuger-und-batteriespeicher-konfiguration` | `inverters-meters` | `producers` | Erzeuger- & Speicheranlagen: Konfiguration & Messstellen | Producers & Storage: Setup & Metric Mapping |
| `sma-sungrow-modbus-tcp-einrichten` | `inverters-meters` | `devices` | Modbus TCP für SMA, Sungrow, Fronius & Deye freischalten | Enabling Modbus TCP for SMA, Sungrow, Fronius & Deye |
| `solar-prognose-und-genauigkeit` | `forecast` | `forecast` | Solar-Prognose, Wettermodelle & Genauigkeitsabgleich | Solar Forecasting, Weather Models & Accuracy Score |
| `lastprognose-und-haushaltsverbrauch` | `forecast` | `forecast` | Haushalts-Lastprognose & Wochentags-Profile | Household Load Forecasting & Weekly Profiles |
| `smart-energy-optimizer-funktionsweise` | `optimizer` | `optimizer` | Smart Energy Optimizer: Zeitfenster & Fahrplan optimal nutzen | Smart Energy Optimizer: 1h/2h/4h Time Windows & Scheduling |
| `stromtarife-und-stichtagsberechnung` | `tariffs` | `tariffs` | Strompreise, Stichtage & Tarifhistorie verwalten | Managing Electricity Tariffs, Effective Dates & Price History |
| `dynamische-stromtarife-und-tibber` | `tariffs` | `tariffs` | Dynamische Börsenstrompreise & Tibber API Anbindung | Dynamic Spot Tariffs & Tibber API Integration |
| `alarmzentrale-und-anomalieerkennung` | `alerts` | `alerts` | Alarm- & Notifikationszentrale: Echtzeit-Regeln | Alert & Notification Center: Live Rules & Anomaly Detection |
| `virtuelle-zaehler-und-submetering` | `billing` | `billing` | Virtuelle Zähler, Sub-Metering & Mieterstrom-Abrechnung | Virtual Meters, Sub-Metering & Multi-Tenant Billing |
| `mqtt-und-smart-home-integration` | `devices-protocols` | `devices` | MQTT, Home Assistant, ioBroker & Shelly Zähler anbinden | Connecting MQTT, Home Assistant, ioBroker & Shelly Meters |

---

### 🚀 Ausführung des Imports auf dem Live-Server

Der Import kann auf dem Produktionsserver über zwei Wege ausgeführt werden:

#### Option A: Über das Django Management Command (Empfohlen)
```bash
python manage.py seed_helpcenter
```

#### Option B: Über das JSON-Fixture
```bash
python manage.py loaddata helpcenter_initial_data.json
```
*(Die Fixture-Datei liegt unter [`helpcenter/fixtures/helpcenter_initial_data.json`](file:///c:/Users/Public/Dev/eswes/helpcenter/fixtures/helpcenter_initial_data.json))*
