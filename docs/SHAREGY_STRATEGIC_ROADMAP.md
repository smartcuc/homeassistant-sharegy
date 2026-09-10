# 🚀 Sharegy Strategische Produkt- & Architektur-Roadmap

**Mission**: Die führende SaaS-Plattform für **Home Energy Management (EMS)** und **Energy Sharing Communities (ESC)**.  
**Stand**: September 2026 (Live v5.2)

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
   │    Status: PRODUKTIV / GEHÄRTET│                               │    Status: PRODUKTIV / GEHÄRTET│
   ├───────────────────────────────┤                               ├───────────────────────────────┤
   │ • Ziel: Für jeden Haushalt    │                               │ • Ziel: Bürgerenergie/Quartier│
   │ • Daten: WSS, MQTT, OTel,     │                               │ • Daten: iMSys Zähler (OBIS   │
   │   Modbus, Home Assistant      │                               │   1.8.0 Bezug, 2.8.0 Einspeis)│
   │ • Takt: Sekunden / Minuten (W)│                               │ • Takt: 15-Minuten-Raster     │
   │ • 4 Pro Hubs: Control, Heat,  │                               │ • Features: P2P-Bilanzierung, │
   │   Mobility & Alerts           │                               │   Tenant-RBAC, Community      │
   │ • Features: Live-Fluss,       │                               │   Cockpit, 48h KI-Prognose,   │
   │   Sankey, Spotpreise, Forecast│                               │   Late Ingestion, Audit-Log   │
   │   Arbitrage, CO2, Aktorik,    │                               │   § 42b EnWG PDF & ERP Exporte│
   │   6-Sprachen i18n, 7d EPEX    │                               │   § 14a EnWG Netzdrosselung   │
   │ • Monetarisierung: Stripe     │                               │ • Monetarisierung: Gebühren   │
   │   (Karten, SEPA, PayPal 7,99€)│                               │   pro Zähler / kWh-Clearing   │
   └───────────────────────────────┘                               └───────────────────────────────┘
```

---

## 🔍 2. Bestandsaufnahme: Was ist fertig, was ist in Arbeit?

### ✅ A. TimescaleDB & Hochfrequenz-Telemetrie
- `core_intervalreading` und `devices_devicemetric` laufen als optimierte TimescaleDB Hypertables.
- Sub-Sekunden-Snapshots über `DeviceLatestMetric` für $O(1)$-Statusabfragen ohne teure Tabellenscans.
- Continuous Aggregates (1h, 1d) für verzögerungsfreie Langzeit-Ladezeiten (< 10 ms).
- **TimescaleDB Decompression-Härtung**: Automatischer Schutz vor Dekomprimierungslimits bei großen Cleanup-Jobs (`SET LOCAL timescaledb.max_tuples_decompressed_per_dml_transaction = 0;`).

### ✅ B. Live-Telemetrie & Plug-and-Play Ingestion (WSS, MQTT, Home Assistant, REST)
- **Outbound WSS Ingestion (`wss://sharegy.de/ws/energy/`)**: DAU-sichere WebSocket-Anbindung für alle Shelly Gen2/Gen3/Pro Geräte (z. B. Shelly 1PM Gen3, Pro 3EM) mit automatischem 5s Live-Polling (`Shelly.GetStatus`) und robuster UUID/Token-Zuordnung.
- **Resilienter MQTT-Consumer**: Automatischer Connection-Reset bei Verbindungsabbrüchen ohne Hänger.
- **Home Assistant Custom Component**: 9 Live-Sensoren, Outbound-HTTPS (`https://sharegy.de`), Telemetrie-Push-Service (`sharegy.push_telemetry`) & Lade-Blueprints.
- **Grafana Enterprise Data Source Bridge**: JSON/Infinity REST-Bridge (`/api/grafana/*`) & Cockpit-Template.

### ✅ C. Energiefluss, Live-Sankey & Sub-Metering Disaggregation
- Vollständige physikalische Flussverteilung in `energy/flow_engine.py` (PV → Last → Batterie → Netz).
- Flackerfreies ECharts & SVG Live-Sankey mit Etagen- und Raum-Gruppierung.
- Automatische Restlast-Disaggregation ($E_{\text{residual}} = E_{\text{Haus}} - \sum E_{\text{gemessen}}$) & historische Trend-Analysen.

