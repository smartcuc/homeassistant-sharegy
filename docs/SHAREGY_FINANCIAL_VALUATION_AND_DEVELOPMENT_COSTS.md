# 💰 Sharegy: Finanzielle Bewertung, Entwicklungskosten & Unternehmenswert

**Dokument-Version**: 1.0  
**Stand**: September 2026  
**Erstellt für**: Geschäftsführung, Gesellschafter, Investoren & Banken / Förderstellen  
**Autor**: Antigravity Principal Engineering & Strategy Review  

---

## Executive Summary

Dieses Dokument liefert eine fundierte, methodisch saubere und marktkonforme finanzielle Bewertung von **Sharegy**:
1. **Detaillierte Schätzung der herkömmlichen Entwicklungskosten**: Was hätte die Entwicklung von Sharegy bei klassischer Vorgehensweise (Inhouse-Softwareteam oder professionelle Digital-Agentur im DACH-Raum) real gekostet?
2. **Bezifferung des aktuellen Unternehmenswerts (Asset- & strategische Bewertung)**: Welchen monetären Wert repräsentiert die Plattform heute auf Basis von Substanzwert (Cost-to-Duplicate), SaaS-Markt-Multiples und strategischem M&A-Akquisitionswert für Energieversorger (EVU), Stadtwerke und Hardwarehersteller?

---

## 🏗️ Teil 1: Geschätzte Entwicklungskosten bei herkömmlicher Entwicklung

### 1.1 Projektumfang & Technologische Komplexität

Sharegy ist keine einfache CRUD-Webanwendung, sondern eine **hochkomplexe, verteilte Dual-Core Energieplattform** mit:
* **Echtzeit-Telemetrie & Sub-Sekunden Streaming** (TimescaleDB Hypertables, Continuous Aggregates, Redis Live-Buffer, Daphne WebSockets).
* **Multi-Protokoll IoT-Gateway** (Outbound-WSS für Shelly Gen2/Gen3/Pro, OCPP 1.6-J CSMS Wallbox-Server, MQTT-Broker, OpenTelemetry OTel, Modbus, ioBroker Adapter & Home Assistant Component).
* **Smart Load Management & Dispatch Engine** (Live Power Budget, 4 Autopilot-Modi, Merit-Order Kaskade, 24h Dispatch-Timeline, BWWP SG-Ready Steuerung mit Verdichter-Taktschutz, Sungrow Cloud OpenAPI Inverter Arbitrage).
* **Machine Learning & Hybrid-Physics Engines** (48h PV-Ertragsprognose mit Open-Meteo 96h Strahlungsmodell, Haushalts-Lastprognose, 7-Tage Auto-ML Baseline Predictive Maintenance).
* **Gesetzliches Energy Sharing & Clearing (§ 42b EnWG)** (15-Minuten OBIS-Bilanzierung, wMSB Discovergy/inexogy REST Hub, 3 Allokationsmodelle, automatische Monatsabrechnungen mit rechtssicheren PDF-, Excel-, CSV- und ERP-XML-Exporten).
* **Modernes Frontend & Native Apps** (React SPA, ECharts Live-Sankey, i18n DE/EN/PL, Support-Desk mit FAQ-Deflection, Capacitor 7 Android App & W3C Web-Push).

---

### 1.2 Aufwands- & Rollen-Kalkulation (Personenmonate & Tagessätze)

*Basis für die Kalkulation sind übliche DACH-Marktsätze (Deutschland/Österreich/Schweiz) im Bereich Energy-Tech, Cloud Architecture und Data Engineering:*
* **Senior Software Engineer / Architekt**: Tagessatz 1.100 € – 1.400 € (Inhouse-Vollkosten: ca. 110.000 € – 135.000 € p.a.)
* **Senior Data & ML Specialist**: Tagessatz 1.200 € – 1.500 € (Inhouse-Vollkosten: ca. 120.000 € – 145.000 € p.a.)
* **Frontend / UI-UX Lead**: Tagessatz 950 € – 1.250 € (Inhouse-Vollkosten: ca. 95.000 € – 115.000 € p.a.)
* **QA / Test Engineer / Security**: Tagessatz 900 € – 1.150 € (Inhouse-Vollkosten: ca. 85.000 € – 105.000 € p.a.)
* **Lead Architect / Product Owner**: Tagessatz 1.300 € – 1.600 € (Inhouse-Vollkosten: ca. 130.000 € – 160.000 € p.a.)

