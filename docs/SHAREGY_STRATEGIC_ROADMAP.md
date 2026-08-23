# 🚀 Sharegy Strategische Produkt- & Architektur-Roadmap

**Mission**: Die führende SaaS-Plattform für **Home Energy Management (EMS)** und **Energy Sharing Communities (ESC)**.

---

## 🏛️ 1. Die Dual-Core Architektur

```
                           ┌──────────────────────────────────────────────┐
                           │            Sharegy SaaS Plattform            │
                           └──────────────────────┬───────────────────────┘
                                                  │
                 ┌────────────────────────────────┴───────────────────────────────┐
                 ▼                                                               ▼
   ┌───────────────────────────────┐                               ┌───────────────────────────────┐
   │    🟢 SÄULE 1: EMS (FREE/PRO) │                               │    🔵 SÄULE 2: ENERGY SHARING │
   │    Fokus: SOFORT FERTIGSTELLEN│                               │    Fokus: PARALLEL VORBEREITEN│
   ├───────────────────────────────┤                               ├───────────────────────────────┤
   │ • Ziel: Für jeden Haushalt    │                               │ • Ziel: Bürgerenergie/Quartier│
   │ • Daten: MQTT, OTel, Modbus,  │                               │ • Daten: iMSys Zähler (OBIS   │
   │   Wechselrichter-APIs         │                               │   1.8.0 Bezug, 2.8.0 Einspeis)│
   │ • Takt: Sekunden / Minuten (W)│                               │ • Takt: 15-Minuten-Raster     │
   │ • Features: Live-Fluss,       │                               │ • Features: Bilanzierung,     │
   │   Sankey, Spotpreise, Forecast│                               │   Allokation, Abrechnung      │
   │ • Monetarisierung: SaaS-Abo   │                               │ • Monetarisierung: Gebühren   │
   │   (Free vs. Pro Festpreis)    │                               │   pro Zähler / kWh-Clearing   │
   └───────────────────────────────┘                               └───────────────────────────────┘
```

---

## 🔍 2. Bestandsaufnahme & Evaluation: Was fehlt oder ist fehlerhaft?

### ⚠️ A. TimescaleDB (Vorhanden, aber im EMS ungenutzt)
- **Status Quo**:
  - `core_intervalreading` (Zählerdaten) ist als Hypertable registriert.
  - **Problem**: `devices_devicemetric` (die hochfrequente EMS-Telemetrie) ist eine normale PostgreSQL-Tabelle! Bei Tausenden Datenpunkten pro Tag führt dies zu Full-Table-Scans.
  - **Problem**: Die Aggregationen (1m, 5m, 15m, 1h in `devices/services/aggregation.py`) laufen aktuell über Celery-Python-Schleifen, statt die native Power von TimescaleDB (Continuous Aggregates) oder schnellen SQL-Fenstern zu nutzen.
- **Lösung für EMS-Free**:
  1. `devices_devicemetric` als Hypertable (`timestamp`) konfigurieren.
  2. Retention Policy (z. B. Rohdaten nach 14 Tagen löschen oder komprimieren, 5m/1h Aggregationen dauerhaft behalten).

### ⚠️ B. Energiefluss & Sankey (Kern-Feature des EMS)
- **Status Quo**:
  - `energy/flow_engine.py`: Die physikalische Aufteilung (PV → Hauslast → Batterie → Netzeinspeisung) ist auskommentiert.
  - `energy/services/sankey.py`: Generiert duplizierte Kanten, wenn mehrere Geräte auf derselben Etage/im selben Raum liegen.
- **Lösung für EMS-Free**:
  - Echte Flussverteilung aktivieren (Schritt 1.6) und Sankey-Kanten sauber summieren (Schritt 4.2).

### ⚠️ C. Daten-Ingestion (MQTT, OTel, Modbus, Inverter)
- **Status Quo**:
  - MQTT Ingestion läuft robust über `mqtt_consume.py` und spiegelt Werte sofort in den Redis-Live-Cache (`device:{id}:latest_power`).
  - OpenTelemetry Ingest (`providers/opentelemetry/`) ist als Endpoint vorhanden.
  - Modbus / Inverter-Direktanbindungen (z. B. Sungrow, SMA, SolarEdge) müssen über konfigurierbare Parser/Profile harmonisiert werden.
