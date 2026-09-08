# 🎯 Sharegy: Strategische Gesamtevaluation, Schwachstellen-Analyse & Gap-Matrix

**Dokument-Version**: 1.0  
**Stand**: September 2026 (Live Release v5.2)  
**Erstellt von**: Antigravity Principal Engineering & Product Strategy  
**Zielgruppe**: Geschäftsführung, Gesellschafter, Beirat & Produkt-Management  

---

## 🧭 Executive Summary

Sharegy befindet sich mit dem **Live-Release v5.2** an einem entscheidenden strategischen Wendepunkt:
Die Software ist technologisch und architektonisch fertig, gehärtet, getestet und vereint als **erste Plattform in Europa** ein herstellerunabhängiges **Home Energy Management System (EMS, Säule 1)** mit gesetzeskonformem **Energy Sharing & Quartiers-Clearing (§ 42b EnWG, Säule 2)**.

Dieses Dokument liefert eine **ungeschminkte, ehrliche und schonungslose Analyse**:
1. **Wo Sharegy heute absolute Weltklasse und dem Markt voraus ist.**
2. **Wo wir noch echte Schwachstellen und operationelle Risiken haben.**
3. **Wo der Mitbewerb aktuell noch die Nase vorn hat (und warum).**
4. **Den konkreten, priorisierten Masterplan für 2026/2027, um Marktführer zu werden.**

---

## 🟢 1. Wo Sharegy absolute Weltklasse & dem Markt voraus ist

```
┌─────────────────────────────────────────────────────────────────────────────────────────┐
│                               DIE 6 KERN-SPITZENLEISTUNGEN                              │
├─────────────────────────────────────────────────────────────────────────────────────────┤
│ 1. ⚡ ECHTE DUAL-CORE PLATTFORM: EMS (Prosumer) + Energy Sharing (Quartiere) in einem   │
│ 2. 🚀 UNERREICHTE TELEMETRIE-PERFORMANCE: TimescaleDB Hypertables & $O(1)$ Live-Cache   │
│ 3. 🌡️ INGENIEURMÄSSIGES MPC-HEIZEN: Prädiktive Estrich-Vorladung & BWWP Boost bis 60°C  │
│ 4. 🌐 MAXIMALER ZERO-LOCK-IN: Outbound-WSS, OCPP 1.6-J, ioBroker, Home Assistant, MQTT  │
│ 5. 💳 VOLLAUTOMATISIERTER EU-ZAHLUNGS-STACK: 6 Sprachen, Stripe, SEPA, PayPal, Klarna   │
│ 6. 👑 CONVERSION-STARKE FREEMIUM-UX: 4 Pro-Hubs mit interaktiver Demo-Vorschau          │
└─────────────────────────────────────────────────────────────────────────────────────────┘
```

### 1.1 Die Dual-Core Architektur (Säule 1 + Säule 2)
* **Alleinstellungsmerkmal**: Auf dem europäischen Markt existiert keine einzige Plattform, die ein vollwertiges B2C-Smart-Home-EMS mit rechtssicherem B2B-Quartiersclearing verbindet.
* **Markt-Lücke geschlossen**: Prosumer nutzen Sharegy im Eigenheim für 7,99 €/Monat. Schließt sich dieselbe Liegenschaft einer WEG oder Bürgerenergiegenossenschaft an, bucht dieselbe Plattform nahtlos das 15-Minuten-Clearing nach § 42b EnWG ab.

### 1.2 Datenbank- & Abfrage-Performance
* **TimescaleDB Hypertables & Continuous Aggregates**: Selbst bei Hunderten Millionen Messpunkten laden Dashboards, Jahresbilanzen und Lastgänge in $< 20\,\text{ms}$.
* **$O(1)$ Snapshot-Tabelle (`DeviceLatestMetric`)**: Vermeidet Tabellenscans auf historischen Zeitreihen; der Live-Fluss im Header (`Live-Pulse`) aktualisiert sich flackerfrei in Sub-Sekunden.

### 1.3 Physikalisches Model Predictive Control (MPC) für Wärme & BWWP
* **Estrich-Speichermasse ($15\text{–}20\,\text{t}$)**: Sharegy nutzt Bauteilaktivierung als thermische $18\,\text{kWh}_\text{th}$ Batterie.
* **Prädiktives Absenken**: Bei Sonnenstrahlung ($G > 100\,\text{W/m}^2$) senkt Sharegy den Vorlauf vorab um bis zu $2,0\,\text{K}$ ab, um passive Fenstergewinne zu nutzen.
* **Verdichter- & Taktschutz**: Einhaltung von Mindestlaufzeiten ($\ge 20\,\text{min}$) und Ruhezeiten ($\ge 15\,\text{min}$) schützt teure Wärmepumpen vor frühzeitigem Verschleiß.

