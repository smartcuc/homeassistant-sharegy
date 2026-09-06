# ⚡ Home Energy Management System (EMS) — Guide

Das Sharegy EMS verarbeitet hochfrequente Gerätemessungen, aggregiert Energieflüsse in Echtzeit und stellt sie flackerfrei im Dashboard und Sankey-Diagramm dar.

---

## 🔄 1. Telemetrie-Ingestion & 2-Stufen Deduplizierung

Geräte (Shelly, Wechselrichter, Smart Plugs, ioBroker) senden Messdaten via MQTT oder REST im 1–5 Sekunden Takt.

```
                      ┌──────────────────────────────────────┐
                      │    MQTT Broker / REST Ingestion      │
                      └──────────────────┬───────────────────┘
                                         │
                                         ▼
                      ┌──────────────────────────────────────┐
                      │     Redis Live-Cache Aktualisierung   │
                      │   (Sofortige UI-Aktualisierung 100%) │
                      └──────────────────┬───────────────────┘
                                         │
                                         ▼
                      ┌──────────────────────────────────────┐
                      │      Deadband- & Heartbeat-Filter    │
                      │  • Δ > 1.0 W Schwellenwert ODER      │
                      │  • Heartbeat-Intervall (60s) erreicht │
                      └──────────────────┬───────────────────┘
                                         │
                    ┌────────────────────┴────────────────────┐
                    ▼                                         ▼
   ┌─────────────────────────────────┐       ┌─────────────────────────────────┐
   │    `DeviceLatestMetric`         │       │     `DeviceMetric`              │
   │    Snapshot (O(1) Status)       │       │     TimescaleDB Hypertable      │
   └─────────────────────────────────┘       └─────────────────────────────────┘
```

---

## 🔋 2. Batterie- & Netz-Vorzeichenkonvention

Im Sharegy EMS gilt folgende einheitliche physikalische Konvention:
- **Erzeuger (PV / Balkonkraftwerk)**: Immer $\ge 0\,\text{W}$.
- **Verbraucher (Haushalt, Wärmepumpe, Wallbox)**: Immer $\ge 0\,\text{W}$.
- **Netzzähler ($P_\text{grid}$)**:
  - $> 0\,\text{W}$ = **Netzbezug (Import)**
  - $< 0\,\text{W}$ = **Netzeinspeisung (Export)**
- **Batteriespeicher ($P_\text{battery}$)**:
  - $> 0\,\text{W}$ = **Entladung** (Batterie liefert Energie ins Hausnetz)
  - $< 0\,\text{W}$ = **Ladung** (Energie fließt in den Speicher)

---

## 🌊 3. Energiefluss-Berechnung & Sankey-Verteilung

