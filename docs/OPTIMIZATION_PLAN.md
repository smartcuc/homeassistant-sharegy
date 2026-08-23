# 🛠️ Codebase Review & Schritt-für-Schritt Optimierungsplan

> 📖 **Strategische Gesamt-Roadmap**: Siehe [`docs/SHAREGY_STRATEGIC_ROADMAP.md`](file:///c:/Users/Public/Dev/eswes/docs/SHAREGY_STRATEGIC_ROADMAP.md) für die Dual-Core Produktarchitektur (EMS vs. Energy Sharing Communities).

---

## 📋 Übersicht & Status

| Phase | Bereich | Fokus | Status | Erledigt | Offen |
|---|---|---|---|---|---|
| **Phase 1** | Kritische Bugs & Flusslogik | 🟢 EMS-Free & Core |  Abgeschlossen | 1.1, 1.2, 1.3, 1.4, 1.6 | 1.5 (Sharing) |
| **Phase 2** | DB- & Performance-Optimierung | 🟢 EMS-Free (TimescaleDB) | 🟢 Abgeschlossen | 2.1, 2.3, 2.4, 2.5, 2.6, 2.7 | 2.2 (Sharing) |
| **Phase 3** | Celery & Buffer-Härtung | 🟢 EMS-Free Stabilität | 🟢 Abgeschlossen | 3.1, 3.2, 3.3, 3.4 | – |
| **Phase 4** | Architektur & Diagramme | 🟢 EMS-Free Sankey & Tests | 🟢 Abgeschlossen | 4.2, 4.3, 4.4 | 4.1 (Sharing) |

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
