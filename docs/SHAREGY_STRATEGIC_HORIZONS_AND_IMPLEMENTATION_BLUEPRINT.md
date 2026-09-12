# 🧭 Sharegy Strategie-Check & Umsetzungs-Blueprint

**Dokument-Status:** Strategisches Management-Audit & Technischer Realisierungsplan  
**Version:** 1.0 (Post-v5.2)  
**Datum:** 12. September 2026  
**Zielgruppe:** Management, Produktentwicklung, Enterprise Vertrieb  

---

## 📊 1. Executive Summary & Status-Matrix

Die folgende Matrix gibt einen transparenten Überblick darüber, welche Module und Funktionen im Sharegy-Repository bereits **vollständig einsatzbereit (100% Live)**, welche **teilweise vorbereitet** und welche als **nächste Schritte** zu realisieren sind.

| Handlungsfeld / Horizont | Status in Sharegy | Bereits implementiert | Was noch fehlt / Nächster Schritt |
|---|:---:|---|---|
| **1.1 Installateurs- & Partner-Hebel** | 🟡 **Teilweise (50%)** | Multi-Tenancy-Modell (`Tenant`, `TenantMembership`), Berechtigungskonzept, Asset-Zuweisung. | Dediziertes Installateurs-Dashboard (Flotten-Übersicht, Störungs-Ticker, 1-Klick-Wartungsfreigabe). |
| **1.2 Bürgerenergie & WEG (§ 42b EnWG)** | 🟢 **100% Live** | Virtueller Summenzähler, 15m-Saldierung (`BalanceSlot`), Community-Tarife, Mieterstrom-PDFs, Communities Hub. | B2B-Vertriebsmaterialien & Lead-Funnel für Hausverwaltungen. |
| **2.1 Interaktive Demo-Vorschau** | 🟢 **100% Live** | 3-Wege Instant-Demo-Switcher (Tenant-Admin, Tenant-User, Privathaushalt) auf Landing Page & Login. | Fortlaufende Pflege der Mock-Telemetrie. |
| **2.2 1-Klick Cloud-Inverter Anbindung** | 🟢 **100% Live** | Sungrow, Fronius, SMA, SolarEdge, Huawei, Deye, Hoymiles, GoodWe, Kostal im Setup-Wizard mit Live-Token-Check. | Anbindung weiterer Nischen-Hersteller bei Bedarf. |
| **3.1 EEBUS & Cloud Ecosystem Bridge** | 🔴 **Konzipiert (20%)** | Datenmodell für steuerbare Lasten (§ 14a EnWG), SG-Ready Relais, Modbus & Cloud-APIs für Wärmepumpen. | Nativer EEBUS SHIP/SPINE Stack bzw. Cloud-to-Cloud Bridge (Home Connect, myVAILLANT, ViCare API). |
| **3.2 BNetzA AS4 Marktkommunikation** | 🔴 **Architektur (20%)** | 15-Minuten-Messwerte (`AggregatedReading`), Zählpunkte, Mieterstrom-Bilanzierung. | REST-API-Adapter zu zertifizierten EDIFACT/AS4-Providern (z. B. powercloud, Schleupen, e-GITS). |
| **Horizont 1: B2B Whitelabel EVU-Portal** | 🟡 **Teilweise (65%)** | Multi-Tenant-Architektur, Mandantentrennung, Rollen, Sub-Zähler, dynamische Tarife. | Dynamic CSS/Theming je Tenant, Custom-Domain-SSL-Handling (CNAME) & White-Label Mail-Templates. |
| **Horizont 2: BNetzA CLS-Kanal & SMGW** | 🟡 **Teilweise (40%)** | § 14a EnWG Dimm- & Abschaltlogik, Lastmanagement, Prioritätssteuerung im EMS. | Lokaler CLS-Proxy-Dienst (HAN-Kommunikation zum Smart Meter Gateway) & FNN-Testfall-Konformität. |
| **Horizont 3: Automatisierter Flex-Handel** | 🟡 **Teilweise (60%)** | VPP Aggregator Engine (`/api/vpp/flexibility/`), aFRR/SRL/FCR Pooling, 96-Viertelstunden-Fahrpläne, Börsenstrom-MPC. | Direkte API-Kopplung zu Flex-Vermarktern (z. B. Next Kraftwerke / Entelios) & Erlösausschüttungs-Clearing. |

---

## 🔍 2. Detaillierte Analyse & Umsetzungspläne für offene Handlungsfelder

---

### 🛠️ 1.1 Installateurs- & Partner-Portal (B2B2C Hebel)

