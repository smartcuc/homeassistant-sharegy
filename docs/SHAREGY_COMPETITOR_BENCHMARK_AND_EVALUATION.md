# 🏆 Sharegy EMS & Energy Sharing: Strategischer Mitbewerber-Vergleich & Gesamtevaluation

**Dokument-Version**: 4.0  
**Stand**: 2. September 2026  
**Zielgruppe**: Investoren, Betatester, B2B-Partner, Energiegenossenschaften & Management  

---

## Executive Summary

Sharegy besetzt eine **einzigartige Marktposition im europäischen Energiemarkt**: Es verbindet ein **herstellerunabhängiges, hochperformantes Home Energy Management System (EMS, Säule 1)** mit einer **vollständigen, eichrechtskonformen Abrechnungs- und Clearing-Plattform für Energy Sharing Communities, Mieterstrom & Quartiere (Säule 2)**.

Mit dem **Release der Zero-Hardware Cloud-Inverter-Integration (1-Klick OAuth 2.0 für Sungrow iSolarCloud sowie nativer Cloud-Profile für Fronius Solar.web, SolarEdge, Kostal Solar Portal und Growatt ShineServer)** eliminiert Sharegy die letzte große Einstiegshürde: Jeder Betreiber einer bestehenden PV- und Speicheranlage kann sein System in unter 60 Sekunden ohne zusätzliche Hardware-Boxen oder Elektroinstallationen mit Sharegy koppeln.

Während B2C-Systeme (1Komma5°, Tibber, Clever-PV) reine Einzelhaushalte ohne P2P-Clearing adressieren und B2B-Enterprise-Lösungen (Exnaton, EDA) als schwergewichtige, teure Abrechnungsmonolithe ohne Geräteintegration und ohne Sub-Sekunden-EMS agieren, vereint Sharegy **Zero-Lock-in, TimescaleDB-Echtzeit-Telemetrie, KI-Anomalieerkennung, Aktorik und automatisiertes 15-Minuten Energy Sharing Clearing in einer integrierten Plattform**.

---

## 📊 1. Großer Feature- & Architektur-Matrix-Vergleich