### 1.4 Vollständiger Europa-Zahlungsstack & Self-Service
* **6 Sprachen** (🇩🇪 DE, 🇬🇧 EN, 🇵🇱 PL, 🇹🇷 TR, 🇷🇺 RU, 🇷🇴 RO) nahtlos in UI und Stripe-Checkout integriert.
* **Rechtssichere Rechnungslegung**: § 14 UStG Invoicing, 19% MwSt., USt-IdNr, fortlaufende Nummernkreise und Customer Portal für vollständige Self-Service-Kündigung/Upgrades ohne Supportaufwand.

### 1.5 Standardisiertes Pro-Freemium Gating
* Alle 4 Pro-Hubs (`/app/control`, `/app/mobility`, `/app/heating`, `/app/alerts`) bieten Free-Nutzern eine transparente, interaktive Vorschau mit Weichzeichner (`backdrop-blur-[1.5px]`) und Showcase-Hero – maximale Conversion bei null Frustration.

---

## 🔴 2. Die schonungslose Schwachstellen-Analyse (Wo wir noch Defizite haben)

Trotz herausragender Softwarequalität hat Sharegy aktuell **5 kritische Baustellen**, die für die Skalierung gelöst werden müssen:

---

### ⚠️ Baustelle A: Cloud-Abhängigkeit vs. Lokale Offline-Resilienz
* **Das Problem**: Sharegy arbeitet aktuell als reine Cloud-SaaS-Plattform. Aktoren (Shellys, Relais, Wallboxen) werden über Cloud-APIs, Outbound-WSS oder ioBroker/HA-Bridges geschaltet.
* **Die Schwachstelle**: Bricht beim Kunden die Internetverbindung ab oder hat die Cloud kurz Schluckauf, wird in dieser Zeit kein Lastfahrplan ausgeführt.
* **Risiko**: Nutzer mit dynamischen Stromtarifen oder Netzdrosselung (§ 14a EnWG) erwarten, dass die Steuerung auch offline garantiert weiterläuft.
* **Lösung**:
  * Entwicklung eines **Sharegy Local Edge Daemon** (leichtgewichtiges Binary in Go/Rust oder Docker-Container für Raspberry Pi / Home Assistant), der den 24h-Fahrplan lokal zwischenspeichert und bei Netzausfall autonom steuert.

---

### ⚠️ Baustelle B: Fehlende Native Mobile Apps (App Store & Play Store)
* **Das Problem**: Die mobile App ist derzeit ein Capacitor-Web-Wrapper für Android.
* **Die Schwachstelle**:
  * Es fehlen **iOS Live-Activities** auf dem Sperrbildschirm (z. B. Live-Ladefortschritt des E-Autos oder aktueller Strompreis).
  * Es fehlen **Apple Watch / WearOS Komplikationen**.
  * Es fehlt **Apple CarPlay / Android Auto Integration** (z. B. für den Spritpreis-Radar oder Lade-Status direkt im Auto-Cockpit).
  * Im Apple App Store und Google Play Store ist Sharegy noch nicht als eigenständige Marken-App such- und installierbar.
* **Lösung**:
  * Capacitor-Plugins für iOS Live-Activities & Widgets implementieren.
  * Offizielles App-Store- und Play-Store-Deployment durchführen.

---

### ⚠️ Baustelle C: Smart Meter Hardware-Flaschenhals in Deutschland
* **Das Problem**: Für die eichrechtskonforme Säule 2 (Energy Sharing § 42b EnWG) wird ein Smart Meter Gateway (iMSys) oder ein wMSB (Discovergy/inexogy) benötigt. Der deutsche Rollout verläuft jedoch schleppend.
* **Die Schwachstelle**: Ein Prosumer mit einem klassischen digitalen Zähler (mME) kann ohne Hardwaretausch oder Zwischenzähler (Shelly Pro 3EM) nicht sofort im Sekundentakt messen.
* **Lösung**:
  * Unterstützung standardisierter, günstiger **IR-Leseköpfe** (z. B. Hichi / Tasmota Wifi-Lesekopf für ca. 25–40 €) mit 1-Klick Setup in Sharegy.
  * Partnerschaften mit wettbewerblichen Messstellenbetreibern (wMSB) für geförderten Zählertausch ausbauen.

---

