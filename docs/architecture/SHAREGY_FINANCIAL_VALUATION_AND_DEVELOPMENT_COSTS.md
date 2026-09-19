# 💰 Sharegy: Finanzielle Bewertung, Entwicklungskosten & Unternehmenswert

**Dokument-Version**: 5.4  
**Stand**: 19. September 2026 (Live v5.4)  
**Erstellt für**: Geschäftsführung, Gesellschafter, Investoren, Banken & Förderstellen  
**Autor**: Antigravity Principal Engineering & Strategy Review  

---

## Executive Summary

Dieses Dokument liefert eine fundierte, methodisch saubere und marktkonforme finanzielle Bewertung von **Sharegy**:
1. **Detaillierte Schätzung der herkömmlichen Entwicklungskosten**: Was hätte die Entwicklung von Sharegy bei klassischer Vorgehensweise (Inhouse-Softwareteam oder professionelle Digital-Agentur im DACH-Raum) real gekostet?
2. **Bezifferung des aktuellen Unternehmenswerts (Asset- & strategische Bewertung)**: Welchen monetären Wert repräsentiert die Plattform heute auf Basis von Substanzwert (Cost-to-Duplicate), SaaS-Markt-Multiples und strategischem M&A-Akquisitionswert für Energieversorger (EVU), Stadtwerke und Hardwarehersteller?

---

## 🏗️ Teil 1: Geschätzte Entwicklungskosten bei herkömmlicher Entwicklung

### 1.1 Projektumfang & Technologische Komplexität

Sharegy ist keine einfache CRUD-Webanwendung, sondern eine **hochkomplexe, verteilte Dual-Core Energie- & Clearing-Plattform** mit:
* **Echtzeit-Telemetrie & Sub-Sekunden Streaming** (TimescaleDB Hypertables, Continuous Aggregates, Redis Live-Buffer, Daphne WebSockets).
* **Multi-Protokoll IoT-Gateway** (Outbound-WSS für Shelly Gen2/Gen3/Pro, OCPP 1.6-J CSMS Wallbox-Server, MQTT-Broker, OpenTelemetry OTel, Modbus, ioBroker Adapter & Home Assistant Component).
* **Multi-Hersteller Cloud-Inverter Ökosystem** (10 Hersteller: Sungrow, Fronius, SMA, SolarEdge, Huawei, Deye, Hoymiles, GoodWe, Kostal, Victron).
* **Smart Meter Gateway CLS & § 14a EnWG Schnittstelle** (BSI TR-03109-1 Ingest, FNN Steuerbox Quittierung, $4{,}2\,\text{kW}$ Summenbudget & Audit-Trail).
* **Virtuelles Kraftwerk (VPP) & 80/20 Clearing** (aFRR/SRL Sekundärregelleistung, FCR, 96-Viertelstunden-Fahrpläne, monatliche Erlösabrechnungen).
* **Zentraler GoBD-konformer Dokumenten-Hub (`/app/documents`)** (Streaming-Exporte für DATEV, BNetzA MSCONS 2.2b, UTILMD, PDF & SHA-256 Hashketten).
* **Granulare Enterprise RBAC-Matrix** (5 Rollen: `SuperAdmin`, `Dispatcher`, `Billing`, `Field Tech`, `Auditor`).
* **Machine Learning & Hybrid-Physics Engines** (96h PV-Ertragsprognose mit Open-Meteo, Haushalts-Lastprognose, 7-Tage Auto-ML Baseline Predictive Maintenance).
* **Gesetzliches Energy Sharing & Clearing (§ 42b EnWG)** (15-Minuten OBIS-Bilanzierung, wMSB Discovergy/inexogy REST Hub, 3 Allokationsmodelle).
* **Modernes Frontend & Native Apps** (React SPA, ECharts Live-Sankey, 6 Sprachen i18n, Skeleton-Loading & SWR Caching, Capacitor 7 Android App & W3C Web-Push).
* **Helpcenter 2.0 & Online-Handbuch** (11 Kategorien, 46 zweisprachige DE/EN Fachartikel).

---

### 1.2 Aufwands- & Rollen-Kalkulation (Personenmonate & Tagessätze)