#### Was ist das?
Ein spezialisiertes B2B-Dashboard für Elektro- und PV-Installateure. Der Installateur verbindet die Anlagen seiner Kunden während der Montage mit Sharegy. Er sieht den Live-Status aller betreuten Anlagen in einer Flottenansicht, erhält proaktive Fehlermeldungen (z. B. Wechselrichter-Ausfall, Isolationsfehler, Batterie-Disbalance) und kann Kunden direkt Support leisten.

#### Aktueller Ist-Stand im Code
* `core/models.py` und `accounts/models.py` besitzen bereits mandantenfähige `Tenant`- und `TenantMembership`-Strukturen mit Rollen (`ROLE_ADMIN`, `ROLE_HELPDESK`, `ROLE_AUDITOR`).
* Es fehlt jedoch eine eigenständige, auf Installateure zugeschnittene Benutzeroberfläche (Partner Cockpit) und der Freigabe-Workflow für Endkunden.

#### Optimale Vorgehensweise zur Umsetzung
1. **Rolle & Datenmodell erweitern:**
   * Ergänzung eines Modells `PartnerCompany` (Installateursbetrieb) mit Verknüpfung zu `User` und `Home`/`ChargingStation`/`InverterDevice`.
   * Modell `MaintenanceConsent` (Kunde erteilt dem Installateur temporäre oder dauerhafte Wartungs- und Fernkonfigurationsrechte gem. DSGVO).
2. **Frontend-Komponente: `PartnerDashboard.jsx`:**
   * **Flotten-Übersicht:** Tabelle aller Kundenanlagen mit Ampelsystem (🟢 Normal, 🟡 Drosselung, 🔴 Störung).
   * **Schnell-Inbetriebnahme:** Wizard zur Zuweisung einer neu montierten Wallbox/Wechselrichters an eine Kunden-E-Mail.
   * **Fernwartung & Live-Diagnose:** Zugriff auf Inverter-Register und Wallbox-Tools (TriggerMessage, Reset, Profile).
3. **Monetarisierung:**
   * Installateur erhält Sharegy für seine Kunden als Mehrwert-Paket („Sharegy Partner Lizenz“: 2,99 €/Anlage/Monat oder einmalige Provision).

---

### 🏠 3.1 EEBUS & Cloud Ecosystem Bridge

#### Was ist das?
**EEBUS** ist der offene europäische Kommunikationsstandard (spezifiziert durch DKE / ZVEI / VDA) für die herstellerübergreifende Vernetzung von Energie-Assets im Gebäude (insb. Wärmepumpen, PV-Speicher, Wallboxen und Haushaltsgroßgeräte) über die Protokolle **SHIP** (Smart Home IP) und **SPINE** (Smart Premises Interoperable Neutral-message Exchange).

```
   ┌─────────────────────────────────────────────────────────┐
   │                  Sharegy Cloud / HEMS                   │
   └────────────────────────────┬────────────────────────────┘
                                │ (EEBUS Cloud API / Local Bridge)
          ┌─────────────────────┼─────────────────────┐
          ▼                     ▼                     ▼
 ┌─────────────────┐   ┌─────────────────┐   ┌─────────────────┐
 │   Wärmepumpe    │   │  Hausgeräte     │   │  Smart Meter GW │
 │(Vaillant/Bosch) │   │ (Home Connect)  │   │  (CLS Schnittst)│
 └─────────────────┘   └─────────────────┘   └─────────────────┘
```

#### Warum brauchen wir das?
Viele moderne Wärmepumpen (Daikin, Vaillant, Viessmann, Bosch, Stiebel Eltron) sowie Smart-Home-Großgeräte (BSH Home Connect: Bosch, Siemens, Neff) unterstützen EEBUS, um Lasten nach **§ 14a EnWG** netzdienlich zu dimmen oder Wasch- und Spülgänge automatisch bei PV-Überschuss zu starten.

#### Optimale Vorgehensweise zur Umsetzung
1. **Zweistufiger Architektur-Ansatz:**
   * **Stufe 1 (Cloud-to-Cloud Bridge – Kurzfristig):** Anbindung über die offiziellen Cloud-APIs der Hersteller (z. B. *Home Connect Developer API* für Haushaltsgeräte, *myVAILLANT API*, *Viessmann Developer API*). Hierüber können Startzeiten und Sollwerte direkt aus der Sharegy Cloud ohne lokale Hardware gesteuert werden.
   * **Stufe 2 (Lokaler EEBUS SHIP/SPINE Stack – Mittelfristig):** Implementierung eines leichtgewichtigen Python-Async-Services (auf Basis offener EEBUS-Bibliotheken wie `eebus-go` oder Python SPINE-Adaption), der über mDNS/Bonjour lokale Geräte im Heimnetzwerk erkennt und TLS-Zertifikate austauscht.
