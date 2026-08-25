# 🧠 Walkthrough: Sharegy Smart Energy Optimizer (1h, 2h, 4h Zeitfenster)

**Datum**: 25. August 2026  
**Bereich**: Frontend (`EnergyDashboard.jsx` & `EnergyOptimizerCard.jsx`), Backend (`energy.services.optimizer` & `energy/api/`)

---

## 🎯 Ziel & Motivation
Flexible Großverbraucher (Wallbox / Elektroauto, Wärmepumpe, Hausspeicher, Waschmaschine, Geschirrspüler) sollen automatisiert oder als klare Empfehlung zu den ökonomisch und ökologisch günstigsten Zeiten betrieben werden.
Der Optimizer kombiniert:
1. **PV-Erzeugungsprognose** (Wetter & Solarstrahlung im 24h/48h-Horizont).
2. **Dynamische Börsenstromtarife** (EPEX Spot Day-Ahead Preise zzgl. Netzentgelte & Steuern bzw. Festpreis).
3. **Einspeisevergütung & Opportunitätskosten** (PV-Eigenverbrauch vs. Netzeinspeisung).

---

## 🛠️ Durchgeführte Implementierungen

### 1. Backend Service: [`energy/services/optimizer.py`](../../energy/services/optimizer.py)
* **Opportunitätskosten-Matrix**: Berechnet für jedes Zeitintervall $t$ den effektiven Arbeitspreis (PV-Überschuss = entgangene Einspeisevergütung z. B. $8{,}2\text{ ct/kWh}$ vs. Netzbezug = EPEX Spot + Nebenkosten).
* **Multi-Dauer Sliding-Window Engine**:
  * **1-Stunden-Fenster (1h)**: Für Waschmaschine, Geschirrspüler, Warmwasser-Booster (typisch $2\text{ kW}$).
  * **2-Stunden-Fenster (2h)**: Für Wärmepumpen-Vorheizzyklus, Wäschetrockner (typisch $3\text{ kW}$).
  * **4-Stunden-Fenster (4h)**: Für Wallbox ($11\text{ kW} \times 4\text{h} = 44\text{ kWh}$) und Speicher-Vollladung.
* **Scoring & Ranking**:
  * Ermittelt das absolute Best-Fenster (Tag / PV-Spitze).
  * Ermittelt das beste Nacht-Fenster (Börsen-Tiefststand / Windstrom).
  * Ermittelt die teuerste Spitzenzeit (Abendpeak 18:00–21:00 Uhr) und berechnet das exakte Einsparpotenzial in Euro.

### 2. API-Endpunkt: [`energy/api/urls.py`](../../energy/api/urls.py) & [`energy/api/views.py`](../../energy/api/views.py)
* `GET /api/energy/optimizer/?horizon=24|36`: Liefert den kompletten 24h-Stundenplan mit Farbcodierung (grün/gelb/rot), PV-kW, Arbeitspreisen und den vorberechneten Empfehlungen für 1h, 2h und 4h.

### 3. Frontend-Komponente: [`EnergyOptimizerCard.jsx`](../../frontend/src/features/energy/components/EnergyOptimizerCard.jsx)
* **Interaktive Dauer-Auswahl**: Umschaltung per Klick zwischen `[ 🧺 1 Stunde ]`, `[ ♨️ 2 Stunden ]` und `[ 🚗 4 Stunden ]`.
* **Empfehlungs-Kacheln**:
  * 🏆 **Beste Zeit**: Start/Ende, Solaranteil (%), Durchschnittspreis und Ersparnis vs. Peak.
  * 🌙 **Nacht-Alternative**: Günstigstes Zeitfenster für Pendler & Übernacht-Ladung.
  * ⚠️ **Spitzenzeit (Vermeiden)**: Warnung vor teuren Abendstunden.
* **24h-Stundenplan & Preisprofil**: Interaktives Säulendiagramm mit dynamischem Highlight-Rahmen und `TOP`-Badge über dem empfohlenen Zeitfenster.
* **Geräte-Tipp**: Kontextuelle Empfehlungen (*z. B. 44 kWh Wallbox-Ladung mit +12,80 € Ersparnis*).

---

## 🧪 Verifikation & Tests
* **Backend-Tests ([`energy/tests.py`](../../energy/tests.py))**:
  * Testfall `test_energy_optimizer_api` prüft lückenlos die Datenstruktur für 1h, 2h und 4h sowie die Fensterberechnung.
  * `manage.py test` $\rightarrow$ **14/14 Tests erfolgreich (`OK in 26.95s`)**.
* **Frontend-Build**:
  * `npm run build` $\rightarrow$ **Erfolgreich in 3.68s (0 Fehler / 0 Warnungen)**.

