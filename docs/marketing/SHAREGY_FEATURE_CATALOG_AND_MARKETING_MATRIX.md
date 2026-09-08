# ⚡ Sharegy Gesamter Feature-Katalog & Marketing-Leistungsmatrix

**Version**: 5.1 (Produktionsstand September 2026)  
**Plattform**: Sharegy Dual-Core Platform (`app.sharegy.de`)  
**Zielgruppen**: Eigenheimbesitzer, Prosumer, Mehrparteienhäuser (WEGs), Bürgerenergiegenossenschaften (EEGs), Quartiere, Vermieter, Stadtwerke & Installateure.

---

## 🌟 Die Dual-Core Vision auf einen Blick

Sharegy ist die **erste ganzheitliche Energie-Plattform**, die hochperformantes **Home Energy Management (Säule 1: EMS)** mit gesetzeskonformer **Quartiers- und Bürgerenergie-Abrechnung (Säule 2: Energy Sharing)** sowie einem **vollautomatisierten Multi-Zahlungs-Stack (Stripe, SEPA, PayPal, Klarna)** vereint.

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
│ • 48h KI-Solarprognose & 7d EPEX Trend     │ • Multi-Community Portfolio Dashboard      │
│ • Stripe & SEPA Checkout (6 EU-Sprachen)   │ • Revisionssicheres Audit-Log & RBAC       │
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
* **EPEX-Spot 7-Tage Trend & Ladefenster**: 6-Tage-Historie + Day-Ahead-Vorschau mit automatischer Identifikation der 3 günstigsten Ladezeiten und Spitzenvermeidung.
* **Interaktive Prioritäten-Kaskade (Merit-Order)**: Zuteilungsreihenfolge flexibler Großverbraucher (z. B. 1. Heimspeicher $\rightarrow$ 2. BWWP $\rightarrow$ 3. Wallbox $\rightarrow$ 4. Pool $\rightarrow$ 5. Klima $\rightarrow$ 6. Haushaltsgeräte).
* **24h-Fahrplan (Dispatch-Timeline)**: Stündliche Vorschau der geplanten Geräteschaltungen basierend auf 48h-Wetterprognose und Day-Ahead EPEX-Spotpreisen.
* **8 Modulare Verbraucher-Karten**:
  1. 🌡️ **Fußbodenheizung & Estrich-Speicher**: Thermische Bauteilaktivierung (+0,5°C bis +1,5°C Vorladung), $15\text{–}20\,\text{t}$ Estrich-Speicher.
  2. ♨️ **Brauchwasserwärmepumpe (BWWP)**: SG-Ready Schaltung, Temperatur-Gauge, Solar-Boost bis 60°C.
  3. 🚗 **Wallbox / EV Charger**: Ladestromregelung, Phasenumschaltung, Min+PV, Schnellladung.
  4. 🔋 **Batteriespeicher**: Dynamische Netzladung (Grid-Charging), Entladesperre bei Negativpreisen.
  5. 🏊 **Poolpumpen & Filterung**: Tägliche Mindestlaufzeit, garantierter Solarbetrieb.
  6. ❄️ **Klimaanlagen (Pre-Cooling)**: 1,5°C Vorkühlung in PV-Spitzenstunden zur Abend-Einsparung.
  7. 🧺 **Smarte Haushaltsgeräte**: Waschmaschine & Spülmaschine im "Ready-to-Start"-Modus.
  8. ⚡ **Heizstäbe (Power-to-Heat)**: Stufenlose Pufferladung zur Restertrags-Verwertung.

---

### 3. 🌡️ Fußbodenheizungs-Steuerung & Thermische Estrich-Vorladung
* **Thermische Bauteilaktivierung als Batterie**:
  * $15\text{–}20\,\text{Tonnen}$ Estrichmasse fungieren als riesiger, abnutzungsfreier thermischer Energiespeicher ($\approx 14\text{–}18\,\text{kWh}_\text{th}$ Kapazität).
  * Automatisches Vorladen (Pre-Heating) um $+0,5\,\text{K}$ bis $+1,5\,\text{K}$ bei PV-Überschuss $\ge 1\,\text{kW}$ oder extrem günstigen/negativen Börsenstrompreisen.
  * Passive, zeitverzögerte Wärmeabgabe während der teuren Abendstunden (Peak-Shaving) zur vollständigen Vermeidung von Netzstrom-Heizbedarfen.
