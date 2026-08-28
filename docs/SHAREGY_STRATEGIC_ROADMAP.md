# 🚀 Sharegy Strategische Produkt- & Architektur-Roadmap

**Mission**: Die führende SaaS-Plattform für **Home Energy Management (EMS)** und **Energy Sharing Communities (ESC)**.  
**Stand**: 26. August 2026 (Live v3)

---

## 🏛️ 1. Die Dual-Core Architektur

```
                           ┌──────────────────────────────────────────────┐
                           │            Sharegy SaaS Plattform            │
                           └──────────────────────┬───────────────────────┘
                                                  │
                 ┌────────────────────────────────┴───────────────────────────────┐
                 ▼                                                               ▼
   ┌───────────────────────────────┐                               ┌───────────────────────────────┐
   │    🟢 SÄULE 1: EMS (FREE/PRO) │                               │    🔵 SÄULE 2: ENERGY SHARING │
   │    Status: PRODUKTIV / GEHÄRTET│                               │    Status: IN VORBEREITUNG    │
   ├───────────────────────────────┤                               ├───────────────────────────────┤
   │ • Ziel: Für jeden Haushalt    │                               │ • Ziel: Bürgerenergie/Quartier│
   │ • Daten: MQTT, OTel, Modbus,  │                               │ • Daten: iMSys Zähler (OBIS   │
   │   Matter 1.3, HA, Inverter    │                               │   1.8.0 Bezug, 2.8.0 Einspeis)│
   │ • Takt: Sekunden / Minuten (W)│                               │ • Takt: 15-Minuten-Raster     │
   │ • Features: Live-Fluss,       │                               │ • Features: P2P-Bilanzierung, │
   │   Sankey, Spotpreise, Forecast│                               │   Allokation, Mieterstrom-    │
   │   Arbitrage, CO2, AI-Alerts   │                               │   Clearing, PDF-Abrechnungen  │
   │ • Monetarisierung: SaaS-Abo   │                               │ • Monetarisierung: Gebühren   │
   │   (Free vs. Pro 4,99 €/M)     │                               │   pro Zähler / kWh-Clearing   │
   └───────────────────────────────┘                               └───────────────────────────────┘
```

---

## 🔍 2. Bestandsaufnahme: Was ist fertig, was ist in Arbeit?

### ✅ A. TimescaleDB & Hochfrequenz-Telemetrie
- `core_intervalreading` und `devices_devicemetric` laufen als optimierte TimescaleDB Hypertables.
- Sub-Sekunden-Snapshots über `DeviceLatestMetric` für $O(1)$-Statusabfragen ohne teure Tabellenscans.
- Continuous Aggregates (1h, 1d) für verzögerungsfreie Langzeit-Ladezeiten (< 10 ms).

### ✅ B. Energiefluss, Live-Sankey & Sub-Metering Disaggregation
- Vollständige physikalische Flussverteilung in `energy/flow_engine.py` (PV → Last → Batterie → Netz).
- Flackerfreies ECharts & SVG Live-Sankey mit Etagen- und Raum-Gruppierung.
- Automatische Restlast-Disaggregation ($E_{	ext{residual}} = E_{	ext{Haus}} - \sum E_{	ext{gemessen}}$) & historische Trend-Analysen.

### ✅ C. Ingestion & Interoperabilität (Matter 1.3, HA, Grafana)
- **Matter 1.3 Hub**: Volle Unterstützung von Cluster `0x0090` (Power), `0x0091` (Energy), `0x0098`/`0x0099` (EVSE/Energy Management) und QR-Code/PIN-Commissioning.
- **Home Assistant Custom Component**: 9 Live-Sensoren, Outbound-HTTPS (`https://sharegy.de`), Telemetrie-Push-Service (`sharegy.push_telemetry`) & Lade-Blueprints.
- **Grafana Enterprise Data Source Bridge**: JSON/Infinity REST-Bridge (`/api/grafana/*`) & Cockpit-Template.

### ✅ D. Forecast-Trio, Batterie-Arbitrage & Live-CO₂-Signal
- **48h PV-Prognose** mit Hybrid Physics + ML (Open-Meteo 96h + PLZ-Geocoding) & Ist-vs-Soll-Trefferquote (WAPE).
- **48h Last- & Batterie-SoC Simulation** mit Verlust- und Degradationsmodellen.
- **Batterie-Arbitrage Simulator**: Netzdienliches Speicherladen bei Tiefst-/Negativpreisen und Peak-Vermeidung (~180–320 € / Jahr Ertragspotenzial).
- **Live CO₂-Grid-Signal**: Echtzeit-Emissionsintensität (g CO₂/kWh) des deutschen Stromnetzes (DE-LU) & Grünstrom-Index.