*Basis für die Kalkulation sind übliche DACH-Marktsätze (Deutschland/Österreich/Schweiz) im Bereich Energy-Tech, Cloud Architecture und Data Engineering:*
* **Senior Software Engineer / Architekt**: Tagessatz 1.150 € – 1.450 € (Inhouse-Vollkosten: ca. 115.000 € – 140.000 € p.a.)
* **Senior Data & ML Specialist**: Tagessatz 1.250 € – 1.550 € (Inhouse-Vollkosten: ca. 125.000 € – 150.000 € p.a.)
* **Frontend / UI-UX Lead**: Tagessatz 980 € – 1.300 € (Inhouse-Vollkosten: ca. 100.000 € – 120.000 € p.a.)
* **Regulatory / FinTech Specialist**: Tagessatz 1.300 € – 1.650 € (Inhouse-Vollkosten: ca. 130.000 € – 165.000 € p.a.)
* **QA / Security / Compliance**: Tagessatz 950 € – 1.200 € (Inhouse-Vollkosten: ca. 90.000 € – 110.000 € p.a.)
* **Lead Architect / Product Owner**: Tagessatz 1.350 € – 1.700 € (Inhouse-Vollkosten: ca. 135.000 € – 170.000 € p.a.)

---

### 1.3 Detaillierte Modul-Aufwandsschätzung

| Entwicklungsmodul | Benötigte Rollen | Aufwand (PT) | Inhouse-Kosten (€) | Agentur-Kosten (€) |
|---|---|:---:|:---:|:---:|
| **1. Backend, TimescaleDB & Telemetrie-Pipeline**<br>• Hypertables, Continuous Aggregates, $O(1)$ LatestMetric<br>• Redis Live-Buffer & Deadband-Filter<br>• Daphne ASGI WebSocket Server & Celery Priority Queues | Senior Backend Eng.<br>DevOps / DBA | 90 PT<br>*(~4,5 PM)* | 72.000 € – 88.000 € | 105.000 € – 135.000 € |
| **2. IoT-Gateways & Multi-Cloud Inverter (10 Marken)**<br>• Outbound WSS Shelly Ingest (Gen2/Gen3/Pro)<br>• Sungrow, Fronius, SMA, SolarEdge, Huawei, Deye, Hoymiles, GoodWe, Kostal, Victron<br>• OCPP 1.6-J CSMS Wallbox Gateway & Smart Charging<br>• Offizieller ioBroker Adapter & Home Assistant Component | Senior IoT Engineer<br>Cloud Protocol Eng. | 110 PT<br>*(~5,5 PM)* | 88.000 € – 110.000 € | 130.000 € – 165.000 € |
| **3. Smart Load Hub, HVAC, BWWP & Aktorik**<br>• 4 Pro Hubs (Control, Mobility, Heating, Alerts)<br>• 🌡️ Fußbodenheizungs-Steuerung & Prädiktives MPC (Estrich-Vorladung)<br>• ⛽ Mobilitäts- & Spritpreis-Radar (MTS-K / Tankerkönig)<br>• BWWP SG-Ready Steuerung (Boost 60°C & Verdichterschutz) | Senior Control Eng.<br>Fullstack Eng. | 125 PT<br>*(~6,2 PM)* | 100.000 € – 125.000 € | 150.000 € – 190.000 € |
| **4. KI-Forecasts, ML-Lastgänge & Anomalieerkennung**<br>• 96h Hybrid Physics + ML PV-Ertragsprognose (Open-Meteo)<br>• Haushalts-Lastprognose & Netto-Überschuss<br>• 7-Tage Auto-ML Baseline (Predictive Maintenance)<br>• Smarte EPEX-Ladefenster & Peak-Shaving Analyse | Senior ML Engineer<br>Data Scientist | 70 PT<br>*(~3,5 PM)* | 58.000 € – 75.000 € | 88.000 € – 115.000 € |
| **5. Energy Sharing, Virtueller Summenzähler & § 42b EnWG**<br>• 15-Minuten NAP-Bilanzierung & Resiliente Ingestion<br>• 3 Allokationsmodelle (Dynamisch, Statisch, Hybrid)<br>• Discovergy/inexogy wMSB REST Hub & Tarife<br>• Rechtssichere Monatsabrechnungen (.pdf, .xlsx, .csv, .xml) | Senior FinTech Eng.<br>Regulatory Energy Eng. | 140 PT<br>*(~7,0 PM)* | 115.000 € – 148.000 € | 170.000 € – 225.000 € |
| **6. § 14a EnWG CLS SMGW Gateway & Netzdrosselung**<br>• BSI TR-03109-1 CLS Ingest API & FNN Steuerbox Quittierung<br>• Dynamisches $4{,}2\,\text{kW}$ Summenbudget & Merit-Order Aktor-Kaskade<br>• Revisionssicheres `EnWG14aDimmingAuditLog` | Senior Energy Telecom Eng.<br>Security Specialist | 65 PT<br>*(~3,2 PM)* | 55.000 € – 72.000 € | 80.000 € – 110.000 € |
| **7. Virtuelles Kraftwerk (VPP) & 80/20 Market Clearing**<br>• Sekundärregelleistung (aFRR/SRL) & FCR Pooling Engine<br>• Connect+ / Redispatch 2.0 96-Viertelstunden-Fahrplan (`PT15M`)<br>• Monetäre Clearing Engine mit 80/20 Split & monatlichen Gutschriften<br>• ÜNB / Aggregator Webhook Interface mit API-Key Auth | Senior FinTech Eng.<br>Grid Specialist | 75 PT<br>*(~3,8 PM)* | 65.000 € – 85.000 € | 95.000 € – 128.000 € |
| **8. Zentraler Dokumenten- & Export-Hub (`/app/documents`)**<br>• Streaming-Generator für DATEV, MSCONS 2.2b, UTILMD, PDF<br>• SHA-256 Hashketten-Validierung & GoBD-Archivierung<br>• Revisionssicheres Prüf-Cockpit | Senior Fullstack Eng.<br>Compliance Specialist | 50 PT<br>*(~2,5 PM)* | 42.000 € – 55.000 € | 62.000 € – 85.000 € |
| **9. Granulare Enterprise RBAC-Matrix & Sidenav-Navigation**<br>• 5 Rollen: SuperAdmin, Dispatcher, Billing, Tech, Auditor<br>• Dynamische Sidenav für EMS, Mieter, Partner & Admins | Senior Fullstack Eng.<br>Frontend Lead | 45 PT<br>*(~2,3 PM)* | 38.000 € – 50.000 € | 55.000 € – 75.000 € |
| **10. Frontend UX, Skeleton-Loading & SWR Caching**<br>• Zero Layout Shift via TanStack Query SWR ($< 20\,\text{ms}$)<br>• Reusable Skeleton-Komponenten & Glassmorphic Dark/Light Mode<br>• ECharts Live-Sankey & Mobile Responsive Drawer/Bottom-Nav | Senior Frontend Eng.<br>UI/UX Designer | 95 PT<br>*(~4,8 PM)* | 75.000 € – 98.000 € | 110.000 € – 145.000 € |
| **11. Native Android App (Capacitor 7) & 6-Sprachen i18n**<br>• Capacitor 7 Native Shell, Fastlane Release Pipeline & FCM Push<br>• Vollständiges i18n für DE, EN, PL, FR, IT, ES mit Auto-Fallback | Senior Mobile Eng.<br>Frontend Eng. | 55 PT<br>*(~2,8 PM)* | 45.000 € – 58.000 € | 65.000 € – 88.000 € |
| **12. Helpcenter 2.0, Handbuch & Dokumentationsportal**<br>• 11 Themen-Kategorien, 46 zweisprachige (DE/EN) Fachartikel<br>• Vollständige Wissensdatenbank & Revisions-Leitfäden | Technical Writer<br>Lead Architect | 60 PT<br>*(~3,0 PM)* | 48.000 € – 62.000 € | 70.000 € – 95.000 € |
| **13. B2B Whitelabeling & Cloudflare Edge CDN Security**<br>• Dynamic CSS Theming, Subdomain Routing, Full Strict SSL<br>• Cloudflare DNSSEC, HSTS, Rate Limiting & WebSockets Anycast | Lead Architect<br>DevOps / Cloud Eng. | 50 PT<br>*(~2,5 PM)* | 42.000 € – 55.000 € | 65.000 € – 90.000 € |
| **14. QA, Testabdeckung, Security & Compliance**<br>• 100% automatisierte Test Suite (180+ Unit- & Integrationstests)<br>• Multi-Tenant Isolation, DSGVO-TOMs, Audit-Logging | QA / Test Engineer<br>Security Specialist | 60 PT<br>*(~3,0 PM)* | 48.000 € – 62.000 € | 70.000 € – 92.000 € |
| **GESAMT-ENTWICKLUNGSAUFWAND** | **Team: 4–6 Experten** | **1.080 PT**<br>*(~54 PM)* | **893.000 € – 1.148.000 €** | **1.295.000 € – 1.713.000 €** |