* **Intelligenter Taktschutz & Sicherheit**:
  * Mindestlaufzeit $\ge 30\,\text{min}$ und Mindestruhezeit $\ge 15\,\text{min}$ gegen schädliches Takten von Wärmepumpe und Stellantrieben.
  * Estrich-Maximaltemperaturschutz ($T_\text{max} \le 24,5^\circ\text{C}$) zur Einhaltung physiologischer Fußboden-Grenzwerte.
* **Live Thermal SoC & 1-Klick Vorlade-Boost**:
  * Echtzeit-Berechnung des thermischen Ladezustands ($\text{SoC}_\text{thermal}$ in $\%$), der gespeicherten Wärme- ($Q_\text{th}$) und Äquivalenz-Stromenergie ($E_\text{el}$).
  * 1-Klick 2-Stunden Vorlade-Boost direkt im HEMS Control Dashboard.

---

### 4. ♨️ BWWP & Wärmepumpen-Lastmanagement (SG-Ready)
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

### 5. 🚗 Multi-Protocol CSMS Gateway & ISO 15118-20 V2G/V2H Bidirektionales Laden
* **Multi-Protocol CSMS (Charging Station Management System)**: Direkte WebSocket-Kopplung mit automatischer Subprotocol-Aushandlung (`ocpp1.6`, `ocpp2.0.1`, `ocpp2.1`) für alle normkonformen Ladestationen (Easee, openWB, cFos, Heidelberg, Mennekes, Alfen, Webasto, Keba).
* **ISO 15118-20 V2G & V2H Bidirektionalität**:
  * 🏠 *Vehicle-to-Home (V2H)*: Fahrzeug speist in teuren Abend- und Nachtstunden bis zu 11 kW in das Hausnetz ein.
  * ⚡ *Vehicle-to-Grid (V2G Arbitrage)*: Laden bei negativen Preisen, Netzeinspeisung bei extremen Börsenspitzen.
  * 🛡️ *Intelligenter Batteriewächter*: Einstellbare Mindest-SoC Notreserve (z. B. 50% / 200 km) zur Schonung des E-Auto-Akkus.
* **Intelligente Lademodi**:
  * ☀️ *Pure Solar*: Lädt ausschließlich mit reinem PV-Überschuss.
  * ⚖️ *Min + PV*: Garantiert Mindestladestrom (z. B. 6 A) und stockt mit Solarstrom auf.
  * 💶 *Börsenpreis-Laden*: Lädt automatisch in den günstigsten Stunden des EPEX Spotmarkts.
  * ⚡ *Fast Charge*: Sofortige Vollladung mit 11 kW / 22 kW.
* **Erweiterte CSMS-Aktorik & Diagnose**:
  * Vollständiges Remote-Management: `SetChargingProfile`, `GetCompositeSchedule`, `ClearChargingProfile`, `ReserveNow`, `CancelReservation`, `TriggerMessage`.
  * Offline-RFID-Synchronisation (`SendLocalList`, `GetLocalListVersion`) und automatischer Protokolldiagnose-Upload (`GetDiagnostics`, `DiagnosticsStatusNotification`).
  * OCPP 2.0.1 / 2.1 Device Model: `TransactionEvent`, `NotifyEvent`, `GetVariables`, `SetVariables` und ISO 15118 Zertifikatsverwaltung (`Get15118EVCertificate`).

---

### 6. ⛽ Mobilitäts- & Spritpreis-Radar (MTS-K / Tankerkönig)
* **Live-Spritpreis-Radar**:
  * Abfrage der günstigsten Tankstellen im Umkreis ($5\,\text{km}$, $10\,\text{km}$, $25\,\text{km}$) für **Super E10**, **Super E5** und **Diesel** über die offizielle Markttransparenzstelle für Kraftstoffe (MTS-K).
  * Anzeige von Marke, Straße, exakter Entfernung und Öffnungsstatus.
* **100-km Real-Kostenvergleich (EV vs. Verbrenner)**:
  * Direkte Gegenüberstellung der Kraftstoff- und Ladekosten pro $100\,\text{km}$:
    * ☀️ **E-Auto Solar**: $\mathbf{1,44\,€ / 100\,\text{km}}$ *(18 kWh à 8 ct Opportunitätskosten)* $\rightarrow$ **bis zu 88% günstiger**
    * 🌙 **E-Auto Börsentarif**: $\mathbf{3,24\,€ / 100\,\text{km}}$ *(18 kWh à 18 ct)*
    * 🛢️ **Diesel**: $\mathbf{\approx 9,50\,€ / 100\,\text{km}}$ *(6,0 l/100km)*
    * ⛽ **Benziner (E10)**: $\mathbf{\approx 12,40\,€ / 100\,\text{km}}$ *(7,2 l/100km)*
  * Live-Vorteilsrechner: Visualisiert jährliche Ersparnisse von über $1.600\,€$ bei $15.000\,\text{km}$ Fahrleistung.