- **Lösung für EMS-Free**:
  - Vereinheitlichter Ingest-Adapter: Egal ob MQTT, OTel oder Webhook – alle schreiben standardisiert in denselben Live-Cache und `DeviceMetric`.

### ⚠️ D. Doppelte Modelle & Bereinigung
- **Status Quo**:
  - `core.Tenant` vs. `tenants.Tenant`: Zwei unterschiedliche Community-Modelle existieren nebeneinander.
- **Lösung**:
  - Konsolidierung auf ein sauberes Modell für Phase 2 (Energy Sharing), damit keine Verwechslungsgefahr mit EMS-Nutzern (`devices.Home`) besteht.

### ⚠️ E. EMS Telemetrie-Deduplizierung & Deadband-Filtering (Neu & Kritisch)
- **Status Quo**:
  - Geräte (Shelly, Tasmota, Wechselrichter) senden alle 1–5 Sekunden Werte. Auch bei unveränderten Werten (z. B. 0 W PV nachts oder konstante 120 W Last) wird jeder Datenpunkt ungefiltert in `DeviceMetric` geschrieben.
  - Das führt zu Millionen redundanter Zeilen, Datenbank-Aufblähung und trägen Aggregationen.
- **Lösung für EMS-Free (2-Stufen-Deduplizierung)**:
  1. **Redis Deadband-Filter im Ingest-Pfad (`mqtt_consume.py` / OTel)**:
     - Live-Cache (`device:{id}:latest_power`) wird bei jedem Paket aktualisiert (UI bleibt ultra-responsiv).
     - DB-Insert in `DeviceMetric` erfolgt nur, wenn:
       a) Der Wert sich signifikant geändert hat ($\Delta > \text{Schwellenwert}$, z. B. $\ge 1\,\text{W}$ oder $0.5\,\%$), ODER
       b) Ein Heartbeat-Intervall abgelaufen ist (z. B. mindestens 1 Record alle 60s als Lebenszeichen).
     - **Ergebnis**: Reduziert DB-Schreiblast und Speicherplatz um **80–90%** ohne Informationsverlust!
  2. **DB Idempotenz-Constraint**:
     - `UniqueConstraint(fields=["device", "metric_key", "timestamp"])` verhindert doppelte Inserts bei Netzwerk-Retries.
  3. **`DeviceLatestMetric` Snapshot-Tabelle ($O(1)$ Statusabfragen)**:
     - Trennung von Zeitreihen-Historie (`DeviceMetric` mit Millionen Zeilen) und aktuellem Gerätestatus (`DeviceLatestMetric` mit exakt 1 Zeile pro Gerät/Metrik).
     - Ersetzt teure `order_by("-timestamp")`-Scans und correlated Subqueries durch blitzschnelle Primärschlüssel-/Index-Lookups ($< 1\,\text{ms}$).

---

## 🎯 3. Die Phasen-Roadmap

