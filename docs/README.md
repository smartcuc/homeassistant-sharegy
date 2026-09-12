# ⚡ Sharegy Documentation & Knowledge Base Index

Willkommen in der offiziellen Dokumentation der **Sharegy**-Plattform (Smart Home Energy Management & Community Energy Sharing).

---

## 📁 Strukturierte Dokumenten-Übersicht

```
docs/
 ├── 🏛️ architecture/    → Strategie, Systemarchitektur, Datenmodelle, Benchmarks & Blueprints
 ├── 🚀 operations/      → Server-Betrieb, Deployment, Backups, System-Administration
 ├── 📱 mobile/          → Native Android App (Capacitor 7), Play Store Release & Push
 ├── 👥 admin/           → Liegenschafts- & Tenant-Administration, RBAC, Support-Desk
 ├── 📖 user/            → Endanwender-Handbücher, Schnellstarts, Einsparungs-Matrizen
 ├── 🔌 integrations/    → Cloud-Inverter, Smart-Meter, Home Assistant & MQTT Guides
 ├── 📢 marketing/       → B2B-Vertriebsmaterialien, Pitch-Kits, Leistungsmatrizen & Teaser
 ├── 📋 walkthroughs/    → Historische Meilenstein- und Entwicklungs-Protokolle
 └── 🧪 wip/             → Entwürfe, Optimierungspläne, Code-Audits & Refactorings
```

---

### 🏛️ 1. Architektur, Strategie & Blueprints ([`docs/architecture/`](./architecture/))

| Dokument | Beschreibung |
|---|---|
| 🌐 **[`DECOUPLED_MONITORING_AND_REMOTE_RPC_ARCHITECTURE.md`](./architecture/DECOUPLED_MONITORING_AND_REMOTE_RPC_ARCHITECTURE.md)** | **NEU:** Entkoppelte Monitoring-Subdomain (`mon.sharegy.de`), WSS Reverse-RPC Fernwartung & Edge-Isolation |
| 🏛️ **[`ARCHITECTURE.md`](./architecture/ARCHITECTURE.md)** | Gesamtsystem-Architektur, Dual-Core Konzept, Tech-Stack & Datenflüsse |
| 🧭 **[`SHAREGY_STRATEGIC_HORIZONS_AND_IMPLEMENTATION_BLUEPRINT.md`](./architecture/SHAREGY_STRATEGIC_HORIZONS_AND_IMPLEMENTATION_BLUEPRINT.md)** | Strategische Handlungsempfehlungen, Umsetzungs-Statusmatrix & Realisierungspläne |
| 🗺️ **[`SHAREGY_STRATEGIC_ROADMAP.md`](./architecture/SHAREGY_STRATEGIC_ROADMAP.md)** | Strategische Produkt-Roadmap (Meilensteine 1 bis 9 inkl. Whitelabel & Mako) |
| 🗄️ **[`DATA_MODEL.md`](./architecture/DATA_MODEL.md)** | Vollständige Datenmodell-Referenz (EMS, Forecast, Market, Metering, Core) |
| 🏢 **[`VPP_AND_VIRTUAL_METER_GUIDE.md`](./architecture/VPP_AND_VIRTUAL_METER_GUIDE.md)** | Virtueller Summenzähler (§ 42b EnWG) & VPP Aggregator Engine (aFRR/SRL, Redispatch 2.0) |
| ⚡ **[`EMS_SYSTEM_GUIDE.md`](./architecture/EMS_SYSTEM_GUIDE.md)** | Home Energy Management System: Telemetrie, Deadband-Filter, Flow-Engine & Sankey |
| 🚗 **[`SHAREGY_V2G_V2H_BIDIRECTIONAL_CHARGING_ARCHITECTURE.md`](./architecture/SHAREGY_V2G_V2H_BIDIRECTIONAL_CHARGING_ARCHITECTURE.md)** | Bidirektionales Laden (V2G/V2H), ISO 15118-20, OCPP 2.0.1 & dynamische Entladestrategien |
| 📊 **[`ENERGY_SHARING_METER_INGEST_GUIDE.md`](./architecture/ENERGY_SHARING_METER_INGEST_GUIDE.md)** | Ingestion-Architektur für 15-Minuten-Lastgänge & Zählpunkte |
| 🎯 **[`SHAREGY_STRATEGIC_EVALUATION_AND_GAP_ANALYSIS.md`](./architecture/SHAREGY_STRATEGIC_EVALUATION_AND_GAP_ANALYSIS.md)** | Gesamtevaluation: Stärken, Schwachstellen & Masterplan |
| 🏆 **[`SHAREGY_COMPETITOR_BENCHMARK_AND_EVALUATION.md`](./architecture/SHAREGY_COMPETITOR_BENCHMARK_AND_EVALUATION.md)** | Mitbewerber-Vergleich (1KOMMA5°, Tibber, evcc, Exnaton, Clever-PV) & Matrix |
| 💰 **[`SHAREGY_FINANCIAL_VALUATION_AND_DEVELOPMENT_COSTS.md`](./architecture/SHAREGY_FINANCIAL_VALUATION_AND_DEVELOPMENT_COSTS.md)** | Finanzielle Bewertung, Substanzwert (Cost-to-Duplicate) & ARR-Multiples |
| 💶 **[`TARIFF_AND_MARKET.md`](./architecture/TARIFF_AND_MARKET.md)** | Stromtarife (Statisch / Dynamisch), EPEX Spot Börsenpreise & Tibber API |
| ☀️ **[`SOLAR_FORECAST.md`](./architecture/SOLAR_FORECAST.md)** | 96h Hybrid-Prognose (Open-Meteo Wetter, Physik-Modell & Random Forest ML) |
| 📈 **[`STRESS_TEST_REPORT_200U_4000D.md`](./architecture/STRESS_TEST_REPORT_200U_4000D.md)** | Lasttest-Bericht (200 parallele Nutzer, 4.000 simulierte IoT-Geräte) |

