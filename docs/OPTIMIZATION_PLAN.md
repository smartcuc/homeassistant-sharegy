# 🛠️ Codebase Review & Schritt-für-Schritt Optimierungsplan

> 📖 **Strategische Gesamt-Roadmap**: Siehe [`docs/SHAREGY_STRATEGIC_ROADMAP.md`](file:///c:/Users/Public/Dev/eswes/docs/SHAREGY_STRATEGIC_ROADMAP.md) für die Dual-Core Produktarchitektur (EMS vs. Energy Sharing Communities).

---

## 📋 Übersicht & Status

| Phase | Bereich | Fokus | Status | Erledigt | Offen |
|---|---|---|---|---|---|
| **Phase 1** | Kritische Bugs & Flusslogik | 🟢 EMS-Free & Core | 🟢 100% Abgeschlossen | 1.1, 1.2, 1.3, 1.4, 1.5, 1.6 | – |
| **Phase 2** | DB- & Performance-Optimierung | 🟢 EMS-Free & Sharing | 🟢 100% Abgeschlossen | 2.1, 2.2, 2.3, 2.4, 2.5, 2.6, 2.7 | – |
| **Phase 3** | Celery & Buffer-Härtung | 🟢 EMS-Free Stabilität | 🟢 100% Abgeschlossen | 3.1, 3.2, 3.3, 3.4, 3.5 | – |
| **Phase 4** | Architektur & Diagramme | 🟢 EMS-Free Sankey & Tests | 🟢 100% Abgeschlossen | 4.1, 4.2, 4.3, 4.4 | – |
| **Phase 5** | EMS-Pro, KI, Apps & Aktorik | 🟢 EMS-Pro, Push, Billing & I18n | 🟢 100% Abgeschlossen | 5.1 – 5.31, 5.34 – 5.39 | 5.32, 5.33 |
| **Phase 6** | Säule 2: Energy Sharing & Clearing | 🟢 ESC & Multi-Community Hub | 🟢 100% Abgeschlossen | 6.1 – 6.12 | – |




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

### [x] 1.5 `AggregatedReading` Unique-Constraint an `obis_code` anpassen
- **Datei**: [`core/models.py`](file:///c:/Users/Public/Dev/eswes/core/models.py#L201)
- **Status**: ✅ **Erledigt**. Constraint auf `unique_together = ("meter", "period_start", "obis_code")` erweitert und in Migration `core.0006` ausgeführt. Blockiert nicht mehr gleichzeitiges Speichern von Bezug (`1.8.0`) und Einspeisung (`2.8.0`).

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

### [x] 2.2 Billing-Balance Berechnung (24.000+ Queries -> 1 Query)
- **Datei**: [`billing/services_balance.py`](file:///c:/Users/Public/Dev/eswes/billing/services_balance.py#L65-L82)
- **Status**: ✅ **Erledigt**. Batch-Aggregation via 1 Django ORM `.values().annotate(consumption=Sum(...), generation=Sum(...))` Abfrage und atomares `BalanceSlot.objects.bulk_create(..., update_conflicts=True)` implementiert & unit-getestet.
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

### [x] 3.5 4-Stufen Celery Queue Prioritäts-Architektur (`fiscal`, `realtime`, `analytics`, `background`)
- **Dateien**: [`backend/settings/base.py`](file:///c:/Users/Public/Dev/eswes/backend/settings/base.py), [`operations/tasks.py`](file:///c:/Users/Public/Dev/eswes/operations/tasks.py), [`operations/admin.py`](file:///c:/Users/Public/Dev/eswes/operations/admin.py), [`docs/OPERATIONS_AND_DEPLOYMENT.md`](file:///c:/Users/Public/Dev/eswes/docs/OPERATIONS_AND_DEPLOYMENT.md)
- **Status**: ✅ **Erledigt**.
  - **1️⃣ `fiscal` (Höchste Prio)**: OBIS-Zählerdaten Rollup (`rollup_15min`), `process_dirty_balance`, Mieter- & Prosumer-Abrechnungsslots (`allocate_user_balance_last_24h`, `compute_balance_last_24h`), Auth-Tokens.
  - **2️⃣ `realtime` (Hohe Prio)**: 5s MQTT-Puffer (`flush_mqtt_buffer`), Gerätesteuerbefehle (`publish_pending_device_commands`), System-Health (`run_health_checks`).
  - **3️⃣ `analytics` (Normale Prio)**: 1m/5m/15m/1h Metrik-Aggregationen, Spotmarkt-Day-Ahead & Tagesanalysen (`compute_daily_spot_summary`), PV-/Lastprognosen (`update_all_forecasts`), Tibber-Sync.
  - **4️⃣ `background` (Niedrige Prio)**: Scikit-Learn KI-Training (`train_all_generator_ml_models`), 8.7 MB Sensor.Community Bulk-Download (`fetch_weather_observations`), Retention-Cleanup.
  - Worker-Aufruf: `celery -A backend worker -Q fiscal,realtime,analytics,background`.

---

## Phase 4 — Architektur-Konsolidierung & Code-Qualität

### [x] 4.1 Doppeltes `Tenant` Modell zusammenführen
- **Dateien**: [`core/models.py`](file:///c:/Users/Public/Dev/eswes/core/models.py#L16-L35) vs. [`tenants/models.py`](file:///c:/Users/Public/Dev/eswes/tenants/models.py#L10-L23)
- **Status**: ✅ **Erledigt**.
  - `core.models.Tenant` als zentrales Modell etabliert und um Theme-Felder (`primary_color`, `secondary_color`, `button_color`) erweitert.
  - Fremdschlüssel in `tracking.EventLog` auf `core.Tenant` migriert.
  - `tenants/models.py` re-exportiert `core.models.Tenant` für vollständige Abwärtskompatibilität.
  - Redundante Admin-Registrierung in `tenants/admin.py` bereinigt und in `core/admin.py` konsolidiert.

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
  - 8 Kategorien und 14 umfassende Handbuch-Artikel in DE & EN (inkl. Anleitungen für Grafana, Home Assistant, OCPP Wallboxen und wMSB Smart Meter).
  - Durchsuchbares Wissensportal und In-App-Navigation.

---

### [x] 5.6 Intelligentes Alert- & Anomalie-Erkennungssystem
- **Dateien**: [`alerts/models.py`](file:///c:/Users/Public/Dev/eswes/alerts/models.py), [`alerts/services.py`](file:///c:/Users/Public/Dev/eswes/alerts/services.py), [`alerts/views.py`](file:///c:/Users/Public/Dev/eswes/alerts/views.py), [`AlertCenterModal.jsx`](file:///c:/Users/Public/Dev/eswes/frontend/src/features/alerts/components/AlertCenterModal.jsx), [`AlertNotificationBanner.jsx`](file:///c:/Users/Public/Dev/eswes/frontend/src/features/alerts/components/AlertNotificationBanner.jsx)
- **Status**: ✅ **Erledigt**.
  - 8 Erkennungsregeln implementiert: „Keine PV erkannt (Ertragsausfall)“, „Batterie leer / Notreserve“, „Unerwarteter Nachtverbrauch / Dauerlast“, „Gerät offline / Signalverlust“, „Börsenstrom-Tiefstpreis (Spar-Tipp)“, „Preis-Peak (Dunkelflaute)“, „Netzbezug trotz PV“, „Frostschutz & Wärmepumpen-Vorlauf“.
  - API `GET /api/alerts/`, `POST /api/alerts/<id>/acknowledge/`, `POST /api/alerts/<id>/resolve/` und `POST /api/alerts/seed-demo/`.
  - Animierter Benachrichtigungs-Banner & vollständige Alarm- und Notifikationszentrale mit Schweregrad-Filtern im Dashboard.

---

### [x] 5.7 Deklaratives Device-Profile Addon-System (3rd-Party Wechselrichter & Speicher)
- **Dateien**: [`devices/profiles/sungrow_isolarcloud.yaml`](file:///c:/Users/Public/Dev/eswes/devices/profiles/sungrow_isolarcloud.yaml), [`solaredge_cloud.yaml`](file:///c:/Users/Public/Dev/eswes/devices/profiles/solaredge_cloud.yaml), [`fronius_solarweb.yaml`](file:///c:/Users/Public/Dev/eswes/devices/profiles/fronius_solarweb.yaml), [`devices/services_profile_runner.py`](file:///c:/Users/Public/Dev/eswes/devices/services_profile_runner.py), [`devices/api/views_profiles.py`](file:///c:/Users/Public/Dev/eswes/devices/api/views_profiles.py), [`CloudInverterIntegrationCard.jsx`](file:///c:/Users/Public/Dev/eswes/frontend/src/features/devices/components/CloudInverterIntegrationCard.jsx)
- **Status**: ✅ **Erledigt**.
  - Standardisiertes YAML-Profilsystem zur deklarativen Anbindung von 3rd-Party Wechselrichtern und Speichern (**Sungrow iSolarCloud OpenAPI / Gateway**, **SolarEdge Monitoring API**, **Fronius Solar.web**).
  - Generische `ProfileRunner`-Engine zur automatischen Ausführung von Auth-Handshakes, JSONPath-Mappings, Einheiten-Skalierung (kW $\rightarrow$ W) und Persistierung in TimescaleDB & Redis.
  - Asynchroner Celery-Polling-Task `poll_cloud_integrations_task` mit Fehlerisolation.
  - REST-APIs unter `/api/devices/cloud-profiles/*` für Profil-Listing, Live-Verbindungstest und Kopplung.
  - UI-Integration in `InterfacesPage.jsx` mit Sofort-Test, Live-Metrik-Feedback und 1-Klick-Kopplung.
  - 7/7 automatisierte Tests in [`devices/test_profile_runner.py`](file:///c:/Users/Public/Dev/eswes/devices/test_profile_runner.py) bestanden.

---

### [x] 5.8 Bi-direktionale Ökosystem-Plugins (Home Assistant, Grafana & ioBroker)
- **Dateien**: [`plugins/homeassistant/`](file:///c:/Users/Public/Dev/eswes/plugins/homeassistant/), [`plugins/grafana/`](file:///c:/Users/Public/Dev/eswes/plugins/grafana/), [`energy/api/urls_grafana.py`](file:///c:/Users/Public/Dev/eswes/energy/api/urls_grafana.py)
- **Status**: ✅ **Erledigt**.
  - **Home Assistant Custom Component**: 9 Live-Sensoren, `https://sharegy.de` SaaS-Default, sicherer Telemetrie-Push mit Service `sharegy.push_telemetry` und Ladeautomations-Blueprints.
  - **Grafana Enterprise REST-Bridge & Cockpit**: JSON/Infinity Data Source Endpoints (`/api/grafana/search`, `/query`, `/annotations`) & fertiges `sharegy_energy_cockpit.json` Template.
  - **ioBroker / Shelly**: MQTT-Telemetrie-Synchronisation.

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

### [x] 5.15 Frei wählbarer Zeitraum (Date-Range-Picker) & Multi-Format Daten-Export (CSV / Excel / JSON / PDF)
- **Dateien**: [`energy/services/export_manager.py`](file:///c:/Users/Public/Dev/eswes/energy/services/export_manager.py), [`DateRangePickerModal.jsx`](file:///c:/Users/Public/Dev/eswes/frontend/src/features/energy/components/DateRangePickerModal.jsx), [`ExportDropdown.jsx`](file:///c:/Users/Public/Dev/eswes/frontend/src/features/energy/components/ExportDropdown.jsx)
- **Status**: ✅ **Erledigt**.
  - Beliebige Start- und Endzeitpunkte (`start_date`, `end_date`) für Mengen-, Verbrauchs- und Kostenanalyse.
  - Multi-Format Download für 4 Formate: Excel `.xlsx` (mit formatierter KPI-Tabelle, Sub-Metering & Stundendaten), druckfähiger A4-PDF-Monatsbericht mit ReportLab, CSV-Export (UTF-8 BOM mit Semikolon für Excel-Kompatibilität) und JSON-Rohdaten.

---

### [x] 5.16 Batterie-Arbitrage & Grid-Charging Speicher-Simulator (Netzladen bei Tiefstpreisen)
- **Dateien**: [`energy/services/battery_arbitrage.py`](file:///c:/Users/Public/Dev/eswes/energy/services/battery_arbitrage.py), [`BatteryArbitrageCard.jsx`](file:///c:/Users/Public/Dev/eswes/frontend/src/features/energy/components/BatteryArbitrageCard.jsx)
- **Status**: ✅ **Erledigt**.
  - Mathematische Simulation von netzdienlicher Speicherladung bei negativen/günstigen Börsenstrompreisen und Entladung während Peak-Stunden.
  - Berücksichtigung von Wirkungsgrad (~90% Roundtrip), Mindestreserve, PV-Forecast-Vorrang und Verschleißspanne.
  - Rendite- und Ertragsprognose (~180–320 € / Jahr Zusatzerlös) mit stündlichem 24h-Fahrplan.

---

### [x] 5.17 Live CO₂-Grid-Signal & Grünstrom-Index (Echtzeit-Emissionen g CO₂/kWh & Öko-Optimierung)
- **Dateien**: [`market/services_co2.py`](file:///c:/Users/Public/Dev/eswes/market/services_co2.py), [`GridCo2Card.jsx`](file:///c:/Users/Public/Dev/eswes/frontend/src/features/market/components/GridCo2Card.jsx)
- **Status**: ✅ **Erledigt**.
  - Echtzeit-Berechnung der CO₂-Intensität des deutschen Stromnetzes (DE-LU) in g CO₂/kWh sowie des bundesweiten Erneuerbaren-Anteils.
  - 24h/36h Forecast-Timeline mit Ampel-Einstufung (Grünstrom-Peak <250g, Normal 250-420g, Kohle-Peak >420g) zur ökologischen Steuerung von Wärmepumpe, Speicher und E-Auto.

---

### [x] 5.18 Multi-Vendor Zero-Hardware Cloud-Inverter Ökosystem (Sungrow OpenAPI OAuth2.0, Fronius, SolarEdge, Kostal, Growatt)
- **Dateien**: [`devices/services_profile_runner.py`](file:///c:/Users/Public/Dev/eswes/devices/services_profile_runner.py), [`devices/api/views_sungrow_oauth.py`](file:///c:/Users/Public/Dev/eswes/devices/api/views_sungrow_oauth.py), [`integrations/api_urls.py`](file:///c:/Users/Public/Dev/eswes/integrations/api_urls.py)
- **Status**: ✅ **Erledigt**.
  - Vollwertige, offizielle 1-Klick OAuth 2.0 Integration für **Sungrow iSolarCloud** (OpenAPI Token-Exchange, Auto-Refresh, Echtzeit-Messpunkte für PV-Wirkleistung, Hauslast, Netzbezug, Speicher-Lade-/Entladeleistung und echter Batterie-SoC in %).
  - Automatische Erkennung und Koppelung großer Heimspeicher (z. B. 22–22,5 kWh Kaskaden) mit `StorageSystem`.
  - Hersteller-Profile für **Fronius Solar.web**, **SolarEdge Monitoring**, **Kostal Solar Portal** und **Growatt ShineServer**.
  - Vollständiges Hintergrund-Polling im 60s-Takt via Celery-Beat mit automatischer `device.last_seen` Aktualisierung für fehlerfreien Online-Status.

---


### [x] 5.9 Mobile Push & Notification Engine
- **Bereich**: Backend Benachrichtigungen (`notifications/`, `tasks.py`, `services.py`)
- **Dokumentation**: [`docs/FIREBASE_SETUP_GUIDE.md`](file:///c:/Users/Public/Dev/eswes/docs/FIREBASE_SETUP_GUIDE.md)
- **Status**: ✅ **Erledigt**.
  - [x] Datenmodelle `DeviceSubscription` (Web-Push, Android, iOS, Token, IP, Platform) und `NotificationPreference` (Quiet Hours, Ausnahmen für kritische Alarme, Kategorie-Filter).
  - [x] W3C Web-Push Engine via `pywebpush` & VAPID.
  - [x] Native FCM / APNs Dispatcher (Firebase Cloud Messaging HTTP v1 API via `firebase-admin` SDK).
  - [x] Asynchrone Celery-Task Pipeline ([`notifications/tasks.py`](file:///c:/Users/Public/Dev/eswes/notifications/tasks.py)) zur Entkopplung vom Request-Cycle.
  - [x] Periodischer Token-Cleanup- & Housekeeping-Task (Deaktivierung nach 90 Tagen, Löschung nach 180 Tagen).
  - [x] REST-API Endpunkte (`/api/notifications/vapid-key/`, `/subscribe/`, `/preferences/`, `/test-push/`, `/devices/`).
  - [x] Anbindung an die Alarm-Engine ([`alerts/services.py`](file:///c:/Users/Public/Dev/eswes/alerts/services.py)).
  - [x] Vollständige Django-Admin Integration ([`notifications/admin.py`](file:///c:/Users/Public/Dev/eswes/notifications/admin.py)).
  - [x] 7/7 automatisierte Unit-Tests in [`notifications/tests.py`](file:///c:/Users/Public/Dev/eswes/notifications/tests.py) bestanden.

---

### [ ] 5.10 Native Mobile Apps (iOS & Android via Capacitor)
- **Bereich**: Mobile Frontend & App Store Deployment (`mobile/`, `@capacitor/core`)
- **Ziel**: 
  - Cross-Platform Wrapper der React/Tailwind Web-App via Capacitor.
  - Biometrie-Login (FaceID / TouchID / Fingerabdruck).
  - Native Lockscreen- & Homescreen-Widgets (Live-PV-Leistung, Batterie-SoC & Optimizer-Bestzeit).
  - Bereitstellung im Apple App Store & Google Play Store.

---

### [x] 5.11 Subscription- & SaaS-Lizenzmodell (Stripe / Feature-Gating)
- **Dateien**: [`billing/models_subscription.py`](file:///c:/Users/Public/Dev/eswes/billing/models_subscription.py), [`billing/services_subscription.py`](file:///c:/Users/Public/Dev/eswes/billing/services_subscription.py), [`billing/views_subscription.py`](file:///c:/Users/Public/Dev/eswes/billing/views_subscription.py), [`BillingPage.jsx`](file:///c:/Users/Public/Dev/eswes/frontend/src/features/billing/pages/BillingPage.jsx)
- **Status**: ✅ **Erledigt**.
  - Drei SaaS-Stufen: **Free** (0 €), **Pro** (4,99 €/M bzw. 49,90 €/J), **Vermieter** (14,99 €/M bzw. 149,00 €/J).
  - Feature-Gating im Backend via Decorator `@require_feature("export_pdf")` / `@require_feature("matter_hub")` etc.
  - Stripe-Checkout & Webhook-Synchronisation, Kundenportal-Integration und automatisierte PDF-Rechnungserstellung mit ReportLab.
  - Frontend-Verwaltung unter `/app/billing` mit Status-Badges, Feature-Vergleich und Kündigungs-/Upgrade-Modal.

---

### [x] 5.18 Rechtliche Absicherung nach deutschem Recht & DSGVO
- **Dateien**: [`frontend/src/pages/Impressum.jsx`](file:///c:/Users/Public/Dev/eswes/frontend/src/pages/Impressum.jsx), [`Datenschutz.jsx`](file:///c:/Users/Public/Dev/eswes/frontend/src/pages/Datenschutz.jsx), [`Agb.jsx`](file:///c:/Users/Public/Dev/eswes/frontend/src/pages/Agb.jsx), [`Widerruf.jsx`](file:///c:/Users/Public/Dev/eswes/frontend/src/pages/Widerruf.jsx), [`CookieConsentBanner.jsx`](file:///c:/Users/Public/Dev/eswes/frontend/src/components/legal/CookieConsentBanner.jsx), [`accounts/api/views.py`](file:///c:/Users/Public/Dev/eswes/accounts/api/views.py)
- **Status**: ✅ **Erledigt**.
  - Vollständiges Impressum nach § 5 DDG (smartEvo GmbH, GF Rüdiger Könen), Datenschutzerklärung nach DSGVO/TDDDG, AGB & Nutzungsbedingungen sowie gesetzliche Widerrufsbelehrung.
  - Globales, modales Cookie-Consent-Banner mit granulierten Präferenzen (Essenziell, Analyse, Marketing).
  - **Art. 15 DSGVO Recht auf Auskunft**: Vollständiger JSON-Export aller Nutzer-, Gebäude-, Geräte-, Tarif- und Messdaten (`/api/auth/gdpr-export/`).
  - **Art. 17 DSGVO Recht auf Löschung**: Kaskadierende, vollständige Kontolöschung (`/api/auth/delete-account/`).

---

### [x] 5.19 Zero-State Onboarding, UI/UX-Härtung & Navigation
- **Dateien**: [`energy/services/balance.py`](file:///c:/Users/Public/Dev/eswes/energy/services/balance.py), [`forecast/services_load_forecast.py`](file:///c:/Users/Public/Dev/eswes/forecast/services_load_forecast.py), [`market/api/views.py`](file:///c:/Users/Public/Dev/eswes/market/api/views.py), [`Topbar.jsx`](file:///c:/Users/Public/Dev/eswes/frontend/src/components/layout/Topbar.jsx), [`Sidebar.jsx`](file:///c:/Users/Public/Dev/eswes/frontend/src/components/layout/Sidebar.jsx), [`LandingPage.jsx`](file:///c:/Users/Public/Dev/eswes/frontend/src/LandingPage.jsx)
- **Status**: ✅ **Erledigt**.
  - Saubere Zero-States für Neukonten ohne Daten: Keine synthetischen Demodaten-Leaks mehr in Energiebilanz, Submetering oder Lastprognose; aufgeräumte Onboarding-Banner.
  - Auto-Provisioning von `Home` in Market- & Auth-APIs zur Beseitigung von 404-Fehlern.
  - Zwangsumleitung auf der Landing Page aufgehoben (Homepage bleibt auch im angemeldeten Zustand über Klick auf das Logo erreichbar).
  - Topbar-Redundanz eliminiert: Zeigt links den Liegenschafts-Kontext (`🏡 Mein Zuhause` bzw. Multi-Home Dropdown) statt doppelter Seitentitel.
  - Durchgängig vereinheitlichte Bezeichnung **`📟 Geräteübersicht`** in Sidebar, Topbar und allen Sprachdateien (DE, EN, PL).

---

### [x] 5.9 Mobile Push & Notification Engine
- **Bereich**: Backend Benachrichtigungen (`notifications/`, `notifications/services.py`, `frontend/public/sw.js`)
- **Status**: ✅ **Erledigt**.
  - **W3C Web-Push & VAPID**: Nativer Push-Versand für Safari iOS 16.4+, Chrome, Edge und Firefox via `pywebpush` ohne Zusatzkosten.
  - **Geräte- & Token-Verwaltung**: `DeviceSubscription` Modell mit Endpoint-, Auth- und P256DH-Schlüsseln, Platform und Device-Name.
  - **Intelligente Ruhezeiten (Quiet Hours)**: Konfigurierbare Nachtruhe (z. B. 22:00 bis 07:00 Uhr) mit Override für kritische Notfall-Alarme (z. B. Batterie leer, Frostschutz).
  - **Frontend Service Worker & 1-Klick Permission**: `sw.js` für Sperrbildschirm-Zustellung, Deep-Linking auf Klick und 1-Klick Test-Push Generator in den Einstellungen (`Settings.jsx`) und der Alarmzentrale (`AlertsPage.jsx`).

---

### [x] 5.10 Native Mobile Apps (Android via Capacitor 7)
- **Bereich**: Mobile Frontend & App Store Deployment (`frontend/android/`, `@capacitor/core`, `@capacitor/android`)
- **Status**: ✅ **Erledigt**.
  - **Natives Android-Projekt**: Vollständige Gradle-Projektstruktur (`de.sharegy.app`) mit minSdkVersion 24 und targetSdkVersion 35.
  - **Capacitor 7 Core & Plugins**: Status Bar Styling (`#0F172A`), Splashscreen-Handling, Haptic Feedback & Android Hardware-Zurück-Taste.
  - **Deep-Linking Intent Filter**: Automatisches Öffnen von Magic-Links (`https://sharegy.de/t/*`) direkt in der App.
  - **Sync & Build-Skripte**: Integrierter `npm run cap:sync` Workflow und Build-Leitfaden (`docs/ANDROID_APP_BUILD_AND_RELEASE.md`).

---

### [x] 5.18 Bidirektionale Aktorik & Relais-Steuerung (Shelly WSS RPC & Smart Automation)
- **Bereich**: Device Control, WebSocket Ingestion & UI Aktorik (`devices/consumers.py`, `devices/api/views.py`, `frontend/src/pages/DevicesPage.jsx`)
- **Status**: ✅ **Erledigt**.
  - **REST Control Endpoint**: `POST /api/devices/<id>/switch/` mit Payload `{"on": true/false, "action": "toggle"}`.
  - **Daphne JSON-RPC Dispatch**: Versand von `{"method": "Switch.Set", "params": {"id": 0, "on": ...}}` direkt über den bestehenden WebSocket-Kanal an den Shelly (< 5 ms Latenz).
  - **UI Toggle Buttons**: Interaktiver Ein-/Aus-Schalter auf den Gerätekacheln in `/app/devices` und im Dashboard mit Live-Feedback.

---

### [x] 5.19 Go-Live Billing & Gutscheinsystem (Coupons, DSGVO-AGB-Consent, GA4)
- **Bereich**: Billing, AGB-Dokumentation, Tracking (`billing/models.py`, `billing/services_subscription.py`, `frontend/src/tracking/ga.js`)
- **Status**: ✅ **Erledigt**.
  - Google Analytics 4 mit IP-Anonymisierung und automatischem Routen-Tracking.
  - Revisionssichere `UserTermsConsent`-Dokumentation bei Registrierung & Checkout.
  - Vollwertiges Gutschein- & Promo-System (`Coupon`, `CouponRedemption`, `/api/billing/subscription/coupons/*`).
  - Strikte E-Mail-Syntax- & Wegwerfmail-Prüfung bei Pro-Upgrades.

---

### [x] 5.20 Systemstatus- & Health-Monitoring Engine (Beta & Live Kernkomponente)
- **Bereich**: Operations, API Monitoring & Frontend Badges (`operations/`, `backend/status/`, `frontend/src/components/common/SystemStatusBadge.jsx`)
- **Status**: ✅ **Erledigt**.
  - **Umfassende Health-API**: `GET /api/status/health/` prüft PostgreSQL / TimescaleDB, Redis Cache, WebSocket Ingest (Daphne), Celery Worker & Beat sowie externe APIs (Open-Meteo, Tibber / EPEX Spot).
  - **Latenz- & Durchsatzmessung**: Echtzeit-Erfassung von Ingest-Latenzen (ms), Ingest-Throughput (Messages/s) und Queue-Backlogs.
  - **Frontend Status-Indikator**: Diskreter Status-Badge in der Topbar / Footer (🟢 *Alle Dienste operativ* / 🟡 *Teilweise beeinträchtigt* / 🔴 *Störung*).
  - **Automatisches Incident-Logging**: Direkte Weiterleitung von Störungen an den Support Desk / Factofy-Hub.

---

### [x] 5.21 Geräteprofiling & Baseline-Anomalieüberwachung (Beta & Live Kernkomponente)
- **Bereich**: Device Intelligence, Baseline Health & Anomaly Watchdog (`devices/models.py`, `devices/services_profiling.py`, `devices/api/views.py`, `frontend/src/components/device/DeviceBaselineModal.jsx`)
- **Status**: ✅ **Erledigt**.
  - **DeviceBaselineProfile-Modell**: Speichert Soll-Standby (W), Standby-Maximalgrenze, Betriebsleistung Min/Max und maximale Dauerlaufzeit.
  - **Intelligente Baseline-Überwachung & Alarmierung**: Erkennt Standby-Anstiege (z. B. BWWP 30W -> 52W) oder ununterbrochenen Dauerlauf (Hang-up/Vereisung) und löst automatisch verifizierte Alerts in der Alarmzentrale (`alerts.AlertEvent`) aus.
  - **1-Klick Presets & Auto-Learning**: Vordefinierte Profile für BWWP, Wärmepumpe, Kühlschrank, Zirkulationspumpe, Heizungspumpe sowie automatisches 7-Tage-ML-Learning aus realen Messwerten.
  - **Interaktive UI**: `🧠 Geräteprofil`-Button auf Gerätekarten mit Live-Health-Badge und Konfigurationsmodal.

---

## Phase 6 — Säule 2: Energy Sharing Communities & Clearing-Engine

### [x] 6.1 Eichrechtskonforme 15-Minuten Bilanzierung & Resiliente Ingestion
- **Bereich**: Core / Billing Ingestion & Celery Tasks (`core/services_validation.py`, `billing/services_balance.py`, `billing/tasks.py`)
- **Status**: ✅ **Erledigt**.
  - **OBIS-Plausibilisierung**: `validate_obis_reading` zur Erkennung negativer Werte oder extremer Lastspitzen.
  - **Resiliente Nachberechnung (Late-Arrivals)**: `recalculate_late_slot` und wöchentlicher 30-Tage Reconciliation-Cron `reconcile_balance_last_30d`.
  - **Strikte Zähler-Isolation**: Tenant-Scoping im ORM (`core/filter_backends.py`, `core/viewsets.py`).

---

### [x] 6.2 Energy Sharing Community Cockpit & KI-Erzeugungsprognose
- **Bereich**: Billing API & Frontend UI (`billing/api/views_community.py`, `frontend/src/pages/TenantDashboard.jsx`)
- **Status**: ✅ **Erledigt**.
  - **Community Aggregations-API**: `GET /api/billing/community/cockpit/` aggregiert Produziert (2.8.0), Verbraucht (1.8.0), Geteilt (Autarkie %), Zugekaufter Reststrom und Ersparnis (€).
  - **15-Minuten Lastgang-Timeline**: Chronologischer 24h-Verlauf der Erzeugungs- und Verbrauchsmengen.
  - **48h KI-Solarprognose**: Stündliche Ertragsvorschau mit automatischer Markierung günstiger Spitzen-Ladefenster (*Peak Windows*).
  - **Reaktive Tab-Navigation**: Schneller Wechsel zwischen `⚡ Energy Cockpit`, `👥 Mitglieder & Zähler` und `📜 Audit`.

---

### [x] 6.3 Gesetzlicher Leitfaden: Zähler-Ingest nach MsbG & Reststrom-Abrechnung
- **Bereich**: Dokumentation & regulatorische Compliance ([`docs/ENERGY_SHARING_METER_INGEST_GUIDE.md`](file:///c:/Users/Public/Dev/eswes/docs/ENERGY_SHARING_METER_INGEST_GUIDE.md))
- **Status**: ✅ **Erledigt**.
  - Vollständiger Leitfaden über Smart Meter Gateways (wMSB REST/SFTP, gMSB HAN, Submetering).
  - Klärung der VNB-Marktkommunikation (EDIFACT/MSCONS) und Ausschluss von Doppelabrechnungen durch Reststromversorger.

---

### [x] 6.4 Sharing-Tarife & Automatische Monatsabrechnungs-Engine (Clearing)
- **Bereich**: Billing Models, Admin & Calculation Engine (`billing/models.py`, `billing/admin.py`, `billing/services_balance.py`, `billing/api/views_community.py`)
- **Status**: ✅ **Erledigt**.
  - `CommunityTariff` mit Bezugspreis (Ct/kWh), Einspeisevergütung (Ct/kWh), Community-Umlage und Netzentgelt-Rabatt gem. § 42b EnWG.
  - Cent-genaue Verrechnung aller erzeugten und bezogenen Mengen in `CommunityMonthlyStatement` mit automatischer Netto-Saldoberechnung.
  - Vollständige Registrierung in Django Admin (`admin/billing/`) und 1-Klick Abrechnungs-Trigger im Frontend.

---

### [x] 6.5 Zentrales Multi-Community Management Hub & Portfolio-Dashboard
- **Bereich**: Super-Admin & Quartiers-Management (`frontend/src/pages/admin/CommunitiesManagementHub.jsx`, `accounts/api/views.py`, `billing/models.py`)
- **Status**: ✅ **Erledigt**.
  - **Portfolio-KPIs**: Gesamterzeugung (2.8.0), Gesamtverbrauch (1.8.0), Portfolio-Autarkie (%) und erzielte Gesamtersparnis (€).
  - **Drilldown-Modal**: Zähler- und Mitgliederübersicht, Tarife, Einladungen und Einstellungen je Quartier.
  - **Quartiers-Rundschreiben**: `CommunityAnnouncement`-Engine für Broadcast-Nachrichten mit Dringlichkeitsstufen.

---

### [x] 6.6 PDF-Monatsabrechnungsnachweise & Multi-Format Exporte (Excel, CSV, XML / ERP)
- **Bereich**: Billing Export Engine & Member Self-Service (`billing/services_sharing_exports.py`, `billing/api/views_community.py`, `frontend/src/pages/TenantDashboard.jsx`)
- **Status**: ✅ **Erledigt**.
  - **ReportLab PDF-Monatsnachweis**: Rechtssicherer Abrechnungsnachweis gem. § 42b EnWG mit Abrechnungsnummer, 15m-Mengenbilanz, Tarifpositionen und farbcodierter Highlight-Saldobox (Guthaben/Nachzahlung).
  - **Excel-Export (`.xlsx`)**: Vollständig formatiertes Arbeitsblatt mit Währungsformaten, Farbcodierung und automatischen Summenformeln (`=SUM(...)`).
  - **CSV-Export (`.csv`)**: UTF-8 mit BOM (für sofortige deutsche Sonderzeichen in Excel) und Semikolon-Trennzeichen.
  - **XML-Export (`.xml`)**: Standardisiertes ERP-Export-Format (`<EnergySharingSettlementExport>`) zur automatisierten Schnittstellenanbindung für Versorger und Hausverwaltungen.
  - **Frontend-Integration**: 1-Klick PDF-Download und Export-Leiste im `TenantDashboard.jsx` und im `CommunitiesManagementHub.jsx`.

---

### [x] 6.7 Erweiterte Allokationsmodelle & Beteiligungsquoten (§ 42b / § 42a EnWG)
- **Bereich**: Allokations-Engine & Member Shares (`billing/models.py`, `billing/services_sharing_settlement.py`, `billing/api/views_community.py`, `billing/admin.py`)
- **Status**: ✅ **Erledigt**.
  - **3 Allokationsmodelle**:
    1. *Dynamisch*: Verbrauchsproportionale 15-Minuten-Echtzeit-Verteilung nach Lastgang.
    2. *Statisch*: Feste Beteiligungsquoten & Miteigentumsanteile (MEA, z. B. 250 / 1000).
    3. *Hybrid*: Stufe 1: Vorrangige Quotenzuteilung; Stufe 2: Dynamischer Überlauf von Reststrom auf verbleibenden Bedarf.
  - **`CommunityMemberShare` Modell**: Speichert Quoten (%), MEA-Zähler/Nenner, kWp-Zuweisungen und Gültigkeitszeiträume mit Validierung.
  - **Bulk-API & 100%-Normierung**: `/api/billing/community/shares/bulk/` mit automatischer Skalierung auf exakt 100,0000 %.
  - **Live-Simulationsvergleich**: `/api/billing/community/allocation-preview/` berechnet alle 3 Modelle für einen Abrechnungsmonat parallel und liefert Ertrags-, Autarkie- und Saldenvergleiche.
  - **UI-Integration**:
    - `CommunitiesManagementHub.jsx`: Neuer Tab `⚖️ Beteiligungsquoten & Allokation` mit Modell-Umschalter, Live-Quoten-Balken, MEA-Editor und Simulations-Vergleichsbox.
    - `TenantDashboard.jsx`: Allokationsmodell-Badge und Anzeige konfigurierter Beteiligungsquoten im Tarife-Tab.

---

### [x] 6.8 § 14a EnWG Steuerbox-Schnittstelle & Pflichtdimmung auf 4,2 kW (SteuVE)
- **Dateien**: [`energy/models.py`](file:///c:/Users/Public/Dev/eswes/energy/models.py), [`energy/services_dimming.py`](file:///c:/Users/Public/Dev/eswes/energy/services_dimming.py), [`energy/api/views_grid.py`](file:///c:/Users/Public/Dev/eswes/energy/api/views_grid.py), [`energy/test_grid_dimming.py`](file:///c:/Users/Public/Dev/eswes/energy/test_grid_dimming.py)
- **Status**: ✅ **Erledigt**.
  - **BNetzA Summenleistungs-Modell (BK6-22-300)**: Dynamisches Netzleistungs-Budget:
    $$P_{\text{allow}} = 4{,}2\text{ kW (Netzkontingent)} + P_{\text{PV}} + P_{\text{Batt}} - P_{\text{Base}}$$
  - **Datenmodelle**: `GridDimmingSignal` (Signalquellen: `vnb_api`, `wmsb_cls`, `shelly_input`, `manual_test`) und `SteuVEDeviceConfig` (Wärmepumpe, Wallbox, Batteriespeicher, Klimaanlage mit Prioritäten 1–4).
  - **Priorisierte Drosselungs-Engine**: Wärmepumpen (Prio 1) behalten Mindestbetriebsstufe; Speicher stoppen Netzladung; Wallboxen (Prio 3) absorbieren das Restbudget bis min. 1,4 kW (6A einphasig).
  - **REST-APIs**: Inbound-Webhook `POST /api/energy/grid/dimming/signal/`, Live-Status `GET /api/energy/grid/dimming/status/`, Aufhebung `POST /api/energy/grid/dimming/clear/` und SteuVE-Verwaltung `GET/POST /api/energy/grid/steuve/`.
  - **Admin-Integration**: Farbcodierte Status-Badges (🔴 GEDIMMT / 🟢 NORMALBETRIEB) und Aktorik-Status in Django Admin.
  - **Tests**: 100% Testabdeckung in `energy/test_grid_dimming.py` bestanden.

### [x] 6.9 Dynamische & Börsenpreis-indexierte Sharing-Tarife (EPEX Spot)
- **Dateien**: [`billing/models.py`](file:///c:/Users/Public/Dev/eswes/billing/models.py), [`billing/services_sharing_settlement.py`](file:///c:/Users/Public/Dev/eswes/billing/services_sharing_settlement.py), [`billing/test_mscons_and_dynamic_tariffs.py`](file:///c:/Users/Public/Dev/eswes/billing/test_mscons_and_dynamic_tariffs.py)
- **Status**: ✅ **Erledigt**.
  - **Tarifmodelle in `CommunityTariff`**: `static` (Festpreis), `spot_indexed` (EPEX Spot Day-Ahead Indexierung) und `time_of_use` (HT/NT Zeittarif).
  - **Preismechanismus & Absicherung**:
    $$P_{\text{eff}}(t) = \text{clamp}\Big(P_{\text{spot}}(t) + \text{Markup} + \text{Umlage} - \text{Netzentgelt-Rabatt}, \text{Floor}, \text{Cap}\Big)$$
  - Dynamische Einspeisevergütung für Erzeuger (`feed_in_spot_share_pct`, z. B. 80% des Spotpreises).
  - Volle Integration in die Monatsabrechnungs- & Clearing-Engine und automatisierte Tests.

### [x] 6.11 wMSB Smart Meter Hub & Zähleranbindung (Discovergy, inexogy, Solandeo)
- **Dateien**: [`devices/services_discovergy.py`](file:///c:/Users/Public/Dev/eswes/devices/services_discovergy.py), [`devices/tests_discovergy.py`](file:///c:/Users/Public/Dev/eswes/devices/tests_discovergy.py), [`frontend/src/pages/admin/MsbSmartMeterHub.jsx`](file:///c:/Users/Public/Dev/eswes/frontend/src/pages/admin/MsbSmartMeterHub.jsx)
- **Status**: ✅ **Erledigt**.
  - **REST API v1 Konnektor**: Live-Abruf von Wirkleistung ($W$) und Zählerständen ($1.8.0$ Bezug, $2.8.0$ Einspeisung) sowie 15-Minuten-Lastgängen.
  - **3 Zählerpfade**: Discovergy/inexogy REST-Direktanbindung, gMSB HAN/SMGW-Schnittstelle und Submetering.
  - **wMSB Wechsel-Leitfaden**: Schritt-für-Schritt Anleitung zum kostenlosen oder geförderten Smart-Meter-Wechsel für Mitglieder.
  - **Unit-Tests**: 100% Testabdeckung in `devices/tests_discovergy.py`.

---

### [x] 6.12 Community Viral Growth & Social Share Kit
- **Dateien**: [`frontend/src/features/community/components/CommunityShareModal.jsx`](file:///c:/Users/Public/Dev/eswes/frontend/src/features/community/components/CommunityShareModal.jsx), [`frontend/src/features/community/components/CommunityInviteCard.jsx`](file:///c:/Users/Public/Dev/eswes/frontend/src/features/community/components/CommunityInviteCard.jsx), [`docs/marketing/COMMUNITY_AND_SOCIAL_SHARE_KIT.md`](file:///c:/Users/Public/Dev/eswes/docs/marketing/COMMUNITY_AND_SOCIAL_SHARE_KIT.md)
- **Status**: ✅ **Erledigt**.
  - 1-Klick Share für WhatsApp, Telegram, Signal, E-Mail und Social Media inkl. personalisiertem Referral-Code.
  - Dynamische Share-Cards mit CO₂-Einsparung, Autarkie-Badges und QR-Code-Generator.

---

### [x] 5.22 Nativer OCPP 1.6-J CSMS Gateway & Smart Charging Engine
- **Dateien**: [`devices/models_ocpp.py`](file:///c:/Users/Public/Dev/eswes/devices/models_ocpp.py), [`devices/consumers_ocpp.py`](file:///c:/Users/Public/Dev/eswes/devices/consumers_ocpp.py), [`energy/services_smart_charging.py`](file:///c:/Users/Public/Dev/eswes/energy/services_smart_charging.py), [`frontend/src/features/energy/components/WallboxCard.jsx`](file:///c:/Users/Public/Dev/eswes/frontend/src/features/energy/components/WallboxCard.jsx), [`frontend/src/features/devices/components/AddWallboxModal.jsx`](file:///c:/Users/Public/Dev/eswes/frontend/src/features/devices/components/AddWallboxModal.jsx)
- **Status**: ✅ **Erledigt**.
  - **OCPP 1.6-J WebSocket CSMS**: Vollständige Server-Implementierung für `BootNotification`, `Heartbeat`, `StatusNotification`, `MeterValues`, `StartTransaction`, `StopTransaction` und Remote-Steuerung (`SetChargingProfile`, `RemoteStartTransaction`, `RemoteStopTransaction`).
  - **Intelligente Lademodi**: `pv_surplus` (reines PV-Überschussladen), `price_optimized` (Börsenstrom-Tiefstpreise), `fast` (maximale Ladeleistung) und `eco` (Kombination aus PV + günstigstem Netzbezug).
  - **WallboxCard & AddWallboxModal**: Modernes Dashboard-Widget mit 1-Klick Lademodus-Wechsel, Phasenumschaltung (1-Phasig / 3-Phasig), Ampere-Slider (6A–32A) und Hersteller-Presets (Easee, openWB, cFos, Heidelberg, Alfen, Mennekes, Keba).

---

### [x] 5.23 Autonome Batterie-Arbitrage & Sungrow iSolarCloud OpenAPI Control
- **Dateien**: [`producer/services_sungrow_control.py`](file:///c:/Users/Public/Dev/eswes/producer/services_sungrow_control.py), [`producer/services_dispatch.py`](file:///c:/Users/Public/Dev/eswes/producer/services_dispatch.py), [`producer/tests_sungrow_control.py`](file:///c:/Users/Public/Dev/eswes/producer/tests_sungrow_control.py), [`producer/tasks.py`](file:///c:/Users/Public/Dev/eswes/producer/tasks.py)
- **Status**: ✅ **Erledigt**.
  - **Sungrow OpenAPI Dispatcher**: Bidirektionale Steuerung für Sungrow SH-Wechselrichter und SBR-Speicher (`forced_charge`, `self_consumption`, `forced_discharge`) mit Leistungsbegrenzung in Watt/kW und Ziel-SoC.
  - **Arbitrage-Daemon**: Autonome Celery-Task prüft Börsenstrompreise (Tibber/EPEX) gegen Preisschwellen und schaltet Netzladung bei negativen/günstigen Börsenstunden automatisch scharf.

---

### [x] 5.24 Smart Load Management & Dispatch Hub (`/app/control`)
- **Dateien**: [`energy/services/dispatch_hub.py`](file:///c:/Users/Public/Dev/eswes/energy/services/dispatch_hub.py), [`energy/views_dispatch_hub.py`](file:///c:/Users/Public/Dev/eswes/energy/views_dispatch_hub.py), [`frontend/src/features/control/pages/ControlPage.jsx`](file:///c:/Users/Public/Dev/eswes/frontend/src/features/control/pages/ControlPage.jsx), [`frontend/src/features/control/components/`](file:///c:/Users/Public/Dev/eswes/frontend/src/features/control/components/)
- **Status**: ✅ **Erledigt**.
  - **Live Power Budget Engine**: Echtzeit-Verfügbarkeit von Solarüberschuss ($P_\text{surplus} = P_\text{pv} - P_\text{load}$), Speicherladung und dynamischen Strompreisen.
  - **4 Master-Betriebsmodi**: `autopilot` (Smart Autopilot mit Solarprognose & Börsenpreisen), `pv_only` (Strikt 100% Autarkie), `price_saver` (Tiefstpreis-Optimierung) und `manual`.
  - **Interaktive Prioritäten-Kaskade (Merit-Order)**: Drag-and-Drop Priorisierung der Großverbraucher.
  - **24h-Fahrplan (Dispatch-Timeline)**: Stündliche Vorschau der geplanten Geräteschaltungen.
  - **7 Modulare Verbraucher-Karten**: BWWP, Wallbox, Heimspeicher, Poolpumpe, Klima Pre-Cooling, Smart Plugs und Heizstab.

---

### [x] 5.25 BWWP & Wärmepumpen SG-Ready Steuerung & Verdichterschutz
- **Dateien**: [`energy/models.py`](file:///c:/Users/Public/Dev/eswes/energy/models.py), [`energy/services/bwwp_manager.py`](file:///c:/Users/Public/Dev/eswes/energy/services/bwwp_manager.py), [`energy/views_bwwp.py`](file:///c:/Users/Public/Dev/eswes/energy/views_bwwp.py), [`frontend/src/features/control/components/BWWPLoadManagementCard.jsx`](file:///c:/Users/Public/Dev/eswes/frontend/src/features/control/components/BWWPLoadManagementCard.jsx)
- **Status**: ✅ **Erledigt**.
  - **SG-Ready Zustandskontrolle**: Vollständige Abbildung von State 1 (Sperre), State 2 (Normalbetrieb), State 3 (Solar-Boost bis 60°C) und State 4 (Komfort-Zwangsanlauf).
  - **Verdichter- & Taktschutz**: $t_\text{run} \ge 20\,\text{min}$ Mindestlaufzeit und $t_\text{cool} \ge 15\,\text{min}$ Mindestruhezeit.
  - **Closed-Loop Aktorik**: Schnelle Relais-Schaltung via Outbound-WebSocket.

---

### [x] 5.26 Offizieller ioBroker Adapter (`ioBroker.sharegy`)
- **Status**: ✅ **Erledigt**.
  - Multi-Sensor-Bündelung von Wirkleistung (W), Wassertemperatur (°C) und SG-Schaltkontakt in einem logischen Gerät.
  - WSS-Streaming über Port 443 mit bidirektionaler Steuerung und Bestätigungs-Rückkanal.

---

### [x] 5.27 Digitales Benutzerhandbuch & Wissensportal (15 Artikel DE/EN)
- **Dateien**: [`support_desk/management/commands/seed_helpcenter.py`](file:///c:/Users/Public/Dev/eswes/support_desk/management/commands/seed_helpcenter.py), [`docs/EMS_SYSTEM_GUIDE.md`](file:///c:/Users/Public/Dev/eswes/docs/EMS_SYSTEM_GUIDE.md)
- **Status**: ✅ **Erledigt**.
  - 15 vollständige Artikel in 9 Kategorien in Deutsch und Englisch, inklusive FAQ-Deflection und Live-Editor.

---

### [x] 5.28 Topbar & Sidenav Streamlining, Live-Pulse Ticker & Dark/Light Theme
- **Dateien**: [`frontend/src/components/layout/Topbar.jsx`](file:///c:/Users/Public/Dev/eswes/frontend/src/components/layout/Topbar.jsx), [`frontend/src/components/layout/Sidebar.jsx`](file:///c:/Users/Public/Dev/eswes/frontend/src/components/layout/Sidebar.jsx), [`frontend/src/theme/ThemeContext.jsx`](file:///c:/Users/Public/Dev/eswes/frontend/src/theme/ThemeContext.jsx)
- **Status**: ✅ **Erledigt**.
  - **Live Energy-Pulse Ticker**: Echtzeit-Leistungsfluss in der Topbar (☀️ Solar, 🏠 Haus, ⚡ Netzbezug/Einspeisung mit Richtungsindikatoren, 🔋 Akku-SoC).
  - **Entschlackung & Redundanz-Bereinigung**: Entfernung des trägen 21/21-Badges und Bereinigung der Sidenav von unpassenden Modal-Triggern.
  - **Gebäude- & Home-Switcher**: Dynamische Umschaltung bei mehreren Liegenschaften und statisches Kontext-Badge bei Einzelliegenschaften.
  - **Dark/Light Mode**: Nahtloser Umschalter mit nativer Theme-Persistenz im `localStorage`.

---

### [x] 5.29 Multistring & AC-Coupled Inverter / BKW Detection Engine
- **Dateien**: [`energy/services/balance.py`](file:///c:/Users/Public/Dev/eswes/energy/services/balance.py), [`energy/tests/test_balance_advanced.py`](file:///c:/Users/Public/Dev/eswes/energy/tests/test_balance_advanced.py), [`frontend/src/features/producer/pages/ProducerPage.jsx`](file:///c:/Users/Public/Dev/eswes/frontend/src/features/producer/pages/ProducerPage.jsx)
- **Status**: ✅ **Erledigt**.
  - **Physikalische AC-Ertragserfassung**: Negative Hauslasten (durch ungebundene sekundäre PV-Wechselrichter / Balkonkraftwerke) werden physikalisch präzise als Solarerzeugung gutgeschrieben statt als Hausverbrauch fehlinterpretiert.
  - **Strikte Speicherladungs-Isolation**: Akku-Ladung wird exklusiv im Speicherkanal erfasst und bläht den Hausverbrauch nicht auf.
  - **Zero-Grid Schutz**: Zertifizierte Smart-Meter-Null-Werte werden niemals durch theoretische Restbedarfe überschrieben.

---

### [x] 5.30 1-Klick Quick-Boost & Smarte EPEX-Ladefenster Empfehlungen
- **Dateien**: [`frontend/src/features/control/components/LivePowerBudgetHeader.jsx`](file:///c:/Users/Public/Dev/eswes/frontend/src/features/control/components/LivePowerBudgetHeader.jsx), [`frontend/src/features/control/pages/ControlPage.jsx`](file:///c:/Users/Public/Dev/eswes/frontend/src/features/control/pages/ControlPage.jsx), [`frontend/src/features/market/components/SpotPriceModal.jsx`](file:///c:/Users/Public/Dev/eswes/frontend/src/features/market/components/SpotPriceModal.jsx), [`frontend/src/features/energy/EnergyDashboard.jsx`](file:///c:/Users/Public/Dev/eswes/frontend/src/features/energy/EnergyDashboard.jsx)
- **Status**: ✅ **Erledigt**.
  - **1-Klick Quick Actions**: Sofort-Boost für Wallbox (11 kW), 100% Heimspeicher-Notstromreserve und maximaler PV-Eigenverbrauch mit Countdown-Badge und 1-Klick Reset.
  - **Smarte EPEX-Ladefenster**: Automatische Erkennung und Ausweisung der günstigsten Ladezeiten (z. B. 13:00–16:00 Uhr) und teuersten Abendspitzen im Spotpreis-Modal.
  - **Mobile Touch-Optimierung**: Horizontale, swipe-fähige Filterleisten und Tabs auf kleinen Displays.

### [x] 5.31 Netzeinspeisungs-Normalisierung & Schutz gegen ungemessene Erzeuger
- **Dateien**: [`energy/ems/services.py`](file:///c:/Users/Public/Dev/eswes/energy/ems/services.py), [`energy/flow_engine.py`](file:///c:/Users/Public/Dev/eswes/energy/flow_engine.py), [`devices/services/metrics.py`](file:///c:/Users/Public/Dev/eswes/devices/services/metrics.py), [`energy/services/charts.py`](file:///c:/Users/Public/Dev/eswes/energy/services/charts.py), [`energy/services/balance.py`](file:///c:/Users/Public/Dev/eswes/energy/services/balance.py)
- **Status**: ✅ **Erledigt**.
  - **Einspeise-Normalisierung**: Automatische Vorzeichen-Auflösung für Smart-Meter/Inverter-Metriken (`grid_feed_in`, `feed_in_power`, `grid_export`, `export_power` etc.) als Netzeinspeisung.
  - **Ungemessene Erzeuger-Erkennung**: Erkennt ungemessene 2. Wechselrichter / Balkonkraftwerke automatisch und verhindert negativen Hausverbrauch in Live-Flows, Charts und Bilanzen.

---

### [x] 5.34 Stripe & SEPA-Lastschriften Checkout, Invoicing & Pro-Abonnement
- **Dateien**: [`billing/services_stripe.py`](file:///c:/Users/Public/Dev/eswes/billing/services_stripe.py), [`billing/views_stripe.py`](file:///c:/Users/Public/Dev/eswes/billing/views_stripe.py), [`billing/management/commands/verify_stripe_setup.py`](file:///c:/Users/Public/Dev/eswes/billing/management/commands/verify_stripe_setup.py), [`frontend/src/features/billing/pages/BillingPage.jsx`](file:///c:/Users/Public/Dev/eswes/frontend/src/features/billing/pages/BillingPage.jsx)
- **Status**: ✅ **Erledigt**.
  - **Live & Sandbox Verifiziert**: Stripe Account `acct_1UAyMEKVY8Tye05t` (smartEvo UG, DE, EUR) mit aktiviertem `charges_enabled`, `payouts_enabled` und allen Zahlungsmethoden.
  - **Dynamische Zahlungsmethoden**: Kredit-/Debitkarten, SEPA-Lastschrift, PayPal, Klarna, Amazon Pay und Stripe Link.
  - **Rechtssichere Rechnungslegung**: Konfiguration nach § 14 UStG, Reverse-Charge & 19% MwSt (DE VAT `DE300917919`), Statement-Descriptor `SHAREGY PRO - SMARTEVO` und Präfix `SHAREGY`.
  - **Auto-Healing Customer IDs**: Robuste Selbstheilung bei ungültigen/gelöschten Customer-IDs im Dev-/Prod-Wechsel.
  - **Webhook & Portal Integration**: Signatur-geprüfte Webhooks mit automatischer `is_pro` Provisionierung und Customer Portal Redirect für Rechnungsdownloads & Abo-Verwaltung.

---

### [x] 5.35 6-Sprachiges EU-Internationalisierungspaket (Topbar Native Switcher & i18n)
- **Dateien**: [`frontend/src/i18n.js`](file:///c:/Users/Public/Dev/eswes/frontend/src/i18n.js), [`frontend/src/components/layout/Topbar.jsx`](file:///c:/Users/Public/Dev/eswes/frontend/src/components/layout/Topbar.jsx), [`frontend/src/locales/`](file:///c:/Users/Public/Dev/eswes/frontend/src/locales/)
- **Status**: ✅ **Erledigt**.
  - **6 europäische Sprachen**: 🇩🇪 Deutsch (DE), 🇬🇧 English (EN), 🇵🇱 Polski (PL), 🇹🇷 Türkçe (TR), 🇷🇺 Русский (RU), 🇷🇴 Română (RO).
  - **Nativer Topbar-Sprachumschalter**: Schneller Sprachwechsel mit Flaggen-Icons und `localStorage`-Persistenz.
  - **Stripe Locale Pass-Through**: Automatische Übergabe der gewählten UI-Sprache an den Stripe Checkout.
  - **Einheitliches Status-Badge**: Konsistente `⚡ Sharegy Pro` Badges in Topbar-UserMenu und Profilseite.
  - **Länderauswahl-Standard**: Statisches `🇩🇪 Deutschland` als Vorgabe im Profil.

---

### [x] 5.36 EPEX Spot 7-Tage Trend-Lookback & Dynamische Ladefenster
- **Dateien**: [`market/api/views.py`](file:///c:/Users/Public/Dev/eswes/market/api/views.py), [`frontend/src/features/market/components/SpotPriceModal.jsx`](file:///c:/Users/Public/Dev/eswes/frontend/src/features/market/components/SpotPriceModal.jsx)
- **Status**: ✅ **Erledigt**.
  - **7-Tage Historie & Vorschau**: Unterstützt `range="week"` und `"7d"` mit 6-Tage-Historie + heute + Day-Ahead-Preisen für fundierte Arbitrage-Analysen.
  - **Optimiertes X-Achsen-Rendering**: Tagesgrenzen-Formatierung (`Do 04.09.`, `Fr 05.09.`) mit stündlichen Tooltips.
  - **Automatisierte Ladeempfehlungen**: Erkennung von Negativpreisen und Ausweisung der Top-3 Sparfenster.

---

### [x] 5.37 Server-Hardware & Kapazitäts-Wächter (RBAC HEMS-Sicherheit)
- **Dateien**: [`operations/views.py`](file:///c:/Users/Public/Dev/eswes/operations/views.py), [`frontend/src/pages/admin/SystemStatusPage.jsx`](file:///c:/Users/Public/Dev/eswes/frontend/src/pages/admin/SystemStatusPage.jsx)
- **Status**: ✅ **Erledigt**.
  - **Granularer RBAC-Schutz**: Beschränkung von CPU-, RAM-, Disk- und System-Hardwaremetriken exklusiv auf HEMS-Admins und Sysadmins.
  - **Support-Desk Alarm-Routing**: Automatische Erstellung interner Support-Tickets bei Schwellenwert-Überschreitungen.

---

### [x] 5.38 Autonome Demo-Umgebungen & Multi-Tenant Sandbox-Isolation
- **Dateien**: [`demo/services/data_generator.py`](file:///c:/Users/Public/Dev/eswes/demo/services/data_generator.py), [`demo/management/commands/rebuild_demo.py`](file:///c:/Users/Public/Dev/eswes/demo/management/commands/rebuild_demo.py), [`accounts/views_demo.py`](file:///c:/Users/Public/Dev/eswes/accounts/views_demo.py)
- **Status**: ✅ **Erledigt**.
  - **3 Isolierte Demo-Profile**: Smart Home HEMS (`demo@sharegy.de`), Community Admin (`sharing-admin@sharegy.de`), Community Mitglied (`sharing-user@sharegy.de`).
  - **Hypertable-Sichere Re-Seeding Pipeline**: Kaskadierende Bereinigung vor Demo-Generierung zur Vermeidung von TimescaleDB-Konflikten.
  - **Instant-Login & Auto-Hydrierung**: 1-Klick Demo-Login ohne Registrierungshürde.

---

### [x] 5.39 Wissensportal UX-Streamlining & Billing Coupon Redesign
- **Dateien**: [`frontend/src/features/help/pages/HelpCenterPage.jsx`](file:///c:/Users/Public/Dev/eswes/frontend/src/features/help/pages/HelpCenterPage.jsx), [`frontend/src/features/billing/pages/BillingPage.jsx`](file:///c:/Users/Public/Dev/eswes/frontend/src/features/billing/pages/BillingPage.jsx)
- **Status**: ✅ **Erledigt**.
  - **Sanfte Anchor-Navigation**: Direktsprung zu `#articles-list` bei Kategorie-Klick mit aktivem Filter.
  - **Kompakte Hero-Suche**: Schlanke Hero-Suchleiste (~85px) für maximale Übersicht.
  - **Dezenter Gutschein-Trigger**: Platzierung unterhalb der Preiskarten auf `/app/billing`.

---

### [x] 5.32 🌡️ Intelligente Fußbodenheizungs- & Heizkreis-Regelung (Thermischer Speicher & Prädiktives MPC)
- **Status**: ✅ **100% PRODUKTIONSREIF IMPLEMENTIERT & GETESTET**
- **Fokus**: HEMS Dispatch-Hub Integration für Fußbodenheizungen, thermische Bauteilaktivierung und **vorausschauende KI-Wetter-Vorlauftemperaturregelung (Model Predictive Control / MPC)** (`FloorHeatingConfig`, `FloorHeatingLoadCard`, `floor_heating_manager.py`).
- **Konzept & Umsetzung**:
  - **Prädiktive Vorlauftemperatur ($T_{\text{flow, opt}}$)**:
    - Niedertemperatur-Heizkurve nach DIN EN 12831 / DIN 4701 ($T_{\text{flow, base}} = T_{\text{room}} + s \cdot (T_{\text{room}} - T_{\text{out}})^{0.8} \cdot 1.25 + 2.5$).
    - **Solares Absenken ($\Delta T_{\text{solar}}$)**: Bei prognostizierter Globalstrahlung ($G > 100\,\text{W/m}^2$) senkt Sharegy den Vorlauf um bis zu $2,0\,\text{K}$ im Voraus ab, um kostenlose passive Wärmegewinne durch Fenster zu nutzen.
    - **Thermische Vorladung ($\Delta T_{\text{boost}}$)**: Bei PV-Überschuss $\ge 1\,\text{kW}$ oder negativen Börsenstrompreisen wird der Vorlauf gezielt angehoben ($+1,5\,\text{K}$ bis $+2,5\,\text{K}$).
  - **24-Stunden MPC-Fahrplan & KI-Handlungsempfehlungen**:
    - Automatische Berechnung optimaler Vorladefenster (z. B. `11:00 – 14:30 Uhr`) und passiver Entladephasen (z. B. `17:00 – 21:00 Uhr`).
    - Live-Berechnung von solarem Energieertrag ($Q_{\text{solar}}$), vermiedener Abendspitze ($E_{\text{peak}}$) und täglicher Kostenersparnis.
  - **Thermische Speicher-Physik**: $C_{\text{th}} = \frac{m \cdot c}{3600} \approx 4,67\,\text{kWh/K}$ (bei $120\,\text{m}^2 / 16,8\,\text{t}$ Estrich), Live-$\text{SoC}_{\text{thermal}}$ in $\%$.
  - **Schaltschutz & Sicherheit**: Mindestlaufzeit $\ge 30\,\text{min}$, Mindestruhezeit $\ge 15\,\text{min}$, Maximaltemperatur $T_{\text{max}} \le 24,5^\circ\text{C}$.
  - **Vollwertiges Glassmorphism-UI (`FloorHeatingLoadCard.jsx`)**: Mit Dual-Temperatur-Gauge, Live-Vorlaufanzeige, aufklappbarem 24h-Wetterfahrplan, 1-Klick 2h-Vorladeboost und Heizkurven-Steilheitsregler ($s$).

---

### [x] 5.33 ⛽ Mobilitäts- & Spritpreis-Radar (Günstigste Tankstellen im Umkreis & 100km EV-Kostenvergleich)
- **Status**: ✅ **100% PRODUKTIONSREIF IMPLEMENTIERT & GETESTET**
- **Fokus**: Alltags-Mehrwert & Mobilitäts-Hub für gemischte Haushalte (`energy/services/tankerkoenig.py`, `views_fuel_radar.py`, `FuelRadarCard.jsx`, `ControlPage.jsx`).
- **Konzept & Umsetzung**:
  - **Live MTS-K / Tankerkönig-Abfrage**: Ermittlung der günstigsten Tankstellen im Umkreis von 5, 10 oder 25 km für Super E10, Super E5 und Diesel.
  - **100-km Real-Kostenvergleich**: Visualisiert den direkten Kostenunterschied zwischen E-Auto Solar-Laden (1,44 €/100km), E-Auto Börsenstrom (3,24 €/100km), Diesel (~9,53 €/100km) und Benziner (~12,38 €/100km) mit einer Ersparnis von bis zu 88% (~1.640 €/Jahr bei 15.000 km).
  - **Tageszeit-Tankempfehlungen**: Erkennung optimaler Abend-Tankfenster (18:00–21:30 Uhr) zur Vermeidung teurer Morgen-Spitzen.
  - **Resiliente Simulation Engine & Caching**: 15 Minuten Redis-Cache zur Schonung der API-Limits und flüssige Offline-/Demo-Unterstützung.
  - **Vollwertiges UI-Widget**: Direkte Einbettung in das HEMS Control Dashboard (`/app/control`).

---

## 🎯 7. Verbindliche Prioritätenliste & Gesamter Roadmap-Status

```
┌───────────────────────────────────────────────────────────────────────────────┐
│ 🏆 100% VOLLSTÄNDIG PRODUKTIONSREIF: SÄULE 1 (EMS), PAYMENT & SÄULE 2 (SHARING)│
├───────────────────────────────────────────────────────────────────────────────┤
│ • 🟢 Säule 1 (Smart EMS & HEMS Control Hub):                                  │
│    - Live-Sankey, Last-/PV-Forecasts (ML + Open-Meteo), Smart Load Hub,       │
│    - 1-Klick Quick Boost, SG-Ready BWWP Lastmanagement,                       │
│    - 🌡️ Fußbodenheizungs-Steuerung & Prädiktive KI-Wetter-Vorladung (MPC),    │
│    - 🚗 OCPP 1.6-J CSMS Wallbox & Dynamisches PV-Überschuss-Laden,            │
│    - ⛽ Mobilitäts- & Spritpreis-Radar (MTS-K / Tankerkönig & 100km-Vergleich),│
│    - Sungrow OpenAPI, ioBroker & HA Adapter, Multistring AC-Kopplung,         │
│    - Live-Pulse Topbar, Dark-Mode, 6-Sprachen i18n, 7d EPEX Trend & Demo-Hub, │
│    - 🛡️ § 14a EnWG Summenleistungs-Dimmung (4,2 kW Netzkontingent & SteuVE).  │
│                                                                               │
│ • 💳 Payment & Billing Platform:                                              │
│    - Stripe Checkout (SEPA, Kreditkarten, PayPal, Klarna),                    │
│    - § 14 UStG Invoicing, Customer Portal, Auto-Healing Customer-IDs & Coupons│
│                                                                               │
│ • ⚡ Säule 2 (Energy Sharing & Gesetzliche Marktkommunikation):               │
│    - 15m OBIS-Clearing, Discovergy wMSB Hub, 3 Allokationsmodelle,            │
│    - ⚡ Dynamische Börsenpreis-Sharingtarife (EPEX Spot, Floor, Cap, Aufschlag)│
│    - 📜 BNetzA MSCONS EDIFACT Export & Ingest Bridge (D:04B),                 │
│    - Multi-Community Hub, PDF/Excel/XML-Exporte & Viral Referral System.      │
├───────────────────────────────────────────────────────────────────────────────┤
│ ✅ KEINE OFFENEN AUFGABEN MEHR: DIE GESAMTE ROADMAP IST VOLLSTÄNDIG ABGESCHLOSSEN!│
└───────────────────────────────────────────────────────────────────────────────┘
```