---

### 1.3 Detaillierte Modul-Aufwandsschätzung

| Entwicklungsmodul | Benötigte Rollen | Aufwand (PT) | Inhouse-Kosten (€) | Agentur-Kosten (€) |
|---|---|:---:|:---:|:---:|
| **1. Backend & Data Pipeline**<br>• TimescaleDB Hypertables & Continuous Aggregates<br>• Redis Live-Buffer & Deadband-Filter<br>• Daphne ASGI WebSocket Server & Celery Priority Queues | Senior Backend Eng.<br>DevOps / DBA | 85 PT<br>*(~4,5 PM)* | 65.000 € – 80.000 € | 95.000 € – 125.000 € |
| **2. IoT-Gateways & Protokolle**<br>• Outbound WSS Shelly Ingest (Gen2/Gen3)<br>• OCPP 1.6-J CSMS Wallbox Gateway & Smart Charging<br>• Offizieller ioBroker Adapter & Home Assistant HACS<br>• Globaler MQTT-Hub & OpenTelemetry OTel | Senior IoT Engineer<br>Senior Backend Eng. | 90 PT<br>*(~4,5 PM)* | 70.000 € – 88.000 € | 105.000 € – 135.000 € |
| **3. Smart Load Hub, BWWP & Aktorik**<br>• Dispatch Hub (`/app/control`) & Live Power Budget<br>• 1-Klick Quick-Boost (11 kW Wallbox, 100% Notstromreserve)<br>• Merit-Order Prioritäten-Kaskade & 24h Fahrplan<br>• BWWP SG-Ready Steuerung & Verdichter-Taktschutz<br>• Sungrow Cloud OpenAPI Inverter Arbitrage | Senior Control Eng.<br>Fullstack Engineer | 85 PT<br>*(~4,2 PM)* | 66.000 € – 83.000 € | 95.000 € – 128.000 € |
| **4. KI-Forecasts & Anomalieerkennung**<br>• 48h Hybrid Physics + ML PV-Ertragsprognose<br>• Haushalts-Lastprognose & Netto-Überschuss<br>• 7-Tage Auto-ML Baseline (Predictive Maintenance)<br>• Smarte EPEX-Ladefenster & Peak-Shaving Analyse | Senior ML Engineer<br>Data Scientist | 65 PT<br>*(~3,2 PM)* | 52.000 € – 68.000 € | 78.000 € – 105.000 € |
| **5. Säule 2: Energy Sharing & Clearing**<br>• 15-Minuten OBIS-Bilanzierung & Resiliente Ingestion<br>• 3 Allokationsmodelle (§ 42b EnWG: Dyn, Stat, Hyb)<br>• Discovergy/inexogy wMSB REST Hub & Tarife<br>• PDF-, Excel-, CSV- & ERP-XML-Abrechnungsengine | Senior FinTech Eng.<br>Regulatory Energy Eng. | 110 PT<br>*(~5,5 PM)* | 88.000 € – 115.000 € | 130.000 € – 175.000 € |
| **6. Frontend UI/UX, Sankey & Native Apps**<br>• Responsive React SPA mit Live-Pulse Ticker & Dark/Light Theme<br>• Multistring AC-Erkennung (2. Wechselrichter / BKW)<br>• Capacitor 7 Android App & W3C Web-Push VAPID<br>• Multi-Language i18n (DE, EN, PL) & Support-Desk | Senior Frontend Eng.<br>Mobile App Eng.<br>UI/UX Designer | 100 PT<br>*(~5,0 PM)* | 76.000 € – 97.000 € | 110.000 € – 148.000 € |
| **7. QA, Testabdeckung, Security & Compliance**<br>• 100% automatisierte Test Suite (30 Unit- & Integrationstests)<br>• Multi-Tenant RBAC, Audit-Logging & DSGVO-Consent<br>• System-Health-Monitoring Engine & Auto-Watchdog | QA / Test Engineer<br>Security Specialist | 50 PT<br>*(~2,5 PM)* | 38.000 € – 50.000 € | 55.000 € – 75.000 € |
| **8. Architektur, Projektleitung & Regulatory**<br>• Technische Gesamtarchitektur & Systemdesign<br>• BNetzA / § 42b EnWG / MsbG Normenabgleich<br>• Handbuch- & Dokumentationserstellung (15 Artikel) | Lead Architect<br>Product Owner | 60 PT<br>*(~3,0 PM)* | 55.000 € – 72.000 € | 80.000 € – 110.000 € |
| **GESAMT-ENTWICKLUNGSAUFWAND** | **Team: 4–6 Experten** | **645 PT**<br>*(~33 PM)* | **510.000 € – 653.000 €** | **748.000 € – 1.001.000 €** |