2. **Integration in den EMS-Optimierer:**
   * Wärmepumpe wird als flexibler thermischer Puffer modelliert (Sollwertanhebung +3°C bei Solarüberschuss oder negativen Börsenstrompreisen).
   * Spül- und Waschmaschinen senden ein `PowerProfile` an Sharegy; Sharegy erteilt die Startfreigabe (`Schedule`), sobald Solarstrom verfügbar ist.

---

### 📑 3.2 BNetzA AS4 Marktkommunikations-Partnerschaft

#### Was ist das?
In Deutschland schreibt die Bundesnetzagentur (BNetzA) für den Austausch von Energiemengen, Zählerständen und Abrechnungsdaten zwischen den Marktpartnern (Verteilnetzbetreiber VNB, Lieferant, Messstellenbetreiber MSB) das standardisierte Format **EDIFACT** (Nachrichtentypen: `UTILMD`, `MSCONS`, `INVOIC`) über das sichere **AS4-Übertragungsprotokoll** mit BSI-Smart-Meter-PKI-Zertifikaten vor.

#### Warum sollte Sharegy das nicht selbst von Grund auf bauen?
* Die direkte AS4-Zertifizierung und der 24/7-Betrieb von Marktkommunikations-Gateways erfordern BSI-Auditierungen, ISO 27001-Zertifizierungen und ständige Anpassungen an die halbjährlichen BNetzA-Formatwechsel (GeLi Gas, WiM, GPKE).
* **Best-Practice:** Alle führenden Energy-SaaS-Plattformen (Tibber, Rabot Charge, Ostrom, 1KOMMA5°) nutzen spezialisierte EDIFACT/AS4-Marktkommunikations-Dienstleister.

#### Optimale Vorgehensweise zur Umsetzung
1. **Marktkommunikations-Adapter (`energy/services/edi_gateway.py`):**
   * Sharegy aggregiert die 15-Minuten-Viertelstunden-Messwerte aus dem `billing`- und `core`-Modul (`BalanceSlot`, `AggregatedReading`).
   * Über eine standardisierte REST-/Webhook-Schnittstelle übergibt Sharegy diese Daten an den zertifizierten Mako-Partner:
     * **Mögliche Partner:** *powercloud*, *Schleupen.CS*, *Somentec*, *Klafka & Hinz*, *e-GITS*, *Enersis*.
2. **Automatisierter Datenexport:**
   * Bereitstellung von standardisierten JSON/CSV-Schnittstellen für `MSCONS` (Zählerstandsgänge für Mieterstrom & Energy Sharing) und `UTILMD` (Stammdaten-Meldung für Ein- und Auszüge).

---

## 🔮 3. Die 3 Strategischen Horizonte (Post-v5.2)

---

### 🏛️ Horizont 1: B2B Whitelabel EVU-Portal (Q1 2027)

#### Was ist das?
Stadtwerke, Regionalversorger und Bürgerenergiegenossenschaften können Sharegy als schlüsselfertige Plattform unter ihrer eigenen Marke betreiben (z. B. `mein-strom.stadtwerke-musterstadt.de`).

```
┌─────────────────────────────────────────────────────────────────────────┐
│                      SHAREGY WHITELABEL PLATFORM                        │
├───────────────────────────┬─────────────────────────────┬───────────────┤
│  Stadtwerke Musterstadt   │  Bürgerenergie Nord eG      │  SolarProfi   │
│  (Brand: Blau/Orange)     │  (Brand: Grün/Gelb)         │  (Install.)   │
│  Domain: kunden.swm.de    │  Domain: sharing.nord.de    │  solar.de/app │
└───────────────────────────┴─────────────────────────────┴───────────────┘
```

#### Technische Umsetzungs-Schritte
1. **Dynamic Theming Engine:**
   * Erweiterung des `Tenant`-Datenmodells um Theme-Attribute:
     * `primary_color`, `secondary_color`, `accent_color`
     * `logo_url`, `favicon_url`, `company_legal_name`, `support_email`
     * `custom_domain` (z. B. `portal.stadtwerke-stadt.de`)
   * Im React-Frontend (`frontend/src/`): Injizieren von CSS-Variablen (`--color-primary`, etc.) basierend auf der geladenen Tenant-Konfiguration.