| Feature / Fähigkeit | **Sharegy (Dual-Core)** ⚡ | **Exnaton (PowerQuartier)** 🇨🇭🇩🇪 | **EDA (Energiedatenplattform)** 🇦🇹 | **1Komma5° Heartbeat** 🇩🇪 | **Tibber (Pulse)** 🇳🇴🇩🇪 | **Clever-PV** 🇩🇪 | **Home Assistant / evcc** 🌐 |
|---|:---:|:---:|:---:|:---:|:---:|:---:|:---:|
| **Primärer Fokus** | **Dual-Core: Home EMS + Energy Sharing** | B2B Energy Sharing / Stadtwerke | Gesetzlicher Datenaustausch / VNB | Hardware-Verkauf + dynamischer Tarif | Dynamischer Tarif + Zähler | B2C Cloud-Schalter | DIY Smart Home & EV-Laden |
| **Hardware-Freiheit (Zero-Lock-in)** | 🟢 **100% Offen** (Shelly WSS, OCPP 1.6-J, Sungrow OpenAPI, HA, MQTT) | 🟡 Nur Zählerdaten (MSCONS/SFTP) | 🔴 Nur registrierte Smart Meter (VNB) | 🔴 Nur Heartbeat-Box & Partner-WR | 🟡 Nur Pulse IR-Lesekopf | 🟢 Cloud-APIs | 🟢 Open-Source |
| **Zero-Hardware Cloud Inverter (1-Klick)** | 🟢 **Ja** (Sungrow OAuth2.0, Fronius, SolarEdge, Kostal, Growatt) | 🔴 Nein (Nur Zählerlastgänge) | 🔴 Nein (Nur SMGW) | 🔴 Nein (Benötigt Heartbeat-Box) | 🔴 Nein (Nur Pulse am Zähler) | 🟡 Ja (Aber kein Energy Sharing) | 🟡 Über HACS-Add-ons |
| **Wallbox- & EV-Laden (Natives CSMS)** | 🟢 **Ja** (OCPP 1.6-J Server, PV-Überschuss, Börsenpreis-Laden) | 🔴 Keine | 🔴 Keine | 🟢 Ja (Heartbeat) | 🟢 Ja (Tibber Smart Charging) | 🟢 Ja (Cloud API) | 🟢 Ja (evcc) |
| **Säule 2: Energy Sharing & 15m Clearing** | 🟢 **Integriert** (RBAC, 15m Slots, Tarife, Multi-Community Hub) | 🟢 **Integriert** (Kernfokus B2B) | 🟡 Reiner Daten-Hub (keine Endabrechnung) | 🔴 Nein | 🔴 Nein | 🔴 Nein | 🔴 Nein |
| **wMSB & Smart Meter Integration** | 🟢 **Ja** (Discovergy, inexogy, Solandeo REST API + MSCONS Ingest) | 🟡 Nur SFTP/MSCONS | 🟢 Gesetzlicher VNB-Hub | 🔴 Nur Heartbeat Zähler | 🟡 Nur Pulse IR | 🔴 Keine | 🟡 Über externe Integrationen |
| **Abrechnungsnachweise & Multi-Format Exporte** | 🟢 **PDF (§ 42b EnWG), Excel .xlsx, CSV, ERP-XML** | 🟢 PDF & ERP-Exporte | 🟡 XML-Rohdaten (MSCONS / EBInterface) | 🔴 Nur monatliche Stromrechnung | 🔴 Nur Tibber-Rechnung | 🔴 Keine | 🔴 Keine |
| **Echtzeit-Telemetrie & Sub-Sekunden Fluss** | 🟢 **TimescaleDB Sub-Sekunde ($O(1)$)** | 🔴 Nur historische 15m-Lastgänge | 🔴 Nur historische 15m-Vortagesdaten | 🟡 Cloud / Minuten-Takt | 🟡 Nur 1 Zähler (Pulse) | 🔴 1–5 Min Polling | 🟢 Lokal Sub-Sekunde |
| **Fluss-Visualisierung & Live-Sankey** | 🟢 **Flackerfreies ECharts Sankey** (Räume/Etagen) | 🔴 Nur Balken-/Kuchendiagramme | 🔴 Kein Endkunden-Dashboard | 🟡 Einfacher Kreis | 🔴 Nur Balken | 🟡 Basis-Fluss | 🟡 Add-on Karten |
| **Smart Aktorik & Relais-Schaltung** | 🟢 **WSS JSON-RPC (< 5ms) & OpenAPI Dispatch** | 🔴 Keine Aktorik / keine Steuerung | 🔴 Keine Aktorik | 🟢 Ja (Heartbeat) | 🟡 Nur E-Auto / WP | 🟢 Ja (Cloud API) | 🟢 Ja (Lokal) |
| **Predictive Maintenance & KI-Profiling** | 🟢 **7-Tage Auto-ML Baseline** (Ruhestrom, Dauerlauf) | 🔴 Keine | 🔴 Keine | 🔴 Statische Schwellen | 🔴 Keine | 🔴 Keine | 🟡 Manuelle YAML-Regeln |
| **48h Hybrid Physics + ML PV-Prognose** | 🟢 **Ja (Open-Meteo 96h + WAPE-Güte)** | 🟡 Basis-Portfolio-Forecast | 🔴 Keine | 🟢 Ja | 🟡 Basis-Forecast | 🟡 Basis-Wetter | 🟡 HACS Add-on |
| **Dynamische Börsenpreise & Arbitrage** | 🟢 **Ja (Tibber/EPEX + Batteriesimulator & OpenAPI Dispatch)** | 🟡 Tarifindexierung | 🔴 Keine | 🟢 Ja (Dynamic Pulse) | 🟢 Ja (Hauptfokus) | 🟢 Ja | 🟢 Ja |
| **Zielgruppe & Anschaffungskosten** | Prosumer, WEGs, Quartiere, Genossenschaften (**Self-Service SaaS**) | Große Stadtwerke & EVUs (**>10.000 € Setup + B2B-Vertrag**) | Netzbetreiber & registrierte EEGs (**Regulatorischer Hub**) | Eigenheim-Käufer (**>20.000 € Neuanlage**) | Single-Haushalte (Tarifwechsel) | B2C-Balkonkraftwerk / PV (Abo) | Tech-Enthusiasten (Hoher Zeitaufwand) |