### ✅ D. Forecast-Trio, Batterie-Arbitrage & Live-CO₂-Signal
- **48h PV-Prognose** mit Hybrid Physics + ML (Open-Meteo 96h + PLZ-Geocoding) & Ist-vs-Soll-Trefferquote (WAPE).
- **48h Last- & Batterie-SoC Simulation** mit Verlust- und Degradationsmodellen.
- **Batterie-Arbitrage Simulator & 7-Tage EPEX Trend**: Netzdienliches Speicherladen bei Tiefst-/Negativpreisen und Peak-Vermeidung (~180–320 € / Jahr Ertragspotenzial).
- **Live CO₂-Grid-Signal**: Echtzeit-Emissionsintensität (g CO₂/kWh) des deutschen Stromnetzes (DE-LU) & Grünstrom-Index.

### ✅ E. Reporting, Multi-Format Exporte & AI-Alerting
- **Date-Range-Picker**: Frei wählbare Auswertungszeiträume mit Schnellwahl-Presets.
- **Multi-Format Export-Engine**: Excel `.xlsx` (formatiert mit Formeln), druckfähiger PDF-Bericht (ReportLab), CSV (UTF-8 BOM Semikolon) und JSON-Rohdaten.
- **Proaktive Alarmzentrale**: 8 Erkennungsregeln (PV-Ertragsausfall, Nachtdauerlast-Leckage, Speicher-Notreserve, Börsen-Preisspitzen).

### ✅ F. Multi-Tenant RBAC, Audit-Log, Helpdesk & Stripe Monetarisierung
- **Quartiers- & Tenant-Rollen**: Granulare Rechte (`admin`, `manager`, `member`, `auditor`).
- **Revisionssicheres Audit-Log**: Automatische Protokollierung von Rollenänderungen, Einladungen und Mitglieder-Entfernungen.
- **Vereinter Hilfe- & Support-Desk**: Ein einzelner Topbar-Button für Wissensportal mit sanfter Anchor-Navigation, FAQ-Deflection und Live-Ticket-Support.
- **Stripe & SEPA Checkout Suite**: Vollautomatisierter Subscription-Billing-Stack (Kreditkarten, SEPA-Lastschrift, PayPal, Klarna, Amazon Pay, Link) mit USt-Ausweis (§ 14 UStG), Auto-Healing Customer-IDs und Customer Portal.
- **6-Sprachen i18n**: Nativer Umschalter in der Topbar für DE, EN, PL, TR, RU, RO mit Stripe-Locale-Übergabe.

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
  └── 1.12 ✅ End-to-End Test Suite & CI/CD Stabilität (100% Tests OK)

