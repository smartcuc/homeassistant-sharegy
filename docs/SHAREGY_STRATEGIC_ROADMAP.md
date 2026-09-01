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
  └── 2.24 ✅ **Operations & Celery-Prioritäts-Queues Härtung**:
             • 5-Stufen Prioritäts-Architektur (`fiscal`, `realtime`, `analytics`, `background`, `celery`)
             • Automatisches HealthState-Pruning veralteter Queues & exakter Device-Count für echte Geräte

┌───────────────────────────────────────────────────────────────────────────────┐
│ MEILENSTEIN 3: PAYMENT, MONETARISIERUNG & BILLING-ARCHITEKTUR (💳 EVALUIERUNG) │
└───────────────────────────────────────────────────────────────────────────────┘
  ├── 3.1 ⏳ **Tarif- & Plan-Modellierung**:
  │          • Free vs. Pro (Monatlich 4,99 € / Jährlich 49,99 €) & Vermieter-/Quartiers-Pakete
  │          • Feature-Gating Matrix (Alarmzentrale, ML-Solarprognose, Batterie-Arbitrage)
  ├── 3.2 ⏳ **Stripe / Payment Gateway Checkout & Customer Portal Flow**:
  │          • Reibungsloser Checkout ohne Medienbruch (SEPA-Lastschrift, Kreditkarte, Apple/Google Pay)
  │          • Self-Service Customer Portal für Abo-Kündigung, Zahlungsmittel-Update & Rechnungsdownload
  │          • *(Hinweis: Zurückgestellt zur finalen Evaluierung der Zahlungsanbieter)*
  ├── 3.3 ⏳ **Automatische Rechnungsstellung & Fiskal-Sicherheit**:
  │          • PDF-Rechnungserstellung (ReportLab mit USt-Ausweis, fortlaufender Rechnungsnummer & Anschrift)
  │          • E-Mail-Versand mit PDF-Anhang bei erfolgreicher Abbuchung (`fiscal` Queue Prio 1)
  └── 3.4 ⏳ **Payment & Webhook-Monitoring (Infrastruktur)**:
             • Stripe-Webhook Health-Check im Systemstatus (`/app/status`)
             • SMTP/E-Mail-Server Erreichbarkeits-Überwachung für transaktionale Mails

