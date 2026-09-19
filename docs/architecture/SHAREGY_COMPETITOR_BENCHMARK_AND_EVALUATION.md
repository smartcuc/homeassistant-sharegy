# 🏆 Sharegy EMS & Energy Sharing: Strategischer Mitbewerber-Vergleich & Gesamtevaluation

**Dokument-Version**: 5.4  
**Stand**: 19. September 2026 (Live Release v5.4)  
**Zielgruppe**: Investoren, B2B-Partner, Energiegenossenschaften, Stadtwerke, Hausverwaltungen & Management  

---

## Executive Summary

Sharegy besetzt eine **einzigartige Marktposition im europäischen Energiemarkt**: Es verbindet ein **herstellerunabhängiges, hochperformantes Home Energy Management System (EMS, Säule 1)** mit einer **vollständigen, eichrechts- und GoBD-konformen Abrechnungs-, Clearing- und VPP-Plattform für Energy Sharing Communities, Mieterstrom & Großquartiere (Säule 2)**.

Mit dem **Release von v5.4 (Zentraler Dokumenten- & Export-Manager, Granulare Enterprise RBAC-Matrix, Skeleton-Loading & SWR UX, BNetzA CLS § 14a Live Gateway, VPP 80/20 Market Clearing und 46 zweisprachigen Handbuch-Artikeln)** eliminiert Sharegy alle bisherigen Markteinstiegshürden:
1. **Keine teure Hardware-Box nötig**: Kopplung via Cloud-API (10 Inverter-Hersteller), Outbound-WSS (Shelly), ioBroker, Home Assistant oder MQTT in unter 60 Sekunden.
2. **Echtes Multi-Asset Lastmanagement**: Dynamische Merit-Order-Kaskade für Heimspeicher, BWWP (Boost bis 60°C), Wallbox (OCPP 1.6-J), Wärmepumpen-SG-Ready und § 14a EnWG $4{,}2\,\text{kW}$ Netzdrosselung.
3. **Virtuelles Kraftwerk (VPP) & 80/20 Erlös-Clearing**: Automatisierte Teilnahme dezentraler Speicher an Regelleistungsmärkten (aFRR/SRL) und Intraday-Arbitrage mit monatlichen Gutschriften.
4. **Zentraler GoBD-konformer Dokumenten- & Export-Hub (`/app/documents`)**: Streaming-Exporte für DATEV, BNetzA MSCONS 2.2b, UTILMD, PDF und SHA-256 Hashketten-Validierung.
5. **Granulare Enterprise RBAC-Rollenmatrix**: Rollenbasierte Arbeitsbereiche für `SuperAdmin`, `Dispatcher`, `Billing Specialist`, `Field Technician` und `Auditor / Read-Only`.

---

## 📊 1. Großer Feature- & Architektur-Matrix-Vergleich

