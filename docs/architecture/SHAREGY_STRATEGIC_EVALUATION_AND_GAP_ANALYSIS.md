# 🎯 Sharegy: Strategische Gesamtevaluation, Schwachstellen-Analyse & Gap-Matrix

**Dokument-Version**: 5.4  
**Stand**: 19. September 2026 (Live Release v5.4)  
**Erstellt von**: Antigravity Principal Engineering & Product Strategy  
**Zielgruppe**: Geschäftsführung, Gesellschafter, Beirat & Produkt-Management  

---

## 🧭 Executive Summary

Sharegy befindet sich mit dem **Live-Release v5.4** an einem entscheidenden strategischen Wendepunkt:
Die Software ist technologisch und architektonisch fertig, gehärtet, getestet und vereint als **erste Plattform in Europa** ein herstellerunabhängiges **Home Energy Management System (EMS, Säule 1)** mit gesetzeskonformem **Energy Sharing & Quartiers-Clearing (§ 42b EnWG, Säule 2)**, integrierter **BNetzA CLS § 14a Netzdrosselung**, **VPP 80/20 Regelleistungs-Vermarktung** und **GoBD-konformem Dokumenten-Hub**.

Dieses Dokument liefert eine **ungeschminkte, ehrliche und schonungslose Analyse**:
1. **Wo Sharegy heute absolute Weltklasse und dem Markt voraus ist.**
2. **Wo wir noch echte Schwachstellen und operationelle Risiken haben.**
3. **Wo der Mitbewerb aktuell noch die Nase vorn hat (und warum).**
4. **Den konkreten, priorisierten Masterplan für 2026/2027, um Marktführer zu werden.**

---

## 🟢 1. Wo Sharegy absolute Weltklasse & dem Markt voraus ist

```
┌─────────────────────────────────────────────────────────────────────────────────────────┐
│                               DIE 8 KERN-SPITZENLEISTUNGEN                              │
├─────────────────────────────────────────────────────────────────────────────────────────┤
│ 1. ⚡ ECHTE DUAL-CORE PLATTFORM: EMS (Prosumer) + Energy Sharing (Quartiere) + VPP      │
│ 2. 🚀 UNERREICHTE TELEMETRIE-PERFORMANCE: TimescaleDB Hypertables & $O(1)$ Live-Cache   │
│ 3. 🛡️ BNETZA CLS § 14a GATEWAY: BSI TR-03109-1 Ingest & FNN Steuerbox-Quittierung       │
│ 4. 📈 VPP REGELENERGIE & 80/20 CLEARING: aFRR/SRL Pooling & automatisierte Gutschriften │
│ 5. 📁 GOBD DOKUMENTEN- & EXPORT-HUB: DATEV-, MSCONS 2.2b- & PDF-Streaming Exporte       │
│ 6. 🔑 GRANULARE ENTERPRISE RBAC-MATRIX: 5 Rollen für Großkunden, Dispatcher & Auditoren │
│ 7. ⏳ SKELETON-LOADING & SWR UX: Ladezeitfreie Navigation ($< 20\,\text{ms}$)           │
│ 8. 🌐 MAXIMALER ZERO-LOCK-IN: 10 Inverter-Clouds, Outbound-WSS, OCPP 1.6-J, ioBroker, HA│
└─────────────────────────────────────────────────────────────────────────────────────────┘
```

### 1.1 Die Dual-Core Architektur (Säule 1 + Säule 2 + VPP)
* **Alleinstellungsmerkmal**: Auf dem europäischen Markt existiert keine einzige Plattform, die ein vollwertiges B2C-Smart-Home-EMS mit rechtssicherem B2B-Quartiersclearing (§ 42b EnWG) und VPP-Regelleistung vereint.
* **Markt-Lücke geschlossen**: Prosumer nutzen Sharegy im Eigenheim für 7,99 €/Monat. Schließt sich dieselbe Liegenschaft einer WEG oder Bürgerenergiegenossenschaft an, bucht dieselbe Plattform nahtlos das 15-Minuten-Clearing nach § 42b EnWG ab und vermarktet Speicher-Flexibilitäten am Regelenergiemarkt.