### ✅ E. Reporting, Multi-Format Exporte & AI-Alerting
- **Date-Range-Picker**: Frei wählbare Auswertungszeiträume mit Schnellwahl-Presets.
- **Multi-Format Export-Engine**: Excel `.xlsx` (formatiert mit Formeln), druckfähiger PDF-Bericht (ReportLab), CSV (UTF-8 BOM Semikolon) und JSON-Rohdaten.
- **Proaktive Alarmzentrale**: 8 Erkennungsregeln (PV-Ertragsausfall, Nachtdauerlast-Leckage, Speicher-Notreserve, Börsen-Preisspitzen).

---

## 🎯 3. Die Phasen-Roadmap

```
┌───────────────────────────────────────────────────────────────────────────────┐
│ MEILENSTEIN 1: EMS-FREE BASIS-PLATTFORM (✅ 100% Abgeschlossen)                │
└───────────────────────────────────────────────────────────────────────────────┘
  ├── 1.1 ✅ TimescaleDB Hypertable & Führende Indizes für `DeviceMetric`
  ├── 1.2 ✅ Ingest-Deduplizierung & Deadband-Filter (Redis + `DeviceLatestMetric`)
  ├── 1.3 ✅ Energiefluss-Berechnung in `energy/flow_engine.py` (PV → Last → Akku → Netz)
  ├── 1.4 ✅ Sankey-Diagramm Kanten-Aggregation, Balancierung & ECharts-Rendering
  ├── 1.5 ✅ Dashboard N+1 Queries aufgelöst (Ladezeit < 50ms)
  ├── 1.6 ✅ Spotpreis-Analyse, Stundenschnitt & Resiliente Börsenpreis-Pipeline
  ├── 1.7 ✅ PV- & Wetter-Prognose für Dachanlagen (Physics + Open-Meteo 96h + Geocoding)
  ├── 1.8 ✅ Operations & Monitoring Dashboard im Django Admin (Live-Badges)
  ├── 1.9 ✅ Enterprise Multi-Metric Support (OTel/MQTT multi-channel Ingest)
  ├── 1.10 ✅ Smart Device Onboarding & Simulator (ioBroker/Shelly/HA)
  ├── 1.11 ✅ Zentraler MQTT-Hub & Multi-Language i18n (DE, EN, PL in UI & Navigation)
  └── 1.12 ✅ End-to-End Test Suite & CI/CD Stabilität (19/19 Tests OK)

┌───────────────────────────────────────────────────────────────────────────────┐
│ MEILENSTEIN 2: EMS-PRO & KI-INTELLIGENZ (✅ Weitgehend fertiggestellt)        │
└───────────────────────────────────────────────────────────────────────────────┘
  ├── 2.1 ✅ Smart Energy Optimizer (1h, 2h, 4h Zeitfenster nach PV-Forecast & Börsenstrom)
  ├── 2.2 ✅ Verbrauchsbilanz, Virtuelle Zähler & Residual-Last Disaggregation
  ├── 2.3 ✅ Machine Learning PV-Prognose (Hybrid Physics + ML - RandomForest/Residuals)
  ├── 2.4 ✅ Solar-Prognosegüte & Ist-vs-Soll-Vergleich (%-Genauigkeit / WAPE)
  ├── 2.5 ✅ Verbrauchs-Prognose (Household Load Forecast Engine & Netto-Überschuss)
  ├── 2.6 ✅ Batterie- & SoC-Prognose (24h/48h Simulation & Nachtautarkie)
  ├── 2.7 ✅ Kontextuelles Help-System & In-App Drawer (DE / EN)
  ├── 2.8 ✅ FAQ-Portal & Digitales Benutzerhandbuch (DE / EN)
  ├── 2.9 ✅ Intelligentes Alert- & Anomalie-Erkennungssystem (Alarmzentrale & 8 Regeln)
  ├── 2.10 ✅ Submeter-Trends & Historische Zeitreihen virtueller Zähler
  ├── 2.11 ✅ Frei wählbarer Zeitraum (Date-Range-Picker) & Multi-Format Daten-Export (XLSX, PDF, CSV, JSON)
  ├── 2.12 ✅ Batterie-Arbitrage & Grid-Charging Speicher-Simulator (Netzladen bei Tiefstpreisen)
  ├── 2.13 ✅ Live CO₂-Grid-Signal & Grünstrom-Index (Echtzeit-Emissionen g CO₂/kWh & 36h Timeline)
  ├── 2.14 ✅ CSA Matter 1.3 Energy Management Hub & Bridge Engine
  ├── 2.15 ✅ Bi-direktionale Ökosystem-Plugins (Home Assistant Custom Component & Grafana REST-Bridge)
  ├── 2.16 ✅ Subscription- & SaaS-Lizenzmodell (Free, Pro 4,99 €, Vermieter 14,99 €, PDF-Invoicing & Feature-Gating)
  ├── 2.17 ✅ Rechtliche Compliance & DSGVO-Rechte (Impressum § 5 DDG, Datenschutz, AGB, Widerruf, Cookie-Manager, Art. 15 Export & Art. 17 Löschung)
  ├── 2.18 ✅ Production-Härtung leere Accounts & UI/UX-Ergonomie (Zero-State Onboarding-Banner, Auto-Home-Provisioning, Topbar-Kontext)
  ├── 2.19 ✅ Universal Helpdesk- & Incident-System (Cross-Project Support für Sharegy HEMS & Factofy Digital Twin)
  ├── 2.20 ⏳ Deklaratives Device-Profile Addon-System (Sungrow, SMA, Deye, Huawei, Kostal, Fronius YAML)
  ├── 2.21 ⏳ Mobile Push Notification Engine (FCM Android & APNs iOS Dispatcher)
  └── 2.22 ⏳ Native Mobile Apps via Capacitor (iOS & Android mit Widgets & Biometrie)

┌───────────────────────────────────────────────────────────────────────────────┐
│ MEILENSTEIN 3: ENERGY SHARING COMMUNITIES & § 14a EnWG (Säule 2)              │
└───────────────────────────────────────────────────────────────────────────────┘
  ├── 3.1 Zähler- & iMSys-Datenmodell finalisieren (`AggregatedReading` OBIS 1.8.0/2.8.0)
  ├── 3.2 Tenant-Modell Konsolidierung (`core.Tenant`)
  ├── 3.3 15-Minuten Community-Bilanzierung & Allokationsschlüssel
  ├── 3.4 Sharing-Tarife, Umlagen & kaufmännische Abrechnungsperioden
  ├── 3.5 B2B/B2C Community-Portal (Erzeuger, Verbraucher, Prosumer)
  └── 3.6 § 14a EnWG Steuerbox-Schnittstelle & Pflichtdimmung auf 4,2 kW (SteuVE)
```