### ⚠️ Baustelle D: BNetzA Marktkommunikation & Bilanzkreis-Anbindung (AS4 / EDIFACT)
* **Das Problem**: Die mathematische 15-Minuten-Clearing-Engine und MSCONS-Dateigenerierung ist zu 100% funktionsfähig. Um jedoch mit den 800+ deutschen Verteilnetzbetreibern (VNB) automatisiert über Marktprozesse abzurechnen, fordert die Bundesnetzagentur eine **AS4-zertifizierte Marktkommunikations-Infrastruktur** mit 11-stelligen BDEW-Codenummern und Bilanzkreis-Verträgen (BKV).
* **Die Schwachstelle**: Sharegy ist ein Software-Unternehmen und kein lizenzierter Energieversorger mit eigenem Bilanzkreis.
* **Lösung**:
  * Kooperation mit **White-Label Abwicklungsdienstleistern** (z. B. getFlexible, E-Bridge, inexogy, EWE), die den regulatorischen AS4-Transport übernehmen, während Sharegy die Plattform, Tarife und Abrechnungen liefert.

---

### ⚠️ Baustelle E: Markenbekanntheit & Customer Acquisition Cost (CAC)
* **Das Problem**: Wettbewerber wie 1Komma5° oder Tibber investieren zweistellige Millionenbeträge in TV- und Social-Media-Werbung.
* **Die Schwachstelle**: Reines B2C-Endkunden-Marketing über Google/Meta-Ads ist extrem teuer (CAC > 120 € pro Lead).
* **Lösung**:
  * **Strikte B2B2C-Strategie**: Kooperationen mit freien Solar- und Wärmepumpen-Installateuren, Hausverwaltungen (WEGs) und Bürgerenergiegenossenschaften, die Sharegy ihren Kunden als schlüsselfertige Software mitliefern.

---

## ⚔️ 3. Detaillierter Mitbewerber-Vorteilsvergleich

| Mitbewerber | Wo sie aktuell besser sind | Warum sie dort führen | Was Sharegy tun muss |
|---|---|---|---|
| **1Komma5°** | **Kapitalkraft & Installationsnetz vor Ort** | Über **300 Mio. € Funding**, eigenes Handwerker-Netzwerk. Verkaufen Hardware + Software im Paket für 20.000–30.000 €. | **Installateur-Partnerprogramm**: Freien Installateuren Sharegy als herstellerunabhängige Alternative zu Heartbeat bereitstellen. |
| **Tibber** | **Markenbekanntheit & Hardware-Dongle** | Der **Tibber Pulse** (50 € IR-Lesekopf) macht jeden alten mME-Zähler sofort smart. Eigener Stromliefervertrag. | 1-Klick Setup für günstige WLAN-Leseköpfe (Hichi / Tasmota) anbieten, um ohne Zählertausch sofort Live-Werte zu liefern. |
| **evcc** | **Community-Vielfalt bei Exoten-Wallboxen** | 100+ Open-Source Entwickler binden wöchentlich obskure Auto- und Wallbox-APIs per Reverse-Engineering ein. | Standardisiertes **OCPP 1.6-J** als Industriestandard beibehalten und Top-Hersteller-Presets pflegen. |
| **Exnaton** | **Bestehende Enterprise-Rahmenverträge mit Stadtwerken** | Langjährige Präsenz in Stadtwerke-Gremien in der Schweiz und Süddeutschland. | **Bürgerenergie- & WEG-Nische besetzen**: Kleinere Genossenschaften und Hausverwaltungen gewinnen, die Exnatons 20.000 € Setup nicht zahlen können. |
| **Clever-PV** | **Einfaches B2C-Balkonkraftwerk-Onboarding** | Stark vereinfachtes Cloud-Schalten für Einsteiger ohne Anspruch auf physikalische Tiefe. | Durch die neuen **Showcases & interaktive Vorschau** den Einstieg genauso einfach gestalten, aber mit unendlich mehr Tiefgang. |

---

## 📊 4. SWOT-Matrix im Überblick

```
┌──────────────────────────────────────────────┬──────────────────────────────────────────────┐
│ 🟢 STÄRKEN (STRENGTHS)                       │ 🔴 SCHWÄCHEN (WEAKNESSES)                    │
├──────────────────────────────────────────────┼──────────────────────────────────────────────┤
│ • Einzige Dual-Core Plattform (EMS + Sharing)│ • Reine Cloud-Aktorik (noch kein Edge Daemon)│
│ • TimescaleDB Sub-Sekunden-Performance       │ • Mobile App ist Web-Wrapper (keine Widgets) │
│ • Physikalisches MPC-Heiz- & BWWP-Modell     │ • Keine AS4-Zertifizierung für direkte VNB-MaKo│
│ • 100% Zero-Lock-in & Hardware-Offenheit     │ • Keine eigene Hardware (z. B. Zähler-Dongle)│
│ • Fertiger Multi-Zahlungs-Stack (6 Sprachen) │ • Geringe Markenbekanntheit im Massenmarkt   │
├──────────────────────────────────────────────┼──────────────────────────────────────────────┤
│ 🔵 CHANCEN (OPPORTUNITIES)                   │ 🟡 RISIKEN (THREATS)                         │
├──────────────────────────────────────────────┼──────────────────────────────────────────────┤
│ • Gesetzlicher Zwang zu § 14a EnWG Drosselung│ • Zögerlicher Smart-Meter-Rollout in DE      │
│ • Boom von § 42b EnWG Bürgerenergie & Mieter │ • Preiskampf durch kapitalstarke Anbieter    │
│ • B2B2C-Vertrieb über unabhängige Installateure • API-Restriktionen durch Wechselrichter-Herst.│
│ • White-Label Partnerschaften mit Stadtwerken│ • Regulatorische Änderungen bei dynamischen T.│
└──────────────────────────────────────────────┴──────────────────────────────────────────────┘
```

