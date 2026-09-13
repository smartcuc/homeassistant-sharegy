# 🚀 [WIP] General Release Testen, Qualitätssicherung & Markteintritt (Go-to-Market)

**Status:** 🟡 In Ausarbeitung / Launch-Vorbereitung  
**Fortschritt:** 🟢 85 %  
**Priorität:** 🔴 Kritisch (Ziel: Q4 2026 / Q1 2027)  
**Lead / Module:** `release`, `devops`, `compliance`, `frontend`, `billing`, `devices`  

---

## 🎯 1. Executive Summary & Zielsetzung

Dieses Dokument definiert den verbindlichen Ablauf für das **General Release Testing (E2E / QA)**, die regulatorische Zertifizierung sowie den **strukturierten Markteintritt (Go-to-Market)** von **Sharegy** im DACH-Raum.

### Kernziele:
1. **Dual-App Ökosystem Launch**: Zeitgleicher Rollout von **Sharegy Home** (`de.sharegy.app`) für Privatnutzer/Mieter und **Sharegy Pro** (`de.sharegy.pro`) für Installateure, Stadtwerke & Hausverwaltungen.
2. **Zero-Defect Telemetrie-Pipeline**: Garantierte Ingestion von 10.000+ parallelen IoT-Streams (Shelly WSS, Inverter Cloud APIs, MQTT, wMSB/SMGW) mit Sub-Sekunden Latenz.
3. **Regulatorische Konformität**: Vollständige Erfüllung von **§ 14a EnWG** (netzdienliche Dimmung & Kaskadierung) und **§ 42b EnWG / MsbG** (15-Minuten-Lastgänge & eichrechtskonforme Abrechnung).
4. **Partner- & Vertriebs-Skalierung**: Automatisierter Onboarding-Trichter für Solarteure und White-Label-Mandanten mit Instant-Provisioning.

---

## 🏗️ 2. Dual-App Release Architektur

```
                            ┌────────────────────────────────────────┐
                            │        Sharegy Cloud Backend           │
                            │   (Django 5, PostgreSQL, TimescaleDB,  │
                            │    Redis Pub/Sub, Mosquitto MQTT)      │
                            └──────────────────┬─────────────────────┘
                                               │
                     ┌─────────────────────────┴─────────────────────────┐
                     ▼                                                   ▼
┌──────────────────────────────────────────┐    ┌──────────────────────────────────────────┐
│      Sharegy Home (B2C & Prosumer)       │    │       Sharegy Pro (B2B & Partner)        │
│   • App ID: de.sharegy.app               │    │   • App ID: de.sharegy.pro               │
│   • Rollen: HEMS Prosumer, Mieterstrom   │    │   • Rollen: Installateur, Admin, wMSB    │
│   • UI: EMS Live-Flow, Einsparungen,     │    │   • UI: Flottenüberwachung, 1-Klick WSS  │
│     Batteriesteuerung, § 14a Status      │    │     Diagnose, Mandanten-Billing, EDIFACT │
└──────────────────────────────────────────┘    └──────────────────────────────────────────┘
```

---

## 🧪 3. Umfassende Test- & QA-Matrix

### 3.1 Backend & Automatisierte Test-Suites

| Test-Kategorie | Prüfumfang | Tooling / Framework | Erfolgs-Kriterium |
|---|---|---|---|
| **Core & Ingestion** | Adapter-Parsing (Growatt, Sungrow, Fronius, Shelly, Victron) | `pytest`, `devices.tests_self_test` | 100% Pass, 0 Fehlinterpretationen bei 0 W Nachtwerten |
| **Billing & Quoten** | Dynamische Tarife, $Ct/\text{kWh}$ Aufteilung, Mieterstrom | `billing.test_multi_community_management` | Cent-genaue Abrechnung, 0 Rundungsfehler |
| **EMS Merit-Order** | PV-Überschuss, Batterieladung, § 14a Drosselung auf $4{,}2\,\text{kW}$ | `energy.tests_flow_engine` | Einhaltung der Leistungsbegrenzung in $< 200\,\text{ms}$ |
| **Multi-Tenancy** | Datenisolation zwischen WEGs & White-Label Mandanten | Django Tenant Test Runner | Keine Datenlecks zwischen Tenants (Mandanten-Sicherheit) |

### 3.2 Last-, Stress- & Latenz-Tests

* **Szenario A (Lastspitze)**: Simulation von $5.000$ zeitgleichen Shelly Pro 3EM WebSocket-Verbindungen (Push-Intervall: $1\,\text{s}$).
  * *Ziel:* CPU-Auslastung $< 60\,\%$, Redis-Queue $< 50\,\text{ms}$ Latenz, 0 Verbindungsabbrüche.
* **Szenario B (Offline-Resilienz)**: Unterbrechung der Internetverbindung eines Smart Homes für $48\,\text{h}$.
  * *Ziel:* Reibungsloser Reconnect und lückenlose Store-and-Forward Nachübertragung ohne Duplikate.

### 3.3 Hardware- & Hersteller-Kompatibilitäts-Audit