2. **Custom Domain & SSL-Handling:**
   * Nginx / Traefik Reverse Proxy mit automatischem Let's Encrypt SSL-Zertifikatsabruf für hinterlegte Kunden-Domains (CNAME-Routing).
3. **EVU-Kundenportal-Features:**
   * Eigenes Onboarding mit Stadtwerke-Tarifverträgen.
   * Automatischer PDF-Rechnungsversand mit Stadtwerke-Briefkopf.

---

### 🔌 Horizont 2: BNetzA CLS-Kanal & Smart-Meter-Gateway (SMGW) Kopplung (Q2 2027)

#### Was ist das?
Nach **§ 14a EnWG** müssen ab 2024 neue steuerbare Verbrauchseinrichtungen (SteuVE: Wallboxen > 4,2 kW, Wärmepumpen, Batteriespeicher) bei Netzüberlastung durch den Verteilnetzbetreiber (VNB) auf 4,2 kW gedimmt werden können.
Die gesetzlich vorgesehene Zielarchitektur ist die Anbindung über den **CLS-Kanal (Controllable Local System)** eines zertifizierten **Smart-Meter-Gateways (SMGW)**.

```
       ┌────────────────────────────────────────────────┐
       │     Verteilnetzbetreiber (VNB) / Leitsystem    │
       └───────────────────────┬────────────────────────┘
                               │ (Gesicherter WAN-Kanal)
                               ▼
               ┌───────────────────────────────┐
               │ Smart Meter Gateway (BSI SMGW)│
               └───────────────┬───────────────┘
                               │ (Lokaler CLS-Kanal / HAN)
                               ▼
               ┌───────────────────────────────┐
               │    Sharegy Local CLS-Proxy    │
               │   (§ 14a EnWG Dimm-Manager)   │
               └───────────────┬───────────────┘
                               │ (OCPP 2.0.1 / Modbus / SG-Ready)
             ┌─────────────────┼─────────────────┐
             ▼                 ▼                 ▼
      ┌─────────────┐   ┌─────────────┐   ┌─────────────┐
      │   Wallbox   │   │ Wärmepumpe  │   │ Heimspeicher│
      │ (Dimm 4.2kW)│   │ (Dimm 4.2kW)│   │(Einspeis-St)│
      └─────────────┘   └─────────────┘   └─────────────┘
```

#### Technische Umsetzungs-Schritte
1. **CLS-Software-Agent / Proxy:**
   * Implementierung eines leichtgewichtigen Dienstes (z. B. Docker-Container auf lokalem Energiemanager oder als Cloud-CLS-Bridge bei SMGWs mit externem CLS-Management).
   * Empfängt Dimm-Befehle (`DimRequest: 4.2 kW`, `Duration: 120 min`) vom SMGW.
2. **EMS-Ansteuerung:**
   * Sharegy schaltet sofort die Prioritätslogik um:
     * Wallbox wird per `SetChargingProfile` auf maximal 6 A (1-phasig ca. 1,4 kW, 3-phasig 4,14 kW) gedrosselt.
     * Heimspeicher deckt eventuelle Spitzenlasten aus der Batterie, sodass der Netzbezug am Hausanschluss exakt $\le 4{,}2\,\text{kW}$ bleibt.
   * Quittierung der Dimmung an das SMGW zur Erfüllung der BNetzA-Nachweispflicht.

---

### 📈 Horizont 3: Automatisierter Flexibilitäts-Handel & VPP Arbitrage (Q3 2027)

#### Was ist das?
Tausende in Sharegy registrierte Heimspeicher und V2G-Fahrzeuge werden in einem **Virtuellen Kraftwerk (VPP)** gepoolt. Die gespeicherte Energie wird automatisiert an den lukrativsten Strommärkten vermarktet:
1. **EPEX Spot Day-Ahead & Intraday Arbitrage:** Laden bei Tiefpreisen / negativen Preisen, Entladen ins Netz zu teuren Spitzenzeiten (Morgens/Abends).
2. **Regelleistungsmarkt (aFRR / SRL):** Bereitstellung von sekundengenauer Netzstabilisierung für die Übertragungsnetzbetreiber (Tennet, Amprion, 50Hertz, TransnetBW).