---

## 📋 4. Konkreter Action-Plan für die nächsten Meilensteine

| Schritt | Modul | Maßnahme | Status / Prio | Impact |
|---|---|---|:---:|---|
| **Step 1** | `devices/profiles/` | **Deklaratives Device-Profile Addon-System**: Vorgefertigte YAML-Templates für Sungrow, SMA, Deye, Huawei, Kostal, Fronius, SolarEdge, Victron | 🔥 **P1 (Sofort)** | 1-Klick Hardware-Setup ohne manuelle Register-Eingabe |
| **Step 2** | `notifications/` | **Mobile Push Notification Engine**: FCM & APNs Dispatcher für PV-Ausfall-, Notreserve- & Negativpreis-Pushs | 📱 **P2** | Aktive Alarmierung auf Smartphones bei geschlossener App |
| **Step 3** | `mobile/` | **Capacitor Mobile App (iOS & Android)**: Biometrie-Login & native Homescreen-Widgets (Live-PV, SoC) | 📱 **P2** | App Store / Play Store Listung & maximale Kundenbindung |
| **Step 4** | `tenants/` | **Tenant-Modell Konsolidierung & P2P-Clearing**: 15-Min-Bilanzierung für Mieterstrom & Quartiere | 🏢 **P3** | Kommerzieller Rollout von Säule 2 (Energy Sharing) |
| **Step 5** | `grid/enwg/` | **§ 14a EnWG Steuerbox & Dimmung**: Dynamische Leistungsbegrenzung auf 4,2 kW für SteuVE (WP, Wallbox, Speicher) | ⚡ **P3** | Gesetzliche Netzbetreiber-Konformität in Deutschland |