```
┌─────────────────┬──────────────────┬─────────────────┬──────────────────┐
│ Hersteller / Typ│ Schnittstelle    │ Protokoll / Auth│ Status / Freigabe│
├─────────────────┼──────────────────┼─────────────────┼──────────────────┤
│ Shelly Gen2/3   │ WSS Outbound     │ TLS (Port 443)  │ 🟢 Zertifiziert  │
│ Sungrow SH-Serie│ Cloud API / OAuth│ REST Bearer     │ 🟢 Zertifiziert  │
│ Growatt SPH/MIN │ ShineServer / V2 │ OpenAPI MD5/Sign│ 🟢 Zertifiziert  │
│ Fronius Gen24   │ Solar.web REST   │ API-Key         │ 🟢 Zertifiziert  │
│ SolarEdge SE    │ Monitoring API   │ HTTP API-Key    │ 🟢 Zertifiziert  │
│ Kostal Plentic. │ Kostal Solar App │ REST Digest     │ 🟢 Zertifiziert  │
│ Victron Cerbo GX│ VRM Portal / MQTT│ Token / TLS     │ 🟢 Zertifiziert  │
│ Deye Hybrid     │ Solarman Cloud   │ REST Bearer     │ 🟢 Zertifiziert  │
│ wMSB Gateways   │ BSI TR-03109-1   │ CLS / HAN WSS   │ 🟡 In Validierung│
└─────────────────┴──────────────────┴─────────────────┴──────────────────┘
```

---

## 📱 4. App Store & Google Play Store Launch-Checkliste

### 4.1 iOS App Store (Apple)
* [x] Bundle IDs registriert: `de.sharegy.app` und `de.sharegy.pro`
* [x] **Account Deletion Flow**: DSGVO-konforme Selbstlöschung direkt im Nutzerprofil (`/app/profile`) implementiert.
* [x] **App Privacy Details (Nutrition Labels)**: Deklaration von Telemetrie- und Verbrauchsdaten ohne Tracking Dritter.
* [x] **Sign in with Apple / Magic Login**: Passwortloser Login ohne Drittanbieter-Zwang.
* [x] **iPad / Tablet Responsive Layouts**: Split-Screen und responsive Navigation validiert.

### 4.2 Google Play Store (Android)
* [x] Package Names konfiguriert: `de.sharegy.app` und `de.sharegy.pro`
* [x] **Target SDK Level**: Android 14 / 15 (API 34/35) Kompatibilität.
* [x] **App-Berechtigungen minimiert**: Keine unnötigen Hintergrund-Standort- oder Kamera-Rechte.
* [x] **Keystore & Signing**: Release-Keystores in CI/CD Secret Store hinterlegt.

---

## 🛡️ 5. Sicherheits-Audit & DSGVO-Compliance

1. **Penetration Testing**:
   * Überprüfung aller REST- und WebSocket-Endpunkte auf IDOR (Insecure Direct Object References).
   * Rate-Limiting gegen Brute-Force auf Login- und Token-Endpunkten.
2. **Eichrecht & Revisionssicherheit**:
   * Unveränderbarkeit von 15-Minuten-Zählerständen in der Datenbank (TimescaleDB Chunk-Signierung).
   * Exportformate nach BNetzA-Standard (MSCONS, EDIFACT, CSV).
3. **Datensparsamkeit**:
   * Anonymisierte Telemetrie-Speicherung für Machine-Learning-Prognosen.
   * Automatische Löschfristen für Roh-Telemetriedaten nach 24 Monaten (Aggregierung zu Monatswerten).

---

## 📈 6. Go-To-Market (GTM) Strategie & Rollout-Phasen

```
Phase 1: Closed Beta (Q3 2026)      ──► 50 Pionier-Installateure & 500 Test-Haushalte (HEMS & Mieterstrom)
Phase 2: Partner Onboarding (Q4 2026)──► Freigabe Sharegy Pro für Stadtwerke, Hausverwaltungen & Solarteure
Phase 3: Public General Release      ──► Bundesweiter Launch in App Store & Google Play mit Whitelabel-Mandanten
```

### 6.1 Partner-Akquise & Onboarding-Trichter:
* **Self-Service Partner-Registrierung**: Installateure können unter `/pro` in $< 3$ Minuten ihren Partner-Account anlegen und Kunden-Anlagen via QR-Code verknüpfen.
* **White-Label Mandantenfähigkeit**: Stadtwerke und Energieversorger erhalten ihr eigenes Branding (Custom Logo, Farbwelt, eigene Domain & SSL-Zertifikat) innerhalb von 24 Stunden.

---

## 🚨 7. Incident Response & 24/7 SLA Playbook

* **Monitoring & Tracing**: Sentry (Frontend Crash-Reporting), Prometheus & Grafana (Server-Health & Ingestion Latenz).
* **Alerting**: PagerDuty-Kopplung bei Ingestion-Ausfällen $> 0{,}5\,\%$ über 5 Minuten.
* **Disaster Recovery**: Tägliche verschlüsselte Backups auf georedundanten Cloud-Storage mit $< 15\,\text{min}$ RPO (Recovery Point Objective).