┌───────────────────────────────────────────────────────────────────────────────┐
│ MEILENSTEIN 4: ENERGY SHARING COMMUNITIES & CLEARING (Säule 2 - ✅ 95% LIVE)  │
└───────────────────────────────────────────────────────────────────────────────┘
  ├── 4.1 ✅ Multi-Tenant RBAC & Rollenhierarchie (`admin`, `user_admin`, `helpdesk`, `auditor`, `member`)
  ├── 4.2 ✅ Revisionssicheres Audit-Log für Tenant-Events (`accounts.AuditLog`)
  ├── 4.3 ✅ Tenant-Dashboard, Einladungslinks & Onboarding-Flow (`/app/tenant`)
  ├── 4.4 ✅ **15-Minuten Community-Bilanzierung & Resiliente Ingestion (OBIS 1.8.0 / 2.8.0)**:
  │          • Eichrechtskonforme 15m-Slot-Aggregation in `BalanceSlot`
  │          • Automatische Plausibilitätsprüfung & Ausreißer-Erkennung (`validate_obis_reading`)
  │          • Asynchrone Nachberechnung bei verzögerten Zählerständen (`recalculate_late_slot`)
  │          • Wöchentlicher 30-Tage Reconciliation-Cron (`reconcile_balance_last_30d`)
  │          • Strikte Tenant-Isolation und Rollenprüfung für Zähler
  ├── 4.5 ✅ **Energy Sharing Community Cockpit (Frontend & Backend API)**:
  │          • Aggregations-API (`GET /api/billing/community/cockpit/`)
  │          • 5 Hero-KPIs: Produziert (2.8.0), Verbraucht (1.8.0), Geteilt (Autarkie %), Zugekauft (Reststrom) & Ersparnis (€)
  │          • 15-Minuten Lastgang-Timeline der letzten 24 Stunden
  │          • 48-Stunden KI-Erzeugungsprognose mit Hervorhebung günstiger Ladefenster (*Peak Windows*)
  │          • Tab-Navigation (`⚡ Energy Cockpit`, `💰 Tarife & Abrechnungen`, `👥 Mitglieder & Zähler`, `📜 Audit`)
  ├── 4.6 ✅ **Sharing-Tarife & Automatische Monatsabrechnungs-Engine (Clearing)**:
  │          • `CommunityTariff`: Bezugspreis (Ct/kWh), Einspeisevergütung (Ct/kWh), Community-Umlage, Netzentgelt-Rabatt (§ 42b EnWG)
  │          • `CommunityMonthlyStatement`: Cent-genaue Verrechnung von Gutschriften & Forderungen mit Netto-Saldo (€)
  │          • 1-Klick Abrechnungs-Trigger im Frontend & Django Admin Integration
  ├── 4.7 ✅ **Zentrales Multi-Community Management Hub & Portfolio-Dashboard**:
  │          • Portfolio-Übersicht (`/admin/communities`) mit Portfolio-Gesamterzeugung, Autarkie & Ersparnis
  │          • Detaillierte Drilldown-Ansicht für jede Energiegemeinschaft (Teilnehmer, Zähler, Tarife, Einstellungen)
  │          • Community-Rundschreiben & Broadcast-Mitteilungen (`CommunityAnnouncement`)
  ├── 4.8 ✅ **Gesetzlicher Ingestion- & Reststrom-Leitfaden (MsbG & MaKo / MSCONS)**:
  │          • Publikationsreifer Guide [`docs/ENERGY_SHARING_METER_INGEST_GUIDE.md`](file:///c:/Users/Public/Dev/eswes/docs/ENERGY_SHARING_METER_INGEST_GUIDE.md)
  │          • 3 Zählerpfade (wMSB REST/SFTP, gMSB HAN-Schnittstelle, Submetering)
  │          • VNB-Marktkommunikation & Vermeidung von Doppelabrechnungen beim Reststromversorger
  ├── 4.9 ✅ **PDF-Monatsabrechnungsnachweise & Multi-Format Exporte (Excel, CSV, XML / ERP)**:
  │          • Druckfähiges ReportLab PDF gem. § 42b EnWG mit Abrechnungsnummer, Mengenbilanz & Saldobox
  │          • Excel-Export (`.xlsx`) mit Spaltenformatierung, Währungsformaten & automatischen Summenformeln
  │          • CSV-Export mit UTF-8 BOM und Semikolon für direkte DATEV-/Excel-Kompatibilität
  │          • Standardisierter XML-Export (`<EnergySharingSettlementExport>`) für Hausverwaltungs- & ERP-Schnittstellen
  │          • Integriert im Tenant-Dashboard (`TenantDashboard.jsx`) & Multi-Community Hub (`CommunitiesManagementHub.jsx`)
  ├── 4.10 ✅ **Erweiterte Allokationsmodelle & Beteiligungsquoten (§ 42b / § 42a EnWG)**:
  │          • 3 Allokationsmodelle: Dynamisch (15m Lastgang), Statisch (MEA-Quoten / Miteigentumsanteile), Hybrid (Vorrang + Überlauf)
  │          • `CommunityMemberShare` Modell mit MEA-Zähler/Nenner, kWp-Zuweisung, automatischer %-Berechnung & 100%-Normierung
  │          • 15-Minuten-scharfe Allokations-Engine in `billing/services_sharing_settlement.py`
  │          • Live 3-Modelle Vergleichs- & Simulations-Engine (`/api/billing/community/allocation-preview/`)
  │          • Integriert im Multi-Community Hub (`CommunitiesManagementHub.jsx`) & Mitglieder-Dashboard (`TenantDashboard.jsx`)
  └── 4.11 ⏳ **§ 14a EnWG Steuerbox-Schnittstelle & Pflichtdimmung auf 4,2 kW (SteuVE)**:
             • EEBUS / Modbus TCP / REST Steuerbox-Anbindung für Wärmepumpen & Wallboxen
```

---

## 📋 4. Konkreter Action-Plan für die nächsten Schritte (Prioritätenmatrix)

| Schritt | Modul | Maßnahme | Status / Prio | Ziel & Nächste Entscheidung |
|---|---|---|:---:|---|
| **Step 1** | `billing/sharing/` | **Beteiligungsquoten & Allokationsmodelle**: Unterstützung von festen Beteiligungs-% an Gemeinschaftsanlagen (statische Quoten vs. dynamische Allokation vs. Hybrid) | ✅ **100% Live** | Flexible Allokation bei gemeinsamen Dachanlagen / Mieterstrom |
| **Step 2** | `grid/enwg/` | **§ 14a EnWG Steuerbox & Dimmung**: Dynamische Leistungsbegrenzung auf 4,2 kW für SteuVE (WP, Wallbox, Speicher) via REST/Modbus | ⚡ **P1 (Nächster Schritt)** | Gesetzliche Netzbetreiber-Konformität in Deutschland |
| **Step 3** | `billing/tariffs/` | **Dynamische & Börsenpreis-gekoppelte Tarife**: Indexierte Sharing-Tarife (Day-Ahead Spotpreis + Formelaufschlag) | ⚡ **P2** | Dynamische Preissignale innerhalb der Community |
| **Step 4** | `billing/payment/` | **Payment- & Provider-Evaluierung**: Klärung von Zahlungsdienstleistern (Stripe, SEPA, GoCardless) für automatischen Beitragseinzug | 💳 **P2 (Nach Evaluierung)** | Vorbereitung des automatischen Einzugs von Mitgliedsbeiträgen |
| **Step 5** | `billing/edifact/` | **Standardisierte Marktkommunikations-Bridge**: Export-Mapping auf MSCONS / EDIFACT zur VNB-Abstimmung | ⚡ **P3** | Nahtloser Austausch mit Netzbetreibern und Aggregatoren |