* **Tageszeit-Tankempfehlung**:
  * Analyse des statistischen Tagespreisverlaufs zur Erkennung günstiger Abendfenster (18:00–21:30 Uhr) und Vermeidung von Morgen-Aufschlägen (+10 bis 14 ct/l).

---

### 7. 🔋 Batterie-Arbitrage & Wechselrichter-Direktanbindung
* **Autonome Börsenstrom-Arbitrage**: Automatisches Grid-Charging bei Tiefst- oder Negativpreisen an der Strombörse (EPEX Spot / Tibber) und Entladung in Hochpreisphasen (Ertragspotenzial: 180–320 € / Jahr).
* **Zero-Hardware Cloud-Inverter Integration**:
  * **Sungrow iSolarCloud**: 1-Klick OpenAPI Steuerung (`forced_charge`, `forced_discharge`, `self_consumption`).
  * **Fronius Solar.web, SolarEdge, Kostal Solar Portal, Growatt ShineServer**: Out-of-the-Box Ingest-Profile.
* **Degradations- & Ladezustands-Simulation**: 48h-Vorausschau des Batterie-SoC unter Berücksichtigung von Ladeverlusten und Entladelimits.

---

### 7. 👑 Standardisierte Pro-Freemium Gating- & Showcase-Architektur
* **Konsequenter 3-Stufen-Aufbau**:
  * **1. Header**: Prominenter Pro-Statusindikator und 1-Klick Upgrade-Button (`⭐ Auf Pro upgraden ab 6,66 €/M`).
  * **2. Pro Hero Showcase Banner**: Dunkles Glassmorphism-Design (Indigo/Slate-Glow) mit 6 fokussierten Kernvorteilen und dynamischer Preisberechnung.
  * **3. Interaktive Demo-Vorschau**: Echte Dashboard-Inhalte und Widgets sind für Free-User mit einem leichten Unschärfe-Filter (`backdrop-blur-[1.5px]`) und zentriertem `🔒 Interaktive Demo-Vorschau`-Lock-Badge sichtbar. Klick öffnet das `ProUpgradeModal`.
* **Sidebar-Harmonisierung**: Konsistente goldene `PRO`-Badges für alle 4 Automationsbereiche (`/app/control`, `/app/mobility`, `/app/heating`, `/app/alerts`).

---

### 8. 🌐 Offene Konnektivität & Zero-Lock-in
* **Offizieller ioBroker Adapter (`ioBroker.sharegy`)**: Native Einbindung aller ioBroker-Objekte mit Multi-Sensor-Bündelung und bidirektionalem Schalt-Rückkanal via Outbound WebSocket.
* **Home Assistant Integration**: Offizielle HACS Custom Component mit 9 Sensoren, Telemetrie-Push (`sharegy.push_telemetry`) und Lade-Blueprints.
* **Outbound-WSS für Shelly Gen2/Gen3/Pro**: Plug-and-Play WebSocket-Verbindung für Shelly 1PM, Pro 3EM, Plus PlugS etc. mit automatischem 5s Live-Polling.
* **Globaler MQTT-Hub**: Einheitliches Topic-Schema (`h/<token>/<identifier>`) mit automatischer Authentifizierung und QR-Code-Setup.
* **OpenTelemetry (OTel) & REST Ingest**: Industriestandard-Ingestion für beliebige IoT-Gateways und kundeneigene Skripte.
* **Grafana Enterprise REST Bridge**: Native Anbindung für Enterprise-Dashboards und externe Leitwarten.

---

### 9. 🧠 KI-Prognosen, Anomalieerkennung & Alarmzentrale
* **48h Hybrid Physics + ML PV-Prognose**: Open-Meteo 96h Globalstrahlung + Anlagenausrichtung + Machine Learning (RandomForest) mit kontinuierlicher WAPE-Güteprüfung.
* **48h Haushalts-Lastprognose**: Wochentags- und stundenspezifische Verbrauchsprognose.
* **Predictive Maintenance & 7-Tage ML-Baseline**: Automatische Ermittlung der Ruhestrom-Baseline zur Erkennung defekter Thermostate, Pumpen-Dauerläufe und schleichender Mehrverbräuche.
* **Proaktive Alarmzentrale (8 Regelwerke)**: Sofortige Benachrichtigung bei PV-Ertragsausfall, Nacht-Leckagen, Batteriespeicher-Tiefentladung und extremen Börsen-Preisspitzen.
* **Live CO₂-Grid-Signal**: 36h-Vorschau der CO₂-Emissionsintensität des deutschen Stromnetzes (g CO₂/kWh) für klimagesteuerte Lastverschiebung.