---

### 1.4 Gesamtfazit der Entwicklungskosten

* **Inhouse-Softwareteam**: Bei Aufbau eines eigenen spezialisierten Entwicklungsteams (4–6 Senior Engineers über eine Laufzeit von **14 bis 18 Monaten**) belaufen sich die reinen Lohn- und Arbeitgeber-Vollkosten auf **ca. 500.000 € bis 650.000 €**.
* **Beauftragung einer Digitalagentur / IT-Dienstleisters**: Bei Vergabe an eine spezialisierte IoT- und Cloud-Agentur im DACH-Raum (inkl. Agentur-Marge, PM-Overhead und Risikopuffer) lägen die Entwicklungskosten bei **ca. 750.000 € bis 1.000.000 € netto**.

---

## 💎 Teil 2: Bewertung & Marktwert von Sharegy in €

Zur Ermittlung des Unternehmens- und Asset-Werts werden in der Praxis drei anerkannte Bewertungsmethoden herangezogen:

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
   │ 650.000 € –       │             │ 1.800.000 € –     │             │ 2.500.000 € –     │
   │ 950.000 €         │             │ 3.500.000 €       │             │ 4.500.000 €       │
   └───────────────────┘             └───────────────────┘             └───────────────────┘
```

---

### 2.1 Methode 1: Substanz- & Wiederbeschaffungswert (Cost-to-Duplicate)
Der Substanzwert bewertet den Wert des geistigen Eigentums (IP), des Source-Codes, der Architektur und der Dokumentation, wenn ein Dritter diesen Stand heute exakt nachbauen müsste.

* **Reine Software- & Codebasis (635 PT)**: 650.000 € – 850.000 €
* **Architektur-Know-how & regulatorische Schnittstellen (§ 42b EnWG, OBIS, wMSB)**: 75.000 € – 100.000 €
* **Produktionsreife Dokumentation & Wissensportal (15 Artikel DE/EN)**: 25.000 € – 35.000 €
* 👉 **Substanzwert (Minimum Asset Value)**: **750.000 € – 985.000 €**

---

### 2.2 Methode 2: SaaS-Ertragswert & Multiple-Verfahren (Markt-Bewertung)
Im Bereich Green-Tech SaaS und Energy Management (B2C Prosumer + B2B Energy Sharing) werden Wachstums-Multiples auf Basis des jährlich wiederkehrenden Umsatzes (**ARR - Annual Recurring Revenue**) angewendet.

#### Erlöspotenzial-Modellierung (Konservatives Szenario Jahr 1–2):
1. **Säule 1: EMS Pro (B2C / Prosumer)**:
   * 3.000 Pro-Abonnenten à 4,99 € / Monat = **179.640 € ARR**
2. **Säule 2: Energy Sharing Communities & Quartiere (B2B)**:
   * 20 Energiegenossenschaften / WEGs mit durchschnittlich 35 Zählern (700 Zähler à 10 € / Monat Zähler-Clearing) = **84.000 € ARR**
   * Transaktions-/Clearing-Fee (0,5 Cent / geteilte kWh bei 5 GWh Durchsatz) = **25.000 € p.a.**
3. **Gesamter ARR-Ansatz**: **ca. 288.640 € ARR**

#### Bewertung über Green-Tech SaaS Multiples:
* Im europäischen Energy-Tech Sektor liegen SaaS-Multiples für hochgradig skalierbare Cloud-Plattformen (Software-Only, Zero-Lock-in) typischerweise bei **8x bis 14x ARR**:
  * Konservativ (8x ARR): `288.640 € × 8` = **~2.300.000 €**
  * Moderat (11x ARR): `288.640 € × 11` = **~3.175.000 €**
* 👉 **SaaS-Marktwert (Jahr 1–2 Traktion)**: **2,3 Mio. € – 3,2 Mio. €**

---

### 2.3 Methode 3: Strategischer Wert / M&A-Transaktionswert (Corporate Acquirer)
Für strategische Käufer (Stadtwerke, große Energieversorger wie E.ON, EnBW, Vattenfall oder Hardware-Konzerne wie Sungrow, Shelly, SMA, Viessmann) hat Sharegy einen deutlich höheren Wert als der reine Ertragswert:

1. **Massiver Time-to-Market Vorteil (18–24 Monate Vorsprung)**:
   * Ein Energieversorger spart 1,5 bis 2 Jahre Entwicklungszeit, um ein marktfertiges Energy-Sharing Produkt nach § 42b EnWG anzubieten.
2. **Eliminierung von Entwicklungs- und Team-Risiken**:
   * Das System ist bereits erprobt, architektonisch gehärtet und umfasst offizielle Integrationen für ioBroker, Home Assistant, Shelly, Sungrow und wMSB (Discovergy).
3. **Verhinderung von Kundenabwanderung (Churn-Reduction)**:
   * EVUs können ihren Prosumern ein modernes EMS und Quartiers-Sharing unter eigener Marke (White-Label) anbieten.
* 👉 **Strategischer M&A-Transaktionswert**: **2,5 Mio. € – 4,5 Mio. €**

---

## 📊 Zusammenfassende Bewertungsmatrix

| Bewertungsansatz | Zweck & Zielgruppe | Wertansatz (€) |
|---|---|:---:|
| **1. Substanzwert (Cost-to-Duplicate)** | Basis für Bilanzierung, Asset-Verkauf & Mindestabsicherung | **ca. 750.000 € – 985.000 €** |
| **2. SaaS-Unternehmensbewertung (Early Growth)** | Seed- / Series-A Finanzierungsrunden mit VCs & Business Angels | **ca. 2,0 Mio. € – 3,2 Mio. €** |
| **3. Strategischer M&A-Unternehmenswert** | Strategische Übernahme / Buy-out durch Stadtwerk, EVU oder Hardware-Konzern | **ca. 2,5 Mio. € – 4,5 Mio. €** |

---

## 🎯 Strategisches Gesamtfazit

1. **Hohe Entwicklungseffizienz**: Die Plattform repräsentiert einen realen Entwicklungsgegenwert von über **750.000 €**, der softwareseitig in herausragender Qualität und mit modernstem Architektur-Stack umgesetzt wurde.
2. **Solider Sockelwert**: Sharegy hat als reine Software-Asset-Basis bereits heute einen unverhandelbaren Mindestwert von **~800.000 €**.
3. **Hebel durch Markteintritt**: Sobald die ersten 1.000 bis 3.000 Prosumer und 10 bis 20 Quartiere auf der Plattform aktiv sind, liegt der faire Unternehmenswert bei **2,5 bis 3,5 Millionen Euro**.
