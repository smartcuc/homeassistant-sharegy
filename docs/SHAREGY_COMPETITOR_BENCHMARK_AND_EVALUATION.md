# 🏆 Sharegy EMS: Strategischer Mitbewerber-Vergleich & Gesamtevaluation

**Dokument-Version**: 3.2  
**Stand**: 30. August 2026  
**Zielgruppe**: Investoren, Betatester, B2B-Partner & Management  

---

## Executive Summary

Sharegy besetzt eine **einzigartige Marktposition**: Es verbindet ein **herstellerunabhängiges, hochperformantes Home Energy Management System (EMS, Säule 1)** mit einer **skalierbaren Plattform für Energy Sharing Communities & Mieterstrom (Säule 2)**.

Während etablierte Player (z. B. 1Komma5°, Sonnen) auf teure, geschlossene Hardware-Ökosysteme setzen und reine Tarif-Apps (z. B. Tibber) lediglich den Hauptzähler visualisieren, bietet Sharegy **Zero-Lock-in, Millisekunden-Telemetrie via TimescaleDB, KI-gestützte Predictive Maintenance & automatisches P2P-Clearing**.

---

## 📊 1. Großer Feature- & Architektur-Matrix-Vergleich

| Feature / Fähigkeit | **Sharegy EMS** ⚡ | **1Komma5° Heartbeat** | **Tibber (Pulse)** | **Sonnen (SonnenFlat)** | **Clever-PV** | **Home Assistant / evcc** | **Hersteller-Portale (SMA, Sungrow)** |
|---|:---:|:---:|:---:|:---:|:---:|:---:|:---:|
| **Hardware-Freiheit (Zero-Lock-in)** | 🟢 **100% Offen** (Shelly WSS, Home Assistant, MQTT, OTel) | 🔴 Nur eigene Heartbeat-Box | 🟡 Nur Pulse IR-Kopf | 🔴 Nur SonnenBatterie | 🟢 Cloud-APIs | 🟢 Open-Source | 🔴 Proprietäres Silo |
| **Säule 2: Energy Sharing & Mieterstrom (P2P)** | 🟢 **Integriert** (RBAC, Audit, 15-Min-Clearing) | 🔴 Nein | 🔴 Nein | 🟡 Nur interne Sonnen-Community | 🔴 Nein | 🔴 Nein | 🔴 Nein |
| **Echtzeit-Telemetrie & Flussvektoren** | 🟢 **TimescaleDB Sub-Sekunde** | 🟡 Cloud / Minuten-Takt | 🟡 Nur 1 Zähler | 🟡 Minuten-Takt | 🔴 1–5 Min Polling | 🟢 Lokal Sub-Sekunde | 🔴 5–15 Min Cloud-Verzögerung |
| **Fluss-Visualisierung & Sankey** | 🟢 **Flackerfreies ECharts Sankey** (Etagen/Räume) | 🟡 Einfacher Flusskreis | 🔴 Nur Balkendiagramm | 🟡 Einfacher Kreis | 🟡 Basis-Fluss | 🟡 Add-on Karten | 🟡 Statische Grafiken |
| **KI-Anomalie-Erkennung & Profiling** | 🟢 **7-Tage Auto-ML Baseline** (Ruhestrom, Dauerlauf) | 🔴 Statische Schwellen | 🔴 Keine | 🔴 Keine | 🔴 Keine | 🟡 Manuelle YAML-Regeln | 🔴 Nur Fehlercodes |
| **48h Hybrid Physics + ML PV-Prognose** | 🟢 **Ja (Open-Meteo 96h + WAPE-Güte)** | 🟢 Ja | 🟡 Basis-Forecast | 🟡 Ja | 🟡 Basis-Wetter | 🟡 Nur per HACS-Add-on | 🟡 Basis-Schätzung |
| **Dynamische Börsenpreise & Arbitrage** | 🟢 **Ja (Tibber/EPEX + Batteriesimulation)** | 🟢 Ja (Dynamic Pulse) | 🟢 Ja (Hauptfokus) | 🟡 Nur intern | 🟢 Ja | 🟢 Ja | 🔴 Meist nicht unterstützt |
| **Sub-Metering & Restlast-Disaggregation** | 🟢 **Ja ($E_{\text{residual}} = E_{\text{Haus}} - \sum E_i$)** | 🔴 Nein | 🔴 Nein | 🔴 Nein | 🟡 Manuell | 🟡 Manuell | 🔴 Nein |
| **Bidirektionale Aktorik & Relais** | 🟢 **WSS JSON-RPC + UI Toggles** | 🟢 Ja | 🟡 Nur E-Auto / WP | 🟢 Ja | 🟢 Ja | 🟢 Ja | 🔴 Nur eigene Relais |
| **Outbound WebSocket Ingestion (DAU-sicher)** | 🟢 **Ja (`wss://sharegy.de/ws/energy/`)** | 🔴 Nein | 🔴 Nein | 🔴 Nein | 🔴 Nein | 🟡 Teilweise | 🔴 Nein |
| **Einrichtungsaufwand für Endanwender** | 🟢 **Extrem gering (Shelly Outbound WSS / HA)** | 🔴 Elektriker erforderlich (>3.000 €) | 🟢 Gering (Zählerkopf) | 🔴 Teure Fachinstallation | 🟢 Gering | 🔴 Extrem hoch (YAML, Linux, Wartung) | 🟡 Gering (nur eigener WR) |

