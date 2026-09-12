# ☀️ 96-Stunden PV-Erzeugungsprognose

Das Sharegy Prognosesystem liefert hochpräzise 96-Stunden Solar-Erzeugungsprognosen in 15-Minuten-Intervallen für jeden konfigurierten Generator-String.

---

## 🛰️ 1. Datenquellen & Wetter-Pipeline

- **Wetterdaten**: Open-Meteo Solar API (GHI: Global Horizontal Irradiance, DHI: Direct/Diffuse Irradiance, Temperatur, Bewölkung).
- **Standort**: Automatische Koordinatenauflösung über Postleitzahl / Stadt des Haushalts.
- **Aktualisierung**: Vollautomatisch per Celery Beat alle 60 Minuten (`forecast.tasks.sync_weather_forecasts`).

---

## 🔬 2. Berechnungsverfahren

### 1. Physikalisches Strahlungsmodell (`Physics`)
- Berechnet den Sonnenstand (Azimut und Zenitwinkel) für jeden Zeitschritt.
- Transformiert die globale Einstrahlung auf die geneigte und ausgerichtete Modulfläche ($	ext{POA} - 	ext{Plane of Array}$).
- Berücksichtigt Modultemperatur-Koeffizienten und Systemwirkungsgrad.

### 2. Machine Learning Modell (`Random Forest ML`)
- Trainiert stringspezifische Scikit-Learn Random Forest Regressoren anhand historischer Messwerte (`DeviceMetric` vs. Einstrahlung & Wetter).
- Erreicht kontinuierlich verbesserte Vorhersagegenauigkeit bei wechselhaften Bewölkungslagen.

### 3. Genauigkeits-Tracking (`ForecastAccuracy`)
- Vergleicht automatisch vergangene Prognosen mit tatsächlich gemessenen Erzeugungswerten und errechnet den mittleren absoluten Fehler (MAE) und Root Mean Square Error (RMSE).
