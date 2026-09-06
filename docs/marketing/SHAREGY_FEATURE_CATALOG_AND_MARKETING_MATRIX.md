# ⚡ Sharegy Gesamter Feature-Katalog & Marketing-Leistungsmatrix

**Version**: 5.0 (Produktionsstand September 2026)  
**Plattform**: Sharegy Dual-Core Platform (`app.sharegy.de`)  
**Zielgruppen**: Eigenheimbesitzer, Prosumer, Mehrparteienhäuser (WEGs), Bürgerenergiegenossenschaften (EEGs), Quartiere, Vermieter, Stadtwerke & Installateure.

---

## 🌟 Die Dual-Core Vision auf einen Blick

Sharegy ist die **erste ganzheitliche Energie-Plattform**, die hochperformantes **Home Energy Management (Säule 1: EMS)** mit gesetzeskonformer **Quartiers- und Bürgerenergie-Abrechnung (Säule 2: Energy Sharing)** vereint.

```
┌─────────────────────────────────────────────────────────────────────────────────────────┐
│                              SHAREGY CLOUD PLATTFORM (SaaS)                             │
├────────────────────────────────────────────┬────────────────────────────────────────────┤
│ 🟢 SÄULE 1: SMART HOME EMS & AKTORIK       │ 🔵 SÄULE 2: ENERGY SHARING & CLEARING     │
│ • Sub-Sekunden Live-Telemetrie & Sankey    │ • Revisionssichere 15-Minuten-Bilanzierung │
│ • Smart Load Management & Dispatch Hub     │ • § 42b EnWG Mieterstrom- & Quartiersabrech│
│ • BWWP & Wärmepumpen SG-Ready Steuerung    │ • Statische, dynamische & hybride Allokation│
│ • Autonome Batterie-Arbitrage & Negativpreise • PDF-Abrechnungsbescheide & DATEV/ERP-Export│
│ • OCPP 1.6-J Wallbox Smart Charging        │ • Smart Meter Gateways (wMSB Discovergy/inex│
│ • 48h KI-Solarprognose & Baseline-Watchdog │ • Multi-Community Portfolio Dashboard      │
└────────────────────────────────────────────┴────────────────────────────────────────────┘
```

---

## 📦 Vollständige Feature-Übersicht nach Modulen

### 1. ⚡ Live-EMS, Topbar-Pulse & Energiefluss-Visualisierung
* **Live Energy-Pulse Ticker (Topbar)**: Sub-Sekunden Echtzeit-Leistungsfluss direkt im Header (☀️ Solarerzeugung, 🏠 Hauslast, ⚡ Netzbezug/Einspeisung mit dynamischen Richtungsindikatoren, 🔋 Speicher-SoC).
* **Flackerfreies Live-Sankey-Diagramm**: Echtzeit-Darstellung aller Energieflüsse (Erzeugung $\rightarrow$ Hausverbrauch $\rightarrow$ Batteriespeicher $\rightarrow$ Netzaustausch) mit automatischer Etagen- und Raumgruppierung.
* **Multistring & AC-Kopplung (BKW-Erkennung)**: Automatische Erkennung und physikalische Gutschrift von sekundären AC-Wechselrichtern und Balkonkraftwerken (negative Hauslasten werden präzise als Ertrag bilanziert).
* **Sub-Sekunden Status ($O(1)$)**: Snapshot-Architektur über Redis und TimescaleDB für verzögerungsfreie Dashboard-Ladezeiten (< 20 ms).
* **Physikalisches Flussmodell**: Saubere Trennung von Speicherladung, Netzexport und Haushaltslast in `flow_engine.py` zur Vermeidung doppelter Zählungen.
* **Virtuelle Zähler & Sub-Metering**: Automatische Restlast-Disaggregation ($E_\text{Rest} = E_\text{Gesamt} - \sum E_\text{Submeter}$) zur Erkennung versteckter Verbraucher.
* **Dark & Light Mode**: Nahtloser Umschalter mit nativer Theme-Persistenz im Browser.