---

### 🚀 2. Server-Betrieb & Deployment ([`docs/operations/`](./operations/))

| Dokument | Beschreibung |
|---|---|
| 🚀 **[`OPERATIONS_AND_DEPLOYMENT.md`](./operations/OPERATIONS_AND_DEPLOYMENT.md)** | Server-Deployment (Ubuntu/Debian), Systemd Services, Redis, Celery & Health-Checks |
| ✅ **[`PRODUCTION_DEPLOYMENT_CHECKLIST.md`](./operations/PRODUCTION_DEPLOYMENT_CHECKLIST.md)** | Checkliste für Produktiv-Rollouts, SSL-Zertifikate, Umgebungsvariablen & DNS |
| 💾 **[`DATABASE_BACKUP_AND_RESTORE.md`](./operations/DATABASE_BACKUP_AND_RESTORE.md)** | PostgreSQL & TimescaleDB Backup-/Restore-Prozeduren und Desaster Recovery |
| 📦 **[`SERVER_LEAN_DEPLOYMENT_SPARSE_CHECKOUT.md`](./operations/SERVER_LEAN_DEPLOYMENT_SPARSE_CHECKOUT.md)** | Lean Deployment via Git Sparse-Checkout für ressourcenschonende Server |
| 🔥 **[`FIREBASE_SETUP_GUIDE.md`](./operations/FIREBASE_SETUP_GUIDE.md)** | Firebase Service-Account, FCM-Schlüssel und Android Push-Setup |

---

### 📱 3. Mobile Apps ([`docs/mobile/`](./mobile/))

| Dokument | Beschreibung |
|---|---|
| 📱 **[`ANDROID_APP_BUILD_AND_RELEASE.md`](./mobile/ANDROID_APP_BUILD_AND_RELEASE.md)** | Native Android App (Capacitor 7, Gradle Build, Deep Linking & Signing) |
| 🛠️ **[`ANDROID_STUDIO_SETUP_GUIDE.md`](./mobile/ANDROID_STUDIO_SETUP_GUIDE.md)** | Schritt-für-Schritt Anleitung: Android Studio, SDKs & Emulator |
| 🛒 **[`PLAY_STORE_RELEASE_AND_ACCOUNT_GUIDE.md`](./mobile/PLAY_STORE_RELEASE_AND_ACCOUNT_GUIDE.md)** | Google Play Console Setup, D-U-N-S Verifikation & Release-Pipeline |
| 🔔 **[`NOTIFICATIONS_AND_MOBILE_PUSH.md`](./mobile/NOTIFICATIONS_AND_MOBILE_PUSH.md)** | Mobile Push & Notification Engine (W3C Web-Push, VAPID, Service Worker & Quiet Hours) |

---

### 👥 4. Administration ([`docs/admin/`](./admin/))

