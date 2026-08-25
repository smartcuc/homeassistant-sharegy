# 🎯 Verbindliche Ausführungs- & Prioritätenliste (Execution Roadmap)

**Datum**: 25. August 2026  
**Bereich**: Sprint-Planung, Meilenstein-Steuerung, Execution Backlog  
**Ziel**: Systematische Abarbeitung der strategischen Meilensteine vom Datenfundament über Integrationen bis hin zu Subscription, Monetarisierung und EMS-Userabrechnung.

---

## 🏛️ Das 5-Stufen-Phasenmodell (Tiers)

Wir arbeiten die offenen Arbeitspakete in 5 sequenziellen Stufen ab, um technische Abhängigkeiten optimal zu nutzen:

```mermaid
graph TD
    subgraph TIER 1: Datenfundament & Prognose-Power
        T1_1["1. TimescaleDB Migration & Continuous Aggregates (Task 5.1)"]
        T1_2["2. Verbrauchs-Prognose Engine (Task 5.2)"]
        T1_3["3. Batterie- & SoC-Prognose Simulation (Task 5.3)"]
        T1_4["4. Solar-Prognosegüte & Ist-vs-Soll Abgleich (Task 5.13)"]
        T1_5["5. Frei wählbarer Zeitraum & Multi-Format Export (Task 5.15)"]
    end

    subgraph TIER 2: Alerting & Push-Engine
        T2_1["6. Alert & Anomalie-Erkennungssystem (Task 5.6)"]
        T2_2["7. Mobile Push & Notification Engine FCM/APNs (Task 5.9)"]
    end

    subgraph TIER 3: Ökosystem-Bridges & Aktorik
        T3_1["8. Deklaratives Device-Profile Addon-System (Task 5.7)"]
        T3_2["9. Bi-direktionale Plugins: Home Assistant, evcc, ioBroker (Task 5.8)"]
    end

    subgraph TIER 4: Mobile Apps & User Experience
        T4_1["10. Native iOS & Android Apps via Capacitor (Task 5.10)"]
        T4_2["11. Kontextuelles Help-System & FAQ/Handbuch DE/EN (Task 5.4 & 5.5)"]
    end

    subgraph TIER 5: Monetarisierung, Sub-Metering & Analytics
        T5_1["12. Subscription & SaaS-Lizenzmodell / Stripe (Task 5.11)"]
        T5_2["13. EMS-Userabrechnung & Mieterstrom / Sub-Metering Billing (Task 5.12)"]
        T5_3["14. Trends & Historische Zeitreihen der virtuellen Zähler (Task 5.14)"]
    end

    T1_1 --> T1_2
    T1_2 --> T1_3
    T1_3 --> T1_4
    T1_4 --> T1_5
    T1_5 --> T2_1
    T2_1 --> T2_2
    T2_2 --> T3_1
    T3_1 --> T3_2
    T3_2 --> T4_1
    T4_1 --> T4_2
    T4_2 --> T5_1
    T5_1 --> T5_2
    T5_2 --> T5_3
```

---

## 📋 Detaillierte Arbeitspakete & Spezifikation

---

### 🟢 TIER 1: DATENFUNDAMENT & PROGNOSE-POWER (Abgeschlossen / In Betrieb)

#### 1. 🗄️ Task 5.1: TimescaleDB Migration & Continuous Aggregates
* **Zweck**: Skalierbare Speicherung von Millionen Telemetrie-Zeilen ohne Performance-Verlust.
* **Maßnahmen**:
  1. `devices_devicemetric` als TimescaleDB-Hypertable (`timestamp`-Partitionierung) konfigurieren.
  2. SQL Continuous Aggregates (1m, 5m, 1h) direkt in PostgreSQL für Sub-10ms Chartabfragen.
  3. Retention & Compression Policy: Automatische Kompression nach 7 Tagen, Rohdaten-Retention nach 30 Tagen.
* **Ergebnis**: 100x schnellere Historien-Abfragen, 90 % weniger Speicherverbrauch.

#### 2. 📈 Task 5.2: Verbrauchs-Prognose (Household Load Forecast Engine)
* **Zweck**: Berechnung der voraussichtlichen Haushaltslast für präzise Netto-Überschussplanung.
* **Maßnahmen**:
  1. Berechnung von Wochentags- und Tageszeit-Lastprofilen aus historischen Zählerdaten.
  2. Heizgradtage-/Temperatur-Kompensation für Wärmepumpen und Klimageräte.
  3. Bereitstellung der 24h–48h Lastkurve in der Prognose-Pipeline.
