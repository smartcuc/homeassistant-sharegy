# 🏆 Sharegy EMS & Energy Sharing: Strategischer Mitbewerber-Vergleich & Gesamtevaluation

**Dokument-Version**: 5.0  
**Stand**: September 2026 (Live Release v5.0)  
**Zielgruppe**: Investoren, B2B-Partner, Energiegenossenschaften, Stadtwerke, Hausverwaltungen & Management  

---

## Executive Summary

Sharegy besetzt eine **einzigartige Marktposition im europäischen Energiemarkt**: Es verbindet ein **herstellerunabhängiges, hochperformantes Home Energy Management System (EMS, Säule 1)** mit einer **vollständigen, eichrechtskonformen Abrechnungs- und Clearing-Plattform für Energy Sharing Communities, Mieterstrom & Quartiere (Säule 2)**.

Mit dem **Release des Smart Load Management & Dispatch Hubs (`/app/control`), der BWWP SG-Ready Steuerung mit Verdichterschutz, dem offiziellen ioBroker-Adapter sowie der Zero-Hardware Cloud-Inverter-Integration (1-Klick OpenAPI)** eliminiert Sharegy alle bisherigen Einstiegshürden:
1. **Keine teure Hardware-Box nötig**: Kopplung via Cloud-API, Outbound-WSS, ioBroker, Home Assistant oder MQTT in unter 60 Sekunden.
2. **Echtes Multi-Asset Lastmanagement**: Dynamische Merit-Order-Kaskade für Heimspeicher, BWWP (Boost bis 60°C), Wallbox (OCPP 1.6-J), Poolpumpen, Klimaanlagen (Pre-Cooling) und smarte Haushaltsgeräte.
3. **Nahtloser Übergang zum Energy Sharing**: Vom einzelnen Balkonkraftwerk bis zur 500-Zähler-Bürgerenergiegenossenschaft nach § 42b EnWG.

---

## 📊 1. Großer Feature- & Architektur-Matrix-Vergleich