┌───────────────────────────────────────────────────────────────────────────────┐
│ MEILENSTEIN 2: EMS-PRO & AKTORIK (✅ 100% Abgeschlossen)                       │
└───────────────────────────────────────────────────────────────────────────────┘
  ├── 2.1 ✅ Smart Energy Optimizer (1h, 2h, 4h Zeitfenster nach PV-Forecast & Börsenstrom)
  ├── 2.2 ✅ Verbrauchsbilanz, Virtuelle Zähler & Residual-Last Disaggregation
  ├── 2.3 ✅ Machine Learning PV-Prognose (Hybrid Physics + ML - RandomForest/Residuals)
  ├── 2.4 ✅ Solar-Prognosegüte & Ist-vs-Soll-Vergleich (%-Genauigkeit / WAPE)
  ├── 2.5 ✅ Verbrauchs-Prognose (Household Load Forecast Engine & Netto-Überschuss)
  ├── 2.6 ✅ Batterie- & SoC-Prognose (24h/48h Simulation & Nachtautarkie)
  ├── 2.7 ✅ Vereinter Helpdesk & Support Desk (Wissensportal + FAQ-Deflection + Tickets)
  ├── 2.8 ✅ Duale Cookie-Persistenz (DSGVO/TDDDG konform, 365 Tage Lebensdauer)
  ├── 2.9 ✅ Intelligentes Alert- & Anomalie-Erkennungssystem (Alarmzentrale & 8 Regeln)
  ├── 2.10 ✅ Submeter-Trends & Historische Zeitreihen virtueller Zähler
  ├── 2.11 ✅ Frei wählbarer Zeitraum (Date-Range-Picker) & Multi-Format Daten-Export (XLSX, PDF, CSV, JSON)
  ├── 2.12 ✅ Batterie-Arbitrage & Grid-Charging Speicher-Simulator (Netzladen bei Tiefstpreisen)
  ├── 2.13 ✅ Live CO₂-Grid-Signal & Grünstrom-Index (Echtzeit-Emissionen g CO₂/kWh & 36h Timeline)
  ├── 2.14 ✅ Universal Telemetrie-Push & OpenTelemetry Ingest Engine (OTel / REST)
  ├── 2.15 ✅ Bi-direktionale Ökosystem-Plugins (Home Assistant Custom Component & Grafana REST-Bridge)
  ├── 2.16 ✅ Outbound-WSS Ingestion für alle Shelly Gen2/Gen3/Pro Modelle (`wss://sharegy.de/ws/energy/`)
  ├── 2.17 ✅ Bidirektionale Aktorik & Relais-Steuerung (Shelly WSS JSON-RPC `Switch.Set`/`Switch.Toggle` & UI Toggles)
  ├── 2.18 ✅ Go-Live Checkout & Gutscheinsystem (Coupons, DSGVO AGB-Audit-Consent, E-Mail-Validation, GA4)
  ├── 2.19 ✅ Systemstatus- & Health-Monitoring Engine (Health-API, Watchdog & UI)
  ├── 2.20 ✅ Geräteprofiling & Intelligente Baseline-Anomalieüberwachung (Predictive Maintenance)
  ├── 2.21 ✅ Mobile Push & Notification Engine (Web-Push VAPID, FCM/APNs & Service Worker)
  ├── 2.22 ✅ Native Mobile Apps via Capacitor (Android `de.sharegy.app`, Gradle & Deep Linking)
  ├── 2.23 ✅ UX/UI & Navigation Overhaul (Slim Sidebar & Zentraler Support-Desk)
  ├── 2.24 ✅ Operations & Celery-Prioritäts-Queues Härtung (5-Stufen Prioritäts-Architektur)
  ├── 2.25 ✅ Nativer OCPP 1.6-J CSMS Gateway & Smart Charging Engine (Easee, openWB, cFos, Keba)
  ├── 2.26 ✅ Autonome Batterie-Arbitrage & Sungrow iSolarCloud OpenAPI Control
  ├── 2.27 ✅ Smart Load Management & Dispatch Hub (`/app/control` - Merit-Order & 24h-Fahrplan)
  ├── 2.28 ✅ BWWP & Wärmepumpen SG-Ready Steuerung & Verdichterschutz (4 Zustände, Boost bis 60°C)
  ├── 2.29 ✅ Offizieller ioBroker Adapter (`ioBroker.sharegy` - WSS Port 443)
  ├── 2.30 ✅ Digitales Benutzerhandbuch & Wissensportal (15 Artikel DE/EN, Anchor-Navigation)
  ├── 2.31 ✅ Topbar Live-Pulse Ticker, Sidenav Streamlining & Dark/Light Theme
  ├── 2.32 ✅ Multistring & AC-Kopplung (BKW-Erkennung) mit physikalischer Entkopplung
  ├── 2.33 ✅ 1-Klick Quick-Boost Override Bar & Smarte EPEX-Ladefenster Empfehlungen
  ├── 2.34 ✅ 6-Sprachiges EU-Internationalisierungspaket (🇩🇪 DE, 🇬🇧 EN, 🇵🇱 PL, 🇹🇷 TR, 🇷🇺 RU, 🇷🇴 RO)
  ├── 2.35 ✅ EPEX Spot 7-Tage Trend-Lookback (`range="week"`/`"7d"`) & Spitzenanalyse
  ├── 2.36 ✅ Server-Hardware & Kapazitäts-Wächter mit RBAC-Schutz (HEMS-/Sysadmin)
  ├── 2.37 ✅ Autonome Demo-Umgebungen & Multi-Tenant Sandbox-Isolation (3 Profile)
  ├── 2.38 ✅ 🌡️ Fußbodenheizungs-Steuerung & Prädiktives MPC (Model Predictive Control & Estrich-Vorladung)
  ├── 2.39 ✅ ⛽ Mobilitäts- & Spritpreis-Radar (MTS-K / Tankerkönig Live-Preise & 100km EV-Vergleich)
  ├── 2.40 ✅ 👑 Standardisiertes Pro-Freemium Gating mit interaktiver Live-Demo-Vorschau (4 Hubs)
  ├── 2.41 ✅ 🧭 Dedizierte Sub-Hubs-Architektur (`/app/mobility`, `/app/heating`) mit Bi-direktionalem Link
  ├── 2.42 ✅ 🔌 Multi-Protocol CSMS Gateway (OCPP 1.6-J, OCPP 2.0.1 & OCPP 2.1 JSON WebSocket Subprotocol Negotiation)
  ├── 2.43 ✅ 🚗 ISO 15118-20 V2G & V2H Bidirektionales Laden (Merit-Order, Peak-Shaving, EPEX-Börsenarbitrage & Entladesteuerung)
  └── 2.44 ✅ 🛡️ Offline-RFID Whitelist Sync (Local Auth List) & Diagnostics Engine (GetDiagnostics, Remote Trigger, Composite Schedule)

