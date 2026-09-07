# 🔧 Sharegy ioBroker Integration (v2.1.0)

Das offizielle ioBroker Skript verbindet dein **Sharegy HEMS** bidirektional (**Messen & Steuern**) mit deiner ioBroker Hausautomation.

---

## ⚡ Highlights
* 🌐 **WSS (Bevorzugte Methode)**: Direkte verschlüsselte WebSocket-Verbindung über Port 443 (HTTPS/WSS). Funktioniert hinter jedem Router (Fritz!Box etc.) **ohne Portweiterleitungen**.
* 📡 **MQTT Alternative**: Volle Kompatibilität mit dem ioBroker `mqtt-client` Adapter.
* 🎛️ **Bidirektionales Messen & Steuern**:
  * **Inbound Telemetrie**: Sende PV-Leistung, Netzbezug, Speicher-SoC und Raumtemperaturen an Sharegy.
  * **Outbound Aktorik**: Empfange optimierte Soll-Vorlauftemperaturen (DIN EN 12831), Estrich-Vorheiz-Boosts und SG-Ready Signale.
* 🛡️ **15-Minuten Fail-Safe Watchdog**: Bei Verbindungsunterbrechung schalten Aktoren nach 15 Minuten automatisch in den sicheren lokalen Normal-/Komfortbetrieb zurück.
* ⏸️ **Not-Aus / Pause Toggle**: Deaktiviere automatisierte Eingriffe jederzeit mit einem Klick auf den Schalter `control.bidirectional_enabled`.

---

## 📦 Installation in 3 Schritten

### 1. Skript in ioBroker anlegen
1. Öffne deine ioBroker Administration → **Skripte**.
2. Erstelle ein neues JavaScript-Skript mit dem Namen `sharegy_bridge`.
3. Kopiere den Inhalt von [`sharegy_iobroker_bridge.js`](file:///c:/Users/Public/Dev/eswes/plugins/iobroker/sharegy_iobroker_bridge.js) in das Editorfeld.

### 2. Konfiguration anpassen
Trage oben im Skript dein persönliches Sharegy Token ein:
```javascript
const CONFIG = {
    HOME_TOKEN: "DEIN_SHAREGY_HOME_TOKEN",
    CONNECTION_MODE: "WSS", // 'WSS' (Empfohlen) oder 'MQTT'
    // ...
};
```

### 3. Starten
Klicke auf **Speichern & Starten**. Das Skript erstellt automatisch alle Datenpunkte unter `0_userdata.0.sharegy`.

---

## 📊 Datenpunkt-Übersicht

### 🎛️ Steuerung & Aktorik (`0_userdata.0.sharegy.control.*`)
| Datenpunkt | Typ | Funktion |
| :--- | :---: | :--- |
| `control.bidirectional_enabled` | `boolean` | **Master-Schalter**: Ein/Aus für alle automatischen Steuereingriffe von Sharegy. |
| `control.floor_heating_boost` | `boolean` | Schaltet die Fußbodenheizungs-Estrich-Schnellaufladung ein/aus. |
| `control.floor_heating_target_temp` | `number` | Gewünschte Soll-Raumtemperatur (z. B. `21.0 °C`). |
| `control.bwwp_boost` | `boolean` | SG-Ready Relais / Boost für Brauchwasser-Wärmepumpe. |
| `control.wallbox_max_current` | `number` | Maximaler Ladestrom für E-Auto (z. B. 6–16 A). |

### 📈 Inbound Telemetrie (`0_userdata.0.sharegy.telemetry.*`)
| Datenpunkt | Einheit | Funktion |
| :--- | :---: | :--- |
| `telemetry.pv_power` | `W` | Aktuelle Solarerzeugung |
| `telemetry.grid_power` | `W` | Netzleistung (positiv: Bezug, negativ: Einspeisung) |
| `telemetry.battery_soc` | `%` | Batteriespeicher Ladestand |
| `telemetry.room_temp` | `°C` | Aktuelle Raumtemperatur |

### 🌡️ Status & Berechnungen (`0_userdata.0.sharegy.status.*`)
| Datenpunkt | Einheit | Funktion |
| :--- | :---: | :--- |
| `status.flow_temp_setpoint` | `°C` | Berechnete DIN EN 12831 Vorlauftemperatur nach Heizkurve |
| `status.screed_soc` | `%` | Ladezustand des thermischen Estrich-Speichers |
| `status.operating_mode` | Text | Aktueller Modus (`PV-Boost`, `Grid-Arbitrage`, `Comfort`, `Eco`) |
| `status.spot_price_ct` | `ct/kWh` | Aktueller Börsenstrompreis |
| `status.failsafe_active` | `boolean` | Zeigt an, ob der 15-Minuten Ausfallschutz aktiv ist |
| `status.connected` | `boolean` | Live-Verbindungsstatus |