---

### 1.4 Gesamtfazit der Entwicklungskosten

* **Inhouse-Softwareteam**: Bei Aufbau eines eigenen spezialisierten Entwicklungsteams (4–6 Senior Engineers über eine Laufzeit von **24 Monaten**) belaufen sich die reinen Lohn- und Arbeitgeber-Vollkosten auf **ca. 890.000 € bis 1.150.000 €**.
* **Beauftragung einer Digitalagentur / IT-Dienstleisters**: Bei Vergabe an eine spezialisierte IoT- und Cloud-Agentur im DACH-Raum lägen die Entwicklungskosten bei **ca. 1.295.000 € bis 1.710.000 € netto**.

---

## 💎 Teil 2: Bewertung & Marktwert von Sharegy in €

```
                  ┌─────────────────────────────────────────────────────────┐
                  │              SHAREGY BEWERTUNGSMETHODEN                 │
                  └────────────────────────────┬────────────────────────────┘
                                               │
             ┌─────────────────────────────────┼─────────────────────────────────┐
             ▼                                 ▼                                 ▼
   ┌───────────────────┐             ┌───────────────────┐             ┌───────────────────┐
   │ 1. Substanzwert   │             │ 2. SaaS Multiple  │             │ 3. Strategischer  │
   │ (Cost-to-Duplicate)│            │ (ARR / DCF)       │             │ Transaktionswert  │
   ├───────────────────┤             ├───────────────────┤             ├───────────────────┤
   │ 1.300.000 € –     │             │ 3.200.000 € –     │             │ 3.800.000 € –     │
   │ 1.680.000 €       │             │ 5.200.000 €       │             │ 6.500.000 €       │
   └───────────────────┘             └───────────────────┘             └───────────────────┘
```