* **Ergebnis**: Realistische Residuallast-Kurve für die nächsten 2 Tage.

#### 3. 🔋 Task 5.3: Batterie- & SoC-Prognose (24h/48h Simulation)
* **Zweck**: Vorausschauende Transparenz über Batterieladung und Autarkie.
* **Maßnahmen**:
  1. 48h SoC-Simulation: $SoC(t+1) = SoC(t) + \eta \cdot (P_{\text{PV}} - P_{\text{Last}})$.
  2. Berücksichtigung von Batterie-Kapazität, Ladebegrenzungen, Mindest-Notstromreserve und Verlusten.
  3. Visualisierung der prognostizierten Ladekurve im Energie-Dashboard.
* **Ergebnis**: Exakte Prognose über Akkulaufzeit und Nachladebedarf.

#### 4. ☀️ Task 5.13: Solar-Prognosegüte & Ist-vs-Soll-Vergleich (%-Genauigkeit & Kalibrierung)
* **Zweck**: Transparenter Abgleich zwischen vorhergesagtem und real erzeugtem Solarstrom zur Qualitätskontrolle und Selbstkalibrierung.
* **Maßnahmen**:
  1. **Mathematischer Genauigkeitsabgleich**: Berechnung der prozentualen Übereinstimmung (Accuracy Score basierend auf WAPE: $\text{Accuracy} = 1 - \frac{\sum |P_{\text{Real}} - P_{\text{Forecast}}|}{\sum P_{\text{Real}}}$).
  2. **Visuelle Soll-Ist-Überlagerung**: Darstellung der prognostizierten Kurve (gestrichelt) und der tatsächlichen Messwerte (Fläche/Balken) im Zeitverlauf.
  3. **Scorecard & Güte-Badge**: Prozentuale Trefferquote (z. B. *„95,2 % Prognosegenauigkeit heute“*) mit Qualitäts-Indikator (Hervorragend / Gut / Abweichend) im Forecast- und Energie-Dashboard.
  4. **Adaptive Selbstkalibrierung**: Nutzung systematischer Abweichungen (z. B. Nachmittags-Verschattung durch Nachbargebäude oder Bäume) zur automatischen Nachjustierung des standortspezifischen String-Korrekturfaktors.
#### 5. 📅 Task 5.15: Frei wählbarer Zeitraum (Date-Range-Picker) & Multi-Format Daten-Export (CSV / Excel / JSON / PDF)
* **Zweck**: Volle Flexibilität zur historischen Auswertung beliebiger Zeitintervalle sowie Download und Weitergabe aller Mess-, Kosten- und Verbrauchsdaten.
* **Maßnahmen**:
  1. **Flexibler Zeitraum-Filter**:
     * Schnellauswahl: *Heute, Gestern, Letzte 7 Tage, Letzte 30 Tage, Dieser Monat, Letzter Monat, Dieses Jahr, Gesamte Historie*.
     * **Freier Datums- & Uhrzeitbereich (Custom Date Range Picker)** für minutengenaue historische Analysen.
  2. **Multi-Format Export-Engine**:
     * **CSV / Excel (.xlsx)**: Tabellarische Zeitreihen (15m-, 1h- und Tagesscheiben) für PV-Erzeugung, Hauslast, Batteriestände, Netzbezug, Einspeisung, Kosten und Zählerstände.
     * **JSON**: Vollständiger strukturierter Rohdaten-Export für eigene Auswertungen, Grafana oder Home Assistant.
     * **PDF-Energiebericht**: Formatierter Monats- oder Zeitraum-Report mit Diagrammen, Autarkiegrad, Eigenverbrauchsquote, CO₂-Einsparung und Kostenübersicht.
* **Ergebnis**: Revisionssichere Datenarchivierung, maximale Transparenz und einfache Weitergabe an Steuerberater oder Hausverwaltungen.

---

### 🟡 TIER 2: ALERTING & PUSH-BENACHRICHTIGUNGEN

