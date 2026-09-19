# 🧭 Sharegy Strategie-Check & Umsetzungs-Blueprint

**Dokument-Status:** Strategisches Management-Audit & Technischer Realisierungsplan  
**Version:** 5.4 (Stand: 19. September 2026 / v5.4 Live)  
**Zielgruppe:** Management, Produktentwicklung, Enterprise Vertrieb  

---

## 📊 1. Executive Summary & Status-Matrix (v5.4)

Die folgende Matrix gibt einen transparenten Überblick darüber, welche Module und Funktionen im Sharegy-Repository bereits **vollständig einsatzbereit (100% Live)**, welche **in aktiver Umsetzung** und welche als **nächste Ausbaustufen** geplant sind.

| Handlungsfeld / Modul | Status in Sharegy | Bereits implementiert | Was noch fehlt / Nächster Schritt |
|---|:---:|---|---|
| **📁 Zentraler Dokumenten- & Export-Hub** | 🟢 **100% Live** | `/app/documents` mit KPI-Karten, On-Demand Streaming-Exporten (DATEV, MSCONS 2.2b, UTILMD, PDF), SHA-256 Hashketten-Prüfung und GoBD-Archivierung. | Weitere ERP-spezifische Buchungsformate bei Bedarf. |
| **🔑 Granulare Enterprise RBAC-Matrix** | 🟢 **100% Live** | 5 Rollen: `SuperAdmin`, `Dispatcher`, `Billing Specialist`, `Field Technician`, `Auditor` in Backend & Frontend (`useUser.js`). | 2FA-Pflicht für privilegierte Rollen enforcen. |
| **⚡ BNetzA CLS-Kanal & SMGW (§ 14a EnWG)** | 🟢 **100% Live** | `POST /api/energy/cls/signal/`, BSI TR-03109-1 Ingest, FNN Steuerbox Quittierung, $4{,}2\,\text{kW}$ Summenbudget & `EnWG14aDimmingAuditLog`. | Hardware-Feldtests mit zertifizierten SMGW-Prüfständen. |
| **📈 VPP Flexibilität & 80/20 Market Clearing** | 🟢 **100% Live** | aFRR/SRL Pooling, 96-Viertelstunden-Fahrpläne, monetäre Clearing Engine mit 80/20 Split (`VPPClearingStatement`) und Aggregator-Webhooks. | Anschluss an lizenzierten Bilanzkreiskoordinator (Next Kraftwerke / Statkraft). |
| **⏳ Skeleton-Loading & SWR UX** | 🟢 **100% Live** | Reusable `Skeleton`-Suite & globales TanStack Query Caching (`staleTime: 2m`) für Zero Layout Shift ($< 20\,\text{ms}$). | Laufende Erweiterung auf neue Views. |
| **1.1 Installateurs- & Partner-Portal** | 🟢 **100% Live** | Partner-Datenmodell (`PartnerCompany`, `MaintenanceConsent`), Flotten-API (`/api/partner/fleet/`), 1-Klick-Inbetriebnahme & `PartnerDashboard.jsx`. | Skalierung des Vertriebsnetzes & Partner-Zertifizierung. |
| **1.2 Bürgerenergie & WEG (§ 42b EnWG)** | 🟢 **100% Live** | Virtueller Summenzähler, 15m-Saldierung (`BalanceSlot`), Community-Tarife, Mieterstrom-PDFs, Communities Hub. | B2B-Vertriebsmaterialien & Lead-Funnel für Hausverwaltungen. |
| **2.1 Multi-Cloud Inverter (10 Hersteller)** | 🟢 **100% Live** | Sungrow, Fronius, SMA, SolarEdge, Huawei, Deye, Hoymiles, GoodWe, Kostal, Victron API v2 im Setup-Wizard. | Anbindung weiterer Nischen-Hersteller bei Bedarf. |
| **3.2 BNetzA AS4 Marktkommunikation** | 🟢 **100% Live** | BNetzA-konformer EDIFACT MSCONS (15m Lastgang § 42b EnWG) & UTILMD Generator, AS4-Gateway Dispatcher. | Live-Anbindung an Produktiv-Gateways (powercloud / Schleupen / direct AS4 PKI). |
| **3.1 EEBUS & Cloud Ecosystem Bridge** | 🟡 **In Konzeption (45%)** | Datenmodell für steuerbare Lasten (§ 14a EnWG), SG-Ready Relais, Modbus & Cloud-APIs für Wärmepumpen. | Nativer EEBUS SHIP/SPINE Stack bzw. Cloud-to-Cloud Bridge (Home Connect, myVAILLANT, ViCare API). |
| **4.1 Enterprise UX Suite (Cmd+K, Toasts, Flyout)** | 🟡 **Spezifiziert (25%)** | Detaillierte Spezifikationen in `docs/wip/` (`WIP_COMMAND_CENTER_...`, `WIP_GLOBAL_TOAST_...`, `WIP_ENTERPRISE_NOTIFICATION_...`). | Frontend-Komponenten `CommandCenterModal.jsx`, `ToastProvider.jsx`, `NotificationFlyout.jsx`. |
| **4.2 Security & Integration (2FA, Webhooks)** | 🟡 **Spezifiziert (20%)** | Detaillierte Spezifikationen in `docs/wip/` (`WIP_TWO_FACTOR_...`, `WIP_OUTBOX_WEBHOOK_...`). | Backend TOTP-Scoping & transaktionaler Celery Outbox Dispatcher. |