---

## 🔍 2. Detaillierte Mitbewerber-Analyse im Profil

---

### 1. Exnaton (PowerQuartier)
* **Profil**: Schweizer ETH-Spin-off mit Fokus auf B2B-Softwarelösungen für Energy Sharing, Eigenverbrauchsgemeinschaften (ZEV in der Schweiz, EEG in Österreich, Energy Sharing nach § 42b EnWG in Deutschland).
* **Geschäftsmodell**: Enterprise B2B SaaS für Stadtwerke, Energieversorger (EVUs) und große Immobilienentwickler.
* **Stärken**:
  * Starke regulatorische Verankerung im B2B-Sektor und Whitelabel-Fähigkeit für Stadtwerke.
  * Solide Berechnungslogik für 15-Minuten-Lastgänge und Quartiersabrechnungen.
* **Schwächen & Lücken**:
  * **Extrem hohe Einstiegshürde & Kosten**: Erfordert sechsstellige Integrationsprojekte oder hohe monatliche Mindestgebühren (> 10.000–30.000 € Setup). Für kleine Genossenschaften, Bürgerenergie-Vereine oder private Mehrparteienhäuser (WEGs) unbezahlbar.
  * **Kein Home EMS (Säule 1 fehlt)**: Exnaton ist ein reines Backoffice-Abrechnungstool. Es hat **keine Geräte-Integration** im Haushalt (kein Shelly, kein Matter, kein Home Assistant), keine Sub-Sekunden-Telemetrie und kein Live-Sankey.
  * **Keine Aktorik & Gerätesteuerung**: Exnaton kann keine Wärmepumpen, Heizstäbe, Relais oder Wallboxen in Echtzeit schalten oder netzdienlich abriegeln.
  * **Reines Batch-System**: Daten werden meist nur einmal täglich (D+1) über SFTP/MSCONS importiert; keine Echtzeit-Transparenz für Mieter oder Anlagenbetreiber.
* **Sharegy-Vorteil**: **Ganzheitliche Dual-Core Plattform zu einem Bruchteil der Kosten**. Sharegy bietet die vollwertige 15m-Abrechnung und Exporte (§ 42b EnWG, PDF, Excel, XML) *kombiniert* mit vollwertigem Live-EMS, Aktorik und Submetering. Sofortige Inbetriebnahme ohne mehrmonatige Consulting-Projekte.

---

### 2. EDA (Energiedatenplattform Österreich / Energy Data Exchange)
* **Profil**: Zentrale österreichische Datenaustauschplattform (betrieben von APCS / Verteilnetzbetreibern) zur Abwicklung von Marktprozessen und Übergabe von 15-Minuten-Smart-Meter-Messwerten an Erneuerbare-Energie-Gemeinschaften (EEG/GEG).
* **Geschäftsmodell**: Gesetzlich mandatierte Infrastrukturplattform zur Marktkommunikation (EBInterface, MSCONS, REST/SFTP).
* **Stärken**:
  * Offizieller Datenkanal für österreichische Netzbetreiber und gesetzlich zertifizierte Zählerdaten.
  * Standardisierte Übermittlung von Viertelstundenwerten für Zuweisungs- und Verrechnungsmodelle.
* **Schwächen & Lücken**:
  * **Kein Endkunden-Produkt**: EDA ist eine reine Daten-Drehscheibe (Clearing-Infrastruktur) und bietet kein modernes, benutzerfreundliches Endkunden-Dashboard oder Cockpit.
  * **Keine automatische Rechnungsstellung / Clearing-Auszahlung**: EDA liefert nur Messwerte, erstellt aber keine Endkunden-Rechnungen, PDF-Nachweise mit USt-Ausweis oder Multi-Format-Exporte für Steuerberater/Hausverwaltungen.
  * **Kein Home EMS & keine Steuerung**: Keine PV-Ertragsprognosen, kein Batteriemanagement, keine Steuerung steuerbarer Lasten (§ 14a EnWG), keine Echtzeit-Flussdaten.