---

### 10. 🛡️ § 14a EnWG Netzdrosselung & Summenleistungs-Modell (SteuVE)
* **BNetzA BK6-22-300 Konformität**: Dynamisches Netzleistungs-Budget:
  $$P_{\text{allow}} = 4{,}2\,\text{kW (Netzkontingent)} + P_{\text{PV}} + P_{\text{Batt}} - P_{\text{Base}}$$
* **Priorisierte Abarbeitung von Drosselsignalen**: Wärmepumpen (Prio 1) bleiben im Mindestbetrieb, Speicher stoppen Netzladung, Wallboxen (Prio 3) modulieren dynamisch auf das Restkontingent herunter.
* **Signalquellen**: Netzbetreiber-API, Steuerbox-CLS, potentialfreier Shelly-Schaltkontakt oder Handtest.

---

### 11. 📱 Native Apps, Push & 6-Sprachiges EU-Paket (i18n)
* **6 Europäische Sprachen**: Vollständige Lokalisierung in 🇩🇪 Deutsch, 🇬🇧 English, 🇵🇱 Polski, 🇹🇷 Türkçe, 🇷🇺 Русский und 🇷🇴 Română mit blitzschnellem Topbar-Umschalter.
* **Native Android App**: Gebaut mit Capacitor 7 (`de.sharegy.app`) mit flackerfreiem Splashscreen und nativem Lifecycle.
* **Web-Push (W3C / VAPID)**: Push-Benachrichtigungen auf Sperrbildschirmen für Android, Desktop und Apple iPhone (iOS 16.4+ Safari).
* **DSGVO & TDDDG Konformität**: Duale Cookie-Persistenz (365 Tage) und lückenlose Audit-Logs.

---

### 12. 🏛️ Säule 2: Energy Sharing Communities & Quartiers-Clearing
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

### 13. 💳 Vollautomatisierter SaaS-Billing & Payment-Stack (Stripe)
* **Multi-Zahlungsmethoden**: Kredit-/Debitkarten (Visa, Mastercard, Amex), SEPA-Lastschrift, PayPal, Klarna, Amazon Pay und Stripe Link.
* **Rechtssichere Rechnungslegung (§ 14 UStG)**: Automatischer USt-Ausweis (19% MwSt., USt-IdNr `DE300917919`), Statement-Descriptor `SHAREGY PRO - SMARTEVO` und fortlaufende Nummernkreise (`SHAREGY-...`).
* **Stripe Customer Portal**: Self-Service-Verwaltung für Zahlungsmethoden, Rechnungs-PDFs und Abo-Status.
* **Self-Healing IDs**: Resiliente automatische Bereinigung ungültiger Customer-IDs zwischen Entwicklungs- und Produktivumgebungen.
* **Gutschein- & Aktionscode-System**: Dezenter Coupon-Trigger zur Einlösung von Rabattcodes.

---

### 14. 🛡️ Enterprise Security, Hardware-Watchdog & Demo-Sandbox
* **Server-Hardware & Kapazitäts-Wächter**: Rollenbasierte Überwachung von CPU, RAM, Disk und Latenzen (RBAC: exklusiv für HEMS- und Sysadmins).
* **Autonome Demo-Sandbox**: 3 isolierte Demo-Profile (Smart Home, Community Admin, Member) für 1-Klick-Logins ohne Registrierung.
* **Kaskadierende Hypertable-Sicherheit**: Sichere Bereinigung und Re-Seeding ohne Datenbank-Blockaden.

---

### 15. 🛟 Integrierter Support- & Helpdesk-Hub
* **Integrierter Support-Drawer**: 1-Klick Ticket-Erstellung direkt aus der Topbar mit automatischer Übermittlung von Fehlermeldungen und Systemkontext.
* **FAQ-Deflection**: Automatische Einblendung passender Handbuch-Lösungen während des Tippens zur Entlastung des Support-Teams.
* **Interaktives Wissensportal (`/app/help`)**: 15 vollwertige Handbuch-Artikel in 9 Kategorien (DE & EN) mit sanfter Anchor-Navigation (`#articles-list`) und Staff-Live-Editor.