---

## 🔍 2. Detaillierte Mitbewerber-Analyse

### 1. 1Komma5° (Heartbeat)
* **Geschäftsmodell**: Hardware-Verkauf (PV, WP, Speicher) + proprietäres Energiemanagement („Heartbeat“).
* **Stärken**: Hohe Markenbekanntheit, Marketing-Power, automatisierte Speicher-Arbitrage mit eigenem dynamischen Tarif.
* **Schwächen**:
  * **Extremer Vendor Lock-in**: Funktioniert nur mit kompatiblen, zertifizierten Wechselrichtern und der Heartbeat-Hardwarebox.
  * **Sehr hohe Einstiegshürde**: Installation meist nur im Paket bei Neuanlagen für 15.000–30.000 €.
  * **Kein Energy Sharing**: Reines Eigenheim-System, keine Unterstützung für Mehrparteienhäuser, Mieterstrom oder Bürgerenergiegenossenschaften.
* **Sharegy-Vorteil**: **Software-Only & Hardware-agnostisch**. Jeder Bestandsanlagen-Besitzer mit einem 20-Euro-Shelly oder Home Assistant kann Sharegy in 3 Minuten nutzen.


---

### 2. Tibber (Pulse)
* **Geschäftsmodell**: Dynamischer Stromtarif + Hardware-Zusatzgeschäft (Pulse IR-Lesekopf).
* **Stärken**: Exzellentes Tarif-Frontend, transparente Börsenpreis-Darstellung, starke Smart-Charging-Funktion für E-Autos.
* **Schwächen**:
  * **Fokus nur auf den Netzübergabepunkt**: Tibber sieht über den Pulse nur den Gesamtnetzbezug/Einspeisung am Zähler.
  * **Kein echtes Sub-Metering**: Einzelverbraucher (Wärmepumpe, BWWP, Waschmaschine, Server, Kühlschrank) können nicht disaggregiert visualisiert oder überwacht werden.
  * **Keine Geräte-Gesundheitsüberwachung**: Erkennt keine defekten Thermostate, Kriechströme oder schleichende Verbrauchssteigerungen.
* **Sharegy-Vorteil**: **Ganzheitliche Energie-Intelligenz**. Sharegy integriert Tibber-Preise nahtlos, bietet aber zusätzlich Tiefen-Monitoring auf Raum-/Geräteebene, PV-ML-Prognosen und KI-Anomalieerkennung.

---