---

### 2. 🎛️ Smart Load Management & Dispatch Hub (`/app/control`)
* **Live Power Budget Header**: Visualisierung von verfügbarem Solarüberschuss ($P_\text{surplus} = P_\text{pv} - P_\text{load}$), Batterie-Ladestand, dynamischem Strompreis und geschalteter Last.
* **1-Klick Quick-Boost & Overrides**: Sofortschaltung für 11 kW Wallbox-Schnellladung, 100% Heimspeicher-Notstromreserve und maximalen PV-Eigenverbrauch mit Countdown-Badge und 1-Klick Reset.
* **4 Master-Autopilot-Modi**:
  * 🤖 *Smart Autopilot*: Vollautomatische Optimierung nach Solarprognose & Börsenpreisen.
  * ☀️ *Nur PV-Überschuss*: Strikt 100% Autarkie-Betrieb ohne zusätzlichen Netzbezug.
  * 💰 *Preise-Optimiert (Sparfuchs)*: Gezielte Aktivierung bei negativen und minimalen Spotmarkt-Preisen.
  * 🛑 *Manuell*: Pausierung der Automatik für manuelle Steuerung.
* **Smarte EPEX-Ladefenster**: Automatische Erkennung der günstigsten Ladezeiten (Top 3 Stunden) und Empfehlungen zur Vermeidung von Abend-Lastspitzen.
* **Interaktive Prioritäten-Kaskade (Merit-Order)**: Zuteilungsreihenfolge flexibler Großverbraucher (z. B. 1. Heimspeicher $\rightarrow$ 2. BWWP $\rightarrow$ 3. Wallbox $\rightarrow$ 4. Pool $\rightarrow$ 5. Klima $\rightarrow$ 6. Haushaltsgeräte).
* **24h-Fahrplan (Dispatch-Timeline)**: Stündliche Vorschau der geplanten Geräteschaltungen basierend auf 48h-Wetterprognose und Day-Ahead EPEX-Spotpreisen.
* **7 Modulare Verbraucher-Karten**:
  1. ♨️ **Brauchwasserwärmepumpe (BWWP)**: SG-Ready Schaltung, Temperatur-Gauge, Solar-Boost bis 60°C.
  2. 🚗 **Wallbox / EV Charger**: Ladestromregelung, Phasenumschaltung, Min+PV, Schnellladung.
  3. 🔋 **Batteriespeicher**: Dynamische Netzladung (Grid-Charging), Entladesperre bei Negativpreisen.
  4. 🏊 **Poolpumpen & Filterung**: Tägliche Mindestlaufzeit, garantierter Solarbetrieb.
  5. ❄️ **Klimaanlagen (Pre-Cooling)**: 1,5°C Vorkühlung in PV-Spitzenstunden zur Abend-Einsparung.
  6. 🧺 **Smarte Haushaltsgeräte**: Waschmaschine & Spülmaschine im "Ready-to-Start"-Modus.
  7. ⚡ **Heizstäbe (Power-to-Heat)**: Stufenlose Pufferladung zur Restertrags-Verwertung.

---

### 3. ♨️ BWWP & Wärmepumpen-Lastmanagement (SG-Ready)
* **4 genormte SG-Ready Zustände**:
  * *Zustand 1*: EVU-Sperre / Überhitzungsschutz ($T \ge 65^\circ\text{C}$).
  * *Zustand 2*: Normalbetrieb nach internem Thermostat ($T_\text{soll} \approx 52^\circ\text{C}$).
  * *Zustand 3*: SG-Ready Solar-Boost auf $60^\circ\text{C}$ als thermische Batterie bei Überschuss $\ge 800\,\text{W}$.
  * *Zustand 4*: Not-Zwangsanlauf bei $T < 45^\circ\text{C}$ (Warmwasser- & Legionellengarantie).