### 1.2 Datenbank- & Abfrage-Performance
* **TimescaleDB Hypertables & Continuous Aggregates**: Selbst bei Hunderten Millionen Messpunkten laden Dashboards, Jahresbilanzen und Lastgänge in $< 20\,\text{ms}$.
* **$O(1)$ Snapshot-Tabelle (`DeviceLatestMetric`)**: Vermeidet Tabellenscans auf historischen Zeitreihen; der Live-Fluss im Header (`Live-Pulse`) aktualisiert sich flackerfrei in Sub-Sekunden.

### 1.3 § 14a EnWG CLS SMGW Gateway & Netzdrosselung
* **BSI TR-03109-1 Konformität**: Empfang und Quittierung von Dimm-Befehlen über den CLS-Kanal mit FNN Steuerbox-Dispatch-Quittierung.
* **Dynamisches Summenleistungs-Modell**: $P_{\text{allow}} = 4{,}2\,\text{kW} (\text{Netz}) + P_{\text{PV}} + P_{\text{Batt}} - P_{\text{Base}}$, wodurch der Wohn- und Ladekomfort trotz Netzdrosselung voll erhalten bleibt.

### 1.4 Virtuelles Kraftwerk (VPP) & 80/20 Erlös-Clearing
* **Regelleistungsmärkte**: Sekundärregelleistung (aFRR/SRL) und FCR mit 96-Viertelstunden-Fahrplänen.
* **Faires Erlösmodell**: 80 % der Erlöse fließen automatisch als Gutschrift an den Kunden, 20 % verbleiben als Plattform-Marge.

### 1.5 Zentraler GoBD-Dokumenten-Hub & Granulare RBAC-Matrix
* **Revisionssicherheit**: Zentraler Download-Hub (`/app/documents`) mit DATEV-Buchungsstapeln, BNetzA MSCONS 2.2b Zeitreihen und SHA-256 Hashketten-Prüfung.
* **Rollenisolation**: 5 dedizierte Profile (`SuperAdmin`, `Dispatcher`, `Billing Specialist`, `Field Technician`, `Auditor / Read-Only`).

---

## 🔴 2. Die schonungslose Schwachstellen-Analyse (Wo wir noch Defizite haben)

Trotz herausragender Softwarequalität hat Sharegy aktuell **4 verbleibende operative Baustellen**, die für die Skalierung gelöst werden müssen:

---

### ⚠️ Baustelle A: Lokale Offline-Resilienz (Edge Daemon)
* **Das Problem**: Sharegy arbeitet aktuell als cloudbasierte SaaS-Plattform. Aktoren (Shellys, Relais, Wallboxen) werden über Cloud-APIs oder Outbound-WSS geschaltet.
* **Die Schwachstelle**: Bricht beim Kunden die Internetverbindung ab, wird in dieser Zeit kein Lastfahrplan ausgeführt.
* **Lösung**: Entwicklung eines leichtgewichtigen **Sharegy Local Edge Daemon** (Go/Rust/Docker für Raspberry Pi / Home Assistant), der 24h-Fahrpläne lokal cacht und bei Netzausfall autonom regelt.

---

### ⚠️ Baustelle B: App-Store-Präsenz & Mobile Widgets
* **Das Problem**: Die mobile App ist als Capacitor 7 Shell gebaut und kompiliert, aber noch nicht im Apple App Store und Google Play Store öffentlich gelistet.
* **Die Schwachstelle**: Es fehlen iOS Live-Activities (z. B. Live-Ladefortschritt des E-Autos auf dem Sperrbildschirm) und Apple Watch / WearOS Komplikationen.
* **Lösung**: Finales Einreichen im Google Play Store & Apple App Store sowie Implementierung nativer Widget-Plugins.

---

### ⚠️ Baustelle C: Smart Meter Hardware-Flaschenhals in Deutschland
* **Das Problem**: Für die eichrechtskonforme Säule 2 (§ 42b EnWG) wird ein Smart Meter Gateway (iMSys) oder ein wMSB (Discovergy/inexogy) benötigt. Der deutsche Rollout verläuft jedoch schleppend.
* **Lösung**: 1-Klick Setup für günstige WLAN-Infrarot-Leseköpfe (Hichi / Tasmota für ca. 25–40 €), um alte digitale Zähler (mME) ohne Zählertausch sofort im Sekundentakt einzubinden.