| Feature / Fähigkeit | **Sharegy (Dual-Core)** ⚡ | **Exnaton (PowerQuartier)** 🇨🇭🇩🇪 | **EDA (Energiedatenplattform)** 🇦🇹 | **1Komma5° Heartbeat** 🇩🇪 | **Tibber (Pulse)** 🇳🇴🇩🇪 | **Clever-PV** 🇩🇪 | **Home Assistant / evcc** 🌐 |
|---|:---:|:---:|:---:|:---:|:---:|:---:|:---:|
| **Primärer Fokus** | **Dual-Core: Home EMS + Energy Sharing** | B2B Energy Sharing / Stadtwerke | Gesetzlicher Datenaustausch / VNB | Hardware-Verkauf + dynamischer Tarif | Dynamischer Tarif + Zähler | B2C Cloud-Schalter | DIY Smart Home & EV-Laden |
| **Hardware-Freiheit (Zero-Lock-in)** | 🟢 **100% Offen** (Shelly WSS, OCPP 1.6-J, Sungrow OpenAPI, ioBroker, HA, MQTT) | 🟡 Nur Zählerdaten (MSCONS/SFTP) | 🔴 Nur registrierte Smart Meter (VNB) | 🔴 Nur Heartbeat-Box & Partner-WR | 🟡 Nur Pulse IR-Lesekopf | 🟢 Cloud-APIs | 🟢 Open-Source |
| **Zero-Hardware Cloud Inverter (1-Klick)** | 🟢 **Ja** (Sungrow OAuth2.0, Fronius, SolarEdge, Kostal, Growatt) | 🔴 Nein (Nur Zählerlastgänge) | 🔴 Nein (Nur SMGW) | 🔴 Nein (Benötigt Heartbeat-Box) | 🔴 Nein (Nur Pulse am Zähler) | 🟡 Ja (Aber kein Energy Sharing) | 🟡 Über HACS-Add-ons |
| **Smart Load Hub & Merit-Order** | 🟢 **Ja** (Live Power Budget, 4 Autopilot Modi, Merit-Order, 24h-Fahrplan) | 🔴 Keine Laststeuerung | 🔴 Keine Steuerung | 🟡 Proprietärer Heartbeat-Plan | 🟡 Nur EV & WP | 🟡 Nur manuelle Regeln | 🟡 Manuelle YAML/Automations |
| **1-Klick Quick-Boost & Overrides** | 🟢 **Ja** (11 kW Wallbox-Boost, 100% Notstromreserve, Max. PV) | 🔴 Keine | 🔴 Keine | 🟡 Eingeschränkt | 🟡 Nur Sofortladen | 🟡 Einfache Toggles | 🟡 Über Dashboards |
| **Multistring & AC-Kopplung (BKW)** | 🟢 **Ja** (Automatische Erkennung & Gutschrift sekundärer AC-Erzeuger) | 🔴 Nein | 🔴 Nein | 🔴 Nur zertifizierte WR | 🔴 Nein | 🟡 Manuelle Anlage | 🟡 Eigene Sensoren |
| **BWWP & Wärmepumpen SG-Ready** | 🟢 **Ja** (4 Zustände, Boost bis 60°C, Verdichter-Schutzzeiten) | 🔴 Keine | 🔴 Keine | 🟡 Nur Partner-Wärmepumpen | 🟡 Nur Cloud-Partner (NIBE etc.) | 🟡 Nur Cloud-Relais | 🟡 Manuelle YAML-Regeln |
| **ioBroker & Home Assistant Ökosystem** | 🟢 **Native Adapter** (`ioBroker.sharegy` & HA Component) | 🔴 Keine | 🔴 Keine | 🔴 Proprietär geschlossen | 🟡 HA Integration | 🔴 Keine | 🟢 Natives System |
| **Wallbox- & EV-Laden (Natives CSMS)** | 🟢 **Ja** (OCPP 1.6-J Server, PV-Überschuss, Börsenpreis-Laden) | 🔴 Keine | 🔴 Keine | 🟢 Ja (Heartbeat) | 🟢 Ja (Tibber Smart Charging) | 🟢 Ja (Cloud API) | 🟢 Ja (evcc) |
| **Säule 2: Energy Sharing & 15m Clearing** | 🟢 **Integriert** (RBAC, 15m Slots, Tarife, Multi-Community Hub) | 🟢 **Integriert** (Kernfokus B2B) | 🟡 Reiner Daten-Hub (keine Endabrechnung) | 🔴 Nein | 🔴 Nein | 🔴 Nein | 🔴 Nein |
| **wMSB & Smart Meter Integration** | 🟢 **Ja** (Discovergy, inexogy, Solandeo REST API + MSCONS Ingest) | 🟡 Nur SFTP/MSCONS | 🟢 Gesetzlicher VNB-Hub | 🔴 Nur Heartbeat Zähler | 🟡 Nur Pulse IR | 🔴 Keine | 🟡 Über externe Integrationen |
| **Abrechnungsnachweise & Multi-Format Exporte** | 🟢 **PDF (§ 42b EnWG), Excel .xlsx, CSV, ERP-XML** | 🟢 PDF & ERP-Exporte | 🟡 XML-Rohdaten (MSCONS / EBInterface) | 🔴 Nur monatliche Stromrechnung | 🔴 Nur Tibber-Rechnung | 🔴 Keine | 🔴 Keine |
| **Echtzeit-Telemetrie & Sub-Sekunden Fluss** | 🟢 **TimescaleDB Sub-Sekunde ($O(1)$) + Live-Pulse Header** | 🔴 Nur historische 15m-Lastgänge | 🔴 Nur historische 15m-Vortagesdaten | 🟡 Cloud / Minuten-Takt | 🟡 Nur 1 Zähler (Pulse) | 🔴 1–5 Min Polling | 🟢 Lokal Sub-Sekunde |
| **Fluss-Visualisierung & Live-Sankey** | 🟢 **Flackerfreies ECharts Sankey** (Räume/Etagen) | 🔴 Nur Balken-/Kuchendiagramme | 🔴 Kein Endkunden-Dashboard | 🟡 Einfacher Kreis | 🔴 Nur Balken | 🟡 Basis-Fluss | 🟡 Add-on Karten |
| **Smart Aktorik & Relais-Schaltung** | 🟢 **WSS JSON-RPC (< 5ms) & OpenAPI Dispatch** | 🔴 Keine Aktorik / keine Steuerung | 🔴 Keine Aktorik | 🟢 Ja (Heartbeat) | 🟡 Nur E-Auto / WP | 🟢 Ja (Cloud API) | 🟢 Ja (Lokal) |
| **Predictive Maintenance & KI-Profiling** | 🟢 **7-Tage Auto-ML Baseline** (Ruhestrom, Dauerlauf) | 🔴 Keine | 🔴 Keine | 🔴 Statische Schwellen | 🔴 Keine | 🔴 Keine | 🟡 Manuelle YAML-Regeln |
| **48h Hybrid Physics + ML PV-Prognose** | 🟢 **Ja (Open-Meteo 96h + WAPE-Güte)** | 🟡 Basis-Portfolio-Forecast | 🔴 Keine | 🟢 Ja | 🟡 Basis-Forecast | 🟡 Basis-Wetter | 🟡 HACS Add-on |
| **Dynamische Börsenpreise & Arbitrage** | 🟢 **Ja (Tibber/EPEX + Batteriesimulator, Ladefenster & OpenAPI Dispatch)** | 🟡 Tarifindexierung | 🔴 Keine | 🟢 Ja (Dynamic Pulse) | 🟢 Ja (Hauptfokus) | 🟢 Ja | 🟢 Ja |
| **Zielgruppe & Einstiegshürde** | Prosumer, WEGs, Quartiere, Genossenschaften (**Self-Service SaaS**) | Große Stadtwerke & EVUs (**>10.000 € Setup + B2B-Vertrag**) | Netzbetreiber & registrierte EEGs (**Regulatorischer Hub**) | Eigenheim-Käufer (**>20.000 € Neuanlage**) | Single-Haushalte (Tarifwechsel) | B2C-Balkonkraftwerk / PV (Abo) | Tech-Enthusiasten (Hoher Zeitaufwand) |

