# 📘 Konzept & Walkthrough: Smartes Geräte-Onboarding & Topic-Assistent

**Datum**: 23. August 2026  
**Bereich**: Frontend UX, Device-Management & Ingest-Assistent  
**Status**: ✅ Abgeschlossen & Produktiv umgesetzt  

---

## 🎯 Ziel & Motivation

Das Hinzufügen neuer Geräte ist der **erste und wichtigste Berührungspunkt** eines Nutzers mit dem Sharegy EMS. Aktuell erfordert das Setup zwei getrennte Modale ([`AddDeviceModal.jsx`](file:///c:/Users/Public/Dev/eswes/frontend/src/components/device/AddDeviceModal.jsx) und [`DeviceSetupModal.jsx`](file:///c:/Users/Public/Dev/eswes/frontend/src/components/device/DeviceSetupModal.jsx)), bietet keine gerätespezifischen Vorlagen (Shelly, Tasmota, OpenDTU, Home Assistant) und lässt den Nutzer ohne direkte Feedbackschleife zurück.

**Ziel**: Zusammenführung zu einem intuitiven, geführten **Smart-Onboarding-Assistenten**, der Geräte in 3 einfachen Schritten anlegt, automatisch semantisch klassifiziert und direkt verifiziert.

---

## 🔍 Ist-Zustand vs. Soll-Zustand

```
IST-ZUSTAND (Bruch im Nutzerfluss):
[ AddDeviceModal ] ──(Name + MQTT Token)──► [ Gerät unkonfiguriert ] ──► [ Banner-Klick ] ──► [ DeviceSetupModal (Rolle, Signal, Raum) ]

SOLL-ZUSTAND (Integrierter Smart-Flow):
[ Smart Device Wizard ]
   ├── Schritt 1: Preset-Auswahl (☀️ Balkonkraftwerk, ⚡ Stromzähler, 🔌 Smart Plug, 🔋 Speicher, 🔧 Generic)
   ├── Schritt 2: Name & Raum (Auto-Klassifizierung: Rolle, Signal-Typ, Metrik werden automatisch gesetzt)
   └── Schritt 3: Verbindung & Live-Test (Shelly/Tasmota/HA Snippets + ⚡ Test-Messwert Simulator + Live-Bestätigung)
```

---

## 💡 Das 3-Schritte Smart-Onboarding Konzept

### Schritt 1: Gerätetyp & Preset auswählen
Statt abstrakter MQTT-Profile wählt der Nutzer aus praxisnahen Kategorien:

1. **☀️ Balkonkraftwerk / PV-Anlage**
   - *Hardware*: Hoymiles, OpenDTU, Shelly Plus 1PM, Envertech, TSUN
   - *Auto-Konfiguration*: Rolle = `producer`, Signal = `solar_production`, Metrik = `power (W)`
2. **⚡ Hauptzähler / Netzeinspeisung**
   - *Hardware*: Shelly Pro 3EM, Powerfox, Tibber Pulse, Tasmota IR-Lesekopf
   - *Auto-Konfiguration*: Rolle = `grid`, Signal = `grid_exchange`, Metrik = `power (W)`
3. **🔌 Smarte Steckdose / Einzelverbraucher**
   - *Hardware*: Shelly Plug S, Gosund/Tasmota, AVM FRITZ!DECT, Wärmepumpe, Wallbox
   - *Auto-Konfiguration*: Rolle = `consumer`, Signal = `household_load`, Metrik = `power (W)`
4. **🔋 Batteriespeicher / Powerstation**
   - *Hardware*: EcoFlow, Anker Solix, Zendure, Victron
   - *Auto-Konfiguration*: Rolle = `both`, Signal = `battery_storage`, Metrik = `power (W)`
5. **🔧 Smart Home Zentrale / Generisch**
   - *Hardware*: Home Assistant, ioBroker, Node-RED, REST / cURL
   - *Auto-Konfiguration*: Individuell wählbar

---

### Schritt 2: Benennung & Ort (Minimal & Schnell)
- **Gerätename**: z. B. *„Balkonkraftwerk Süd“* oder *„Waschmaschine“*
- **Raum / Etage (optional)**: Direkt zuweisbar (Küche, Balkon, Keller, etc.)
- **Nennleistung (optional)**: z. B. `800 W` für Balkonkraftwerke zur Prognose-Plausibilisierung
- *(Alle technischen Parameter wie Signal-Typ und Metrik sind bereits im Hintergrund vorkonfiguriert)*

---

### Schritt 3: Verbindung, Setup-Snippets & Sofort-Test
Das Modal generiert das individuelle Topic (`h/<mqtt_token>/<identifier>`) und bietet maßgeschneiderte Anleitungen:

- **Tab 1: Shelly Web-UI Anleitung**:
  - `Internet & Security` $\rightarrow$ `MQTT` $\rightarrow$ `Enable`
  - Host/Port: `mqtt.sharegy.de:1883`
  - User/Pass: Vorbefüllt mit 1-Klick-Kopierbuttons
  - Topic Prefix: `h/<token>/<identifier>`
- **Tab 2: Tasmota / OpenDTU**:
  - Konfigurations-String für die Web-Konsole
- **Tab 3: Home Assistant**:
  - Fertiges `configuration.yaml` MQTT-Publish Snippet
- **Tab 4: REST / cURL**:
  - Direkter `curl -X POST https://api.sharegy.de/api/v1/telemetry/ ...` Befehl

#### ⚡ Interaktiver Live-Test & Feedback
- **Button „Test-Messwert senden (450 W)“**: Sendet sofort einen Test-Datenpunkt an das Backend.
- **Live-Status**: Zeigt bei Datenempfang:
  ```
  🟢 Verbunden: 452.8 W empfangen (vor 2 Sekunden)
  [ Zum Dashboard → ]
  ```

---

## 🛠️ Technische Umsetzung

### 1. Erweiterung des Device-Create Endpoints
Der Endpoint `/api/devices/` (POST) akzeptiert in einem Aufruf direkt die Vorkonfiguration:
```json
{
  "name": "Balkonkraftwerk Süd",
  "identifier": "balkonkraftwerk_sued",
  "role_key": "producer",
  "energy_signal_key": "solar_production",
  "metric_key": "power",
  "room_id": 2,
  "generator_type_key": "solar"
}
```
Das Backend legt das `Device` und das zugehörige `DeviceConfig` atomar als bereits klassifiziert (`configured=True`) an.

### 2. Simulator-Endpoint
Ein abgesicherter Endpoint `/api/devices/<id>/simulate/` (POST):
- Schreibt einen synthetischen Messwert in Redis-Live-Cache und `DeviceMetric`.
- Triggert das WebSocket-Event für Echtzeit-Feedback im Frontend.

---

## 📋 Nächste Meilensteine

1. [ ] Backend: Parameter `role_key`, `energy_signal_key`, `room_id` im Create-Serializer verarbeiten.
2. [ ] Backend: Test-Signal Simulator-Endpoint `/api/devices/<id>/simulate/` bereitstellen.
3. [ ] Frontend: [`AddDeviceModal.jsx`](file:///c:/Users/Public/Dev/eswes/frontend/src/components/device/AddDeviceModal.jsx) mit 3-Schritte-Assistent, Preset-Karten und Snippet-Tabs neu aufbauen.
4. [ ] Verifikation: End-to-End Test (Preset wählen $\rightarrow$ Anlegen $\rightarrow$ Test-Messwert senden $\rightarrow$ Live im Sankey sichtbar).

