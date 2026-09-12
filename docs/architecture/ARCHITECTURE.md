# 🏛️ System-Architektur & Technologie-Stack

**Sharegy** basiert auf einer hochgradig performanten, modular erweiterbaren und asynchronen **Dual-Core-Architektur**:

1. **Säule 1: Home Energy Management System (EMS Free & Pro)** — Hochfrequente IoT-Telemetrie (1–15s), Echtzeit-Energiefluss (Sankey), PV-/Last-/Batterie-Prognosen, Börsenpreis- & Arbitrage-Optimierung, Live-CO₂-Signale, AI-Alerting und Multi-Format-Reporting für Privathaushalte und Gewerbe.
2. **Säule 2: Energy Sharing Communities (ESC)** — Viertelstündliche iMSys-Zähler-Bilanzierung (OBIS 1.8.0 / 2.8.0), lokale Peer-to-Peer Stromallokation, Mieterstrom-Clearing & automatisierte Quartiersabrechnung.

---

## 📐 1. Umfassendes Architektur-Diagramm

```
                           ┌────────────────────────────────────────────────────────┐
                           │                    Client-Schicht                      │
                           │   React 19 • Vite • TailwindCSS • Apache ECharts       │
                           │   PWA • Capacitor Mobile • i18next (DE / EN / PL)      │
                           └───────────────────────────┬────────────────────────────┘
                                                       │ HTTPS / REST / WebSockets
                                                       ▼
                           ┌────────────────────────────────────────────────────────┐
                           │                 API- & Gateway-Schicht                 │
                           │      Django 5.x ASGI (Daphne) • Django REST Framework  │
                           │      Token-Auth • API-Keys • Session • Rate-Limiting   │
                           └─────────────┬───────────────────────────┬──────────────┘
                                         │                           │
          ┌──────────────────────────────┼───────────────────────────┴──────────────────────────────┐
          ▼                              ▼                                                          ▼
┌───────────────────┐          ┌───────────────────┐                                      ┌───────────────────┐
│ Ingestion & IoT   │          │ Datenbank & Cache │                                      │ Intelligenz & KI  │
├───────────────────┤          ├───────────────────┤                                      ├───────────────────┤
│ • MQTT Broker     │          │ • TimescaleDB     │                                      │ • Hybrid PV-Model │
│ • OCPP CSMS 2.0.1 │          │   (Hypertables)   │                                      │   (Physics + ML)  │
│ • Shelly WSS Relais│         │ • Continuous Aggr.│                                      │ • WAPE Treffer-   │
│ • Home Assistant  │          │ • DeviceLatest-   │                                      │   quoten-Prüfung  │
│   REST-Bridge     │          │   Metric Snapshot │                                      │ • 48h Last- & SoC-│
│ • OpenTelemetry   │          │ • Redis Pub/Sub   │                                      │   Simulation      │
│   OTLP Ingest     │          │ • Deadband-Filter │                                      │ • Multi-Window    │
│ • Tibber GraphQL  │          │ • Celery Broker   │                                      │   Spot-Optimizer  │
│ • SMARD / EPEX    │          │                   │                                      │ • Battery-        │
│   Spot Pipeline   │          │                   │                                      │   Arbitrage & CO2 │
└───────────────────┘          └───────────────────┘                                      └───────────────────┘
```

---

## 🛠️ 2. Detaillierter Technologie-Stack

### A. Backend & API Core
* **Framework**: Django 5.x / Python 3.12 (ASGI & WSGI via Daphne / Gunicorn).
* **API Layer**: Django REST Framework (DRF) mit Token-, Session- und API-Key-Authentifizierung (`HTTP_X_API_KEY` für Plugins & Edge-Geräte).
* **Echtzeit & Messaging**: Django Channels 4.x, WebSockets & Redis Channel-Layer für verzögerungsfreie Live-Telemetrie.
* **Asynchrone Workflows & Scheduler**: Celery 5.x mit Redis als Message Broker & Result Backend; zeitgesteuerte Cron-Jobs via Celery Beat (Börsenpreis-Import, Wetterabruf, 15-Min-Bilanzierung).
* **Datenbank**: PostgreSQL 16 mit **TimescaleDB**-Erweiterung für Zeitreihen (`DeviceMetric` und `IntervalReading` Hypertables, Chunk-Time: 7 Tage, automatische Kompression und Continuous Aggregates für 1h/1d Auswertungen).
* **In-Memory Cache**: Redis 7.x für Deadband-Filterung, Snapshot-Speicherung (`device:{id}:latest_power`) und Token-Blacklisting.

---

### B. Frontend & Visualisierung
* **Framework**: React 18 / 19 mit Vite 6.x Build-Tooling.
* **Routing**: React Router DOM v6 mit modular verschachtelten Routen, Lazy Loading und Auth-Guards.
* **State Management & Data Fetching**: TanStack React Query v5 (Optimistic Updates, automatisches Polling, intelligentes Cache-Management).
* **Visualisierungs-Engines**:
  * **Apache ECharts** via `echarts-for-react`: Interaktives Live-Sankey-Diagramm (Etagen-/Raum-Aggregation), historische Verbrauchs-Sparklines, Submeter-Trends und 48h-Prognosecharts.
  * **SVG-Vektor-Charts**: Hochperformante Donut- und Flussmatrix-Visualisierungen.
* **Internationalisierung (i18n)**: `i18next` & `react-i18next` mit nativer Multi-Language Unterstützung (🇩🇪 Deutsch, 🇬🇧 English, 🇵🇱 Polski).
* **Styling & UI**: Tailwind CSS 4.x, Lucide-Icons, Headless UI, modale Dialoge und dynamische Benachrichtigungs-Banner.
* **Exporte & Reporting**: Client-seitige Download-Trigger für formatierte Excel-Dateien (`.xlsx`), druckfähige A4-PDFs (ReportLab), CSV (UTF-8 BOM) und JSON-Payloads.