#### 4. 🚨 Task 5.6: Intelligentes Alert- & Anomalie-Erkennungssystem (Umgesetzt)
* **Maßnahmen**:
  1. Hintergrundprüfung auf Kern-Anomalien:
     * 🔥 **„Keine PV erkannt“**: Globalstrahlung vorhanden, aber PV-Leistung $= 0\,\text{W}$.
     * 🔥 **„Batterie leer / Tiefstand“**: SoC fällt unter Schwellwert (z. B. $< 10\,\%$).
     * 🔥 **„Unerwarteter Nachtverbrauch“**: Dauerlast $> 1.500\,\text{W}$ nachts.
     * 🟢 **„Börsenstrom-Preischance / Negativer Strompreis“**: Günstige Ladefenster erkennen.
  2. Dedizierte Alarmzentrale-Seite (`/app/alerts`), Modal & Live-Badge in der Sidebar.
* **Ergebnis**: Proaktiver Schutz vor Ertragsverlust, Tiefentladung und Stromverschwendung.

#### 5. 📲 Task 5.9: Mobile Push & Notification Engine (Backend)
* **Maßnahmen**:
  1. Django `notifications`-App mit `DeviceToken`-Verwaltung (iOS/Android/Web-Push).
  2. Integration von Firebase Cloud Messaging (`FCM`) und Apple Push Notification Service (`APNs`).
  3. Konfigurierbare Benachrichtigungs-Präferenzen, Ruhezeiten (Quiet Hours) und Dringlichkeitsstufen.
* **Ergebnis**: Sofortige Zustellung kritischer Alarme auf das Smartphone.

---

### 🔵 TIER 3: ÖKOSYSTEM-BRIDGES & HARDWARE-INTEGRATION

#### 6. 📄 Task 5.7: Deklaratives Device-Profile Addon-System (🟢 ABGESCHLOSSEN)
* **Maßnahmen**:
  1. Trennung von Transport (MQTT/REST) und Daten-Mapping.
  2. YAML-Profil-Bibliothek (`sungrow_sh10rt.yaml`, `sma_tripower.yaml`, `fronius_solarapi.json`, `deye_hybrid.yaml`, `huawei_fusionsolar.yaml`).
  3. Automatischer Mapper in die Sharegy-Standardmetriken (`pv_power_w`, `battery_soc`, `grid_power_w`).
* **Ergebnis**: Plug & Play Einbindung neuer Wechselrichter in 10 Minuten ohne Backend-Codeänderung.

#### 7. 🔌 Task 5.8: Bi-direktionale Plugins: Home Assistant, Grafana & ioBroker (🟢 ABGESCHLOSSEN / 100%)
* **Maßnahmen**:
  1. **Home Assistant Custom Component (`plugins/homeassistant/`)**:
     * 9 automatische Sensoren (PV, Last, Netz, Batterie-SoC, Autarkie, Börsenpreis, Best-Ladefenster).
     * Bidirektionaler Service `sharegy.push_telemetry` zur verschlüsselten Übertragung lokaler Zähler.
  2. **Grafana REST-Bridge & Cockpit (`plugins/grafana/`)**:
     * SimpleJSON / Infinity kompatible Endpoints (`/api/grafana/search`, `/query`, `/annotations`).
     * Fertiges `sharegy_energy_cockpit.json` Dashboard Template.
  3. **ioBroker & Shelly MQTT Integration**: 2-Wege-Sync über globale MQTT-Zugangsdaten.
* **Ergebnis**: 100 % Kompatibilität zu Home Assistant, Grafana und Smart-Home-Umgebungen.

#### 8. ⚡ Task 5.12 (Matter Hub): Matter Bridge & CSA Matter 1.3 Energy Management (🟢 ABGESCHLOSSEN / 100%)
* **Maßnahmen**:
  1. **Matter 1.3 Cluster Engine (`providers.matter`)**:
     * `0x0090` Electrical Power Measurement (Live W, V, A, Power Factor).
     * `0x0091` Electrical Energy Measurement (kWh Zählerstände).
     * `0x0006` On/Off Switch & Relais Control.
     * `0x0098` / `0x0099` Device Energy Management & EVSE Wallbox-Ladedrosselung.
  2. **Commissioning Engine**:
     * Matter QR-Code Parser (`MT:...`), 11-/21-stelliger Pairing-Code & Setup-PIN Decoder.
  3. **Frontend UI**:
     * `MatterHubCard.jsx` & `MatterPairingModal.jsx` in `InterfacesPage.jsx`.
* **Ergebnis**: Direkte, herstellerunabhängige Anbindung modernster Matter-Geräte (Eve Energy, Shelly Matter, Wallboxen).

---

### 🟣 TIER 4: MOBILE APPS & USER EXPERIENCE

