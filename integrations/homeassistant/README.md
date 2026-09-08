# Sharegy Integration for Home Assistant (v2.2.0)

![Logo](logo.png)

[![hacs_badge](https://img.shields.io/badge/HACS-Custom-41BDF5.svg)](https://github.com/hacs/default)
[![GitHub Release](https://img.shields.io/github/v/release/smartcuc/homeassistant-sharegy)](https://github.com/smartcuc/homeassistant-sharegy/releases)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

Official Home Assistant Integration for the **Sharegy Energy Management Platform** ([sharegy.de](https://sharegy.de)).

Connects your Home Assistant smart home (PV systems, battery storages, heat pumps, floor heating, BWWP, wallboxes, smart meters, Shelly, Zigbee, ESPHome, KNX, Homematic) with Sharegy for:
- ☀️ **Realtime EMS Telemetry** (Live energy flow, PV generation, grid feed-in/import, battery SoC)
- 🔥 **Wärme, Heizung & Raumklima (DIN EN 12831 / MPC)**: Vorausschauende Fußbodenheizungs- & thermische Estrichspeicher-Steuerung
- 🛡️ **Lokale 24h-Offline-Resilienz**: Cacht den 24h-MPC-Fahrplan lokal in SQLite und regelt die Heizung bei Internetausfall vollkommen autonom weiter
- 🌡️ **Custom Devices & Submeters** (Heatpumps, Brauchwasserwärmepumpen, temperature sensors, smart plugs)
- 📦 **SQLite Store & Forward Offline Buffer** (Lückenlose Historie ohne Datenverlust bei Internetausfall)
- 🎛️ **Bidirectional Smart Load Control** (SG-Ready und dynamische Tarif-Optimierung direkt in HA-Entities)

---

## 🚀 Installation via HACS (Recommended)

1. Ensure [HACS (Home Assistant Community Store)](https://hacs.xyz/) is installed.
2. In Home Assistant, open **HACS** ➔ **Integrations**.
3. Click the **3 dots** in the top right corner and select **Custom repositories**.
4. Enter repository URL:
   ```
   https://github.com/smartcuc/homeassistant-sharegy
   ```
   Category: **Integration**
5. Click **Add**, find **Sharegy Energy Management**, and click **Download**.
6. **Restart Home Assistant**.

---

## ⚙️ Configuration

1. In Home Assistant, go to **Settings** ➔ **Devices & Services** ➔ **Add Integration**.
2. Search for **Sharegy**.
3. Enter your **Sharegy Home Token** (from the Sharegy Web-App under *Settings ➔ Interfaces*).
4. Select your EMS sensors (Grid Power, Solar Generation, Battery SoC/Power, House Load).
5. **Fußbodenheizung & Estrich (Wärme & Raumklima)**:
   - Wähle deine Raumtemperatur-, Vorlauftemperatur- und Estrich-Sensoren.
   - Wähle das Heizkreis-Relais / Ventil-Entity und optional das Vorlauf-Solltemperatur-Entity.
   - Stelle Zieltemperatur, Vorladehub (+K) und maximale Estrich-Sicherheitstemperatur ein.
6. Fertig! Die Daten werden live synchronisiert und bei Internetausfall steuert die lokale 24h-Offline-Resilienz deine Heizung autonom weiter.

---

## 📊 Diagnostik- & Status-Sensoren
Die Integration stellt folgende Entitäten in Home Assistant bereit:
- `sensor.sharegy_cloud_verbindung`: Live-Verbindungsstatus (online / offline)
- `sensor.sharegy_offline_resilienz_status`: Autonome Offline-Regelung aktiv / inaktiv
- `sensor.sharegy_integration_version`: Aktuelle Adapter-Version (z. B. `2.2.0`)
- `sensor.sharegy_offline_puffer_warteschlange`: Anzahl gepufferter Offline-Messwerte
- `sensor.sharegy_fbh_vorlauf_solltemperatur`: Berechneter Vorlauf-Sollwert nach DIN EN 12831 / MPC
- `sensor.sharegy_fbh_estrich_speicher_ladestand_soc`: Thermischer Estrich-Ladezustand in %
- `sensor.sharegy_fbh_betriebsmodus`: Aktueller Optimierungsmodus
- `sensor.sharegy_borsenstrompreis`: Dynamischer Börsenpreis in ct/kWh