---

### C. Ingestion, Protokolle & Hardware-Schnittstellen
* **OCPP 1.6-J / 2.0.1 / 2.1 Charging Station Management System (CSMS)**:
  * Nativer WebSocket-Endpoint (`wss://sharegy.de/ocpp/{chargebox_id}`).
  * Dynamic Smart Charging Profiles, Departure Ready Zielladen & Automatische 1p/3p Phasenumschaltung (1,4 kW – 11/22 kW).
  * Bidirektionales Laden (V2H & V2G Peak Shaving).
* **Shelly Outbound WebSocket & Relais-Aktorik**:
  * Direkte, verschlüsselte Outbound-WSS-Verbindung (Port 443) für Shelly Plus, Pro und Gen3.
  * < 50 ms Latenz für SG-Ready Wärmepumpensteuerung und Echtzeit-Schaltungen ohne Cloud-Kosten.
* **MQTT-Hub & Deadband-Ingestion** (`core/management/commands/mqtt_consume.py`):
  * Paho MQTT Daemon mit Redis-Live-Cache.
  * 2-Stufen-Deadband-Filterung: Datenbank-Writes erfolgen nur bei signifikantem Delta ($\Delta > 1\,\text{W}$) oder Heartbeat (60s), wodurch die DB-Schreiblast um **85 %** reduziert wird.
* **Home Assistant Integration** (`plugins/homeassistant/`):
  * Native Custom Component (`custom_components/sharegy`).
  * 9 Live-Sensoren (PV, Hauslast, Netzbezug, Einspeisung, Batterie-Leistung, SoC, Tagesverbrauch, Ersparnis, Autarkie).
  * Cloud-First Architektur (`https://sharegy.de`) & Service `sharegy.push_telemetry`.
* **Grafana Enterprise Data Source Bridge** (`plugins/grafana/` & `energy/api/urls_grafana.py`):
  * REST-Bridge für JSON- & Infinity-Data-Sources (`/api/grafana/search`, `/query`, `/annotations`).
  * Fertiges Dashboard-Template (`sharegy_energy_cockpit.json`).
* **OpenTelemetry (OTel)** (`providers/opentelemetry/`):
  * OTLP/HTTP Metrics Receiver für Multi-Channel Smart-Meter und Server-Telemetrie.
* **Tibber & EPEX Spot Pipeline**:
  * GraphQL API Client für Zähler- und Vertragssynchronisation.
  * Automatisierter SMARD- & Energy-Charts-Fetcher für Day-Ahead-Börsenstrompreise.

---

### D. Berechnungs-, KI- & Optimierungs-Engines

```
┌────────────────────────────────────────────────────────────────────────────────┐
│                           SHAREGY INTELLIGENCE CORE                            │
├──────────────────────────────────────┬─────────────────────────────────────────┤
│ ☀️ SOLAR FORECAST ACCURACY           │ 🔋 BATTERY ARBITRAGE SIMULATOR          │
│ • Open-Meteo 96h Strahlungsdaten     │ • Netzdienliches Laden bei Tiefpreisen  │
│ • Hybrid Physics + Random Forest ML  │ • Roundtrip-Effizienzmodell (~90%)      │
│ • WAPE Trefferquoten-Evaluation (%)  │ • Peak-Vermeidung (~180–320 € / Jahr)   │
├──────────────────────────────────────┼─────────────────────────────────────────┤
│ 🏠 LOAD & SOC FORECAST               │ 🌿 LIVE CO₂ GRID SIGNAL                 │
│ • 48h Haushaltslast-Synthese         │ • Echtzeit g CO₂/kWh Netzmix (DE-LU)    │
│ • 48h Batterie-SoC Simulation        │ • 36h Grünstrom-Timeline & Öko-Fenster  │
│ • Nachtautarkie-Ermittlung           │ • Ampel-Klassifikation (<250g Grün)     │
├──────────────────────────────────────┼─────────────────────────────────────────┤
│ ⚡ MULTI-WINDOW OPTIMIZER             │ 🛡️ PROAKTIVE ALARMZENTRALE              │
│ • Sliding-Windows (1h, 2h, 4h)       │ • 8 Erkennungsregeln (PV-Ausfall,       │
│ • Opportunitätskosten-Kalkulation    │   Nachtleckage, Notreserve, Peak)       │
│ • Börsenpreis + EEG-Vergütung        │ • Schweregrade & Acknowledgment-Flow    │
└──────────────────────────────────────┴─────────────────────────────────────────┘
```

---

## 🔒 3. Sicherheits- & Betriebs-Architektur

1. **SaaS Cloud-Sicherheit**:
   * Alle externen Verbindungen (OCPP, Shelly WSS, Home Assistant, Web-Clients) kommunizieren ausschließlich über gesichertes Outbound-HTTPS/WSS (`Port 443`) und TLS-verschlüsseltes MQTT (`Port 8883`).
   * Keine Portweiterleitungen oder DynDNS im lokalen Heimnetzwerk des Nutzers erforderlich.
2. **Daten-Isolation & Multi-Tenancy**:
   * Strikte Tenant- und Home-Isolation auf ORM-Ebene (`Home.objects.filter(user=request.user)`).
   * Eindeutige kryptografische API-Tokens pro Home für Push- und Ingestion-Schnittstellen.
3. **Idempotenz & Ausfallsicherheit**:
   * Unique-Constraints auf `(device, metric_key, timestamp)` verhindern doppelte Metrik-Einträge bei Netzwerk-Retries.
   * Resiliente Fallback-Tarife und Ausfall-Modelle für Wetter- und Börsenstromdaten bei API-Timeouts.