---

### ⚠️ Baustelle D: B2B2C Vertriebsskalierung & Markenbekanntheit
* **Das Problem**: Wettbewerber wie 1Komma5° investieren zweistellige Millionenbeträge in Werbung.
* **Lösung**: Fokus auf **B2B2C Hebel**: Freie Solar- und Wärmepumpen-Installateure, Hausverwaltungen (WEGs) und Stadtwerke, die Sharegy ihren Kunden als schlüsselfertige Lösung mitgeben.

---

## 📊 3. SWOT-Matrix im Überblick

```
┌──────────────────────────────────────────────┬──────────────────────────────────────────────┐
│ 🟢 STÄRKEN (STRENGTHS)                       │ 🔴 SCHWÄCHEN (WEAKNESSES)                    │
├──────────────────────────────────────────────┼──────────────────────────────────────────────┤
│ • Einzige Dual-Core Plattform (EMS+Sharing)  │ • Reine Cloud-Aktorik (noch kein Edge Daemon)│
│ • TimescaleDB Sub-Sekunden-Performance       │ • Apps noch nicht in Store-Verzeichnissen   │
│ • § 14a CLS SMGW Gateway & VPP 80/20 Clearing│ • Keine eigene Zähler-Hardware               │
│ • Zentraler GoBD Dokumenten- & Export-Hub    │ • Geringere Markenbekanntheit als 1Komma5°   │
│ • 100% Zero-Lock-in & 10 Inverter-Clouds     │                                              │
├──────────────────────────────────────────────┼──────────────────────────────────────────────┤
│ 🔵 CHANCEN (OPPORTUNITIES)                   │ 🟡 RISIKEN (THREATS)                         │
├──────────────────────────────────────────────┼──────────────────────────────────────────────┤
│ • Gesetzlicher Zwang zu § 14a EnWG Drosselung│ • Zögerlicher Smart-Meter-Rollout in DE      │
│ • Boom von § 42b EnWG Bürgerenergie & WEGs   │ • Preiskampf durch kapitalstarke Anbieter    │
│ • B2B2C-Vertrieb über freie Installateure    │ • API-Restriktionen durch Inverter-Hersteller│
│ • White-Label Partnerschaften mit Stadtwerken│                                              │
└──────────────────────────────────────────────┴──────────────────────────────────────────────┘
```

---

## 🚀 4. Der strategische 3-Stufen-Wachstumsplan (2026 / 2027)

```
┌───────────────────────────────────────────────────────────────────────────────┐
│ STUFE 1: MONETARISIERUNG & B2B2C-HEBEL (Q4 2026)                              │
│ • Installateur-Portal: White-Label Dashboard für Solarteure & Elektriker      │
│ • B2B-Offensive: 20 Bürgerenergiegenossenschaften & WEGs für Säule 2 gewinnen │
│ • App Store & Play Store Live-Release der nativen Apps                        │
│                                                                               │
│ STUFE 2: HARDWARE- & OFFLINE-RESILIENZ (Q1–Q2 2027)                           │
│ • Sharegy Edge Daemon (Offline-First Dispatch für Raspberry Pi / HA)          │
│ • 1-Klick Ingestion für Infrarot-Leseköpfe (Hichi / Tasmota)                  │
│ • EEBUS & Cloud API Bridge für herstellerunabhängige Wärmepumpen-Kopplung    │
│                                                                               │
│ STUFE 3: INSTITUTIONELLE SKALIERUNG & B2B-CLEARING (Q3–Q4 2027)               │
│ • White-Label AS4 Marktkommunikations-Partnerschaft für EVUs & Stadtwerke     │
│ • Ausbau auf 10.000 Pro-Haushalte und 100 Quartiere                           │
│ • Bewertung von 5,0 Mio. €+ für Series-A oder strategischen M&A-Exit          │
└───────────────────────────────────────────────────────────────────────────────┘
```