* **Integrierter Verdichter- & Taktschutz (Anti-Cycling)**:
  * Mindestlaufzeit $\ge 20\,\text{min}$ (verhindert Takten bei kurzen Wolkenfeldern).
  * Mindestruhezeit $\ge 15\,\text{min}$ (schont den Kältekreislauf).
* **Multi-Sensor Bündelung**: Gleichzeitige Verarbeitung von Wirkleistung (W), Wassertemperatur (°C) und SG-Schaltkontakt in einem logischen Gerät.

---

### 4. 🚗 OCPP 1.6-J Wallbox Gateway & Smart EV-Charging
* **Natives CSMS (Charging Station Management System)**: Direkte WebSocket-Kopplung (`/ws/ocpp/<cp_id>/`) für alle normkonformen Wallboxen (Easee, openWB, cFos, Heidelberg, Mennekes, Alfen, Webasto).
* **Intelligente Lademodi**:
  * ☀️ *Pure Solar*: Lädt ausschließlich mit reinem PV-Überschuss.
  * ⚖️ *Min + PV*: Garantiert Mindestladestrom (z. B. 6 A) und stockt mit Solarstrom auf.
  * 💶 *Börsenpreis-Laden*: Lädt automatisch in den 3 bis 5 günstigsten Stunden der Nacht.
  * ⚡ *Fast Charge*: Sofortige Vollladung mit 11 kW / 22 kW.
* **Dynamische Phasenumschaltung & Ampere-Slider**: Nahtlose Stromstärkeregelung von 6 A bis 32 A in Echtzeit.

---

### 5. 🔋 Batterie-Arbitrage & Wechselrichter-Direktanbindung
* **Autonome Börsenstrom-Arbitrage**: Automatisches Grid-Charging bei Tiefst- oder Negativpreisen an der Strombörse (EPEX Spot / Tibber) und Entladung in Hochpreisphasen (Ertragspotenzial: 180–320 € / Jahr).
* **Zero-Hardware Cloud-Inverter Integration**:
  * **Sungrow iSolarCloud**: 1-Klick OpenAPI Steuerung (`forced_charge`, `forced_discharge`, `self_consumption`).
  * **Fronius Solar.web, SolarEdge, Kostal Solar Portal, Growatt ShineServer**: Out-of-the-Box Ingest-Profile.
* **Degradations- & Ladezustands-Simulation**: 48h-Vorausschau des Batterie-SoC unter Berücksichtigung von Ladeverlusten und Entladelimits.

---

### 6. 🌐 Offene Konnektivität & Zero-Lock-in
* **Offizieller ioBroker Adapter (`ioBroker.sharegy`)**: Native Einbindung aller ioBroker-Objekte mit Multi-Sensor-Bündelung und bidirektionalem Schalt-Rückkanal via Outbound WebSocket.
* **Home Assistant Integration**: Offizielle HACS Custom Component mit 9 Sensoren, Telemetrie-Push (`sharegy.push_telemetry`) und Lade-Blueprints.
* **Outbound-WSS für Shelly Gen2/Gen3/Pro**: Plug-and-Play WebSocket-Verbindung für Shelly 1PM, Pro 3EM, Plus PlugS etc. mit automatischem 5s Live-Polling.
* **Globaler MQTT-Hub**: Einheitliches Topic-Schema (`h/<token>/<identifier>`) mit automatischer Authentifizierung und QR-Code-Setup.
* **OpenTelemetry (OTel) & REST Ingest**: Industriestandard-Ingestion für beliebige IoT-Gateways und kundeneigene Skripte.
* **Grafana Enterprise REST Bridge**: Native Anbindung für Enterprise-Dashboards und externe Leitwarten.

---