* **Sharegy-Vorteil**: **Das fehlende Anwendungs- & Cockpit-Layer**. Sharegy fungiert als moderne Intelligenz- und Visualisierungsplattform, die Daten aus Plattformen wie EDA (oder deutschen Smart Meter Gateways / wMSB) aufnimmt, centgenau abrechnet, visualisiert und mit Aktorik und Prognosen anreichert.

---

### 3. 1Komma5° (Heartbeat)
* **Geschäftsmodell**: Hardware-Verkauf (PV, WP, Speicher) + proprietäres Energiemanagement („Heartbeat“).
* **Stärken**: Hohe Markenbekanntheit, Marketing-Power, automatisierte Speicher-Arbitrage mit eigenem dynamischen Tarif.
* **Schwächen**:
  * **Extremer Vendor Lock-in**: Funktioniert nur mit kompatiblen, zertifizierten Wechselrichtern und der Heartbeat-Hardwarebox.
  * **Sehr hohe Einstiegshürde**: Installation meist nur im Paket bei Neuanlagen für 15.000–30.000 €.
  * **Kein Energy Sharing**: Reines Eigenheim-System, keine Unterstützung für Mehrparteienhäuser, Mieterstrom oder Bürgerenergiegenossenschaften.
* **Sharegy-Vorteil**: **Software-Only & Hardware-agnostisch**. Jeder Bestandsanlagen-Besitzer mit einem 20-Euro-Shelly oder Home Assistant kann Sharegy in 3 Minuten nutzen.

---

### 4. Tibber (Pulse)
* **Geschäftsmodell**: Dynamischer Stromtarif + Hardware-Zusatzgeschäft (Pulse IR-Lesekopf).
* **Stärken**: Exzellentes Tarif-Frontend, transparente Börsenpreis-Darstellung, starke Smart-Charging-Funktion für E-Autos.
* **Schwächen**:
  * **Fokus nur auf den Netzübergabepunkt**: Tibber sieht über den Pulse nur den Gesamtnetzbezug/Einspeisung am Zähler.
  * **Kein echtes Sub-Metering**: Einzelverbraucher (Wärmepumpe, BWWP, Waschmaschine, Server, Kühlschrank) können nicht disaggregiert visualisiert oder überwacht werden.
  * **Keine Geräte-Gesundheitsüberwachung**: Erkennt keine defekten Thermostate, Kriechströme oder schleichende Verbrauchssteigerungen.
  * **Kein Energy Sharing**: Reine 1:1 Belieferung vom Versorger zum Haushalt.
* **Sharegy-Vorteil**: **Ganzheitliche Energie-Intelligenz**. Sharegy integriert Tibber-Preise nahtlos, bietet aber zusätzlich Tiefen-Monitoring auf Raum-/Geräteebene, PV-ML-Prognosen und KI-Anomalieerkennung.

---

### 5. Clever-PV / SolarPlus
* **Geschäftsmodell**: Cloud-basiertes Überschussladen und Relais-Schaltung für Prosumer.
* **Stärken**: Schnelle Einrichtung für Shellys und Wallboxen per Cloud-API.
* **Schwächen**:
  * **Reines Schalt-Tool ohne Tiefe**: Kein physikalisches Flussmodell, keine Continuous Aggregates oder TimescaleDB-Performance.
  * **Keine Predictive Maintenance**: Keine statistischen Baseline-Lernalgorithmen.
  * **Kein Energy Sharing (Säule 2)**: Reines B2C-Single-Home-Tool.
* **Sharegy-Vorteil**: **Enterprise-Architektur**. Echtes Live-Sankey, Sub-Sekunden-Reaktionszeiten via Outbound-WSS, ML-Ertragsprognosen und revisionssicheres Multi-Tenant-Sharing.

---

