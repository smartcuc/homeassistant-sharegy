# 📊 Sharegy Grafana Integration & Energy Cockpit

Binde deine Sharegy HEMS-Messdaten, PV-Erzeugung, Batteriespeicher, Börsenstrompreise und virtuellen Zähler direkt in **Grafana** ein.

---

## 🚀 1. Schnellstart & Authentifizierung

Sharegy stellt eine hochperformante, JSON-kompatible REST-Schnittstelle bereit.

### Endpoints
* **Base URL**: `http://<sharegy-ip>:8000/api/grafana` (oder `https://app.sharegy.de/api/grafana`)
* **Healthcheck**: `GET /api/grafana/`
* **Metrik-Suche**: `POST /api/grafana/search`
* **Zeitreihen-Abfrage**: `POST /api/grafana/query`
* **Alarme & Ereignisse**: `POST /api/grafana/annotations`

### Authentifizierung
Füge in den Datasource-Einstellungen einen HTTP-Header hinzu:
* **Header-Name**: `Authorization`
* **Header-Wert**: `Bearer <DEIN_API_KEY_ODER_MQTT_TOKEN>`  
*(Deinen Schlüssel findest du in Sharegy unter **Einstellungen → Smart Home / MQTT**)*

---

## 🔌 2. Grafana Datasource einrichten

### Option A: Via Grafana UI (Infinity / JSON Datasource)
1. Installiere in Grafana das Plugin **JSON API** oder **Infinity** (oder `simpod-json-datasource`).
2. Erstelle eine neue Datenquelle vom Typ **JSON**.
3. **URL**: `http://<sharegy-ip>:8000/api/grafana`
4. Aktiviere **Custom HTTP Headers**:
   * Header: `Authorization`
   * Value: `Bearer <DEIN_TOKEN>`
5. Klicke auf **Save & Test** (muss grün bestätigen: *„Sharegy Grafana Bridge Online“*).

### Option B: Automatisches Provisioning
Kopiere die Datei [`provisioning/datasources/sharegy_datasource.yaml`](./provisioning/datasources/sharegy_datasource.yaml) in dein Grafana-Verzeichnis `/etc/grafana/provisioning/datasources/`.

---

## 📈 3. Dashboard importieren

1. Öffne in Grafana **Dashboards → New → Import**.
2. Lade die Datei [`dashboards/sharegy_energy_cockpit.json`](./dashboards/sharegy_energy_cockpit.json) hoch.
3. Wähle als Datenquelle **Sharegy HEMS** aus.
4. Klicke auf **Import**.

### Enthaltene Visualisierungen:
* ☀️ **Live PV-Erzeugung & Autarkiegrad (%)** (Gauges mit Farb-Schwellwerten).
* 🔋 **Batteriespeicher SoC (%)** und Lade-/Entladeleistung.
* 🏠 **Hausverbrauch vs. Solarerzeugung vs. Netzbezug** im 24h-/7d-Zeitverlauf.
* 💶 **Dynamischer Börsenstrompreis** (EPEX Spot in ct/kWh).
* 🧮 **Sub-Metering & Virtuelle Zähler** (Wallbox, Wärmepumpe, Restlast).
* 🚨 **Live Alerts & Alarme** als Grafana Annotations im Diagramm.