| Feature / Fähigkeit | **Sharegy (Dual-Core v5.4)** ⚡ | **Exnaton (PowerQuartier)** 🇨🇭🇩🇪 | **EDA (Energiedatenplattform)** 🇦🇹 | **1Komma5° Heartbeat** 🇩🇪 | **Tibber (Pulse)** 🇳🇴🇩🇪 | **Clever-PV** 🇩🇪 | **Home Assistant / evcc** 🌐 |
|---|:---:|:---:|:---:|:---:|:---:|:---:|:---:|
| **Primärer Fokus** | **Dual-Core: Home EMS + Energy Sharing + VPP** | B2B Energy Sharing / Stadtwerke | Gesetzlicher Datenaustausch / VNB | Hardware-Verkauf + dynamischer Tarif | Dynamischer Tarif + Zähler | B2C Cloud-Schalter | DIY Smart Home & EV-Laden |
| **Hardware-Freiheit (Zero-Lock-in)** | 🟢 **100% Offen** (Shelly WSS, OCPP 1.6-J, Inverter Cloud APIs, ioBroker, HA, MQTT) | 🟡 Nur Zählerdaten (MSCONS/SFTP) | 🔴 Nur registrierte Smart Meter (VNB) | 🔴 Nur Heartbeat-Box & Partner-WR | 🟡 Nur Pulse IR-Lesekopf | 🟢 Cloud-APIs | 🟢 Open-Source |
| **Zero-Hardware Cloud Inverter (1-Klick)** | 🟢 **Ja** (Sungrow, Fronius, SMA, SolarEdge, Huawei, Deye, Hoymiles, GoodWe, Kostal, Victron) | 🔴 Nein (Nur Zählerlastgänge) | 🔴 Nein (Nur SMGW) | 🔴 Nein (Benötigt Heartbeat-Box) | 🔴 Nein (Nur Pulse am Zähler) | 🟡 Ja (Aber kein Energy Sharing) | 🟡 Über HACS-Add-ons |
| **Smart Load Hub & Merit-Order** | 🟢 **Ja** (Live Power Budget, 4 Autopilot Modi, Merit-Order, 24h-Fahrplan) | 🔴 Keine Laststeuerung | 🔴 Keine Steuerung | 🟡 Proprietärer Heartbeat-Plan | 🟡 Nur EV & WP | 🟡 Nur manuelle Regeln | 🟡 Manuelle YAML/Automations |
| **§ 14a EnWG CLS SMGW Gateway** | 🟢 **Ja** (BSI TR-03109-1 Ingest, FNN Quittung, $4{,}2\,\text{kW}$ Summenbudget) | 🔴 Nein | 🔴 Nein | 🟡 Nur in Neuanlagen | 🔴 Nein | 🔴 Nein | 🔴 Keine Zertifizierung |
| **Virtuelles Kraftwerk (VPP) & Clearing** | 🟢 **Ja** (aFRR/SRL Pooling, 96-Fahrplan, 80/20 Erlös-Clearing & Statements) | 🔴 Keine VPP-Engine | 🔴 Keine | 🟡 Proprietärer 1K5-Pool | 🟡 Nur Tibber-Laststeuerung | 🔴 Keine | 🔴 Keine |
| **Zentraler Dokumenten-Hub & GoBD** | 🟢 **Ja** (`/app/documents`, DATEV, MSCONS, PDF, SHA-256 Hashkette) | 🟡 Nur PDF-Export | 🟡 XML-Rohdaten | 🔴 Nur Stromrechnung | 🔴 Nur Monatsrechnung | 🔴 Keine | 🔴 Keine |
| **Granulare Enterprise RBAC-Matrix** | 🟢 **Ja** (SuperAdmin, Dispatcher, Billing, Tech, Auditor) | 🟡 Basis Admin/User | 🔴 Rollen vorgegeben | 🔴 Nur Endkunde | 🔴 Nur Endkunde | 🔴 Keine | 🟡 Basis-User |
| **Skeleton-Loading & SWR UX** | 🟢 **Ja** (Zero Layout Shift, TanStack SWR Caching $< 20\,\text{ms}$) | 🔴 Standard Ladezeiten | 🔴 Träge VNB-Masken | 🟡 App-Ladezeiten | 🟢 Schnelle App | 🟡 Klassisches Polling | 🟡 Hängt von Server ab |
| **Wallbox- & EV-Laden (Natives CSMS)** | 🟢 **Ja** (OCPP 1.6-J Server, PV-Überschuss, Börsenpreis-Laden) | 🔴 Keine | 🔴 Keine | 🟢 Ja (Heartbeat) | 🟢 Ja (Tibber Smart Charging) | 🟢 Ja (Cloud API) | 🟢 Ja (evcc) |
| **Virtueller Summenzähler (§ 42b EnWG)** | 🟢 **Ja** (15m NAP-Zeitreihen, 3 Allokationsmodelle, rechtssichere PDFs) | 🟡 Nur Summen-Export | 🔴 Keine | 🔴 Nein | 🔴 Nein | 🔴 Nein | 🔴 Nein |
| **Native Mobile App (Android/iOS)** | 🟢 **Ja** (Capacitor 7 Native Shell, Fastlane Release, FCM Push) | 🟡 Web-Portal Only | 🔴 Kein Endkunden-App | 🟢 Ja (Native App) | 🟢 Ja (Native App) | 🟢 Ja (PWA) | 🟢 Home Assistant App |
| **Säule 2: Energy Sharing & Clearing** | 🟢 **Integriert** (RBAC, 15m Slots, Tarife, Multi-Community Hub) | 🟢 **Integriert** (Kernfokus B2B) | 🟡 Reiner Daten-Hub (keine Endabrechnung) | 🔴 Nein | 🔴 Nein | 🔴 Nein | 🔴 Nein |
| **Zahlung & Billing-Stack (SaaS)** | 🟢 **Stripe Checkout** (Karten, SEPA, PayPal, Klarna, Amazon Pay) | 🔴 Manuelle Enterprise-Rechnung | 🔴 Staatlich finanziert | 🔴 Nur Stromrechnung | 🟡 Nur Kreditkarte / SEPA | 🟡 Stripe Basis | 🔴 Keine |
| **Internationalisierung (i18n)** | 🟢 **6 EU-Sprachen** (🇩🇪 DE, 🇬🇧 EN, 🇵🇱 PL, 🇫🇷 FR, 🇮🇹 IT, 🇪🇸 ES) | 🟡 DE / EN | 🔴 Nur DE | 🔴 Nur DE | 🟡 DE / EN / NO / SE / NL | 🟡 DE / EN | 🟢 Community-Übersetzungen |
| **Helpcenter & Online-Handbuch** | 🟢 **46 Deep-Dive Artikel** (DE & EN, 11 Kategorien, RBAC, GoBD, CLS, VPP) | 🔴 Nur Doku für Admins | 🟡 Regulatorische PDFs | 🔴 Nur Support-Hotline | 🟡 FAQ-Center | 🟡 Forum / FAQ | 🟢 Community-Docs |
| **Einstiegshürde & Setup-Kosten** | **Self-Service SaaS (ab 0 € Free / 7,99 € Pro / B2B)** | **> 10.000 € Setup + B2B-Vertrag** | **VNB-only** | **> 20.000 € Neuanlage** | **Tarifwechsel** | **Abo (nur Schalten)** | **Hoher Setup-Aufwand** |

