# 🏠 Sharegy Home Assistant Custom Component

Die offizielle Home Assistant Integration verbindet dein **Sharegy HEMS** mit Home Assistant:
* ☀️ **Live-Sensoren**: PV-Erzeugung, Hauslast, Netzleistung, Batteriespeicher-SoC und Autarkiegrad.
* 💶 **Börsenstrompreis & Optimizer**: Bereitstellung der dynamischen EPEX Spot-Preise und der besten 1h-, 2h- und 4h-Ladefenster für deine HA-Automationen (z. B. E-Auto laden oder Wärmepumpe ansteuern).
* 🔒 **Verschlüsselter Telemetrie-Rückkanal**: Übertrage Messwerte lokaler Smart-Home-Zähler (Shelly 3EM, Zigbee/Tasmota Steckdosen, Easee Wallbox) direkt an Sharegy.

---

## 📦 Installation

### Option 1: Manuelle Installation
1. Lade den Ordner `custom_components/sharegy` herunter.
2. Kopiere ihn in dein Home Assistant Konfigurationsverzeichnis nach `/config/custom_components/sharegy/`.
3. Starte Home Assistant neu.

### Option 2: Via HACS (Home Assistant Community Store)
1. Öffne HACS in Home Assistant → **Integrationen**.
2. Klicke oben rechts auf das Drei-Punkte-Menü → **Benutzerdefiniertes Repository hinzufügen**.
3. Gib die Repository-URL ein und wähle die Kategorie **Integration**.
4. Installiere **Sharegy HEMS** und starte Home Assistant neu.

---

## ⚙️ Konfiguration

1. Gehe in Home Assistant zu **Einstellungen → Geräte & Dienste → Integration hinzufügen**.
2. Suche nach **Sharegy HEMS**.
3. Trage deine Zugangsdaten ein:
   * **Host**: `https://sharegy.de` (Standard vorausgefüllt)
   * **API-Key / MQTT-Token**: Dein Token aus Sharegy (**Schnittstellen & MQTT**)
   * **Abfrage-Intervall**: Standard 10 Sekunden (einstellbar 5 bis 300 Sekunden).
4. Fertig! Alle 9 Sensoren werden automatisch erstellt.

---

## 📊 Verfügbare Sensoren

| Entität | Einheit | Beschreibung |
| :--- | :---: | :--- |
| `sensor.sharegy_solar_erzeugung` | `W` | Aktuelle Solarleistung aller PV-Strings |
| `sensor.sharegy_hausverbrauch` | `W` | Gesamte Haushaltslast |
| `sensor.sharegy_netzleistung` | `W` | Netzbezug (positiv) / Netzeinspeisung (negativ) |
| `sensor.sharegy_batterieleistung` | `W` | Batterieladung (positiv) / Entladung (negativ) |
| `sensor.sharegy_batterie_ladestand_soc` | `%` | Aggregierter Ladestand des Speichers |
| `sensor.sharegy_autarkiegrad` | `%` | Heutiger Autarkiegrad |
| `sensor.sharegy_eigenverbrauchsquote` | `%` | Heutige Eigenverbrauchsquote |
| `sensor.sharegy_borsenstrompreis` | `ct/kWh` | Aktueller dynamischer Strompreis |
| `sensor.sharegy_optimizer_best_zeitfenster` | String | Bestes 2h-Zeitfenster (z. B. `13:00 - 15:00`) |

---

## 🤖 Beispiel-Automation: E-Auto im günstigsten Zeitfenster laden

```yaml
alias: "Sharegy: Wallbox im günstigsten Ladefenster einschalten"
description: "Startet das Laden, sobald das vom Optimizer empfohlene Zeitfenster aktiv ist"
trigger:
  - platform: template
    value_template: >
      {% set window = states('sensor.sharegy_optimizer_best_zeitfenster') %}
      {% if ' - ' in window %}
        {% set start_time = window.split(' - ')[0] %}
        {{ now().strftime('%H:%M') == start_time }}
      {% else %}
        false
      {% endif %}
condition:
  - condition: state
    entity_id: binary_sensor.wallbox_car_connected
    state: "on"
action:
  - service: switch.turn_on
    target:
      entity_id: switch.wallbox_charging
```

---

## 📤 Lokale Messwerte an Sharegy senden (Service `push_telemetry`)

Übertrage eigene Smart-Home-Zähler (z. B. Shelly 3EM) in festen Intervallen verschlüsselt an Sharegy:

```yaml
alias: "Sharegy: Shelly 3EM Telemetrie übertragen"
trigger:
  - platform: time_pattern
    seconds: "/10"
action:
  - service: sharegy.push_telemetry
    data:
      devices:
        - identifier: "shelly_3em_grid"
          name: "Shelly 3EM Hauptanschluss"
          power_w: "{{ states('sensor.shelly_3em_total_power') | float }}"
          energy_kwh: "{{ states('sensor.shelly_3em_total_energy') | float }}"
          role: "grid"
        - identifier: "shelly_heatpump"
          name: "Wärmepumpe"
          power_w: "{{ states('sensor.heatpump_power') | float }}"
          role: "consumer"
```

