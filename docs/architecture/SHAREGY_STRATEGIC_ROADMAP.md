# 🚀 Sharegy Strategische Produkt- & Architektur-Roadmap

**Mission**: Die führende europäische SaaS-Plattform für **Home Energy Management (EMS)**, **Energy Sharing Communities (ESC)** und **Virtuelle Kraftwerke (VPP)**.  
**Stand**: 19. September 2026 (Live v5.4)

---

## 🏛️ 1. Die Tri-Pillar Dual-Core Architektur

```
                           ┌──────────────────────────────────────────────┐
                           │            Sharegy SaaS Plattform            │
                           └──────────────────────┬───────────────────────┘
                                                  │
                 ┌────────────────────────────────┼───────────────────────────────┐
                 ▼                                ▼                               ▼
   ┌───────────────────────────────┐┌───────────────────────────────┐┌───────────────────────────────┐
   │   🟢 SÄULE 1: SMART EMS (PRO) ││   🔵 SÄULE 2: ENERGY SHARING  ││   ⚡ SÄULE 3: VPP & § 14a EnWG│
   │   Status: PRODUKTIV / GEHÄRTET││   Status: PRODUKTIV / GEHÄRTET││   Status: PRODUKTIV / GEHÄRTET│
   ├───────────────────────────────┤├───────────────────────────────┤├───────────────────────────────┤
   │ • Ziel: Privater Prosumer     ││ • Ziel: Bürgerenergie/Quartier││ • Ziel: Netzbetreiber & Markt │
   │ • Daten: 10 Cloud-Inverter,   ││ • Daten: iMSys Zähler (OBIS   ││ • Daten: BSI TR-03109-1 CLS,  │
   │   WSS, MQTT, OTel, Modbus, HA ││   1.8.0 Bezug, 2.8.0 Einspeis)││   Connect+ 96-Fahrplan `PT15M`│
   │ • Takt: Sub-Sekunde (Timescale)││ • Takt: 15-Minuten-Raster     ││ • Takt: 4-Sekunden / 15-Min.  │
   │ • 4 Pro Hubs: Control, Heat,  ││ • Features: P2P-Bilanzierung, ││ • Features: aFRR/SRL Pooling, │
   │   Mobility & Alerts           ││   Tenant-RBAC, Community      ││   80/20 Erlös-Clearing,       │
   │ • Features: Live-Sankey,      ││   Cockpit, 96h KI-Prognose,   ││   § 14a $4{,}2\,\text{kW}$    │
   │   7d EPEX Trend, Arbitrage,   ││   § 42b EnWG PDF & DATEV      ││   Summenbudget, FNN Quittung  │
   │   SG-Ready BWWP bis 60°C,     ││   Exporte, SHA-256 Hashketten,││ • Monetarisierung: 20%        │
   │   Capacitor 7 Android App     ││   GoBD-konformes Archiv       ││   Vermarktungsmarge / MWh     │
   │ • Monetarisierung: Stripe     ││ • Monetarisierung: Gebühren   ││                               │
   │   (Karten, SEPA, PayPal 7,99€)││   pro Zähler / kWh-Clearing   ││                               │
   └───────────────────────────────┘└───────────────────────────────┘└───────────────────────────────┘
```

---

## 🔍 2. Bestandsaufnahme der Meilensteine (v5.0 bis v5.4)

### ✅ Meilenstein 1–9 (Core HEMS, Sharing, Inverter & Apps):
- **TimescaleDB Hypertables & $O(1)$ Live-Cache**: Sub-Sekunden-Snapshots über `DeviceLatestMetric`.
- **Multi-Protokoll Ingestion**: Outbound WSS (Shelly Gen2/Gen3/Pro), MQTT, Home Assistant HACS, Grafana REST Bridge.
- **Multi-Cloud Inverter (10 Hersteller)**: Sungrow, Fronius, SMA, SolarEdge, Huawei, Deye, Hoymiles, GoodWe, Kostal, Victron API v2.
- **Energiefluss & Sankey-Engine**: Flackerfreie ECharts & SVG Visualisierung, dynamische Restlast-Disaggregation.
- **48h/96h Hybrid Physics + ML Forecast**: PV-Ertragsprognose, Lastprognose, 7-Tage Auto-ML Baseline Predictive Maintenance.
- **Smart Load Management & Aktorik**: 4 Autopilot-Modi, Live Power Budgeting, SG-Ready BWWP Boost bis 60°C.
- **Native Android App**: Capacitor 7 Shell, Fastlane Release Pipeline, FCM Push-Benachrichtigungen.
- **6-Sprachen i18n**: DE, EN, PL, FR, IT, ES in Web-App und Stripe-Checkout.