Die [`energy/flow_engine.py`](file:///c:/Users/Public/Dev/eswes/energy/flow_engine.py) berechnet in Echtzeit die physikalisch korrekte Leistungsaufteilung:

1. **PV-Eigenverbrauch**: Deckt primär den direkten Hausverbrauch ($P_\text{pv\_to\_load} = \min(P_\text{pv}, P_\text{load})$).
2. **PV-Batterieladung**: Überschuss lädt die Batterie ($P_\text{pv\_to\_battery} = \min(P_\text{pv\_rem}, P_\text{battery\_charge})$).
3. **PV-Netzeinspeisung**: Restliche PV-Leistung wird eingespeist ($P_\text{pv\_to\_grid}$).
4. **Batterie-Entladung**: Deckt verbleibende Hauslast ($P_\text{battery\_to\_load}$).
5. **Netzbezug**: Deckt etwaige Deckungslücken ($P_\text{grid\_to\_load}$).

### Sankey-Knotentrennung
Batterieladung (`battery_charge`) und Netzeinspeisung (`grid_export`) münden **nicht** in den zentralen Hausknoten, sondern zweigen als separate Zielknoten ab, um den tatsächlichen Haushaltsverbrauch nicht zu verfälschen.

---

## 🔌 4. Smartes Geräte-Onboarding & Presets

Im geführten 3-Schritte-Assistenten ([`AddDeviceModal.jsx`](file:///c:/Users/Public/Dev/eswes/frontend/src/components/device/AddDeviceModal.jsx)) können neue Geräte schnell eingerichtet werden:

| Preset | Hardware-Beispiele | Automatische Vorkonfiguration |
|---|---|---|
| ☀️ **Balkonkraftwerk & PV** | Hoymiles, OpenDTU, Shelly Plus 1PM, TSUN | Rolle: `producer`, Signal: `solar_production`, Metrik: `power (W)` |
| ⚡ **Haupt- & Netzzähler** | Shelly Pro 3EM / EM, Powerfox, Tibber Pulse | Rolle: `consumer`, Signal: `grid_exchange`, Metrik: `power (W)` |
| 🔌 **Smarte Steckdose & Last**| Shelly Plug S, Tasmota, Wärmepumpe, Wallbox | Rolle: `consumer`, Signal: `household_load`, Metrik: `power (W)` |
| 🔋 **Batteriespeicher** | EcoFlow, Anker Solix, Zendure, Victron | Rolle: `both`, Signal: `battery_storage`, Metrik: `power (W)` |
| 🔧 **ioBroker & Smart Home** | ioBroker MQTT-Adapter, Home Assistant, Node-RED | Rolle: `consumer`, Signal: `household_load`, Metrik: `power (W)` |
| 🌡️ **Klima- & Umweltsensor** | Shelly Plus H&T, BME280, Zigbee-Sensoren | Rolle: `consumer`, Metrik: `temperature (°C)` / `humidity (%)` |

---

## 📊 5. Multi-Metric Support & Standard-SI-Einheiten

Geräte können beliebige Sensorwerte und SI-Einheiten über MQTT, OTel oder REST übermitteln:
- **Elektrisch**: `power` (`W`), `voltage` (`V`), `current` (`A`), `frequency` (`Hz`), `energy` (`kWh`).
- **Speicher**: `soc` (Ladezustand in `%`), `soh` (Gesundheit in `%`).
- **Klima / Umwelt**: `temperature` (`°C`), `humidity` (`%`), `pressure` (`hPa`), `co2` (`ppm`), `voc` (`ppb`), `illuminance` (`lx`), `solar_radiation` (`W/m²`), `wind_speed` (`m/s`).
- **Wärme**: `flow_temperature` (`°C`), `return_temperature` (`°C`), `flow_rate` (`l/h`), `heat_power` (`kW`).

Im Chart-Modal ([`DeviceChartModal.jsx`](file:///c:/Users/Public/Dev/eswes/frontend/src/components/device/DeviceChartModal.jsx)) schaltet der Nutzer dynamisch zwischen allen aktiven Messkanälen um.

---

## 📡 6. Globale MQTT-Schnittstelle

Jeder Haushalt besitzt ein festes MQTT-Präfix:
- **Topic-Format**: `h/<token>/<identifier>`
- **Broker-Daten**: Unter [`/app/settings`](file:///c:/Users/Public/Dev/eswes/frontend/src/pages/Settings.jsx) einsehbar (Host, Port 1883, Benutzer, maskiertes Passwort, QR-Code & Passwort-Rotation).

---

## 🎛️ 7. Smart Load Management & Dispatch Hub (`/app/control`)

Der **Dispatch Hub** steuert das dynamische Leistungsbudget des Haushalts in Echtzeit und verteilt solaren Überschuss sowie Tiefstpreis-Stunden auf alle steuerbaren Haushalts-Assets:

```
                  ┌─────────────────────────────────────────┐
                  │          Live Power Budget Engine       │
                  │   P_surplus = P_pv - P_base_load        │
                  └────────────────────┬────────────────────┘
                                       │
                                       ▼
                  ┌─────────────────────────────────────────┐
                  │    Prioritäten-Kaskade (Merit-Order)    │
                  │   [1. Speicher ➔ 2. BWWP ➔ 3. Wallbox]  │
                  └────────────────────┬────────────────────┘
                                       │
                  ┌────────────────────┼────────────────────┐
                  ▼                    ▼                    ▼
        ┌──────────────────┐  ┌──────────────────┐  ┌──────────────────┐
        │  ♨️ BWWP SG-Ready │  │  🚗 Wallbox EV   │  │  🏊 Pool & Klima │
        │  (Boost bis 60°C)│  │  (Min+PV / Solar)│  │  (Peak-Shaving)  │
        └──────────────────┘  └──────────────────┘  └──────────────────┘
```

### Die 4 Master-Autopilot-Modi
1. 🤖 **Smart Autopilot**: Maximiert Eigenverbrauch und optimiert Speicher/Lasten prädiktiv anhand von Solarprognose und EPEX-Spotpreisen.
2. ☀️ **Nur PV-Überschuss**: Strikt autarkieorientiert; schaltet Verbraucher nur ein, wenn $P_\text{grid} < 0\,\text{W}$.
3. 💰 **Preise-Optimiert**: Nutzt gezielt stündliche Negativpreis- und Tiefstpreisfenster an der Strombörse.
4. 🛑 **Manuell**: Deaktiviert die automatische Zuteilung für manuelle Einzelschaltungen.

---

## ♨️ 8. Brauchwasserwärmepumpe (BWWP) & SG-Ready Integration

Die BWWP wird als steuerbare thermische Batterie betrieben:
- **Temperatur-Schwellenwerte**:
  - $T_\text{min} = 45^\circ\text{C}$ (Komfort- & Legionellensicherung, erzwungener Normalbetrieb)
  - $T_\text{soll} = 52^\circ\text{C}$ (Standard-Solltemperatur)
  - $T_\text{boost} = 60^\circ\text{C}$ (SG-Ready State 3 bei Solarüberschuss $\ge 800\,\text{W}$)
  - $T_\text{max} = 65^\circ\text{C}$ (Sicherheitsabschaltung & Überhitzungsschutz)
- **Verdichter- & Taktschutz (Anti-Cycling)**:
  - Mindestlaufzeit: $t_\text{run} \ge 20\,\text{min}$ (verhindert Abschalten bei kurzen PV-Einbrüchen)
  - Mindestruhezeit: $t_\text{cool} \ge 15\,\text{min}$ (schont den Kältekreislauf vor schnellem Wiedereinschalten)
- **Aktorik-Anbindung**:
  - Outbound WebSocket (`/ws/outbound/`) an ioBroker-Adapter (`iobroker.sharegy`), Home Assistant oder Shelly Relais.

---

## 🟢 9. ioBroker Multi-Metric Adapter (`ioBroker.sharegy`)

Der offizielle ioBroker-Adapter erlaubt das Bündeln mehrerer lokaler Datenpunkte zu einem logischen Sharegy-Gerät:
- **BWWP-Bündel**:
  - `power`: Wirkleistung des Verdichters (W)
  - `temperature`: Speichertemperatur (°C)
  - `sg_switch`: Relaiskontakt (SG-Ready State 2/3)
- **Echtzeit-Rückkanal**: Closed-Loop Rückmeldung bei Schaltungen innerhalb von < 100 ms.

---

## 🚗 10. Smart EV Charging & Departure Ready Planner

Die Wallbox-Steuerung bietet einen intelligenten Abfahrtszeit-Planer:
- **km-Reichweiten-Zuwachs**: Umrechnung der Ladeenergie in Reichweite ($\text{km} = E_\text{geladen} / 17\,\text{kWh} \times 100$).
- **Fahrzeug-SoC-Schätzung**: Prozentuale Ladezustandsanzeige.
- **Nacht-Spotpreis-Kopplung**: Automatischer Ladefenster-Abgleich mit den günstigsten Day-Ahead-Stunden bis zur gewünschten Abfahrtszeit (z. B. `07:30 Uhr`).
- **1-Klick Quick-Boost**: 1h Vollladung ohne Menüschachteln.

---

## 🌊 11. Live Surplus-Waterfall Kaskade

Echtzeit-Visualisierung der Merit-Order-Energieverteilung ($P_\text{PV} \rightarrow \text{Last} \rightarrow \text{Speicher} \rightarrow \text{BWWP} \rightarrow \text{Wallbox} \rightarrow \text{Netz}$) mit Live-Leistungsbalken und prozentualem Deckungsstatus direkt auf dem Dispatch Hub.

---

## 📊 12. Monatlicher Finanz- & ROI-Recap

Monatliche Gegenüberstellung des wirtschaftlichen Mehrwerts:
- **Netto-Sparvorteil in €** gegenüber dem Grundversorgertarif ($32\,\text{ct/kWh}$).
- **Autarkie- und Eigenverbrauchsgrad**.
- **Vermiedene CO₂-Emissionen** und Baum-Äquivalent.
- **§ 14a EnWG Netzentgelt-Bonus** (+160 €/Jahr Pauschalvorteil).
- **1-Klick Share-Modal** zum Teilen der Energiebilanz.

---

## 📖 Detaillierte Anwenderdokumentation

Das vollständige Anwenderhandbuch mit Schritt-für-Schritt-Anleitungen zu allen Schnittstellen (1–7) und EMS-Funktionen ist in [`docs/SHAREGY_USER_MANUAL_EMS_EXTENSIONS.md`](file:///c:/Users/Public/Dev/eswes/docs/SHAREGY_USER_MANUAL_EMS_EXTENSIONS.md) verfügbar.