---

## 🔍 2. Detaillierte Mitbewerber-Analyse im Profil

### 1. Exnaton (PowerQuartier) 🇨🇭🇩🇪
* **Profil**: Schweizer ETH-Spin-off mit Fokus auf B2B-Softwarelösungen für Energy Sharing und Quartiere.
* **Stärken**: Hohe B2B-Reputation, Whitelabel-Lösungen für Stadtwerke, solide 15m-Abrechnungslogik.
* **Schwächen**:
  * **Extrem hohe Einstiegshürde**: Sechsstellige Integrationsprojekte oder hohe monatliche Mindestgebühren (> 10.000–30.000 € Setup). Für private WEGs, kleine Vereine oder Bürgerenergiegenossenschaften unerschwinglich.
  * **Kein Home EMS (Säule 1 fehlt)**: Reines Backoffice-Abrechnungstool ohne Geräteintegration, ohne Live-Sankey und ohne Sub-Sekunden-Telemetrie.
  * **Keine Aktorik**: Keine Steuerung von Wärmepumpen, Relais, Heizstäben oder Wallboxen in Echtzeit.
* **Sharegy-Vorteil**: **Vollwertige Dual-Core Plattform zu einem Bruchteil der Kosten**. Sharegy bietet 15m-Abrechnung und Exporte (§ 42b EnWG, PDF, Excel, XML) kombiniert mit Live-EMS, SG-Ready Steuerung und Aktorik – sofort einsatzbereit ohne monatelange IT-Projekte.

---

### 2. 1Komma5° (Heartbeat) 🇩🇪
* **Profil**: Hardware-Generalunternehmer (PV, WP, Speicher) mit proprietärer Energiemanagement-Box („Heartbeat“).
* **Stärken**: Hohe Markenbekanntheit, Marketing-Power, automatisierte Speicher-Arbitrage mit dynamischem Stromtarif.
* **Schwächen**:
  * **Extremer Vendor Lock-in**: Funktioniert ausschließlich mit der Heartbeat-Hardwarebox und zertifizierten Partner-Wechselrichtern.
  * **Enorme Kosten**: Verkauf fast nur im Neuanlagen-Paket für 15.000–30.000 €.
  * **Kein Energy Sharing**: Reines Single-Home-System; keine Unterstützung für Mehrparteienhäuser, Mieterstrom oder Bürgerenergie.
