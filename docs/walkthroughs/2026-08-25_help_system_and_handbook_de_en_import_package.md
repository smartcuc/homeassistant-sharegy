# 📚 Walkthrough: Help-System & Wissensportal – Vollständiges Importpaket (DE & EN)

**Datum**: 25. August 2026  
**Bereich**: In-App Help-Drawer, Wissensportal, FAQ-System, Headless CMS, Live-Import  
**Status**: ✅ Vollständig implementiert & verifiziert

---

## 🎯 1. Überblick & Zusammenfassung

Für das **Help-System & Wissensportal** (Task 5.4 & Task 5.5) wurden alle 8 Hauptkategorien sowie 11 vollständige Handbuch-Artikel und FAQ-Themen zweisprachig auf **Deutsch (DE)** und **Englisch (EN)** ausgearbeitet und als betriebsbereites Importpaket bereitgestellt.

Damit stehen sowohl für das **In-App Slide-Over Help-Drawer** (kontextsensitive Schnellhilfe je Route) als auch für das **vollständige Wissensportal** (/app/help) alle redaktionellen und technischen Inhalte direkt zur Verfügung.

---

## 📦 2. Enthaltene Kategorien (8 Hauptbereiche)

| Icon | Key | Kategorie (DE) | Category (EN) | Beschreibung / Scope |
| :--- | :--- | :--- | :--- | :--- |
| 🚀 | getting-started | **Erste Schritte & Grundlagen** | **Getting Started & Basics** | Schnelleinstieg, Onboarding, Dashboard-Navigation, Autarkie & Eigenverbrauch. |
| ☀️ | inverters-meters | **Erzeuger, Speicher & Wechselrichter** | **Inverters, Storage & PV** | SMA, Sungrow, Fronius, Deye, Huawei, Strings, Batteriespeicher & Zähler. |
| 📈 | orecast | **Solar- & Lastprognose** | **Solar & Load Forecast** | Hybrid-Wettermodell, Güte-Score (%-Genauigkeit), Ist-vs-Soll-Vergleich, Lastmuster. |
| 🤖 | optimizer | **Smart Energy Optimizer & EMS** | **Smart Energy Optimizer & EMS** | 1h/2h/4h Zeitfenster, Wallbox-Laden, Wärmepumpen-SG-Ready, Speicherfahrpläne. |
| ⚡ | 	ariffs | **Strompreise & Börsenstrom** | **Electricity Tariffs & Dynamic Pricing** | Dynamische Tarife, Tibber API, Day-Ahead-Preise, Formeln, Stichtagshistorie. |
| 🚨 | lerts | **Alarm- & Notifikationszentrale** | **Alert & Notification Center** | 8 Echtzeit-Regeln: Ertragsausfall, Tiefentladeschutz, Dauerlast, Börsentief-Chance. |
| 🧾 | illing | **Abrechnung & Mieterstrom** | **Billing & Sub-Metering** | Virtuelle Zähler, Sub-Metering, Zählerallokation WEG, monatliche PDF-Reports. |
| 🔌 | devices-protocols | **Geräte, MQTT & Protokolle** | **Devices, MQTT & Protocols** | Home Assistant, ioBroker, Shelly 3EM, Tasmota, Modbus TCP/RTU, REST APIs. |

---

## 📄 3. Enthaltene Handbuch-Artikel & FAQ-Kapitel (Volltext DE & EN)

| Slug | Kategorie | Context-Key | Titel (DE) | Title (EN) |
| :--- | :--- | :--- | :--- | :--- |
| energiebilanz-und-autarkiegrad | getting-started | energy_dashboard | Energiebilanz, Autarkiegrad & Eigenverbrauchsquote | Energy Balance, Autarky Rate & Self-Consumption |
| erzeuger-und-batteriespeicher-konfiguration | inverters-meters | producers | Erzeuger- & Speicheranlagen: Konfiguration & Messstellen | Producers & Storage: Setup & Metric Mapping |
| sma-sungrow-modbus-tcp-einrichten | inverters-meters | devices | Modbus TCP für SMA, Sungrow, Fronius & Deye freischalten | Enabling Modbus TCP for SMA, Sungrow, Fronius & Deye |
| solar-prognose-und-genauigkeit | orecast | orecast | Solar-Prognose, Wettermodelle & Genauigkeitsabgleich | Solar Forecasting, Weather Models & Accuracy Score |
| lastprognose-und-haushaltsverbrauch | orecast | orecast | Haushalts-Lastprognose & Wochentags-Profile | Household Load Forecasting & Weekly Profiles |
| smart-energy-optimizer-funktionsweise | optimizer | optimizer | Smart Energy Optimizer: Zeitfenster & Fahrplan optimal nutzen | Smart Energy Optimizer: 1h/2h/4h Time Windows & Scheduling |
| stromtarife-und-stichtagsberechnung | 	ariffs | 	ariffs | Strompreise, Stichtage & Tarifhistorie verwalten | Managing Electricity Tariffs, Effective Dates & Price History |
| dynamische-stromtarife-und-tibber | 	ariffs | 	ariffs | Dynamische Börsenstrompreise & Tibber API Anbindung | Dynamic Spot Tariffs & Tibber API Integration |
| larmzentrale-und-anomalieerkennung | lerts | lerts | Alarm- & Notifikationszentrale: Echtzeit-Regeln | Alert & Notification Center: Live Rules & Anomaly Detection |
| irtuelle-zaehler-und-submetering | illing | illing | Virtuelle Zähler, Sub-Metering & Mieterstrom-Abrechnung | Virtual Meters, Sub-Metering & Multi-Tenant Billing |
| mqtt-und-smart-home-integration | devices-protocols | devices | MQTT, Home Assistant, ioBroker & Shelly Zähler anbinden | Connecting MQTT, Home Assistant, ioBroker & Shelly Meters |

---

## 🚀 4. Import & Deployment auf dem Live-System

Für das Einspielen der Daten in die Produktionsdatenbank stehen zwei Standard-Wege zur Verfügung:

### Option A: Über den Django Management-Befehl (Empfohlen)
`ash
python manage.py seed_helpcenter
`
* Führt idempotente update_or_create-Operationen für alle Kategorien und Artikel aus.
* Überschreibt oder aktualisiert bestehende Standardartikel sauber und sicher.

### Option B: Über die generierte JSON-Fixture
`ash
python manage.py loaddata helpcenter_initial_data.json
`
* **Dateipfad**: helpcenter/fixtures/helpcenter_initial_data.json
* Enthält 19 serialisierte Datenbank-Objekte (8 Kategorien + 11 Artikel) in reinem UTF-8.

---

## 🧪 5. Verifikation & Qualitätssicherung

* **Django Tests**: Alle 31 Backend-Tests erfolgreich (Ran 31 tests in 47.31s - OK).
* **Frontend-Build**: Vite Production Build erfolgreich (✓ built in 4.72s).
* **Zweisprachigkeit**: Alle Artikel verfügen über vollständige Felder 	itle_de, 	itle_en, summary_de, summary_en, content_de, content_en inklusive Markdown-Alerts (> [!NOTE], > [!TIP]) und LaTeX-Formeln (\text{...}).