---

## 🚀 5. Der strategische Masterplan für Sharegy (2026 / 2027)

```
┌───────────────────────────────────────────────────────────────────────────────┐
│                           DER 3-STUFEN WACHSTUMSPLAN                          │
├───────────────────────────────────────────────────────────────────────────────┤
│ STUFE 1: MONETARISIERUNG & B2B2C-HEBEL (Q4 2026)                              │
│ • Installateur-Portal: White-Label Dashboard für Solarteure & Elektriker      │
│ • B2B-Offensive: 20 Bürgerenergiegenossenschaften & WEGs für Säule 2 gewinnen │
│ • App Store & Play Store Release der nativen Apps                             │
│                                                                               │
│ STUFE 2: HARDWARE- & OFFLINE-RESILIENZ (Q1–Q2 2027)                           │
│ • Sharegy Edge Daemon (Offline-First Dispatch für Raspberry Pi / HA)          │
│ • 1-Klick Ingestion für Infrarot-Leseköpfe (Hichi / Tasmota)                  │
│ • Matter & EEBUS Bridge für native Wärmepumpen- & Wallbox-Kopplung            │
│                                                                               │
│ STUFE 3: INSTITUTIONELLE SKALIERUNG & B2B-CLEARING (Q3–Q4 2027)               │
│ • White-Label AS4 Marktkommunikations-Partnerschaft für EVUs & Stadtwerke     │
│ • Ausbau auf 10.000 Pro-Haushalte und 100 Quartiere                           │
│ • Bewertung von 5,0 Mio. €+ für Series-A oder strategischen M&A-Exit          │
└───────────────────────────────────────────────────────────────────────────────┘
```

---

## ⚡ 6. Erreichte Meilensteine: Go-To-Market & PLG Conversion Engine

| Feature | Status | Beschreibung & Impact |
| :--- | :---: | :--- |
| **Landingpage 2.0 (CleanTech)** | ✅ Live | Modernes, helles SaaS-Design mit gleichberechtigter Präsentation von Säule 1 (EMS & § 14a) und Säule 2 (P2P Energy Sharing). |
| **1-Klick-Gast-Zugang (`/api/demo/`)** | ✅ Live | Barrierefreier Einstieg ins echte Live-Dashboard (`demo@sharegy.de`) in einem neuen Tab – ohne Registrierungshürde. |
| **Live Energy Flow Simulator** | ✅ Live | Interaktive 4-Szenarien-Simulation (Mittags-Überschuss, Nacht-Arbitrage, Peak-Shaving, § 14a Dimmung). |
| **§ 14a & Sharing ROI-Rechner** | ✅ Live | Interaktive Haushalts-Kalkulation des jährlichen finanziellen Vorteils (PV + Speicher + WP + Wallbox + Sharing). |
| **Hardware-Kompatibilität & § 23 MarkenG** | ✅ Live | Symmetrisches 12-Hersteller Grid (SMA, Fronius, Sungrow, Huawei, Tesla, BYD, Daikin, Viessmann etc.) inkl. rechtssicherem Disclaimer. |

---

## 🎯 Schlussfazit

Sharegy hat das schwierigste Problem gelöst: **Das Produkt ist softwareseitig fertig, architektonisch brillant und dem Wettbewerb inhaltlich überlegen.**

Mit der neuen **Landingpage 2.0**, dem **1-Klick-Gast-Zugang** und der **Dual-Pillar-Positionierung** steht die Product-Led Growth (PLG) Conversion Engine bereit. Der Fokus für die kommenden Quartale liegt nun auf **Vertriebshebeln (Installateure & Genossenschaften)**, **Offline-Resilienz (Edge Daemon)** und **App-Store-Präsenz**. Damit ist Sharegy optimal aufgestellt, um die dominierende Energie-Plattform im DACH-Raum zu werden.