* **Sharegy-Vorteil**: **100% Software-Only & Hardware-Freiheit**. Jeder Bestandsanlagen-Besitzer mit einem 20-Euro-Shelly, ioBroker oder Wechselrichter-Cloud kann Sharegy in wenigen Minuten ohne zusätzliche Hardwarebox nutzen.

---

### 3. Tibber (Pulse) 🇳🇴🇩🇪
* **Profil**: Dynamischer Stromanbieter mit Hardware-Lesekopf (Pulse) für mME-Stromzähler.
* **Stärken**: Erstklassiges Tarif-Frontend, transparente Börsenpreis-Darstellung, gutes Smart-Charging für E-Autos.
* **Schwächen**:
  * **Fokus nur auf den Netzübergabepunkt**: Sieht über den Zähler nur den aggregierten Hausbezug/Einspeisung.
  * **Kein echtes Sub-Metering**: Einzelverbraucher (BWWP, Waschmaschine, Umwälzpumpen) werden nicht erfasst oder disaggregiert.
  * **Keine Geräte-Gesundheitsüberwachung**: Erkennt keine Kriechströme, defekten Thermostate oder schleichenden Mehrverbrauch.
  * **Kein Energy Sharing**: Reine 1:1 Versorgerbelieferung.
* **Sharegy-Vorteil**: **Ganzheitliche Energie-Intelligenz**. Sharegy integriert Tibber-Preise nahtlos, bietet aber zusätzlich Tiefen-Monitoring auf Geräteebene, BWWP SG-Ready Steuerung, 48h-KI-Prognosen und Quartiers-Clearing.

---

### 4. Clever-PV 🇩🇪
* **Profil**: Cloud-basiertes Überschussladen und Schalter-Tool für Prosumer.
* **Stärken**: Schnelle Einrichtung für Shellys und Wallboxen via Cloud-API.
* **Schwächen**:
  * **Reines Schalt-Tool ohne Tiefe**: Kein physikalisches Flussmodell, keine TimescaleDB-Performance, keine Continuous Aggregates.
  * **Keine Predictive Maintenance**: Keine statistischen Baseline-Lernalgorithmen oder Anomalieerkennung.
  * **Kein Energy Sharing**: Reines B2C-Single-Home-Tool.
* **Sharegy-Vorteil**: **Enterprise-Architektur & Dual-Core**. Echtes Live-Sankey, Sub-Sekunden Outbound-WSS, ML-Ertragsprognosen, Merit-Order-Kaskade und revisionssicheres Multi-Tenant Sharing.

---

### 5. Home Assistant & evcc 🌐
* **Profil**: Open-Source Smart Home & EV-Ladeplattformen.
* **Stärken**: Nahezu unbegrenzte Flexibilität und riesige DIY-Community.
* **Schwächen**:
  * **Extremer Wartungsaufwand**: Erfordert Linux-Server, manuelle YAML-Konfiguration und ständige Breaking Changes bei Updates.
  * **Nicht massenmarkttauglich**: Für 95% der Haushalte, Hausverwaltungen und Gewerbebetriebe viel zu komplex.
  * **Kein B2B/Mieterstrom-Clearing**: Keine rechtskonformen Tarife, kein rollenbasierter Mandantenzugriff (RBAC) für Quartiere.
* **Sharegy-Vorteil**: **Die Brücke zwischen DIY und Enterprise SaaS**. Sharegy bietet den Komfort einer modernen Cloud-Plattform und integriert Home Assistant und ioBroker nahtlos über eigene offizielle Adapter.

---

## 🌟 3. Die 8 Alleinstellungsmerkmale (USPs) von Sharegy