### ✅ Meilenstein 10: BNetzA CLS SMGW Gateway & § 14a EnWG Netzdrosselung (100% Live)
- `POST /api/energy/cls/signal/`: BSI TR-03109-1 konformer Ingest von Dimm-Befehlen.
- FNN Steuerbox Quittierung (Dispatch Acknowledgment) mit Millisekunden-Reaktionszeit.
- Dynamisches $4{,}2\,\text{kW}$ Summenleistungsbudget ($P_{\text{allow}} = 4{,}2\,\text{kW} + P_{\text{PV}} + P_{\text{Batt}} - P_{\text{Base}}$).
- Revisionssicheres `EnWG14aDimmingAuditLog` für Netzbetreiber-Nachweise.

### ✅ Meilenstein 11: Virtuelles Kraftwerk (VPP) & 80/20 Market Clearing (100% Live)
- Aggregation dezentraler Heimspeicher für Sekundärregelleistung (aFRR/SRL) und FCR.
- 96-Viertelstunden-Fahrpläne nach Connect+ / Redispatch 2.0 Standard (`PT15M`).
- Monetäre Clearing Engine: Automatische 80/20 Erlösaufteilung (80% Kunde / 20% Plattform) mit monatlichen `VPPClearingStatement` Gutschriften.
- Aggregator-Webhook-Schnittstelle mit API-Key Authentifizierung.

### ✅ Meilenstein 12: Zentraler Dokumenten- & Export-Hub (`/app/documents`) (100% Live)
- Zentrales Cockpit für alle PDF-Abrechnungen (§ 42b EnWG), DATEV-Buchungsstapel, BNetzA MSCONS 2.2b / UTILMD Exporte.
- On-Demand Streaming-Generator (`/api/core/documents/generate/`).
- SHA-256 Hashketten-Prüfung und GoBD-konforme Revisionsarchivierung.

### ✅ Meilenstein 13: Granulare Enterprise RBAC-Rollenmatrix (100% Live)
- 5 Rollenprofile: `SuperAdmin`, `Dispatcher`, `Billing Specialist`, `Field Technician`, `Auditor / Read-Only`.
- Reaktive Frontend-Rollen-Hooks (`useUser.js`) und Berechtigungsmatrix (`ROLE_PERMISSIONS`).

### ✅ Meilenstein 14: Skeleton-Loading & SWR Caching UX (100% Live)
- Reusable `Skeleton`-Suite (`SkeletonCard`, `SkeletonKpiGrid`, `SkeletonChart`, `SkeletonTable`).
- Globales TanStack Query SWR-Caching (`staleTime: 2m`) für ladezeitfreie Navigation ($< 20\,\text{ms}$) und Zero Layout Shift.

### ✅ Meilenstein 15: Helpcenter 2.0 & Online-Handbuch (100% Live)
- 11 Themen-Kategorien, 46 zweisprachige (DE/EN) Enterprise-Artikel.

---

## 🔮 3. Roadmap 2026/2027 (Nächste Ausbaustufen)

```
┌───────────────────────────────────────────────────────────────────────────────┐
│ PHASE 1: ENTERPRISE POWER-USER UX & SECURITY (Q4 2026)                        │
├───────────────────────────────────────────────────────────────────────────────┤
│ • ⚡ Globales Cmd+K / Ctrl+K Spotlight Command-Center (Fuzzy-Suche < 300ms)    │
│ • 🔔 Enterprise Notification & Activity Flyout (4 Tabs: Störung, VPP, IBN, Sys)│
│ • 🍞 Globales Toast-Notification-System (mit 5s Undo-Support)                 │
│ • 🔐 2FA / MFA Authentifizierung via TOTP (Google Authenticator / 1Password)  │
│ • 🪝 Outbox-Pattern Webhook Dispatcher für ERP/CRM (SAP, DATEV, Salesforce)   │
│                                                                               │
│ PHASE 2: EEBUS & OFFLINE-RESILIENZ (Q1–Q2 2027)                               │
├───────────────────────────────────────────────────────────────────────────────┤
│ • 🏠 EEBUS Cloud-to-Cloud Bridge (BSH Home Connect, myVAILLANT, ViCare)       │
│ • 📡 Nativer EEBUS SHIP/SPINE Stack für lokale Wärmepumpen-Direktanbindung    │
│ • 🛰️ Sharegy Local Edge Daemon (Autonomer Offline-Fahrplan für Raspberry Pi) │
│ • 🔌 1-Klick Ingestion für Infrarot-Leseköpfe (Hichi / Tasmota)               │
│                                                                               │
│ PHASE 3: APP STORE LISTING & INSTITUTIONELLE SKALIERUNG (Q3–Q4 2027)          │
├───────────────────────────────────────────────────────────────────────────────┤
│ • 📱 Google Play Store & Apple App Store Live-Veröffentlichung                │
│ • 🏢 Skalierung auf 100+ Quartiere und 10.000+ aktive Pro-Haushalte           │
│ • 💼 Vorbereitung für Series-A oder strategische M&A-Partnerschaften          │
└───────────────────────────────────────────────────────────────────────────────┘
```