```
   ┌────────────────────────────────────────────────────────────┐
   │            EPEX Spot / Regelleistungs-Markt                │
   └─────────────────────────────┬──────────────────────────────┘
                                 │ (Handelsschnittstelle API)
                                 ▼
   ┌────────────────────────────────────────────────────────────┐
   │       Sharegy VPP Aggregator & Dispatch Optimizer          │
   │      (/api/vpp/flexibility/ · 96-Viertelstunden-Fahrplan)  │
   └─────────────────────────────┬──────────────────────────────┘
                                 │ (Pool-Dispatch Order)
         ┌───────────────────────┼───────────────────────┐
         ▼                       ▼                       ▼
 ┌───────────────┐       ┌───────────────┐       ┌───────────────┐
 │ Home 1 (10kWh)│       │ Home 2 (15kWh)│       │ Home N (V2G)  │
 └───────────────┘       └───────────────┘       └───────────────┘
```

#### Aktueller Ist-Stand im Code
* Sharegy verfügt in `vpp/` bereits über eine vollständige **VPP Aggregator Engine**:
  * `/api/vpp/flexibility/`: Ermittelt in Echtzeit die abrufbare Flexibilität (Laden/Entladen) des gesamten Bestands.
  * `/api/vpp/dispatch/`: Sendet Dispatch-Orders an alle Heimspeicher und Wallboxen mit Sub-Sekunden-Reaktion.
  * Fahrplanerstellung für 96 Viertelstunden (`PT15M` nach Connect+ / Redispatch 2.0 Standard).
  * UI: `VppAggregatorCockpit.jsx` für Netzbetreiber und Aggregatoren.

#### Nächste Schritte zur vollen Marktreife
1. **Aggregatoren-Anbindung (Marktzugang):**
   * Kooperation mit einem lizenzierten Bilanzkreiskoordinator / Direktvermarkter (z. B. *Next Kraftwerke*, *Entelios*, *Statkraft*, *EnBW*).
   * Anbindung über das standardisierte **OpenADR 2.0b** oder **IEC 60870-5-104** Protokoll.
2. **Automatisches Erlös-Clearing für Endkunden:**
   * Erweiterung des `billing`-Moduls um eine **Erlös-Ausschüttungstabelle**:
     * Ausgeschütteter Betrag = Erzielter Markterlös $\times$ Kunden-Anteil $\times$ (1 - Sharegy Platform Fee, z. B. 15%).
   * Anzeige im Kunden-Dashboard: *„Heute mit Speicher-Flexibilität verdient: +3,45 €“*.

---

## 🎯 4. Handlungsempfehlung für die nächste Sprint-Planung

Zur Maximierung des geschäftlichen ROI und schnellen Kundenwachstums empfiehlt sich folgende Priorisierung:

```
                  ┌──────────────────────────────────────────────┐
                  │ 1. PARTNER- & INSTALLATEURS-DASHBOARD        │
                  │ (Sofortiger B2B2C Vertriebshebel für Q4 2026)│
                  └──────────────────────┬───────────────────────┘
                                         ▼
                  ┌──────────────────────────────────────────────┐
                  │ 2. CLOUD-TO-CLOUD EEBUS/ECOSYSTEM BRIDGE     │
                  │ (Home Connect & Wärmepumpen-Cloud-APIs)      │
                  └──────────────────────┬───────────────────────┘
                                         ▼
                  ┌──────────────────────────────────────────────┐
                  │ 3. WHITELABEL EVU-THEMING & CUSTOM DOMAINS   │
                  │ (Q1 2027: Stadtwerke-Rollout)                │
                  └──────────────────────┬───────────────────────┘
                                         ▼
                  ┌──────────────────────────────────────────────┐
                  │ 4. VPP AGGREGATOREN-ANBINDUNG (OPENADR/MARKET)│
                  │ (Q2/Q3 2027: Monetarisierung Flex-Handel)    │
                  └──────────────────────────────────────────────┘
```

1. **Sprint 1 (Quick Win): Installateurs-Cockpit:**
   * Bereitstellung einer B2B-Partner-Übersicht für Fachbetriebe, um Sharegy als Standard-HEMS bei Neuinstallationen zu etablieren.
2. **Sprint 2 (Erweiterung): Cloud Ecosystem Bridge:**
   * BSH Home Connect API für Geschirrspüler/Waschmaschinen und Cloud-Wärmepumpen-Kopplung (myVAILLANT / ViCare) für erweitertes PV-Surplus-Management.
3. **Sprint 3 (B2B Expansion): Whitelabel-Theming:**
   * Dynamic Color theming und CNAME-Domain-Verwaltung für Stadtwerke-Kooperationen.
4. **Sprint 4 (Marktzugang): Flexibilitäts-Monetarisierung:**
   * Anbindung des bestehenden VPP-Moduls an einen Vermarktungspartner zur Generierung wiederkehrender Flexibilitäts-Erlöse.
