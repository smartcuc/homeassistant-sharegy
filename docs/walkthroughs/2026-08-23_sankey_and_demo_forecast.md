# ⚡ Walkthrough: Sankey-Flussberechnung & Demo-Haushalt mit 96h PV-Forecast

**Datum**: 23. August 2026  
**Bereich**: EMS Flow-Engine, ECharts Sankey & Demo-Generierung  

---

## 🎯 Ziel & Motivation
1. Korrektur der physikalischen Vorzeichenkonvention für Batteriespeicher und Netz ($P_	ext{battery} > 0$ Entladung ins Haus, $< 0$ Ladung in den Speicher).
2. Saubere Trennung der Sankey-Knoten: Batterieladung und Netzeinspeisung dürfen nicht in den Haushaltsverbrauch einfließen.
3. Autarke Demo-Generierung mit echter Dachanlagen-Struktur (`GeneratorSystem` + `GeneratorString`) und Initial-Berechnung des 96h Open-Meteo PV-Forecasts.

---

## 🛠️ Durchgeführte Implementierungen

### 1. Sankey-Knotentrennung & Visualisierung
- **[`energy/services/sankey.py`](../../energy/services/sankey.py)**:
  - `battery_charge` und `grid_export` als eigenständige Zielknoten außerhalb des `sum` (Haus) Knotens definiert.
- **[`LiveEnergySankeyECharts.jsx`](../../frontend/src/features/energy/components/LiveEnergySankeyECharts.jsx)**:
  - Tooltips mit klaren Bezeichnungen und automatischer Einheitenskalierung ($< 1000\,	ext{W} ightarrow 	ext{W}$, $\ge 1000\,	ext{W} ightarrow 	ext{kW}$).
  - Speicherbereinigung über den nativen `echarts-for-react` Lifecycle.

### 2. Autarker Demo-Haushalt & 96h PV-Forecast
- **[`demo/services/data_generator.py`](../../demo/services/data_generator.py)**:
  - Erstellt 10 kWp PV-Dachanlage (Süd 180°, 35° Neigung, 24 Module) mit `GeneratorSystem` und `GeneratorString`.
  - Ruft beim Initial-Setup (`rebuild_demo`) automatisch Open-Meteo Wetterdaten ab und errechnet den 96h PV-Forecast.
  - Weist jedem Gerät korrekte `energy_signal_type` Werte (`pv`, `battery`, `grid`, `load`) zu.
- **[`demo/tasks.py`](../../demo/tasks.py)** & **[`backend/settings/base.py`](../../backend/settings/base.py)**:
  - Veraltete Synchronisierungs-Tasks (`demo-device-sync`, `demo-config-sync`) entfernt.
  - Nur 15s Telemetrie-Generierung (`sync-demo-metrics`) und tägliche Datenbereinigung (`demo-cleanup`) beibehalten.

---

## ✅ Verifikation
- Frontend Build & ESLint: **0 Fehler**.
- Backend Tests: **15/15 Tests erfolgreich (`OK`)**.