### 7. 🧠 KI-Prognosen, Anomalieerkennung & Alarmzentrale
* **48h Hybrid Physics + ML PV-Prognose**: Open-Meteo 96h Globalstrahlung + Anlagenausrichtung + Machine Learning (RandomForest) mit kontinuierlicher WAPE-Güteprüfung.
* **48h Haushalts-Lastprognose**: Wochentags- und stundenspezifische Verbrauchsprognose.
* **Predictive Maintenance & 7-Tage ML-Baseline**: Automatische Ermittlung der Ruhestrom-Baseline zur Erkennung defekter Thermostate, Pumpen-Dauerläufe und schleichender Mehrverbräuche.
* **Proaktive Alarmzentrale (8 Regelwerke)**: Sofortige Benachrichtigung bei PV-Ertragsausfall, Nacht-Leckagen, Batteriespeicher-Tiefentladung und extremen Börsen-Preisspitzen.
* **Live CO₂-Grid-Signal**: 36h-Vorschau der CO₂-Emissionsintensität des deutschen Stromnetzes (g CO₂/kWh) für klimagesteuerte Lastverschiebung.

---

### 8. 📱 Native Apps, Push & User Experience
* **Native Android App**: Gebaut mit Capacitor 7 (`de.sharegy.app`) mit flackerfreiem Splashscreen und nativem Lifecycle.
* **Web-Push (W3C / VAPID)**: Push-Benachrichtigungen auf Sperrbildschirmen für Android, Desktop und Apple iPhone (iOS 16.4+ Safari).
* **Multi-Language (i18n)**: Vollständig dreisprachige Benutzeroberfläche (Deutsch, Englisch, Polnisch).
* **DSGVO & TDDDG Konformität**: Duale Cookie-Persistenz (365 Tage) und lückenlose Audit-Logs.

---

### 9. 🏛️ Säule 2: Energy Sharing Communities & Quartiers-Clearing
* **Eichrechtskonforme 15-Minuten Bilanzierung**: Exakte Abrechnungsschnittstelle basierend auf OBIS-Zählerständen (`1.8.0` Bezug, `2.8.0` Einspeisung).
* **3 Flexible Allokationsmodelle (§ 42b / § 42a EnWG)**:
  * *Dynamisch*: Zuteilung nach zeitgleichem 15-Minuten Lastgang.
  * *Statisch*: Zuteilung nach festen Miteigentumsanteilen (MEA-Quoten / kWp-Zuweisung).
  * *Hybrid*: Vorrangige Eigenversorgung mit anschließender dynamischer Überschuss-Verteilung.
* **Automatische Monatsabrechnungs-Engine (Clearing)**: Cent-genaue Verrechnung von Community-Strom, Netzentgelt-Rabatten und Reststrom-Zukauf.
* **Rechtssichere Nachweise & ERP-Exporte**:
  * Druckfähiges PDF-Abrechnungsdokument (§ 42b EnWG konform).
  * Excel `.xlsx` mit Formeln, CSV (UTF-8 BOM Semikolon für DATEV) und standardisiertes XML für Hausverwaltungs-Software.
* **wMSB Smart Meter Hub**: Direkte REST-API Konnektoren für wettbewerbliche Messstellenbetreiber (Discovergy, inexogy, Solandeo) sowie gMSB HAN-Support.
* **Zentrales Multi-Community Management Hub**: Portfolio-Verwaltung für Energiegenossenschaften und Stadtwerke mit Drilldown, Tarifen und Rundschreiben.
* **Social Sharing & Viral Referral**: Share-Cards mit persönlicher CO₂- und Autarkie-Bilanz für WhatsApp, Telegram und Social Media.

---

### 10. 🛟 Integrierter Support- & Helpdesk-Hub
* **Integrierter Support-Drawer**: 1-Klick Ticket-Erstellung direkt aus der Topbar mit automatischer Übermittlung von Fehlermeldungen und Systemkontext.
* **FAQ-Deflection**: Automatische Einblendung passender Handbuch-Lösungen während des Tippens zur Entlastung des Support-Teams.
* **Interaktives Wissensportal (`/app/help`)**: 15 vollwertige Handbuch-Artikel in 9 Kategorien (DE & EN) mit Staff-Live-Editor.
