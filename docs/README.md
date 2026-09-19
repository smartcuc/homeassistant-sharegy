# ⚡ Sharegy Documentation & Knowledge Base Index

**Stand:** 19. September 2026 (v5.4 / Enterprise & Compliance Live)

Willkommen im offiziellen Wissens- und Dokumentations-Hub der **Sharegy**-Plattform (Smart Home Energy Management & Community Energy Sharing).

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
 └── 🧪 wip/             → Aktiver Entwicklungs-Backlog & Optimierungs-Masterplan
```

---

### 🏛️ 1. Architektur, Strategie & Blueprints ([`docs/architecture/`](./architecture/))

| Dokument | Beschreibung |
|---|---|
| ⚡ **[`BNETZA_CLS_SMART_METER_GATEWAY_INTEGRATION.md`](./architecture/BNETZA_CLS_SMART_METER_GATEWAY_INTEGRATION.md)** | **NEU:** BNetzA CLS-Kanal & Smart Meter Gateway (SMGW) Kopplung (§ 14a EnWG Drosselung, FNN Steuerbox Quittierung) |
| 📈 **[`AUTOMATED_FLEXIBILITY_AND_VPP_MARKET_CLEARING.md`](./architecture/AUTOMATED_FLEXIBILITY_AND_VPP_MARKET_CLEARING.md)** | **NEU:** Automatisierter Flexibilitäts- & Regelleistungshandel (aFRR/SRL, 80/20 Erlös-Clearing & Aggregator-Schnittstelle) |
| ⚡ **[`VPP_FLEXIBILITY_BONUS_ECOSYSTEM_AND_PROCESS_GUIDE.md`](./architecture/VPP_FLEXIBILITY_BONUS_ECOSYSTEM_AND_PROCESS_GUIDE.md)** | Virtuelles Kraftwerk (VPP) Flexibilitäts-Bonus: Ökosystem, Kooperationsmatrix, End-to-End Prozesse & Erlösmodelle |
| 🌐 **[`DECOUPLED_MONITORING_AND_REMOTE_RPC_ARCHITECTURE.md`](./architecture/DECOUPLED_MONITORING_AND_REMOTE_RPC_ARCHITECTURE.md)** | Entkoppelte Monitoring-Subdomain (`mon.sharegy.de`), WSS Reverse-RPC Fernwartung & Edge-Isolation |
| 🔌 **[`API_REFERENCE_AND_ENDPOINTS.md`](./architecture/API_REFERENCE_AND_ENDPOINTS.md)** | Vollständige REST- & WebSocket-API-Referenz, Authentifizierung (JWT/API-Keys) & Endpunktkatalog |
| 🏛️ **[`ARCHITECTURE.md`](./architecture/ARCHITECTURE.md)** | Gesamtsystem-Architektur, Dual-Core Konzept, Tech-Stack, Subdomains & Datenflüsse |
| 🧭 **[`SHAREGY_STRATEGIC_HORIZONS_AND_IMPLEMENTATION_BLUEPRINT.md`](./architecture/SHAREGY_STRATEGIC_HORIZONS_AND_IMPLEMENTATION_BLUEPRINT.md)** | Strategische Handlungsempfehlungen, Umsetzungs-Statusmatrix & Realisierungspläne |
| 🗺️ **[`SHAREGY_STRATEGIC_ROADMAP.md`](./architecture/SHAREGY_STRATEGIC_ROADMAP.md)** | Strategische Produkt-Roadmap (Meilensteine 1 bis 9 inkl. Whitelabel & Mako) |
| 🗄️ **[`DATA_MODEL.md`](./architecture/DATA_MODEL.md)** | Vollständige Datenmodell-Referenz (EMS, Forecast, Market, Metering, Core, Partner) |
| 🏢 **[`VPP_AND_VIRTUAL_METER_GUIDE.md`](./architecture/VPP_AND_VIRTUAL_METER_GUIDE.md)** | Virtueller Summenzähler (§ 42b EnWG), 15m-Lastgänge & VPP Aggregator Engine (aFRR/SRL, Redispatch 2.0) |
| ⚡ **[`EMS_SYSTEM_GUIDE.md`](./architecture/EMS_SYSTEM_GUIDE.md)** | Home Energy Management System: Telemetrie, Deadband-Filter, Flow-Engine, Tarife, Tibber & 96h Solar-Forecast |
| 🚗 **[`SHAREGY_V2G_V2H_BIDIRECTIONAL_CHARGING_ARCHITECTURE.md`](./architecture/SHAREGY_V2G_V2H_BIDIRECTIONAL_CHARGING_ARCHITECTURE.md)** | Bidirektionales Laden (V2G/V2H), ISO 15118-20, OCPP 2.0.1 & dynamische Entladestrategien |
| 🎯 **[`SHAREGY_STRATEGIC_EVALUATION_AND_GAP_ANALYSIS.md`](./architecture/SHAREGY_STRATEGIC_EVALUATION_AND_GAP_ANALYSIS.md)** | Gesamtevaluation: Stärken, Marktlücken & strategischer Masterplan |
| 🏆 **[`SHAREGY_COMPETITOR_BENCHMARK_AND_EVALUATION.md`](./architecture/SHAREGY_COMPETITOR_BENCHMARK_AND_EVALUATION.md)** | Mitbewerber-Vergleich (1KOMMA5°, Tibber, evcc, Exnaton, Clever-PV) & Matrix |
| 💰 **[`SHAREGY_FINANCIAL_VALUATION_AND_DEVELOPMENT_COSTS.md`](./architecture/SHAREGY_FINANCIAL_VALUATION_AND_DEVELOPMENT_COSTS.md)** | Finanzielle Bewertung, Substanzwert (Cost-to-Duplicate) & ARR-Multiples |
| 📈 **[`STRESS_TEST_REPORT_200U_4000D.md`](./architecture/STRESS_TEST_REPORT_200U_4000D.md)** | Lasttest-Bericht (200 parallele Nutzer, 4.000 simulierte IoT-Geräte) |

---

### 🚀 2. Server-Betrieb & Deployment ([`docs/operations/`](./operations/))

| Dokument | Beschreibung |
|---|---|
| ⚡ **[`VPP_FLEXIBILITY_AND_MARKET_CLEARING_OPERATIONS.md`](./operations/VPP_FLEXIBILITY_AND_MARKET_CLEARING_OPERATIONS.md)** | Virtuelles Kraftwerk (VPP), Regelleistung (aFRR/FCR), 80/20 Market Clearing, Aggregator-Webhooks & Runbooks |
| 🚀 **[`OPERATIONS_AND_DEPLOYMENT.md`](./operations/OPERATIONS_AND_DEPLOYMENT.md)** | Server-Deployment (Ubuntu/Debian), Systemd Services, Redis, Celery & Health-Checks |
| 🛡️ **[`DATA_PRIVACY_AND_GDPR_COMPLIANCE.md`](./operations/DATA_PRIVACY_AND_GDPR_COMPLIANCE.md)** | DSGVO-Konzept, Technische und Organisatorische Maßnahmen (TOMs), AVV-Muster & Löschfristen |
| ✅ **[`PRODUCTION_DEPLOYMENT_CHECKLIST.md`](./operations/PRODUCTION_DEPLOYMENT_CHECKLIST.md)** | Checkliste für Produktiv-Rollouts, SSL-Zertifikate, Umgebungsvariablen & DNS |
| 💾 **[`DATABASE_BACKUP_AND_RESTORE.md`](./operations/DATABASE_BACKUP_AND_RESTORE.md)** | PostgreSQL & TimescaleDB Backup-/Restore-Prozeduren und Desaster Recovery |
| 📦 **[`SERVER_LEAN_DEPLOYMENT_SPARSE_CHECKOUT.md`](./operations/SERVER_LEAN_DEPLOYMENT_SPARSE_CHECKOUT.md)** | Lean Deployment via Git Sparse-Checkout für ressourcenschonende Server |
| 🔥 **[`FIREBASE_SETUP_GUIDE.md`](./operations/FIREBASE_SETUP_GUIDE.md)** | Firebase Service-Account, FCM-Schlüssel und Android Push-Setup |

---

### 📱 3. Mobile Apps ([`docs/mobile/`](./mobile/))

| Dokument | Beschreibung |
|---|---|
| 📱 **[`ANDROID_APP_DEVELOPMENT_AND_RELEASE_GUIDE.md`](./mobile/ANDROID_APP_DEVELOPMENT_AND_RELEASE_GUIDE.md)** | Native Android App (Capacitor 7, Android Studio Setup, Emulatoren, Gradle Build & Signing) |
| 🛒 **[`PLAY_STORE_RELEASE_AND_ACCOUNT_GUIDE.md`](./mobile/PLAY_STORE_RELEASE_AND_ACCOUNT_GUIDE.md)** | Google Play Console Setup, D-U-N-S Verifikation & Release-Pipeline |
| 🔔 **[`NOTIFICATIONS_AND_MOBILE_PUSH.md`](./mobile/NOTIFICATIONS_AND_MOBILE_PUSH.md)** | Mobile Push & Notification Engine (W3C Web-Push, VAPID, Service Worker & Quiet Hours) |

---

### 👥 4. Administration ([`docs/admin/`](./admin/))

| Dokument | Beschreibung |
|---|---|
| 🧭 **[`ROLE_BASED_NAVIGATION_AND_CONTEXT_SWITCHING.md`](./admin/ROLE_BASED_NAVIGATION_AND_CONTEXT_SWITCHING.md)** | **NEU:** Rollen- & kontextbasierte Aufteilung der Side-Navigation für EMS, Mieter, Partner & Admins |
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
| 🚀 **[`GENERAL_RELEASE_TESTING_AND_GO_TO_MARKET.md`](./marketing/GENERAL_RELEASE_TESTING_AND_GO_TO_MARKET.md)** | **NEU:** General Release QA-, Test- und Rollout-Masterplan für B2C & B2B |
| 💼 **[`COMMERCIAL_SALES_PITCH_AND_B2B_KIT.md`](./marketing/COMMERCIAL_SALES_PITCH_AND_B2B_KIT.md)** | B2B-Sales-Kits für WEGs, Hausverwaltungen, Energiegenossenschaften & Installateure |
| ⚡ **[`SHAREGY_FEATURE_CATALOG_AND_MARKETING_MATRIX.md`](./marketing/SHAREGY_FEATURE_CATALOG_AND_MARKETING_MATRIX.md)** | Gesamter Feature-Katalog & Marketing-Leistungsmatrix aller 15 Module |
| 📱 **[`APP_TEASER.md`](./marketing/APP_TEASER.md)** | App Store Beschreibungen, Teaser-Texte und Marken-Farbkonzepte |

---

### 🔌 7. Integrationen & Hardware ([`docs/integrations/`](./integrations/))

| Dokument | Bereich | Beschreibung |
|---|---|---|
| ☀️ **[`FACTOFY_SUPPORT_INTEGRATION_GUIDE.md`](./integrations/FACTOFY_SUPPORT_INTEGRATION_GUIDE.md)** | Support & Ticketing | Deep-Integration von Factofy Support-Tools & Remote-Diagnostik |
| 🌐 **[`PUBLIC_ADAPTER_DEPLOYMENT_GUIDE.md`](./integrations/PUBLIC_ADAPTER_DEPLOYMENT_GUIDE.md)** | Public Adapter / ioBroker | Deployment & Anbindung externer Open-Source Home-Automation Adapter |
| ⚡ **[`SHELLY_LOCAL_NON_CLOUD_SETUP_GUIDE.md`](./integrations/SHELLY_LOCAL_NON_CLOUD_SETUP_GUIDE.md)** | Shelly Local / Non-Cloud | Lokale WSS & Outbound WebSocket Konfiguration für Shelly Gen2/Gen3/Pro |

---

### 🧪 8. Entwicklungs-Backlog & Aktive WIP-Features ([`docs/wip/`](./wip/))

| Dokument | Bereich | Status & Priorität | Beschreibung |
|---|---|:---:|---|
| 🛠️ **[`OPTIMIZATION_AND_AUDIT_MASTERPLAN.md`](./wip/OPTIMIZATION_AND_AUDIT_MASTERPLAN.md)** | Masterplan | 🟢 v5.4 Live | Konsolidierter Status (78% Live, 14% WIP, 8% Backlog) & Roadmap |
| ⚡ **[`WIP_COMMAND_CENTER_SPOTLIGHT_SEARCH.md`](./wip/WIP_COMMAND_CENTER_SPOTLIGHT_SEARCH.md)** | Power-User UX | 🟡 25% / 🔴 Hoch | Tastaturgesteuertes Cmd+K / Ctrl+K Quick-Nav Overlay ($<300\,\text{ms}$) |
| 🔔 **[`WIP_ENTERPRISE_NOTIFICATION_AND_ACTIVITY_FLYOUT.md`](./wip/WIP_ENTERPRISE_NOTIFICATION_AND_ACTIVITY_FLYOUT.md)** | Operator UX | 🟡 20% / 🔴 Hoch | Reaktives Topbar-Dropdown mit 4 Tabs (Störungen, VPP, IBN, System) |
| 🍞 **[`WIP_GLOBAL_TOAST_NOTIFICATION_SYSTEM.md`](./wip/WIP_GLOBAL_TOAST_NOTIFICATION_SYSTEM.md)** | Micro-UX | 🟡 25% / 🔴 Hoch | Nicht-blockierende Toasts für Erfolge & Warnungen mit Undo-Support |
| 🔐 **[`WIP_TWO_FACTOR_AUTHENTICATION_MFA.md`](./wip/WIP_TWO_FACTOR_AUTHENTICATION_MFA.md)** | Security | 🟡 20% / 🔴 Hoch | Pflicht-2FA für Admins & Dispatcher (TOTP QR-Code, Backup-Codes) |
| 🪝 **[`WIP_OUTBOX_WEBHOOK_DISPATCHER_ERP_CRM.md`](./wip/WIP_OUTBOX_WEBHOOK_DISPATCHER_ERP_CRM.md)** | B2B Integration | 🟡 15% / 🔴 Hoch | Transaktionales Outbox-Pattern für SAP, DATEV & CRM mit HMAC-SHA256 |
| 📱 **[`WIP_DUAL_APP_ECOSYSTEM_USER_VS_PARTNER.md`](./wip/WIP_DUAL_APP_ECOSYSTEM_USER_VS_PARTNER.md)** | Mobile App | 🟢 **90%** / 🔴 Hoch | Two-App Strategie (`Sharegy Home` vs. `Sharegy Pro` mit QR-Inbetriebnahme) |
| 🔒 **[`WIP_DYNAMIC_WHITELABEL_SSL_PROVISIONING.md`](./wip/WIP_DYNAMIC_WHITELABEL_SSL_PROVISIONING.md)** | Whitelabel / TLS | 🟡 **70%** / 🟡 Mittel | Automatisierte Let's Encrypt SSL-Provisionierung für CNAME-Domains |
| 🌐 **[`WIP_SMARTEVO_WEBSITE_PRODUCT_INTEGRATION.md`](./wip/WIP_SMARTEVO_WEBSITE_PRODUCT_INTEGRATION.md)** | Dachmarken-Web | 🟡 **65%** / 🟡 Mittel | Integration von Sharegy & Factofy im smartEvo.de Webauftritt |
| 🔌 **[`WIP_DECOUPLED_MONITORING_CLUSTER_AND_REVERSE_RPC.md`](./wip/WIP_DECOUPLED_MONITORING_CLUSTER_AND_REVERSE_RPC.md)** | Edge & WSS | 🟡 **55%** / 🔴 Hoch | Auslagerung auf `mon.sharegy.de` & Zero-Trust WSS Reverse-RPC Wartung |
| 🏠 **[`WIP_EEBUS_AND_CLOUD_ECOSYSTEM_BRIDGE.md`](./wip/WIP_EEBUS_AND_CLOUD_ECOSYSTEM_BRIDGE.md)** | HEMS / Wärmepumpe | 🟡 **45%** / 🔴 Hoch | EEBUS SHIP/SPINE Stack & Cloud-APIs (myVAILLANT, Home Connect) |

---

### 📋 9. Walkthroughs & Meilensteine ([`docs/walkthroughs/`](./walkthroughs/))

Chronologische Entwicklungs- und Release-Protokolle:
* 📝 **[`2026-09-16_code_review_and_vpp_resilience_optimization.md`](./walkthroughs/2026-09-16_code_review_and_vpp_resilience_optimization.md)**: DTOs, Redis-Caching für Flottenaggregation & Circuit-Breaker API-Resilienz
* 📂 **[Alle Meilenstein-Protokolle ansehen](./walkthroughs/)**