#### 9. 📱 Task 5.10: Native iOS & Android Apps via Capacitor
* **Maßnahmen**:
  1. Capacitor-Integration für die React/Tailwind Web-App.
  2. Biometrie-Login (FaceID, TouchID, Fingerabdruck).
  3. Native Lockscreen- und Homescreen-Widgets (Live-PV, Batterie-SoC, Optimizer-Fahrplan).
  4. Build-Pipelines für Apple App Store & Google Play Store.
* **Ergebnis**: Echte App-Store-Präsenz, maximale Kundenbindung und täglicher Blickfang über Widgets.

#### 10. ❓ Task 5.4 & 5.5: Kontextuelles Help-System & FAQ/Handbuch (DE/EN) (🟢 ABGESCHLOSSEN / 100%)
* **Maßnahmen**:
  1. In-App Side-Drawer mit Quick-Guides auf allen Hauptseiten.
  2. Durchsuchbares FAQ- und Wissensportal (8 Kategorien, 14 umfassende Artikel) inkl. Grafana, Home Assistant und Matter 1.3.
  3. Zweisprachig gepflegt (Deutsch / Englisch).
* **Ergebnis**: Nahtloses Onboarding und minimale Support-Aufwände.

---

### 🟠 TIER 5: MONETARISIERUNG & EMS-ABRECHNUNG

#### 11. 💳 Task 5.11: Subscription- & SaaS-Lizenzmodell (Stripe / Feature-Gating)
* **Zweck**: Kommerzielle Monetarisierung für Endkunden (B2C) und Prosumer/Installateure (B2B).
* **Maßnahmen**:
  1. **Tarifstufen-Definition**:
     * 🆓 **Free / Community**: 1 Haushalt, 7 Tage Historie, Basis-Monitoring, Standard-Alarmierung.
     * ⚡ **Pro HEMS (€ 4,99 / Monat)**: Unbegrenzte Historie, 48h KI-Last- & Solar-Prognose, Intelligenter Dynamic-Tariff-Optimizer, Push-Notifications, Wallbox-/Wärmepumpen-Aktorik.
     * 🏢 **Multi-Home / Vermieter (€ 14,99 / Monat)**: Mehrere Zähler/Haushalte, Mieterstrom-Allokation, PDF-Abrechnungs-Generator.
  2. **Payment & Stripe Integration**:
     * Stripe Checkout, Customer Portal (Kreditkarte, SEPA-Lastschrift, PayPal, Apple/Google Pay).
     * Webhook-Handler für automatische Verlängerung, Kündigung, Upgrade und Downgrade.
  3. **Feature-Gating & Entitlements**:
     * Deklarative Berechtigungsprüfung im Backend (`user.has_feature("optimizer_pro")`) und Frontend (`<FeatureGate feature="pro_forecast">`).
* **Ergebnis**: Automatisierte Zahlungsabwicklung, wiederkehrender MRR (Monthly Recurring Revenue) und klarer Kundennutzen.

#### 12. 📊 Task 5.14: Trends & Historische Zeitreihen der virtuellen Zähler (🟢 ABGESCHLOSSEN / 100%)
* **Zweck**: Tiefgehende historische Analyse, Trend-Erkennung und grafische Gegenüberstellung aller virtuellen Unterzähler (Wallbox, Wärmepumpe, Einliegerwohnung, Restverbrauch etc.).
* **Maßnahmen**:
  1. **Historische Zeitreihen-Visualisierung**:
     * Interaktive Verbrauchs- und Kostenkurven (Tag, Woche, Monat, Jahr & gleitender Durchschnitt) für jeden einzelnen virtuellen Zähler.
  2. **Quellen-Aufschlüsselung je virtuellem Verbraucher**:
     * Transparente Darstellung: Zu wie viel Prozent wurde der Verbrauch eines Zählers durch *PV-Direktverbrauch*, *Batterie-Entladung* oder *Netzbezug* gedeckt?
  3. **Multi-Zähler-Vergleich & Anteils-Analyse**:
     * Gestapelte Balken- und Sankey-Diagramme zur Visualisierung der prozentualen Verbrauchsanteile (z. B. Wärmepumpe vs. Wallbox vs. Grundlast).
  4. **Kosten- & Einsparungs-Trends**:
     * Ermittlung vermiedener Stromkosten durch Eigenverbrauchsnutzung je Verbraucher im historischen Zeitverlauf.
* **Ergebnis**: Lückenlose Verbrauchstransparenz für alle Sub-Stromkreise und verlässliche Datengrundlage zur Dimensionierung künftiger Speicher- und PV-Erweiterungen.

