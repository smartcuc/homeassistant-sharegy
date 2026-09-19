# 🚀 General Release Testen, Qualitätssicherung & Markteintritt (Go-to-Market Masterplan)

**Dokument-Status:** Offizielle GTM- & QA-Systemdokumentation  
**Version:** 2.0.0 (GTM & QA Master Edition)  
**Stand:** 19. September 2026 (v5.4 Live)  

---

## 🧭 Inhaltsverzeichnis
1. [Executive Summary & Markteintritts-Philosophie](#1-executive-summary--markteintritts-philosophie)
2. [Die 4-Phasen-Markteintritts-Roadmap](#2-die-4-phasen-markteintritts-roadmap)
3. [E2E-Qualitätssicherung & Test-Matrix](#3-e2e-qualitaetssicherung--test-matrix)
4. [Hardware- & Wechselrichter-Zertifizierung](#4-hardware--wechselrichter-zertifizierung)
5. [App Store & Google Play Launch-Voraussetzungen](#5-app-store--google-play-launch-voraussetzungen)
6. [Sicherheits-Audit, DSGVO & Eichrecht](#6-sicherheits-audit-dsgvo--eichrecht)
7. [Detaillierte Go-To-Market Playbooks](#7-detaillierte-go-to-market-playbooks)

---

## 🎯 1. Executive Summary & Markteintritts-Philosophie

Der Erfolg von Sharegy basiert auf einem **praxisnahen, 2-stufigen Markteintritt**:
1. **Stufe 1 (Bodenhaftung & Traktion):** Fokus auf das, was **heute sofort funktioniert**:
   * **Private Prosumer & Haushalte:** Kostenloses HEMS-Monitoring, PV-Überschussladen, dynamische Stromtarife und Autarkie-Optimierung.
   * **Fachpartner & Solarteure:** Kostenloses Flottenmanagement, 3-Sekunden-Inbetriebnahmetest mit PDF-Protokoll und dauerhafter Kunden-Wartungszugang.
   * **Mehrfamilienhäuser & WEGs:** Gemeinschaftliche Gebäudeversorgung (§ 42b EnWG) und Mieterstrom-Abrechnungen ohne Großkraftwerks-Zertifizierung.
2. **Stufe 2 (Skalierung & Flexibilitätsmärkte):** Sobald eine installierte Basis von **100+ aktiven Speichern** im Feld erprobt ist, wird die Schwarm-Vermarktung (VPP / Flex-Bonus) mit Master-Aggregatoren (Next Kraftwerke / Statkraft) aktiviert.

---

## 🗺️ 2. Die 4-Phasen-Markteintritts-Roadmap

```
+───────────────────────────────────────────────────────────────────────────────────────────+
| PHASEN-ROADMAP ZUM REGULATORISCH & WIRTSCHAFTLICH SICHEREN MARKTEINTRITT                 |
+───────────────────────────────────────────────────────────────────────────────────────────+

[ Phase 1: Closed Beta (Monat 1-2) ]
  • 10 befreundete Solarteure / Elektro-Fachbetriebe
  • 50 Pilot-Haushalte (Sungrow, SMA, Fronius, Deye, Shelly)
  • E2E-Härtung der Latenz, Push-Telemetrie und Fehler-Triage
                                 │
                                 ▼
[ Phase 2: Partner- & Prosumer-Launch (Monat 3-4) ]
  • Freigabe von Sharegy Pro für Fachpartner & Installateure
  • B2C-Rollout über PV-Communities & Social Proof
  • Launch von Energy Sharing (§ 42b EnWG) für Mehrfamilienhäuser & WEGs
                                 │
                                 ▼
[ Phase 3: Feld-Stresstest für Speichersteuerung (Monat 5-6) ]
  • Flottengröße: 100 bis 300 Heimspeicher im Feld
  • Geschlossene Testabrufe (Interne Netz- und Ladelasttests)
  • Vorbereitung des VPP-Audits & Präqualifikation
                                 │
                                 ▼
[ Phase 4: Kommerzieller VPP- & Flexibilitäts-Start (Monat 7+) ]
  • Aufschaltung an Master-Aggregator (Next Kraftwerke / Statkraft)
  • Aktivierung des 80/20 Flexibilitäts-Bonus für Endkunden
  • bundesweite Skalierung über Stadtwerke- & Whitelabel-Partner
```

---

## 🧪 3. E2E-Qualitätssicherung & Test-Matrix

| Test-Kategorie | Prüfumfang & Test-Szenarien | Tooling & Automatisierung | Akzeptanz-Kriterium |
| :--- | :--- | :--- | :--- |
| **1. Telemetrie & Ingestion** | Ingestion von Sungrow, Fronius, SMA, Deye, Shelly Pro 3EM, Home Assistant WSS | `devices.tests_self_test`, WebSocket Stress-Runner | Latenz $< 2\,\text{s}$, 0 Datenverlust bei 24h Dauerbetrieb |
| **2. Billing & 15m-Clearing** | § 42b EnWG Allokationsmodelle (Dynamisch, MEA-Schlüssel, Hybrid), DATEV-Export | `billing.test_multi_community_management` | 100% cent-genaue Übereinstimmung der Saldierung |
| **3. Optimizer & Merit-Order** | PV-Überschussladung Wallbox, Wärmepumpen-SG-Ready, § 14a Drosselung auf $4{,}2\,\text{kW}$ | `energy.tests_flow_engine` | Reaktionszeit $< 5\,\text{s}$, Einhaltung der Netzkontingente |
| **4. Offline-Resilienz** | 48-Stunden Internet-Ausfall des lokalen HEMS | SQLite Store & Forward Buffer Test | Lückenlose Nachübertragung nach Reconnect ohne Duplikate |
| **5. Multi-Tenancy & RBAC** | Rollentrennung: Private EMS vs. Partner vs. Tenant-Admin vs. Support-Agent | Django Auth Test Suites | Strikte Datenisolation, keine Mandanten-Lecks |

---

## 🔌 4. Hardware- & Wechselrichter-Zertifizierung

```
+───────────────────+────────────────────+───────────────────+────────────────────+
| Hersteller / Typ  | Schnittstelle      | Protokoll / Auth  | Freigabe-Status    |
+───────────────────+────────────────────+───────────────────+────────────────────+
| Shelly Gen2/3/Pro | WSS Outbound       | TLS (Port 443)    | 🟢 Voll zertifiziert|
| Sungrow SH-Serie  | Modbus TCP / Cloud | Port 502 / REST   | 🟢 Voll zertifiziert|
| SMA Tripower/SB   | Speedwire / Modbus | Port 502 (Unit 3) | 🟢 Voll zertifiziert|
| Fronius Gen24/Symo| SolarAPI / Modbus  | Port 502 / JSON   | 🟢 Voll zertifiziert|
| SolarEdge SE      | Modbus TCP SunSpec | Port 1502 / 502   | 🟢 Voll zertifiziert|
| Deye Hybrid       | Modbus TCP / RTU   | Port 502 SunSpec  | 🟢 Voll zertifiziert|
| Huawei SUN2000    | Modbus TCP Bridge  | Port 502          | 🟢 Voll zertifiziert|
| Wallboxen (OCPP)  | OCPP 1.6-J CSMS    | WSS (Port 443)    | 🟢 Voll zertifiziert|
| Home Assistant    | Native HACS Bridge | Outbound WSS      | 🟢 Voll zertifiziert|
| SMGW CLS-Kanal    | BSI TR-03109-1     | TLS CLS Proxy     | 🟢 Voll zertifiziert|
+───────────────────+────────────────────+───────────────────+────────────────────+
```

---

## 📱 5. App Store & Google Play Launch-Voraussetzungen

### 🍏 Apple App Store (`de.sharegy.app` & `de.sharegy.pro`)
* [x] **Account Deletion Flow:** DSGVO-konforme Selbstlöschung im Profil (`/app/profile`) implementiert.
* [x] **App Privacy Labels:** Transparente Deklaration aller Telemetrie- und Energiedaten.
* [x] **Passwortloser Login:** Magic Login per E-Mail und Sign-in with Apple.
* [x] **Responsive Layouts:** Optimiert für iOS, iPadOS und Web-App (PWA).

### 🤖 Google Play Store (`de.sharegy.app` & `de.sharegy.pro`)
* [x] **Target SDK Level:** Android 14/15 (API 34/35) Kompatibilität.
* [x] **Rechte-Minimierung:** Keine unnötigen Standort-, Kamera- oder Speicherberechtigungen.
* [x] **Keystore & Signierung:** Release-Keys im sicheren Secrets-Vault hinterlegt.

---

## 🛡️ 6. Sicherheits-Audit, DSGVO & Eichrecht

1. **Penetration Testing & API-Sicherheit:**
   * Schutz aller REST- und WebSocket-Endpunkte gegen IDOR und Brute-Force via Rate-Limiting.
2. **Revisionssicherheit nach BNetzA-Standard:**
   * 15-Minuten-Zeitreihen in TimescaleDB manipulationssicher archiviert.
   * Exportfähig nach DATEV-, EDIFACT- und MSCONS-Standards.
3. **Datensparsamkeit:**
   * Anonymisierte Telemetrie für Prognose-Algorithmen; automatische Verdichtung von 1-Sekunden-Rohdaten nach 30 Tagen zu 15-Minuten-Werten.

---

## 📚 7. Detaillierte Go-To-Market Playbooks

Für die operative Markteinführung stehen zwei dedizierte Playbooks zur Verfügung:

1. **👨‍👩‍👧‍👦 [Consumer & Prosumer GTM Playbook](./GTM_PLAYBOOK_CONSUMER_AND_PROSUMER.md):**
   * Zielgruppen (Dach-PV, Balkonkraftwerk, E-Auto, Mieter).
   * 0-zu-Aha Onboarding-Trichter ($< 120\,\text{Sekunden}$).
   * Virale Sharing-Schleifen & Community-Akquise.
   * Freemium-zu-Pro Conversion Strategie.

2. **🔧 [Partner & Solarteure GTM Playbook](./GTM_PLAYBOOK_PARTNERS_AND_INSTALLERS.md):**
   * Zielgruppen (Solarteure, Elektro-Fachbetriebe, Stadtwerke, Hausverwaltungen).
   * Nutzenversprechen: Kostenloses Flottenmanagement, 3-Sekunden-Inbetriebnahmetest mit PDF-Protokoll.
   * Kaltakquise-Skripte, Partner-Schulung & Zertifizierungsprogramm.
   * Partner-Incentives & wiederkehrende Service-Erlöse.