### 6. Home Assistant / evcc
* **Geschäftsmodell**: Open-Source / Do-It-Yourself.
* **Stärken**: Nahezu unbegrenzte Konfigurierbarkeit und gigantische Community.
* **Schwächen**:
  * **Massiver Wartungsaufwand**: Erfordert Linux-Server, manuelle YAML-Konfiguration, ständige Breaking Changes bei Updates.
  * **Nicht massenmarkttauglich**: Für 95% der Haushalte, Hausverwaltungen und Gewerbebetriebe viel zu komplex.
  * **Keine B2B/Mieterstrom-Abrechnung**: Keine integrierten Tarife, kein rollenbasierter Mandantenzugriff (RBAC) für Quartiere.
* **Sharegy-Vorteil**: **Die goldene Brücke**. Sharegy bietet den Komfort einer modernen Cloud-SaaS mit der Mächtigkeit von Home Assistant (inkl. eigener offizieller HA Custom Component).

---

## 🌟 3. Die 7 Alleinstellungsmerkmale (USPs) von Sharegy

```
┌─────────────────────────────────────────────────────────────────────────────────────────┐
│                                DIE 7 KERN-USPs VON SHAREGY                              │
├─────────────────────────────────────────────────────────────────────────────────────────┤
│ 1. 🌐 ECHTER ZERO-LOCK-IN: Outbound-WSS (Shelly Gen2/3), OCPP 1.6-J, HA & MQTT          │
│ 2. ☁️ ZERO-HARDWARE CLOUD-INVERTER: 1-Klick OAuth & OpenAPI Steuerung (Sungrow, Fronius)│
│ 3. ⚡ DUAL-CORE EMS + ENERGY SHARING: Vom Balkonkraftwerk bis zum 500-User-Quartier     │
│ 4. 💶 GESETZESKONFORMES CLEARING (§ 42b EnWG): 15m-Slots, PDF-Nachweise, Excel & ERP-XML│
│ 5. 🧠 HYBRIDE KI-ANOMALIE-ERKENNUNG: 7-Tage-ML-Baseline & Kriechstrom-/Dauerlauf-Schutz │
│ 6. 🚀 ENTERPRISE PERFORMANCE: TimescaleDB Hypertables & Continuous Aggregates (< 10 ms)│
│ 7. ☀️ HYBRID PHYSICS + ML FORECAST: 48h Solar- & Lastprognose mit WAPE-Güteprüfung      │
└─────────────────────────────────────────────────────────────────────────────────────────┘
```


---

## 🎯 4. Gesamtevaluation & Fazit

### 📈 Reifegrad-Bewertung: **9.7 / 10 (Production-Ready Live)**

* **Backend- & Telemetrie-Architektur (10/10)**: TimescaleDB Hypertables, Continuous Aggregates, Redis Ingest-Buffer, Daphne WebSockets, Celery Priority Queues und vollständige Testabdeckung.
* **Säule 1: EMS-Funktionalität (9.9/10)**: Sub-Sekunden-Fluss, Live-Sankey, 48h Hybrid-Forecasts, autonome Batterie-Arbitrage (Sungrow Cloud OpenAPI), OCPP 1.6-J Wallbox CSMS, Live-CO₂-Grid-Signal, Aktorik via WSS JSON-RPC und Native Mobile App.
* **Säule 2: Energy Sharing & Clearing (9.6/10)**: 15-Minuten-Bilanzierung (OBIS 1.8.0/2.8.0), wMSB Discovergy/inexogy Konnektor, Resiliente Late Ingestion, Community Cockpit, Tarife, Multi-Community Hub, PDF-Monatsabrechnungen und Multi-Format Exporte (.xlsx, .csv, .xml).
* **Strategische Marktposition (10/10)**: Sharegy schließt die massive Lücke zwischen reinen B2C-Schalt-Apps (ohne Sharing) und unbezahlbaren B2B-Enterprise-Monolithen (Exnaton, EDA) als erste erschwingliche, hardware-offene und allumfassende Energie-Plattform im DACH-Raum.

---
*Erstellt durch das Sharegy Product & Engineering Team.*