---

## 🔮 2. Die Strategischen Horizonte für 2026/2027

---

### 🏛️ Horizont 1: Enterprise-UX & B2B-Integration (Q4 2026)
* **Cmd+K Spotlight Search**: Tastaturgesteuertes Quick-Nav-Overlay für Power-User & Admins.
* **Notification Flyout**: Reaktives Topbar-Dropdown für Störungen, VPP-Aktionen, IBN-Protokolle & System-Events.
* **Global Toast System**: Nicht-blockierende Erfolgs- und Statusmeldungen mit 5s Undo-Support.
* **Pflicht-2FA (TOTP)**: Schutz kritischer VPP- und Admin-Rollen durch Authenticator-App-Zwang.
* **Outbox-Pattern Webhook Dispatcher**: Transaktionale Event-Benachrichtigung für ERP- und CRM-Systeme von Stadtwerken und Verwaltern (SAP, DATEV, Salesforce).

---

### 🏠 Horizont 2: EEBUS & Cloud Ecosystem Bridge (Q1–Q2 2027)
* **Zweistufiger Ansatz**:
  1. *Cloud-to-Cloud Bridge*: Anbindung herstellereigener Cloud-APIs (BSH Home Connect, myVAILLANT, Viessmann ViCare) für PV-Surplus-Startzeiten und Heizungssollwertanhebung.
  2. *Lokaler EEBUS SHIP/SPINE Stack*: Leichtgewichtiger Daemon für die direkte mDNS-Kopplung von Wärmepumpen und Haushaltsgroßgeräten im lokalen Netzwerk.

---

### 🛰️ Horizont 3: Entkoppelter Monitoring-Cluster & Offline Edge Daemon (Q2–Q3 2027)
* **Zero-Trust Control Plane (`mon.sharegy.de`)**: Dual-Socket WSS-Architektur zur sauberen Trennung von Fachdaten und Flotten-Fernwartung.
* **Local Edge Daemon**: Lokales Go/Rust-Binary für Raspberry Pi & Home Assistant zur 100% ausfallsicheren, autonomen Ausführung von 24h-Lastfahrplänen auch bei vollständigem Internet-Ausfall.

---

## 🎯 3. Handlungsempfehlung für die nächste Sprint-Planung

```
[1. Spotlight Cmd+K & Toast System] ──► [2. Topbar Notification Flyout]
                                                         │
[4. Outbox Webhook Dispatcher]       ◄── [3. 2FA / MFA Authentifizierung]
```