### 3. Clever-PV / SolarPlus
* **Geschäftsmodell**: Cloud-basiertes Überschussladen und Relais-Schaltung für Prosumer.
* **Stärken**: Schnelle Einrichtung für Shellys und Wallboxen per Cloud-API.
* **Schwächen**:
  * **Reines Schalt-Tool ohne Tiefe**: Kein physikalisches Flussmodell, keine Continuous Aggregates oder TimescaleDB-Performance.
  * **Keine Predictive Maintenance**: Keine statistischen Baseline-Lernalgorithmen.
  * **Kein Energy Sharing (Säule 2)**: Reines B2C-Single-Home-Tool.
* **Sharegy-Vorteil**: **Enterprise-Architektur**. Echtes Live-Sankey, Sub-Sekunden-Reaktionszeiten via Outbound-WSS, ML-Ertragsprognosen und revisionssicheres Multi-Tenant-Sharing.

---

### 4. Home Assistant / evcc
* **Geschäftsmodell**: Open-Source / Do-It-Yourself.
* **Stärken**: Nahezu unbegrenzte Konfigurierbarkeit und gigantische Community.
* **Schwächen**:
  * **Massiver Wartungsaufwand**: Erfordert Linux-Server, manuelle YAML-Konfiguration, ständige Breaking Changes bei Updates.
  * **Nicht massenmarkttauglich**: Für 95% der Haushalte, Hausverwaltungen und Gewerbebetriebe viel zu komplex.
  * **Keine B2B/Mieterstrom-Abrechnung**: Keine integrierten Tarife, kein rollenbasierter Mandantenzugriff (RBAC) für Quartiere.
* **Sharegy-Vorteil**: **Die goldene Brücke**. Sharegy bietet den Komfort einer modernen Cloud-SaaS mit der Mächtigkeit von Home Assistant (inkl. eigener offizieller HA Custom Component).

---

## 🌟 3. Die 6 Alleinstellungsmerkmale (USPs) von Sharegy EMS

```
┌─────────────────────────────────────────────────────────────────────────────────────────┐
│                                DIE 6 KERN-USPs VON SHAREGY                              │
├─────────────────────────────────────────────────────────────────────────────────────────┤
│ 1. 🌐 ECHTER ZERO-LOCK-IN: Outbound-WSS (Shelly Gen2/3), Home Assistant & MQTT          │
│ 2. ⚡ DUAL-CORE EMS + ENERGY SHARING: Vom Balkonkraftwerk bis zur 500-User-Genossenschaft│
│ 3. 🧠 HYBRIDE KI-ANOMALIE-ERKENNUNG: 7-Tage-ML-Baseline & Kriechstrom-/Dauerlauf-Schutz │
│ 4. 🚀 ENTERPRISE PERFORMANCE: TimescaleDB Hypertables & Continuous Aggregates (< 10 ms)│
│ 5. ☀️ HYBRID PHYSICS + ML FORECAST: 48h Solar- & Lastprognose mit WAPE-Güteprüfung      │
│ 6. 💶 AUTOMATISIERTE BATTERIE-ARBITRAGE: Netzdienliches Laden bei Negativ-Börsenpreisen │
└─────────────────────────────────────────────────────────────────────────────────────────┘

```

---

## 🎯 4. Gesamtevaluation & Fazit

### 📈 Reifegrad-Bewertung: **9.4 / 10 (Production-Ready)**
* **Backend-Architektur (10/10)**: TimescaleDB, Redis-Caching, Daphne WebSocket-Layer, Celery Background Worker und Sentry Error Tracking garantieren höchste Ausfallsicherheit und minimale Latenz.
* **Feature-Vollständigkeit Säule 1 (9.5/10)**: Alle Kernfunktionen eines modernen Home EMS (Monitoring, Forecasting, Arbitrage, Aktorik, Live-Sankey, PDF/Excel-Reporting, KI-Profiling) sind produktiv implementiert und durch automatisierte Test-Suiten abgedeckt.
* **Wettbewerbspositionierung (9.5/10)**: Durch den Verzicht auf proprietäre Hardware und den dualen Ansatz (Home EMS + Energy Sharing) ist Sharegy sowohl für Privatkunden als auch für Energiegenossenschaften und Mieterstromprojekte im DACH-Raum konkurrenzlos flexibel.

---
*Erstellt durch das Sharegy Product & Engineering Team.*