| Dokument | Beschreibung |
|---|---|
| 🏢 **[`TENANT_ADMIN_HANDBOOK_AND_FAQ.md`](./admin/TENANT_ADMIN_HANDBOOK_AND_FAQ.md)** | Mandanten-Handbuch: Gebäude anlegen, Mieter verwalten, Zähler zuweisen & Tarife |
| 👥 **[`RBAC_AND_USER_MANAGEMENT_GUIDE.md`](./admin/RBAC_AND_USER_MANAGEMENT_GUIDE.md)** | Multi-Tenant Rollen- & Berechtigungskonzept (Plattform- & Community-Rollen) |
| 🎫 **[`HELPDESK_MODULE_DOCUMENTATION.md`](./admin/HELPDESK_MODULE_DOCUMENTATION.md)** | Support Desk, Ticket-System, ITIL-Prioritäten, Deflection & Factofy-Integration |

---

### 📖 5. Benutzer-Anleitungen ([`docs/user/`](./user/))

| Dokument | Beschreibung |
|---|---|
| 📖 **[`SHAREGY_USER_MANUAL_EMS_EXTENSIONS.md`](./user/SHAREGY_USER_MANUAL_EMS_EXTENSIONS.md)** | Ausführliches Endanwender-Handbuch für alle HEMS- & Energiefluss-Funktionen |
| ⚡ **[`FEATURE_USER_SAVINGS_MATRIX.md`](./user/FEATURE_USER_SAVINGS_MATRIX.md)** | Detaillierte Nutzer-Einsparungsmatrix für alle 15 Sharegy Module |
| ✨ **[`QUICKSTART_DEMO_AND_HELP_IMPORT.md`](./user/QUICKSTART_DEMO_AND_HELP_IMPORT.md)** | Schnellstart-Anleitung & Import von Hilfe-Artikeln |

---

### 📢 6. Marketing & Vertrieb ([`docs/marketing/`](./marketing/))

| Dokument | Beschreibung |
|---|---|
| 💼 **[`COMMERCIAL_SALES_PITCH_AND_B2B_KIT.md`](./marketing/COMMERCIAL_SALES_PITCH_AND_B2B_KIT.md)** | B2B-Sales-Kits für WEGs, Hausverwaltungen, Energiegenossenschaften & Installateure |
| ⚡ **[`SHAREGY_FEATURE_CATALOG_AND_MARKETING_MATRIX.md`](./marketing/SHAREGY_FEATURE_CATALOG_AND_MARKETING_MATRIX.md)** | Gesamter Feature-Katalog & Marketing-Leistungsmatrix aller 15 Module |
| 📱 **[`APP_TEASER.md`](./marketing/APP_TEASER.md)** | App Store Beschreibungen, Teaser-Texte und Marken-Farbkonzepte |

---

### 🔌 7. Integrationen & Hardware ([`docs/integrations/`](./integrations/))

| Dokument / Bereich | Beschreibung |
|---|---|
| ☀️ **`inverters/`** | Multi-Cloud-Inverter Anbindung (Sungrow, Fronius, SMA, SolarEdge, Huawei, Deye, Hoymiles, GoodWe, Kostal) |
| ⚡ **`shelly/`** | Direkte WSS-Anbindung für Shelly Gen2/Gen3/Pro Messrelais |
| 📡 **`homeassistant/`** | Custom Component & Push-Service für Home Assistant |

---

### 🧪 8. Work-in-Progress & Audits ([`docs/wip/`](./wip/))

| Dokument | Beschreibung |
|---|---|
| 🛠️ **[`OPTIMIZATION_PLAN.md`](./wip/OPTIMIZATION_PLAN.md)** | Umfassender Optimierungs- und Härtungsplan |
| 🔍 **[`SHAREGY_CODEBASE_AUDIT_AND_FEATURE_EXPANSION.md`](./wip/SHAREGY_CODEBASE_AUDIT_AND_FEATURE_EXPANSION.md)** | Codebase-Audit, Performancehebel & Bundle-Optimierung |
| 🌐 **[`CODE_REVIEW_I18N_AUDIT_AND_FEATURE_PROPOSALS.md`](./wip/CODE_REVIEW_I18N_AUDIT_AND_FEATURE_PROPOSALS.md)** | i18n Übersetzungsaudit & Feature-Vorschläge |
| 🎨 **[`UI_AUDIT_AND_IMPROVEMENT_PROPOSALS.md`](./wip/UI_AUDIT_AND_IMPROVEMENT_PROPOSALS.md)** | UI/UX-Audit und Gestaltungsverbesserungen |

---

### 📋 9. Walkthroughs & Meilensteine ([`docs/walkthroughs/`](./walkthroughs/))

Chronologische Entwicklungs- und Release-Protokolle.