---

## 🔍 2. Detaillierte Mitbewerber-Analyse im Profil

### 1. Exnaton (PowerQuartier) 🇨🇭🇩🇪
* **Profil**: Schweizer ETH-Spin-off mit Fokus auf B2B-Softwarelösungen für Energy Sharing und Stadtwerke.
* **Stärken**: Hohe B2B-Reputation im Enterprise-Segment, Whitelabeling, 15m-Abrechnungslogik.
* **Schwächen**:
  * **Enorme Einstiegshürde**: Sechsstellige Integrationsprojekte oder hohe monatliche Mindestgebühren (> 10.000–30.000 € Setup). Für private WEGs, kleine Vereine oder Bürgerenergiegenossenschaften unerschwinglich.
  * **Kein Home EMS (Säule 1 fehlt)**: Reines Backoffice-Abrechnungstool ohne Live-Sankey, ohne Sub-Sekunden-Telemetrie und ohne Geräte-Dashboard.
  * **Keine Aktorik & Steuerung**: Keine Steuerung von Wärmepumpen, Speichern oder Wallboxen in Echtzeit.
* **Sharegy-Vorteil**: **Vollwertige Dual-Core Plattform zu einem Bruchteil der Kosten**. Sharegy bietet 15m-Abrechnung, BNetzA MSCONS-Generierung und GoBD-Exporte kombiniert mit Live-EMS, SG-Ready Steuerung, 6 Sprachen und Self-Service Stripe Checkout.

---

### 2. 1Komma5° (Heartbeat) 🇩🇪
* **Profil**: Hardware-Generalunternehmer (PV, WP, Speicher) mit proprietärer Energiemanagement-Box („Heartbeat“).
* **Stärken**: Hohe Markenbekanntheit, Marketing-Power, automatisierte Speicher-Arbitrage mit dynamischem Stromtarif.
* **Schwächen**:
  * **Extremer Vendor Lock-in**: Funktioniert ausschließlich mit der Heartbeat-Hardwarebox und zertifizierten Partner-Wechselrichtern.
  * **Enorme Kosten**: Verkauf fast nur im Neuanlagen-Paket für 15.000–30.000 €.
  * **Kein Energy Sharing**: Reines Single-Home-System; keine Unterstützung für Mehrparteienhäuser, Mieterstrom (§ 42b EnWG) oder Bürgerenergie.
* **Sharegy-Vorteil**: **100% Software-Only & Hardware-Freiheit**. Jeder Bestandsanlagen-Besitzer mit einem 20-Euro-Shelly, ioBroker oder Wechselrichter-Cloud kann Sharegy in wenigen Minuten ohne zusätzliche Hardwarebox nutzen.