---

### 2.1 Methode 1: Substanz- & Wiederbeschaffungswert (Cost-to-Duplicate)

* **Reine Software- & Codebasis (1.080 PT)**: 1.100.000 € – 1.420.000 €
* **Architektur-Know-how & regulatorische Schnittstellen (§ 42b EnWG, § 14a EnWG CLS, VPP aFRR, GoBD)**: 150.000 € – 200.000 €
* **Produktionsreifes Helpcenter & Handbuch (46 Artikel DE/EN)**: 50.000 € – 80.000 €
* 👉 **Substanzwert (Minimum Asset Value)**: **1.300.000 € – 1.680.000 €**

---

### 2.2 Methode 2: SaaS-Ertragswert & Multiple-Verfahren (Markt-Bewertung)

#### Erlöspotenzial-Modellierung (Konservatives Szenario Jahr 1–2):
1. **Säule 1: EMS Pro (B2C / Prosumer)**:
   * 4.000 Pro-Abonnenten à 7,99 € / Monat = **~320.000 € ARR**
2. **Säule 2: Energy Sharing Communities & Quartiere (B2B)**:
   * 35 Energiegenossenschaften / WEGs mit je 30 Zählern (1.050 Zähler à 10 € / Monat) = **126.000 € ARR**
   * Transaktions-/Clearing-Fee (0,5 Cent / geteilte kWh bei 8 GWh Durchsatz) = **40.000 € p.a.**
3. **Säule 3: VPP Flexibilitäts-Aggregation & 80/20 Clearing**:
   * 600 aggregierte Heimspeicher & Wärmepumpen (20% Plattform-Marge aus Regelleistung) = **60.000 € ARR**
4. **Gesamter ARR-Ansatz**: **ca. 546.000 € ARR**

#### Bewertung über Green-Tech SaaS Multiples (8x bis 12x ARR):
* Konservativ (8x ARR): `546.000 € × 8` = **~4.368.000 €**
* Moderat (10x ARR): `546.000 € × 10` = **~5.460.000 €**
* 👉 **SaaS-Marktwert (Jahr 1–2 Traktion)**: **3,2 Mio. € – 5,2 Mio. €**

---

### 2.3 Methode 3: Strategischer Wert / M&A-Transaktionswert (Corporate Acquirer)

Für strategische Käufer (Stadtwerke, große Energieversorger wie E.ON, EnBW, Vattenfall oder Hardware-Konzerne wie Sungrow, Shelly, SMA, Viessmann) repräsentiert Sharegy:
* **Time-to-Market Vorteil**: 24 Monate Vorsprung gegenüber Inhouse-Neuentwicklungen.
* **Dual-Core Synergie**: Einzige Plattform im Markt, die privates HEMS mit § 42b EnWG Quartiersabrechnung, § 14a CLS SMGW Drosselung und VPP-Regelleistung vereint.
* 👉 **Strategischer M&A-Transaktionswert**: **3,8 Mio. € – 6,5 Mio. €**

---

## 📊 Zusammenfassende Bewertungsmatrix

| Bewertungsansatz | Zweck & Zielgruppe | Wertansatz (€) |
|---|---|:---:|
| **1. Substanzwert (Cost-to-Duplicate)** | Basis für Bilanzierung, Asset-Verkauf & Mindestabsicherung | **ca. 1,30 Mio. € – 1,68 Mio. €** |
| **2. SaaS-Unternehmensbewertung (Early Growth)** | Seed- / Series-A Finanzierungsrunden mit VCs & Business Angels | **ca. 3,20 Mio. € – 5,20 Mio. €** |
| **3. Strategischer M&A-Unternehmenswert** | Strategische Übernahme / Buy-out durch Stadtwerk, EVU oder Hardware-Konzern | **ca. 3,80 Mio. € – 6,50 Mio. €** |
