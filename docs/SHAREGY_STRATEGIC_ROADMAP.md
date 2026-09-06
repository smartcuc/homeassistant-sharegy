# 🚀 Sharegy Strategische Produkt- & Architektur-Roadmap

**Mission**: Die führende SaaS-Plattform für **Home Energy Management (EMS)** und **Energy Sharing Communities (ESC)**.  
**Stand**: 1. September 2026 (Live v3.4)

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
   │ • Features: Live-Fluss,       │                               │ • Features: P2P-Bilanzierung, │
   │   Sankey, Spotpreise, Forecast│                               │   Tenant-RBAC, Community      │
   │   Arbitrage, CO2, Aktorik     │                               │   Cockpit, 48h KI-Prognose,   │
   │ • Monetarisierung: SaaS-Abo   │                               │   Late Ingestion, Audit-Log   │
   │   (Free vs. Pro 4,99 €/M)     │                               │ • Monetarisierung: Gebühren   │
   └───────────────────────────────┘                               │   pro Zähler / kWh-Clearing   │
                                                                   └───────────────────────────────┘
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
- **Batterie-Arbitrage Simulator**: Netzdienliches Speicherladen bei Tiefst-/Negativpreisen und Peak-Vermeidung (~180–320 € / Jahr Ertragspotenzial).
- **Live CO₂-Grid-Signal**: Echtzeit-Emissionsintensität (g CO₂/kWh) des deutschen Stromnetzes (DE-LU) & Grünstrom-Index.

### ✅ E. Reporting, Multi-Format Exporte & AI-Alerting
- **Date-Range-Picker**: Frei wählbare Auswertungszeiträume mit Schnellwahl-Presets.
- **Multi-Format Export-Engine**: Excel `.xlsx` (formatiert mit Formeln), druckfähiger PDF-Bericht (ReportLab), CSV (UTF-8 BOM Semikolon) und JSON-Rohdaten.
- **Proaktive Alarmzentrale**: 8 Erkennungsregeln (PV-Ertragsausfall, Nachtdauerlast-Leckage, Speicher-Notreserve, Börsen-Preisspitzen).

### ✅ F. Multi-Tenant RBAC, Audit-Log & Helpdesk
- **Quartiers- & Tenant-Rollen**: Granulare Rechte (`admin`, `manager`, `member`, `auditor`).
- **Revisionssicheres Audit-Log**: Automatische Protokollierung von Rollenänderungen, Einladungen und Mitglieder-Entfernungen.
- **Vereinter Hilfe- & Support-Desk**: Ein einzelner Topbar-Button für Wissensportal, FAQ-Deflection und Live-Ticket-Support.
- **Duale Cookie-Persistenz**: 365 Tage Speicherung über `localStorage` + persistenten HTTP-Cookie (`sharegy_cookie_consent_v1`).

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
│ MEILENSTEIN 2: EMS-PRO & AKTORIK (✅ In Umsetzung / Aktualisiert)               │
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
  ├── 2.19 ✅ **Systemstatus- & Health-Monitoring Engine (Health-API, Watchdog & UI)**:
  │          • Umfassende Health-Check API (`/api/status/health/`) für DB, Redis, Daphne WSS, Celery, Open-Meteo & Tibber
  │          • Live-Status-Dashboard (`/app/status`) mit Latenzmessung, Ingest-Throughput und Störungsmeldung
  │          • Automatischer Watchdog mit Auto-Ticket-Erstellung bei Subsystem-Ausfällen und Auto-Healing
  ├── 2.20 ✅ **Geräteprofiling & Intelligente Baseline-Anomalieüberwachung (Predictive Maintenance)**:
  │          • `DeviceBaselineProfile` Modell für Standby-Baseline, Grenzwerte, Betriebsleistung und max. Laufzeit
  │          • 1-Klick Presets für BWWP, Wärmepumpen, Kühlschränke, Zirkulationspumpen & Umwälzpumpen
  │          • 7-Tage Auto-ML-Learning aus realen Telemetrie-Zeitreihen (Quantil-Segmentierung)
  │          • Echtzeit-Watchdog mit automatischer Alarmierung bei Ruhestrom-Anstieg (z. B. 30W -> 52W) oder Dauerlauf
  ├── 2.21 ✅ **Mobile Push & Notification Engine (Web-Push VAPID, FCM/APNs & Service Worker)**:
  │          • W3C Web-Push mit VAPID-Verschlüsselung für iPhones (iOS Safari 16.4+), Android & Desktop
  │          • `DeviceSubscription` & `NotificationPreference` Modelle mit Quiet Hours & Notfall-Override
  │          • Service Worker (`sw.js`) für Sperrbildschirm-Zustellung und Deep-Link-Fokussierung
  │          • 1-Klick Permission Request & Sofort-Test-Push in Einstellungen & Alarmzentrale
  ├── 2.22 ✅ **Native Mobile Apps via Capacitor (Android Initialisierung, Gradle & Deep Linking)**:
│          • Capacitor 7 Plattform-Engine für Android (`frontend/android/`, `de.sharegy.app`)
│          • Natives Lifecycle-Management, Status Bar Styling & flackerfreier Splashscreen
│          • Deep-Linking Intent-Filter für Magic-Links (`https://sharegy.de/t/*`) & Alarme
│          • Integrierte Build- & Sync-Pipelines (`npm run cap:open`)
  ├── 2.23 ✅ **UX/UI & Navigation Overhaul (Slim Sidebar & Zentraler Support-Desk)**:
│          • Schlanke Sidebar mit neuer Sektion `⚙️ Systemeinstellungen` (ohne redundante Links)
│          • Vollständig integrierter `🛟 Hilfe & Support`-Drawer in der Topbar (Tickets, Triage & FAQ)
│          • `📖 Wissensportal & Handbuch` (`/app/help`) mit Staff Live-Editor (Markdown, DE/EN)
  ├── 2.24 ✅ **Operations & Celery-Prioritäts-Queues Härtung**:
│          • 5-Stufen Prioritäts-Architektur (`fiscal`, `realtime`, `analytics`, `background`, `celery`)
│          • Automatisches HealthState-Pruning veralteter Queues & exakter Device-Count für echte Geräte
  ├── 2.25 ✅ **Nativer OCPP 1.6-J CSMS Gateway & Smart Charging Engine**:
│          • WebSocket CSMS Server (`/ws/ocpp/<charge_point_id>/`) für Easee, openWB, cFos, Heidelberg, Mennekes, Alfen
│          • 4 Intelligente Lademodi: PV-Überschuss, Börsenpreis-Tiefstpreise, Fast & Eco
│          • `WallboxCard` Widget & `AddWallboxModal` mit Phasenumschaltung & Stromstärke-Slider
  ├── 2.26 ✅ **Autonome Batterie-Arbitrage & Sungrow iSolarCloud OpenAPI Control**:
│          • Bidirektionaler Inverter-Dispatch (`forced_charge`, `self_consumption`, `forced_discharge`)
│          • Dynamische Netzladung bei Negativ- und Tiefstpreisen (Tibber/EPEX) via automatischer Celery-Task
│          • Sub-Sekunden Statuscaching für Dashboard-Visualisierung
  ├── 2.27 ✅ **Smart Load Management & Dispatch Hub (`/app/control`)**:
│          • Live Power Budget Header ($P_\text{surplus} = P_\text{pv} - P_\text{load}$, SoC, Spotpreis, Schaltlast)
│          • 4 Master-Autopilot-Modi (Smart Autopilot, Nur PV-Überschuss, Sparfuchs, Manuell)
│          • Interaktive Prioritäten-Kaskade (Merit-Order) für solare Überschussverteilung
│          • 24h-Fahrplan (Dispatch-Timeline) mit stündlicher Solar- & Preisallokation
  ├── 2.28 ✅ **BWWP & Wärmepumpen SG-Ready Steuerung & Verdichterschutz**:
│          • 4 SG-Ready Betriebszustände mit Wassertemperatur-Schwellen ($T_\text{min}=45^\circ\text{C}$, $T_\text{soll}=52^\circ\text{C}$, $T_\text{boost}=60^\circ\text{C}$, $T_\text{max}=65^\circ\text{C}$)
│          • Integrierter Verdichter- & Taktschutz ($t_\text{run} \ge 20\,\text{min}$, $t_\text{cool} \ge 15\,\text{min}$)
│          • Closed-Loop Aktorik über Outbound-WebSocket in Echtzeit
  ├── 2.29 ✅ **Offizieller ioBroker Adapter (`ioBroker.sharegy`)**:
│          • Multi-Sensor-Bündelung von Wirkleistung (W), Temperatur (°C) und Schaltrelais
│          • WSS-Kopplung über TLS Port 443 mit Sub-100ms Reaktionszeit
  ├── 2.30 ✅ **Digitales Benutzerhandbuch & Wissensportal (15 Artikel DE/EN)**:
│          • 15 Handbuch-Artikel in 9 Kategorien im integrierten Support-Desk
│          • Dynamische FAQ-Deflection und Live-Editor
  ├── 2.31 ✅ **Topbar Live-Pulse Ticker, Sidenav Streamlining & Dark Theme**:
│          • Sub-Sekunden Leistungsfluss in der Topbar (Solar, Haus, Netz, Akku)
│          • Bereinigung redundanter Badges und nahtloser Liegenschafts-Switcher
│          • Dark- & Light-Mode mit nativer ThemeContext-Persistenz
  ├── 2.32 ✅ **Multistring & AC-Kopplung (BKW-Erkennung) mit physikalischer Entkopplung**:
│          • Automatische Gutschrift negativer Hauslasten als Solarerzeugung
│          • Strikte Trennung von Speicherladung und Haushaltsverbrauch
│          • Smart-Meter Zero-Grid Schutz vor rechnerischen Verfälschungen
  └── 2.33 ✅ **1-Klick Quick-Boost Override Bar & Smarte EPEX-Ladefenster**:
             • 1-Klick Aktionen (11 kW Wallbox-Boost, 100% Notstromreserve, Max. PV-Eigenverbrauch)
             • Live-Countdown & 1-Klick Reset zur nahtlosen Autopilot-Rückkehr
             • Automatische Ermittlung von Best-Price Ladefenstern & Peak-Shaving im EPEX-Modal

┌───────────────────────────────────────────────────────────────────────────────┐
│ MEILENSTEIN 3: PAYMENT, MONETARISIERUNG & BILLING-ARCHITEKTUR (💳 OFFEN)      │
└───────────────────────────────────────────────────────────────────────────────┘
  ├── 3.1 ⏳ **Tarif- & Plan-Modellierung**:
  │          • Free vs. Pro (Monatlich 4,99 € / Jährlich 49,99 €) & Vermieter-/Quartiers-Pakete
  │          • Feature-Gating Matrix (Alarmzentrale, ML-Solarprognose, Batterie-Arbitrage)
  ├── 3.2 ⏳ **Stripe / Payment Gateway Checkout & Customer Portal Flow**:
  │          • Reibungsloser Checkout ohne Medienbruch (SEPA-Lastschrift, Kreditkarte, Apple/Google Pay)
  │          • Self-Service Customer Portal für Abo-Kündigung, Zahlungsmittel-Update & Rechnungsdownload
  ├── 3.3 ⏳ **Automatische Rechnungsstellung & Fiskal-Sicherheit**:
  │          • PDF-Rechnungserstellung (ReportLab mit USt-Ausweis, fortlaufender Rechnungsnummer & Anschrift)
  │          • E-Mail-Versand mit PDF-Anhang bei erfolgreicher Abbuchung (`fiscal` Queue Prio 1)
  └── 3.4 ⏳ **Payment & Webhook-Monitoring (Infrastruktur)**:
             • Stripe-Webhook Health-Check im Systemstatus (`/app/status`)
             • SMTP/E-Mail-Server Erreichbarkeits-Überwachung für transaktionale Mails

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

---

## 📋 4. Konkreter Action-Plan (Ausschließlich offene Aufgaben)

| Schritt | Modul | Maßnahme | Status / Prio | Ziel & Umsetzung |
|---|---|---|:---:|---|
| **Prio 1** | `grid/enwg/` | **§ 14a EnWG Steuerbox & Dimmung**: Dynamische Leistungsbegrenzung auf 4,2 kW für SteuVE (WP, Wallbox, Speicher) via REST/Modbus/EEBUS | ⚡ **P1 (Nächster Fokus)** | Gesetzliche Netzbetreiber-Konformität & Abregelungs-Protokollierung |
| **Prio 2** | `billing/payment/` | **Stripe & SEPA Checkout Integration**: Anbindung von Stripe Subscription Billing für Free vs. Pro (4,99 €/Monat) inkl. Webhooks | 💳 **P2** | Automatisierte Monetarisierung & Self-Service Portal |
| **Prio 3** | `billing/tariffs/` | **Dynamische Börsenpreis-Sharingtarife**: Indexierte Community-Tarife mit Formelaufschlag auf EPEX-Spotpreise | ⚡ **P3** | Marktnahe Bepreisung innerhalb von Bürgerenergie-Quartieren |
| **Prio 4** | `billing/edifact/` | **Standardisierte Marktkommunikations-Bridge**: Automatischer Export von MSCONS / EDIFACT-Datensätzen zur VNB-Abstimmung | ⚡ **P4** | Direkter Datenaustausch mit Verteilnetzbetreibern |