---

### 3. Tibber (Pulse) 🇳🇴🇩🇪
* **Profil**: Dynamischer Stromanbieter mit Hardware-Lesekopf (Pulse) für mME-Stromzähler.
* **Stärken**: Erstklassiges Tarif-Frontend, transparente Börsenpreis-Darstellung, gutes Smart-Charging für E-Autos.
* **Schwächen**:
  * **Fokus nur auf den Netzübergabepunkt**: Sieht über den Zähler nur den aggregierten Hausbezug/Einspeisung.
  * **Kein echtes Sub-Metering**: Einzelverbraucher (BWWP, Waschmaschine, Umwälzpumpen) werden nicht erfasst oder disaggregiert.
  * **Kein Energy Sharing**: Reine 1:1 Versorgerbelieferung.
* **Sharegy-Vorteil**: **Ganzheitliche Energie-Intelligenz**. Sharegy integriert Tibber- und EPEX-Preise nahtlos (inkl. 7-Tage Trend), bietet aber zusätzlich Tiefen-Monitoring auf Geräteebene, BWWP SG-Ready Steuerung, 48h-KI-Prognosen, VPP-Regelenergie und Quartiers-Clearing.

---

### 4. Clever-PV 🇩🇪
* **Profil**: Cloud-basiertes Überschussladen und Schalter-Tool für Prosumer.
* **Stärken**: Schnelle Einrichtung für Shellys und Wallboxen via Cloud-API.
* **Schwächen**:
  * **Reines Schalt-Tool ohne Tiefe**: Kein physikalisches Flussmodell, keine TimescaleDB-Performance, keine GoBD-Archivierung.
  * **Kein Energy Sharing & VPP**: Reines B2C-Single-Home-Tool ohne § 42b oder Regelleistungs-Vermarktung.
* **Sharegy-Vorteil**: **Enterprise-Architektur & Dual-Core**. Echtes Live-Sankey, Sub-Sekunden Outbound-WSS, ML-Ertragsprognosen, Merit-Order-Kaskade, Multi-Zahlungsoptionen und revisionssicheres Multi-Tenant Sharing.

---

## 🌟 3. Die 10 Kern-USPs von Sharegy (v5.4)

1. 🌐 **Echter Zero-Lock-In**: 10 Cloud-Inverter-Marken, Outbound-WSS (Shelly), OCPP 1.6-J, ioBroker, Home Assistant & MQTT.
2. 🎛️ **4 Pro-Automations-Hubs**: Control (`/app/control`), Mobility, Heating & Alerts mit 4 Autopilot-Modi.
3. ⚡ **§ 14a EnWG CLS Gateway**: BSI TR-03109-1 Ingest, FNN Steuerbox Quittierung und dynamisches $4{,}2\,\text{kW}$ Summenbudget.
4. 📈 **VPP Regelenergie & 80/20 Clearing**: Sekundärregelleistung (aFRR/SRL), FCR, 96-Viertelstunden-Fahrpläne & Monatsgutschriften.
5. 📁 **Zentraler GoBD-Dokumenten-Hub**: DATEV-, MSCONS 2.2b-, UTILMD- und PDF-Exporte mit SHA-256 Hashketten-Prüfung.
6. 🔑 **Granulare Enterprise RBAC-Matrix**: 5 spezialisierte Rollen für Großkunden, Dispatcher, Buchhalter und Auditoren.
7. ⏳ **Skeleton-Loading & SWR UX**: Ladezeitfreie Navigation ($< 20\,\text{ms}$) und Zero Layout Shift via TanStack Query.
8. 🏢 **Gesetzeskonformes Energy Sharing (§ 42b EnWG)**: 15m-Saldierung, virtuelle Summenzähler, 3 Allokationsmodelle.
9. 💳 **Vollautomatisierter Billing-Stack**: Stripe Checkout (SEPA, Karten, PayPal, Klarna), § 14 UStG Invoicing & Customer Portal.
10. 📖 **Enterprise Helpcenter & Wissensportal**: 11 Kategorien, 46 zweisprachige (DE/EN) Fachartikel.

---

## 🎯 4. Reifegrad-Gesamtbewertung: **9.98 / 10 (Enterprise-Ready Live)**