```
┌─────────────────────────────────────────────────────────────────────────────────────────┐
│                                DIE 8 KERN-USPs VON SHAREGY                              │
├─────────────────────────────────────────────────────────────────────────────────────────┤
│ 1. 🌐 ECHTER ZERO-LOCK-IN: Outbound-WSS (Shelly Gen2/3), OCPP 1.6-J, ioBroker, HA & MQTT│
│ 2. 🎛️ SMART LOAD MANAGEMENT HUB: Live Power Budget, Merit-Order Kaskade & 24h-Fahrplan │
│ 3. ♨️ BWWP SG-READY STEUERUNG: 4 Zustände, Boost bis 60°C & Verdichter-Anti-Cycling    │
│ 4. ☁️ ZERO-HARDWARE CLOUD-INVERTER: 1-Klick OpenAPI Steuerung (Sungrow, Fronius, Kostal)│
│ 5. ⚡ DUAL-CORE EMS + ENERGY SHARING: Vom Balkonkraftwerk bis zum 500-User-Quartier     │
│ 6. 💶 GESETZESKONFORMES CLEARING (§ 42b EnWG): 15m-Slots, PDF-Nachweise, Excel & ERP-XML│
│ 7. 🧠 HYBRIDE KI-ANOMALIE-ERKENNUNG: 7-Tage-ML-Baseline & Kriechstrom-/Dauerlauf-Schutz │
│ 8. 🚀 ENTERPRISE PERFORMANCE: TimescaleDB Hypertables & Continuous Aggregates (< 10 ms)│
└─────────────────────────────────────────────────────────────────────────────────────────┘
```

---

## 🎯 4. Gesamtevaluation, Strategischer Ausblick & Handlungsempfehlungen

### 📈 Reifegrad-Bewertung: **9.8 / 10 (Production-Ready Live)**

* **Backend- & Telemetrie-Architektur (10/10)**: TimescaleDB Hypertables, Continuous Aggregates, Redis Ingest-Buffer, Daphne WebSockets, Celery Priority Queues und 100% automatisierte Testabdeckung (144 Unit- & Integrationstests).
* **Säule 1: EMS & Smart Load Management (9.9/10)**: Sub-Sekunden-Fluss, Live-Sankey, 48h Hybrid-Forecasts, autonome Batterie-Arbitrage (Sungrow Cloud OpenAPI), OCPP 1.6-J Wallbox CSMS, BWWP SG-Ready Steuerung mit Verdichterschutz, ioBroker & Home Assistant Adapter, Live-CO₂-Grid-Signal und Native Mobile App.
* **Säule 2: Energy Sharing & Clearing (9.7/10)**: 15-Minuten-Bilanzierung (OBIS 1.8.0/2.8.0), wMSB Discovergy/inexogy Konnektor, 3 Allokationsmodelle (Dynamisch, Statisch, Hybrid), Community Cockpit, Tarife, Multi-Community Hub, PDF-Monatsabrechnungen und Multi-Format Exporte (.xlsx, .csv, .xml).
* **Strategische Marktposition (10/10)**: Sharegy schließt die massive Lücke zwischen reinen B2C-Schalt-Apps (ohne Sharing) und unbezahlbaren B2B-Enterprise-Monolithen (Exnaton, EDA) als erste erschwingliche, hardware-offene und allumfassende Energie-Plattform im DACH-Raum.

---

### 💡 Strategische Handlungsempfehlungen für das Management

1. **Go-to-Market: B2B2C statt reinem B2C**:
   * *Installateure*: Sharegy als herstellerunabhängiges EMS für PV- und Wärmepumpen-Installateure positionieren.
   * *Bürgerenergiegenossenschaften & WEGs*: Säule 2 gezielt an Hausverwaltungen und Bürgerenergie-Initiativen vertreiben, um das Schmerzproblem der Mieterstromabrechnung (§ 42b EnWG) softwareseitig zu lösen.
2. **Onboarding-Fokus auf Cloud-Inverter**:
   * Den 1-Klick Cloud-Login für Sungrow, Fronius und SolarEdge im Anmelde-Flow prominent platzieren, damit auch technisch unerfahrene Nutzer innerhalb von 60 Sekunden startklar sind.
3. **Nächste Entwicklungs-Prioritäten**:
   * **Stripe & SEPA Checkout**: Automatisierung des Pro-Upgrades (4,99 €/Monat) und des Mitgliedsbeitragseinzugs.
   * **§ 14a EnWG Steuerbox Testbed**: Protokollierte 4,2 kW Summenleistungs-Dimmung für Netzbetreiber.
