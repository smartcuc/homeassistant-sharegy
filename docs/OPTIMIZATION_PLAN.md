# 🛠️ Codebase Review & Schritt-für-Schritt Optimierungsplan

> 📖 **Strategische Gesamt-Roadmap**: Siehe [`docs/SHAREGY_STRATEGIC_ROADMAP.md`](file:///c:/Users/Public/Dev/eswes/docs/SHAREGY_STRATEGIC_ROADMAP.md) für die Dual-Core Produktarchitektur (EMS vs. Energy Sharing Communities).

---

## 📋 Übersicht & Status

| Phase | Bereich | Fokus | Status | Erledigt | Offen |
|---|---|---|---|---|---|
| **Phase 1** | Kritische Bugs & Flusslogik | 🟢 EMS-Free & Core | 🟢 Abgeschlossen | 1.1, 1.2, 1.3, 1.4, 1.6 | 1.5 (Sharing) |
| **Phase 2** | DB- & Performance-Optimierung | 🟢 EMS-Free (TimescaleDB) | 🟢 Abgeschlossen | 2.1, 2.3, 2.4, 2.5, 2.6, 2.7 | 2.2 (Sharing) |
| **Phase 3** | Celery & Buffer-Härtung | 🟢 EMS-Free Stabilität | 🟢 Abgeschlossen | 3.1, 3.2, 3.3, 3.4 | – |
| **Phase 4** | Architektur & Diagramme | 🟢 EMS-Free Sankey & Tests | 🟢 Abgeschlossen | 4.2, 4.3, 4.4 | 4.1 (Sharing) |
| **Phase 5** | EMS-Pro, KI, Apps & Alerting | 🚀 Next Milestones | 🟡 In Planung | – | 5.1 – 5.10 |

---

## Phase 1 — Kritische Bugs & Laufzeitfehler (Sofort beheben)

### [x] 1.1 `NameError: float_val` im MQTT-Ingest beheben
- **Datei**: [`core/management/commands/mqtt_consume.py`](file:///c:/Users/Public/Dev/eswes/core/management/commands/mqtt_consume.py#L222-L240)
- **Status**: ✅ **Erledigt**. `_to_float(value)` wird in `float_val` gespeichert und sicher an `DeviceMetric` und Redis-Cache übergeben.

---

### [x] 1.2 `load_dotenv` Reihenfolge & `ALLOWED_HOSTS` absichern
- **Datei**: [`backend/settings/base.py`](file:///c:/Users/Public/Dev/eswes/backend/settings/base.py#L14-L65)
- **Status**: ✅ **Erledigt**. `load_dotenv()` wird vor allen `os.getenv()` Aufrufen geladen; `ALLOWED_HOSTS`, `CORS` und `CSRF` Listen sind abgesichert.

---

### [x] 1.3 `FieldError: Cannot resolve keyword 'tenant'` in Forecast Accuracy beheben
- **Datei**: [`forecast/services_forecast_accuracy.py`](file:///c:/Users/Public/Dev/eswes/forecast/services_forecast_accuracy.py)
- **Status**: ✅ **Erledigt**. `_resolve_home_and_coords()` löst Home/Koordinaten für Home- und Tenant-Objekte sauber auf; `home`-Filter statt `tenant` verwendet.

---

### [x] 1.4 Doppelte Routing-Einträge & Prefixe in `urls.py` bereinigen
- **Datei**: [`backend/urls.py`](file:///c:/Users/Public/Dev/eswes/backend/urls.py#L58-L82)
- **Status**: ✅ **Erledigt**. Doppelte `email/open/`-Route entfernt; `/api/public/`-Prefix korrigiert.

---

### [ ] 1.5 `AggregatedReading` Unique-Constraint an `obis_code` anpassen
- **Datei**: [`core/models.py`](file:///c:/Users/Public/Dev/eswes/core/models.py#L201)
- **Problem**: `unique_together = ("meter", "period_start")` blockiert das gleichzeitige Speichern von Bezug (`1.8.0`) und Einspeisung (`2.8.0`) desselben Zählers im selben Slot.
- **Lösung**: Constraint erweitern:
  ```python
  unique_together = ("meter", "period_start", "obis_code")
  ```
  *(Anschließend Migration generieren und ausführen)*.

---

### [x] 1.6 Vollständige Energiefluss-Berechnung in `flow_engine.py` aktivieren
- **Datei**: [`energy/flow_engine.py`](file:///c:/Users/Public/Dev/eswes/energy/flow_engine.py#L5-L75)
- **Status**: ✅ **Erledigt**. Vollständige physikalische Verteilungslogik (PV $\rightarrow$ Last $\rightarrow$ Batterie $\rightarrow$ Netz) ist aktiviert und balanciert.

---

## Phase 2 — High-Impact Datenbank- & Query-Optimierung

### [x] 2.1 Index mit führendem `timestamp` auf `DeviceMetric` anlegen
- **Datei**: [`devices/models.py`](file:///c:/Users/Public/Dev/eswes/devices/models.py#L378-L405)
- **Status**: ✅ **Erledigt**. `dm_ts_dev_key_idx` (`["timestamp", "device", "metric_key"]`) und `dm_device_timestamp_idx` (`["device", "-timestamp"]`) sind migriert und aktiv.

---

### [ ] 2.2 Billing-Balance Berechnung (24.000+ Queries -> 1 Query)
- **Datei**: [`billing/services_balance.py`](file:///c:/Users/Public/Dev/eswes/billing/services_balance.py#L65-L82)
- **Problem**: `compute_balance_range` führt pro Slot und Zähler 4-5 Queries aus (Schleife über 96 Slots).
- **Lösung**: Datenbank-seitige Aggregation via Django ORM:
  ```python
  from django.db.models import Sum, Q

  def compute_balance_range_optimized(start, end):
      start = floor_to_billing_slot(start)
      end = floor_to_billing_slot(end)

      rows = (
          AggregatedReading.objects.filter(period_start__gte=start, period_start__lt=end)
          .values("meter_id", "meter__tenant_id", "period_start")
          .annotate(
              consumption=Sum("value", filter=Q(obis_code__startswith="1.8")),
              generation=Sum("value", filter=Q(obis_code__startswith="2.8")),
          )
      )

      slots_to_upsert = []
      for r in rows:
          c = r["consumption"] or Decimal("0")
          g = r["generation"] or Decimal("0")
          slots_to_upsert.append(
              BalanceSlot(
                  meter_id=r["meter_id"],
                  tenant_id=r["meter__tenant_id"],
                  period_start=r["period_start"],
                  consumption_kwh=c,
                  generation_kwh=g,
                  self_consumption_kwh=min(c, g),
                  grid_import_kwh=max(c - g, Decimal("0")),
                  grid_export_kwh=max(g - c, Decimal("0")),
              )
          )

      BalanceSlot.objects.bulk_create(
          slots_to_upsert,
          update_conflicts=True,
          unique_fields=["meter", "period_start"],
          update_fields=[
              "consumption_kwh",
              "generation_kwh",
              "self_consumption_kwh",
              "grid_import_kwh",
              "grid_export_kwh",
          ],
      )
  ```

---

### [x] 2.3 Doppeltes Speichern in `store_weather_payload_for_home` entfernen
- **Datei**: [`forecast/services_weather.py`](file:///c:/Users/Public/Dev/eswes/forecast/services_weather.py#L136-L200)
- **Status**: ✅ **Erledigt**. Auf atomares `bulk_create(..., update_conflicts=True)` umgestellt und doppelten Save entfernt.

---

### [x] 2.4 `bulk_create` in Spot-Price, Forecast & Aggregation Tasks nutzen
- **Dateien**:
  - [`market/tasks.py`](file:///c:/Users/Public/Dev/eswes/market/tasks.py#L50-L165)
  - [`forecast/services_store.py`](file:///c:/Users/Public/Dev/eswes/forecast/services_store.py#L16-L135)
  - [`devices/services/aggregation.py`](file:///c:/Users/Public/Dev/eswes/devices/services/aggregation.py#L82-L220)
  - [`forecast/services_weather_observations.py`](file:///c:/Users/Public/Dev/eswes/forecast/services_weather_observations.py#L62-L155)
  - [`backend/tasks.py`](file:///c:/Users/Public/Dev/eswes/backend/tasks.py)
- **Status**: ✅ **Erledigt**. Alle `update_or_create`-Schleifen wurden durch `bulk_create(..., update_conflicts=True)` ersetzt.

---

### [x] 2.5 `DeviceLatestMetric` Snapshot-Tabelle für $O(1)$ Live-Werte
- **Dateien**: [`devices/models.py`](file:///c:/Users/Public/Dev/eswes/devices/models.py), [`devices/services/metrics.py`](file:///c:/Users/Public/Dev/eswes/devices/services/metrics.py), [`core/management/commands/mqtt_consume.py`](file:///c:/Users/Public/Dev/eswes/core/management/commands/mqtt_consume.py), [`devices/api/views.py`](file:///c:/Users/Public/Dev/eswes/devices/api/views.py)
- **Status**: ✅ **Erledigt**.
  - Ersetzt teure `DeviceMetric.objects.order_by("-timestamp")`-Scans auf Millionen Zeilen durch eine schlanke Snapshot-Tabelle mit exakt 1 Zeile pro Gerät/Metrik (`UniqueConstraint(["device", "metric_key"])`).
  - Direkte Aktualisierung beim Ingest in `mqtt_consume.py`.
  - Blitzschnelle Fallback-Lookups ($< 1\,\text{ms}$) in `get_latest_values()` und im `sankey_data` API-Endpoint.

---

### [x] 2.6 N+1 Queries im Dashboard-Request auflösen
- **Dateien**:
  - [`energy/services/energy.py`](file:///c:/Users/Public/Dev/eswes/energy/services/energy.py#L65-L103): 4 separate Abfragen auf `EMSSignalSource` zu 1 Batch-Abfrage zusammengefasst und mit DeviceConfig konsolidiert.
  - [`energy/services/sankey.py`](file:///c:/Users/Public/Dev/eswes/energy/services/sankey.py#L24-L30): Optimierte Preloads.
- **Status**: ✅ **Erledigt**.

---

### [x] 2.7 EMS Telemetrie-Deduplizierung & Deadband-Filter
- **Dateien**:
  - [`core/management/commands/mqtt_consume.py`](file:///c:/Users/Public/Dev/eswes/core/management/commands/mqtt_consume.py)
  - [`devices/models.py`](file:///c:/Users/Public/Dev/eswes/devices/models.py)
- **Status**: ✅ **Erledigt**.
  1. Live-Cache in Redis wird bei jedem Paket aktualisiert (UI bleibt echtzeitfähig).
  2. DB-Insert in `DeviceMetric` erfolgt nur bei Wertänderung ($\Delta \ge 1.0\,\text{W}$) oder nach 60s Heartbeat.
  3. `DeviceLatestMetric` Snapshot wird bei jedem Update aktualisiert.

---

## Phase 3 — Celery Scheduling, Redis Buffer & Ingest-Härtung

### [x] 3.1 Atomares Auslesen des MQTT-Buffers in Redis
- **Datei**: [`integrations/tasks.py`](file:///c:/Users/Public/Dev/eswes/integrations/tasks.py#L280-L340)
- **Status**: ✅ **Erledigt**. `lrange` und `ltrim` werden atomar in einer Redis-Pipeline ausgeführt; Batch-Device-Lookup und `DeviceMetric`-Felder korrigiert.

---

### [x] 3.2 Celery Beat Schedule Tuning & Public Spot-Price Fallback
- **Dateien**: [`backend/settings/base.py`](file:///c:/Users/Public/Dev/eswes/backend/settings/base.py), [`market/tasks.py`](file:///c:/Users/Public/Dev/eswes/market/tasks.py)
- **Status**: ✅ **Erledigt**.
  1. `fetch-spot-prices-daily`: Läuft im Veröffentlichungsfenster (13:00 - 18:59 Uhr) alle 15 Minuten (`crontab(hour="0,13,14,15,16,17,18", minute="5,20,35,50")`).
  2. Intelligente Day-Ahead Erkennung: Sobald Preise für MORGEN ($\ge 24$ Werte) geladen sind, cacht der Task das Ergebnis und beendet Folgeläufe sofort in $<1\,\text{ms}$.
  3. Öffentliche Fallback-Kaskade: Energy-Charts (Fraunhofer ISE) $\rightarrow$ SMARD (Bundesnetzagentur).
  4. `allocate-user-balance` auf 15-Minuten-Takt (`crontab(minute="*/15")`) harmonisiert.

---

### [x] 3.3 Synchrones `print()` im MQTT-Consumer durch Logger ersetzen
- **Datei**: [`core/management/commands/mqtt_consume.py`](file:///c:/Users/Public/Dev/eswes/core/management/commands/mqtt_consume.py)
- **Status**: ✅ **Erledigt**. Alle `print()`-Aufrufe wurden durch strukturierte Logging-Methoden (`logger.debug`, `logger.info`, `logger.warning`, `logger.error`) ersetzt.

---

### [x] 3.4 Django Admin Operations & Health Monitoring Dashboard
- **Dateien**: [`operations/admin.py`](file:///c:/Users/Public/Dev/eswes/operations/admin.py), [`operations/tasks.py`](file:///c:/Users/Public/Dev/eswes/operations/tasks.py), [`devices/admin.py`](file:///c:/Users/Public/Dev/eswes/devices/admin.py)
- **Status**: ✅ **Erledigt**.
  - 🔌 **Letzte erfolgreiche Tibber-Synchronisation** (`check_tibber_sync`).
  - ☀️ **Letzte Wetterdaten-Aktualisierung** (`check_weather_sync` mit Horizont-Prüfung).
  - 📡 **Letzter MQTT-Message-Eingang** (`check_mqtt` mit Alters-Check).
  - ⚡ **Anzahl aktiver Devices** (`check_active_devices` mit 15m-Online-Status).
  - Visuelle Farb-Badges (🟢 OK, 🟡 WARN, 🔴 ERROR), formatierte JSON-Details und manueller Ausführen-Action-Button im Django Admin.

---

## Phase 4 — Architektur-Konsolidierung & Code-Qualität

### [ ] 4.1 Doppeltes `Tenant` Modell zusammenführen
- **Dateien**: [`core/models.py`](file:///c:/Users/Public/Dev/eswes/core/models.py#L16-L35) vs. [`tenants/models.py`](file:///c:/Users/Public/Dev/eswes/tenants/models.py#L10-L23)
- **Problem**: Zwei separate Tenant-Tabellen mit unterschiedlichen Feldern.
- **Lösung**: Ein zentrales Tenant-Modell etablieren und Fremdschlüssel (`tracking.EventLog`) konsolidieren.

---

### [x] 4.2 Sankey-Kanten im Diagramm aggregieren & Balancierung
- **Datei**: [`energy/services/sankey.py`](file:///c:/Users/Public/Dev/eswes/energy/services/sankey.py#L155-L280)
- **Status**: ✅ **Erledigt**. 
  - Kanten mit identischem `(source, target)` werden vor der JSON-Ausgabe summiert.
  - Vollständige physische Balancierung: PV / Batterie / Netz $\rightarrow$ Haus $\rightarrow$ Einzelverbraucher + Nicht erfasst.
  - Eigene Senken für `Netzeinspeisung` und `Batterieladung`.

---

### [x] 4.3 Resiliente Stundenpreis-Berechnung
- **Datei**: [`market/services_price_analysis.py`](file:///c:/Users/Public/Dev/eswes/market/services_price_analysis.py#L29)
- **Status**: ✅ **Erledigt**. Dynamischer Durchschnitt berechnet auch bei unvollständigen Viertelstundenwerten präzise Mittelwerte.

---

### [x] 4.4 Automatisierte Tests ergänzen
- **Dateien**: [`energy/tests.py`](file:///c:/Users/Public/Dev/eswes/energy/tests.py), [`devices/tests.py`](file:///c:/Users/Public/Dev/eswes/devices/tests.py), [`market/tests.py`](file:///c:/Users/Public/Dev/eswes/market/tests.py), [`forecast/tests.py`](file:///c:/Users/Public/Dev/eswes/forecast/tests.py)
- **Status**: ✅ **Erledigt**. Umfassende Unit-Tests für Energy Flow Engine, Spot-Preis-Analyse, Metrik-Aggregationen und Forecast Physics & Storage wurden erstellt.

---

## Phase 5 — Erweiterte EMS-Pro Features, KI-Prognosen & Alerting

### [x] 5.1 Umstellung auf TimescaleDB Hypertables & Continuous Aggregates
- **Dateien**: [`devices/management/commands/setup_timescaledb.py`](file:///c:/Users/Public/Dev/eswes/devices/management/commands/setup_timescaledb.py), [`db/sql/timescaledb_setup.sql`](file:///c:/Users/Public/Dev/eswes/db/sql/timescaledb_setup.sql)
- **Status**: ✅ **Erledigt**.
  - `devices_devicemetric` (7d Chunks), `devices_devicemetric1m/5m/15m/1h`, `market_spotprice` und `core_intervalreading` als TimescaleDB Hypertables eingerichtet.
  - Automatische Kompressions-Policy (nach 7 Tagen) und Retention-Policy (30 Tage Rohdaten / 60 Tage 1m) aktiviert.
  - Management-Befehl `python manage.py setup_timescaledb` für idempotente Ausführung implementiert.

---

### [x] 5.2 Verbrauchs-Prognose (Household Load Forecast Engine)
- **Dateien**: [`forecast/services_load_forecast.py`](file:///c:/Users/Public/Dev/eswes/forecast/services_load_forecast.py), [`forecast/views.py`](file:///c:/Users/Public/Dev/eswes/forecast/views.py), [`HouseholdLoadForecastCard.jsx`](file:///c:/Users/Public/Dev/eswes/frontend/src/features/forecast/components/HouseholdLoadForecastCard.jsx)
- **Status**: ✅ **Erledigt**.
  - Wochentags- und stundenbasierte Lastprofilberechnung aus historischen `DeviceMetric1h`-Daten mit H0-Standard-Fallback.
  - Temperatur- & Heizgradtage-Kompensation für Wärmepumpen und Klimatisierung aus `WeatherForecast`.
  - Netto-Solarüberschuss- & Netzbezugs-Timeline für 24h/48h.
  - API `GET /api/forecast/load/` & interaktive Frontend-Karte mit Dual-Balken-Chart (PV vs. Last) und Autarkieprognose.

---

### [x] 5.3 Batterie- & SoC-Prognose (State-of-Charge Simulation)
- **Dateien**: [`energy/services/battery_forecast.py`](file:///c:/Users/Public/Dev/eswes/energy/services/battery_forecast.py), [`energy/api/views.py`](file:///c:/Users/Public/Dev/eswes/energy/api/views.py), [`BatteryForecastCard.jsx`](file:///c:/Users/Public/Dev/eswes/frontend/src/features/energy/components/BatteryForecastCard.jsx)
- **Status**: ✅ **Erledigt**.
  - 24h/48h SoC-Verlaufssimulation unter Berücksichtigung von PV-Ertrag, Haushaltslast, Wirkungsgrad (95%) und Notstromreserve (10%).
  - Automatische Berechnung von Voll-Ladezeitpunkt, Entladestand und Nacht-Autarkiegrad.
  - API `GET /api/energy/battery-forecast/` & interaktive Timeline-Karte mit Farbzonen (grün/gelb/rot) und Fluss-Indikatoren im Dashboard.

---

### [x] 5.4 Kontextuelles Help-System (DE / EN)
- **Dateien**: [`frontend/src/features/help/components/HelpDrawer.jsx`](file:///c:/Users/Public/Dev/eswes/frontend/src/features/help/components/HelpDrawer.jsx), [`helpcenter/urls.py`](file:///c:/Users/Public/Dev/eswes/helpcenter/urls.py)
- **Status**: ✅ **Erledigt**.
  - In-App Side-Drawer & Quick-Help-Overlays auf allen Hauptseiten (Dashboard, Energiebilanz, Optimizer, Tarife, Geräte).
  - Kontextsensitive Fachbegriffserklärungen und zweisprachige Pflege (DE / EN).

---

### [x] 5.5 FAQ-Portal & Digitales Benutzerhandbuch (DE / EN)
- **Dateien**: [`helpcenter/management/commands/seed_helpcenter.py`](file:///c:/Users/Public/Dev/eswes/helpcenter/management/commands/seed_helpcenter.py), [`helpcenter/fixtures/helpcenter_initial_data.json`](file:///c:/Users/Public/Dev/eswes/helpcenter/fixtures/helpcenter_initial_data.json)
- **Status**: ✅ **Erledigt**.
  - 8 Kategorien und 14 umfassende Handbuch-Artikel in DE & EN (inkl. Anleitungen für Grafana, Home Assistant und Matter 1.3).
  - Durchsuchbares Wissensportal und In-App-Navigation.

---

### [x] 5.6 Intelligentes Alert- & Anomalie-Erkennungssystem
- **Dateien**: [`alerts/models.py`](file:///c:/Users/Public/Dev/eswes/alerts/models.py), [`alerts/services.py`](file:///c:/Users/Public/Dev/eswes/alerts/services.py), [`alerts/views.py`](file:///c:/Users/Public/Dev/eswes/alerts/views.py), [`AlertCenterModal.jsx`](file:///c:/Users/Public/Dev/eswes/frontend/src/features/alerts/components/AlertCenterModal.jsx), [`AlertNotificationBanner.jsx`](file:///c:/Users/Public/Dev/eswes/frontend/src/features/alerts/components/AlertNotificationBanner.jsx)
- **Status**: ✅ **Erledigt**.
  - 8 Erkennungsregeln implementiert: „Keine PV erkannt (Ertragsausfall)“, „Batterie leer / Notreserve“, „Unerwarteter Nachtverbrauch / Dauerlast“, „Gerät offline / Signalverlust“, „Börsenstrom-Tiefstpreis (Spar-Tipp)“, „Preis-Peak (Dunkelflaute)“, „Netzbezug trotz PV“, „Frostschutz & Wärmepumpen-Vorlauf“.
  - API `GET /api/alerts/`, `POST /api/alerts/<id>/acknowledge/`, `POST /api/alerts/<id>/resolve/` und `POST /api/alerts/seed-demo/`.
  - Animierter Benachrichtigungs-Banner & vollständige Alarm- und Notifikationszentrale mit Schweregrad-Filtern im Dashboard.

---

### [ ] 5.7 Deklaratives Device-Profile Addon-System (3rd-Party Wechelrichter)
- **Bereich**: Ingest & Hardware-Abstraktion (`devices/adapters/`, `profiles/`)
- **Ziel**: 
  - Standardisiertes YAML/JSON-Profilsystem zur Anbindung von 3rd-Party Wechselrichtern und Speichern (Sungrow, SMA, Fronius, Deye, Huawei, Kostal, SolarEdge).
  - Deklaratives Mapping von herstellerspezifischen Modbus-/API-Feldern auf standardisierte Sharegy-Metriken (`pv_power_w`, `battery_soc`, etc.).
- **Impact**: Neue Wechselrichter können in 10 Minuten ohne Backend-Codeänderungen per YAML-Profil eingebunden werden.

---

### [x] 5.8 Bi-direktionale Ökosystem-Plugins (Home Assistant, Grafana & ioBroker)
- **Dateien**: [`plugins/homeassistant/`](file:///c:/Users/Public/Dev/eswes/plugins/homeassistant/), [`plugins/grafana/`](file:///c:/Users/Public/Dev/eswes/plugins/grafana/), [`energy/api/urls_grafana.py`](file:///c:/Users/Public/Dev/eswes/energy/api/urls_grafana.py)
- **Status**: ✅ **Erledigt**.
  - **Home Assistant Custom Component**: 9 Live-Sensoren, `https://sharegy.de` SaaS-Default, sicherer Telemetrie-Push mit Service `sharegy.push_telemetry` und Ladeautomations-Blueprints.
  - **Grafana Enterprise REST-Bridge & Cockpit**: JSON/Infinity Data Source Endpoints (`/api/grafana/search`, `/query`, `/annotations`) & fertiges `sharegy_energy_cockpit.json` Template.
  - **ioBroker / Shelly**: MQTT-Telemetrie-Synchronisation.

---

### [x] 5.12 Matter 1.3 Energy Management Hub & Bridge Engine
- **Dateien**: [`providers/matter/`](file:///c:/Users/Public/Dev/eswes/providers/matter/), [`MatterHubCard.jsx`](file:///c:/Users/Public/Dev/eswes/frontend/src/features/matter/components/MatterHubCard.jsx), [`MatterPairingModal.jsx`](file:///c:/Users/Public/Dev/eswes/frontend/src/features/matter/components/MatterPairingModal.jsx)
- **Status**: ✅ **Erledigt**.
  - Vollständige Implementierung des neuen **CSA Matter 1.3 Energy Management Standards**.
  - Cluster `0x0090` (Electrical Power Measurement: W, V, A, PF), `0x0091` (Electrical Energy Measurement: kWh), `0x0006` (On/Off Relais), `0x0098` / `0x0099` (EVSE & Energy Management).
  - Commissioning-Parser für Matter QR-Codes (`MT:...`), 11-/21-stellige Pairing-Codes und Setup-PINs.
  - REST- und Webhook-APIs unter `/api/matter/*` & Pairing-UI in `InterfacesPage.jsx`.

---

### [x] 5.13 Solar-Prognosegüte & Ist-vs-Soll-Vergleich (%-Genauigkeit)
- **Dateien**: [`forecast/services_accuracy.py`](file:///c:/Users/Public/Dev/eswes/forecast/services_accuracy.py), [`ForecastAccuracyCard.jsx`](file:///c:/Users/Public/Dev/eswes/frontend/src/features/forecast/components/ForecastAccuracyCard.jsx)
- **Status**: ✅ **Erledigt**.
  - Mathematischer Abgleich zwischen prognostizierter und real erzeugter PV-Leistung (WAPE-Formel).
  - Trefferquoten-Scorecard (%-Genauigkeit), Soll-Ist-Überlagerungschart und automatischer String-Korrekturfaktor.

---

### [x] 5.14 Trends & Historische Zeitreihen der virtuellen Zähler
- **Dateien**: [`energy/services/submeter_trends.py`](file:///c:/Users/Public/Dev/eswes/energy/services/submeter_trends.py), [`SubmeterTrendsCard.jsx`](file:///c:/Users/Public/Dev/eswes/frontend/src/features/energy/components/SubmeterTrendsCard.jsx)
- **Status**: ✅ **Erledigt**.
  - Zeitreihenanalyse für alle Sub-Zähler (Wallbox, Wärmepumpe, Einliegerwohnung, Restverbrauch).
  - Transparente Quellen-Aufteilung (Solaranteil vs. Netzbezug vs. Batterie) und Kosteneinsparungs-Trends.

---

### [ ] 5.15 Frei wählbarer Zeitraum (Date-Range-Picker) & Multi-Format Daten-Export (CSV / Excel / JSON / PDF)
- **Bereich**: Energiebilanz, Charts & Reporting (`energy/services/export.py`, `DateRangePicker.jsx`)
- **Ziel**: 
  - Beliebige Start- und Endzeitpunkte für die Auswertung von Verbrauchs-, Erzeugungs- und Kostendaten.
  - Multi-Format Download (Excel `.xlsx`, CSV, JSON und druckfähiger PDF-Monatsbericht) für Steuerberater und Hausverwaltungen.

---

### [ ] 5.9 Mobile Push & Notification Engine
- **Bereich**: Backend Benachrichtigungen (`notifications/`, `tasks_push.py`)
- **Ziel**: 
  - Anbindung von Firebase Cloud Messaging (FCM für Android) und Apple Push Notification Service (APNs für iOS).
  - Verwaltung von Geräte-Tokens (`DeviceToken`-Modell mit Platform, Last-Active, Token).
  - Intelligente Ruhezeiten (Quiet Hours) und Filter für unkritische Hinweise vs. Notfall-Alarme.

---

### [ ] 5.10 Native Mobile Apps (iOS & Android via Capacitor)
- **Bereich**: Mobile Frontend & App Store Deployment (`mobile/`, `@capacitor/core`)
- **Ziel**: 
  - Cross-Platform Wrapper der React/Tailwind Web-App via Capacitor.
  - Biometrie-Login (FaceID / TouchID / Fingerabdruck).
  - Native Lockscreen- & Homescreen-Widgets (Live-PV-Leistung, Batterie-SoC & Optimizer-Bestzeit).
  - Bereitstellung im Apple App Store & Google Play Store.

---

### [ ] 5.11 Subscription- & SaaS-Lizenzmodell (Stripe)
- **Bereich**: Monetarisierung & Billing (`billing/subscriptions/`, `stripe`)
- **Ziel**: 
  - Free / Pro (€ 4,99 / Monat) / Vermieter (€ 14,99 / Monat) Pläne mit automatischer Stripe-Abrechnung.
  - Feature-Gating im Backend und Frontend.

---

## 🎯 6. Verbindliche Prioritätenliste für die nächsten Schritte

```
┌───────────────────────────────────────────────────────────────────────────────┐
│ NÄCHSTER MEILENSTEIN (Sofort starten)                                         │
├───────────────────────────────────────────────────────────────────────────────┤
│ 1. 📅 Task 5.15: Frei wählbarer Zeitraum & Multi-Format Daten-Export          │
│ 2. 📄 Task 5.7: Deklaratives Device-Profile Addon-System (YAML-Templates)     │
└───────────────────────────────────────────────────────────────────────────────┘
                                       │
                                       ▼
┌───────────────────────────────────────────────────────────────────────────────┐
│ MOBILE APPS & PUSH-BENACHRICHTIGUNGEN                                         │
├───────────────────────────────────────────────────────────────────────────────┤
│ 3. 📲 Task 5.9: Mobile Push & Notification Engine (FCM & APNs Dispatcher)    │
│ 4. 📱 Task 5.10: Native iOS & Android Apps via Capacitor (Widgets & Stores)   │
└───────────────────────────────────────────────────────────────────────────────┘
                                       │
                                       ▼
┌───────────────────────────────────────────────────────────────────────────────┐
│ SAAS-MONETARISIERUNG & STRIPE BILLING                                         │
├───────────────────────────────────────────────────────────────────────────────┤
│ 5. 💳 Task 5.11: Subscription- & SaaS-Lizenzmodell (Stripe / Feature-Gating)  │
│ 6. 🧹 Task 4.1: Tenant-Modell Konsolidierung                                  │
└───────────────────────────────────────────────────────────────────────────────┘
```