┌───────────────────────────────────────────────────────────────────────────────┐
│ MEILENSTEIN 3: PAYMENT, MONETARISIERUNG & BILLING-ARCHITEKTUR (✅ 100% LIVE)   │
└───────────────────────────────────────────────────────────────────────────────┘
  ├── 3.1 ✅ **Tarif- & Plan-Modellierung**:
  │          • Free vs. Pro (Monatlich 7,99 € / Jährlich 79,90 €)
  │          • 4 Pro Hubs (Control, Mobility, Heating, Alerts) mit interaktiver Demo-Vorschau
  ├── 3.2 ✅ **Stripe / Payment Gateway Checkout & Customer Portal Flow**:
  │          • Vollständig aktiviert: Kreditkarten, SEPA-Lastschrift, PayPal, Klarna, Amazon Pay, Link
  │          • Self-Service Customer Portal für Abo-Verwaltung, Zahlungsmittel & Rechnungen
  ├── 3.3 ✅ **Automatische Rechnungsstellung & Fiskal-Sicherheit (§ 14 UStG)**:
  │          • Rechnungs- und Belegkonfiguration mit 19% MwSt (USt-IdNr `DE300917919`)
  │          • Statement-Descriptor `SHAREGY PRO - SMARTEVO` & Nummernpräfix `SHAREGY-...`
  └── 3.4 ✅ **Payment & Webhook-Monitoring & Diagnose**:
             • Webhook-Handler mit Signatur-Prüfung & automatischem `is_pro` Provisioning
             • Auto-Healing Customer-IDs & Diagnosebefehl `verify_stripe_setup`

┌───────────────────────────────────────────────────────────────────────────────┐
│ MEILENSTEIN 4: ENERGY SHARING COMMUNITIES & CLEARING (Säule 2 - ✅ 100% LIVE) │
└───────────────────────────────────────────────────────────────────────────────┘
  ├── 4.1 ✅ Multi-Tenant RBAC & Rollenhierarchie (`admin`, `user_admin`, `helpdesk`, `auditor`, `member`)
  ├── 4.2 ✅ Revisionssicheres Audit-Log für Tenant-Events (`accounts.AuditLog`)
  ├── 4.3 ✅ Tenant-Dashboard, Einladungslinks & Onboarding-Flow (`/app/tenant`)
  ├── 4.4 ✅ 15-Minuten Community-Bilanzierung & Resiliente Ingestion (OBIS 1.8.0 / 2.8.0)
  ├── 4.5 ✅ Energy Sharing Community Cockpit (Frontend & Backend API)
  ├── 4.6 ✅ Sharing-Tarife & Automatische Monatsabrechnungs-Engine (Clearing)
  ├── 4.7 ✅ Zentrales Multi-Community Management Hub & Portfolio-Dashboard
  ├── 4.8 ✅ Gesetzlicher Ingestion- & Reststrom-Leitfaden (MsbG & MaKo / MSCONS)
  ├── 4.9 ✅ PDF-Monatsabrechnungsnachweise & Multi-Format Exporte (Excel, CSV, XML / ERP)
  ├── 4.10 ✅ Erweiterte Allokationsmodelle & Beteiligungsquoten (§ 42b / § 42a EnWG - Statisch, Dynamisch, Hybrid)
  ├── 4.11 ✅ wMSB Smart Meter Hub & API-Konnektor (Discovergy, inexogy, Solandeo)
  └── 4.12 ✅ Community Viral Growth & Social Referral System