```
┌───────────────────────────────────────────────────────────────────────────────┐
│ MEILENSTEIN 1: EMS-FREE VERSION (✅ Abgeschlossen & Produktiv gehärtet)         │
└───────────────────────────────────────────────────────────────────────────────┘
  ├── 1.1 ✅ TimescaleDB Hypertable & Führende Indizes für `DeviceMetric`
  ├── 1.2 ✅ Ingest-Deduplizierung & Deadband-Filter (Redis + Snapshot-Tabelle `DeviceLatestMetric`)
  ├── 1.3 ✅ Energiefluss-Berechnung in `energy/flow_engine.py` (PV → Last → Akku → Netz)
  ├── 1.4 ✅ Sankey-Diagramm Kanten-Aggregation, Balancierung & Flackerfreies Rendering
  ├── 1.5 ✅ Dashboard N+1 Queries aufgelöst (Ladezeit < 50ms)
  ├── 1.6 ✅ Spotpreis-Analyse, Stundenschnitt & Resiliente Public Börsenpreis-Pipeline (13:00-18:59 Schedule)
  ├── 1.7 ✅ PV- & Wetter-Prognose für Dachanlagen (Physics + Open-Meteo 96h + PLZ-Geocoding)
  ├── 1.8 ✅ Operations & Monitoring Dashboard im Django Admin (Live-Badges & Health-Checks)
  ├── 1.9 ✅ Enterprise Multi-Metric Support (OTel/MQTT multi-channel Ingest, API & Modal-Kanalumschalter)
  └── 1.10 ✅ End-to-End Test Suite (15/15 Tests erfolgreich)

┌───────────────────────────────────────────────────────────────────────────────┐
│ MEILENSTEIN 2: EMS-PRO VERSION (Monetarisierung via SaaS-Abo)                  │
└───────────────────────────────────────────────────────────────────────────────┘
  ├── 2.1 Smarte Speicher- & Last-Steuerung (Optimierung nach Börsenstrompreisen & PV-Forecast)
  ├── 2.2 ✅ Machine Learning PV-Prognose (Hybrid Physics + ML - RandomForest/Residuals)
  ├── 2.3 Erweiterte Langzeit-Historie & Export-Funktionen (XLSX, CSV, PDF Berichte)
  └── 2.4 Stripe Subscription-Integration (Free vs. Pro Module)

┌───────────────────────────────────────────────────────────────────────────────┐
│ MEILENSTEIN 3: ENERGY SHARING COMMUNITIES (Vollintegrierte Säule 2)           │
└───────────────────────────────────────────────────────────────────────────────┘
  ├── 3.1 Zähler- & iMSys-Datenmodell finalisieren (`AggregatedReading` OBIS 1.8.0/2.8.0)
  ├── 3.2 Tenant-Modell Konsolidierung (`core.Tenant`)
  ├── 3.3 15-Minuten Community-Bilanzierung & Allokationsschlüssel
  ├── 3.4 Sharing-Tarife, Umlagen & kaufmännische Abrechnungsperioden
  └── 3.5 B2B/B2C Community-Portal (Erzeuger, Verbraucher, Prosumer)
```

---

## 📋 4. Konkreter Action-Plan für die EMS-Free Fertigstellung

| Schritt | Modul | Maßnahme | Impact |
|---|---|---|---|
| **Step 1** | `energy/flow_engine.py` | Vollständige Verteilungslogik (PV → Last → Akku → Netz) aktivieren | 🔥 **Live-Sankey & Energieflüsse 100% korrekt** |
| **Step 2** | `core/management/commands/mqtt_consume.py` | Redis Deadband- & Heartbeat-Filter vor DB-Insert einbauen | 🛡️ **80–90% weniger DB-Speicher / Deduplication** |
| **Step 3** | `devices/models.py` & DB | TimescaleDB Hypertable & führenden Index auf `DeviceMetric.timestamp` anlegen | 🚀 **100x schnellere Historien-Abfragen** |
| **Step 4** | `energy/services/sankey.py` | Kanten-Duplikate vor JSON-Generierung summieren | 🛠️ **Keine Render-Abstürze im Frontend** |
| **Step 5** | `energy/services/energy.py` | EMS-Signal-Abfragen von 4 Einzelqueries auf 1 Batch zusammenfassen | ⚡ **Dashboard Ladezeit unter 50ms** |
| **Step 6** | `market/tasks.py` | Resiliente Börsenpreis-Pipeline & smartes Nachmittags-Polling (Energy-Charts & SMARD) | 📈 **Resiliente Börsenpreis-Darstellung** |
| **Step 7** | `operations/admin.py` & `tasks.py` | Monitoring-Dashboard mit Live-Badges für Tibber, Wetter, MQTT, Spotpreise & aktive Devices | 📊 **Echtzeit-Transparenz im Admin-Backend** |
| **Step 8** | `providers/opentelemetry/` & `DeviceChartModal.jsx` | Multi-Metric Device Ingest, Lead-Power Auto-Detection & Kanal-Auswahl im Chart-Modal | 🎛️ **Volle Multi-Kanal Unterstützung (Shelly 3EM, Inverter, OTel)** |