┌───────────────────────────────────────────────────────────────────────────────┐
│ MEILENSTEIN 5: ENERGIE-PROFIL-ENGINE & ADAPTIVES UI (✅ 100% LIVE)             │
└───────────────────────────────────────────────────────────────────────────────┘
  ├── 5.1 ✅ **Mathematische Matrix-Engine (A.1 bis F.1)**:
  │          • 6 Archetypen: Kein Solar, BKW, EV, Wärmepumpe, Prosumer, All-In
  │          • Automatische Hardware-Erkennung & manuelle Anpassung mit 24h-Cache
  ├── 5.2 ✅ **Dynamischer 4-Kanal Ersparnisrechner**:
  │          • Berechnung von Netto-Sparpotenzial (€/a) & verschiebbaren Lasten ($E_\text{shiftable}$)
  │          • Aufschlüsselung: PV-Eigenverbrauch, § 14a EnWG Netzentgelt-Rabatt, Börsentiefs & Arbitrage
  ├── 5.3 ✅ **Kontextuelles Tarif-Verdikt & Kaskadenmessung**:
  │          • Festpreis vs. Dynamischer Börsenstromtarif
  │          • Gegenüberstellung: 2. Zählerplatz (80–120 €/a Zusatzkosten) vs. 1 smarter Zähler
  ├── 5.4 ✅ **Profil-Adaptives UI-System**:
  │          • Zentraler React-Hook `useEnergyProfile()` für alle Komponenten
  │          • Hero Quick-Actions auf dem Dashboard & Tarif-Kompass auf `/app/tariff`
  ├── 5.5 ✅ **4-Säulen Omi-Check V2**:
  │          • Direkte Profil-Verknüpfung im Readiness-Header
  └── 5.6 ✅ **Wissensportal & Help Center 2.0**:
             • 9 Kategorien & 20 fundierte Handbuch-Artikel in DE & EN
             • Kontextuelle Leitfaden-Empfehlung direkt für das eigene Profil

---

## 📋 4. Konkreter Action-Plan (Roadmap zu 100% abgeschlossen)

| Schritt | Modul | Maßnahme | Status | Ziel & Umsetzung |
|---|---|---|:---:|---|
| **Prio 1** | `mobility/radar/` | **⛽ Mobilitäts- & Spritpreis-Radar**: Integration der Tankerkönig-API / MTS-K für die 3 günstigsten Tankstellen (Diesel, E5, E10) & 100km-EV-Vergleich | ✅ **100% Fertig** | Alltags-Mehrwert & Kostenvergleich für gemischte Haushalte |
| **Prio 2** | `energy/hvac/` | **🌡️ Fußbodenheizungs-Steuerung & Prädiktives MPC**: Wettergeführte Vorlauftemperatur & thermische Estrich-Vorladung | ✅ **100% Fertig** | 100% Eigenverbrauch & Peak-Shaving im HEMS Dispatch-Hub |
| **Prio 3** | `devices/ocpp/` | **🔌 Multi-Protocol CSMS Gateway**: OCPP 1.6-J, OCPP 2.0.1 & OCPP 2.1 (Subprotocol Negotiation, TransactionEvents, Device Model Variables, Local Auth List, Diagnostics) | ✅ **100% Fertig** | Normkonforme Anbindung aller modernen & kommenden Ladestationen |
| **Prio 4** | `energy/v2g/` | **🚗 ISO 15118-20 V2G & V2H Bidirektionales Laden**: Fahrzeugakku als Heimspeicher-Ersatz, Spitzenlast-Pufferung & dynamic Börsen-Arbitrage | ✅ **100% Fertig** | Bidirektionales Laden & Netzentlastung bei 100% Batterieschutz |

> 🏆 **Vollständiger Funktionsumfang verifiziert & produktionsreif**:
> - ⛽ **Mobilitäts- & Spritpreis-Radar** (`energy/services/tankerkoenig.py`, `views_fuel_radar.py`, `FuelRadarCard.jsx`)
> - 🌡️ **Fußbodenheizungs-Steuerung & thermische Estrich-Vorladung** (`energy/models.py`, `floor_heating_manager.py`, `FloorHeatingLoadCard.jsx`)
> - 🔌 **Multi-Protocol CSMS Gateway (OCPP 1.6-J, 2.0.1 & 2.1)** (`devices/consumers_ocpp.py`, `devices/models_ocpp.py`, `devices/tests_ocpp.py`, `devices/tests_ocpp_v2.py`)
> - 🚗 **ISO 15118-20 V2G & V2H Bidirektionales Entlademanagement** (`energy/services/services_v2g.py`, `WallboxToolsModal.jsx`, `WallboxCard.jsx`)
> - 🛡️ **§ 14a EnWG Dimmung & Summenleistungsmodell** (`energy/services_dimming.py`, `energy/test_grid_dimming.py`, `ControlPage.jsx`)
> - ⚡ **Dynamische Börsenpreis-Sharingtarife (EPEX Spot, Cap, Floor)** (`billing/services_sharing_settlement.py`, `billing/test_mscons_and_dynamic_tariffs.py`)
> - 📜 **VNB Marktkommunikations-Bridge (EDIFACT / MSCONS Export & Import D:04B)** (`billing/services_mscons.py`, `CommunitiesManagementHub.jsx`, `MsbSmartMeterHub.jsx`)






