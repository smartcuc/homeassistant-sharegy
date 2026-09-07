# 🏠 Sharegy Home Assistant Custom Component (v2.1.0)

Die offizielle Home Assistant Integration verbindet dein **Sharegy HEMS** bidirektional (**Messen & Steuern**) mit Home Assistant:
* ☀️ **Live-Sensoren**: PV-Erzeugung, Hauslast, Netzleistung, Batteriespeicher-SoC und Autarkiegrad.
* 🌡️ **Fußbodenheizung & Estrich-Speicher**: Echtzeit-Berechnung der DIN EN 12831 Vorlauftemperatur, Ladezustand des Estrich-Speichers (SoC %) und aktueller Betriebsmodus.
* 🎛️ **Bidirektionale Aktorik & Schalter**: Direkte Schaltung von Vorheiz-Boosts, SG-Ready Anhebung für Brauchwasser-Wärmepumpen und Anpassung der Ziel-Raumtemperatur.
* 💶 **Börsenstrompreis & Optimizer**: Bereitstellung der dynamischen EPEX Spot-Preise und der besten Ladefenster für deine HA-Automationen.
* 🔒 **Sichere Kommunikation (WSS bevorzugt)**: Volle Unterstützung für Outbound WSS über Port 443 (Firewall- und NAT-sicher ohne Portfreigaben) sowie MQTT.

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
   * **API-Key / Home-Token**: Dein Token aus Sharegy (**Schnittstellen**)
   * **Abfrage-Intervall**: Standard 10 Sekunden (einstellbar 5 bis 300 Sekunden).
4. Fertig! Alle Sensoren, Schalter und Schieberegler werden automatisch erstellt.

---

## 📊 Verfügbare Entitäten

### 📈 Sensoren (Messen & Monitoring)

| Entität | Einheit | Beschreibung |
| :--- | :---: | :--- |
| `sensor.sharegy_solar_erzeugung` | `W` | Aktuelle Solarleistung aller PV-Strings |
| `sensor.sharegy_hausverbrauch` | `W` | Gesamte Haushaltslast |
| `sensor.sharegy_netzleistung` | `W` | Netzbezug (positiv) / Netzeinspeisung (negativ) |
| `sensor.sharegy_batterieleistung` | `W` | Batterieladung (positiv) / Entladung (negativ) |
| `sensor.sharegy_batterie_ladestand_soc` | `%` | Aggregierter Ladestand des Batteriespeichers |
| `sensor.sharegy_autarkiegrad` | `%` | Heutiger Autarkiegrad |
| `sensor.sharegy_eigenverbrauchsquote` | `%` | Heutige Eigenverbrauchsquote |
| `sensor.sharegy_borsenstrompreis` | `ct/kWh` | Aktueller dynamischer Strompreis |
| `sensor.sharegy_optimizer_best_zeitfenster` | String | Bestes Lade-/Heizfenster (z. B. `13:00 - 15:00`) |
| `sensor.sharegy_fbh_vorlauf_solltemperatur` | `°C` | Berechnete DIN EN 12831 Heizkurven-Soll-Vorlauftemperatur |
| `sensor.sharegy_fbh_estrich_speicher_ladestand_soc` | `%` | Ladezustand des thermischen Estrich-Speichers |
| `sensor.sharegy_fbh_heizleistung` | `kW` | Aktuelle thermische Heizleistung |
| `sensor.sharegy_fbh_betriebsmodus` | String | Betriebsmodus (`PV-Überschuss Boost`, `Netz-Arbitrage`, `Komfort`, `Eco`) |
| `sensor.sharegy_fbh_ist_raumtemperatur` | `°C` | Aktuelle Raumtemperatur |
| `sensor.sharegy_bwwp_sg_ready_status` | String | Status der Warmwasser-Wärmepumpe |

### 🎛️ Schalter & Regler (Steuern & Aktorik)

| Entität | Typ | Beschreibung |
| :--- | :---: | :--- |
| `switch.sharegy_bidirektionale_steuerung` | Schalter | Globaler Not-Aus / Pause für automatische Aktorik |
| `switch.sharegy_fussbodenheizung_boost` | Schalter | Manueller Vorheiz-Boost für den thermischen Estrich-Speicher |
| `switch.sharegy_fussbodenheizung_modul_aktiv` | Schalter | Fußbodenheizungs-Dispatch-Modul aktivieren / deaktivieren |
| `switch.sharegy_brauchwasser_wp_boost` | Schalter | SG-Ready Boost Anhebung für BWWP |
| `number.sharegy_fbh_soll_raumtemperatur` | Schieberegler | Gewünschte Komfort-Zielraumtemperatur (18.0 - 24.0 °C) |
| `number.sharegy_fbh_estrich_uberhitzungs_toleranz` | Schieberegler | Max. Estrich-Puffertoleranz in Kelvin (0.5 - 3.0 K) |

---

## 🤖 Beispiel-Automationen

### 1. Fußbodenheizung bei dynamischem Tiefpreis vorheizen
```yaml
alias: "Sharegy: Fußbodenheizung bei Negativ-/Tiefpreis boosten"
description: "Aktiviert den thermischen Estrich-Vorheiz-Boost bei günstigem Börsenstrompreis"
trigger:
  - platform: numeric_state
    entity_id: sensor.sharegy_borsenstrompreis
    below: 15.0 # unter 15 ct/kWh
condition:
  - condition: state
    entity_id: switch.sharegy_bidirektionale_steuerung
    state: "on"
action:
  - service: switch.turn_on
    target:
      entity_id: switch.sharegy_fussbodenheizung_boost
```

### 2. Lokale Messwerte (z. B. Shelly 3EM) an Sharegy senden
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
        - identifier: "heatpump_main"
          name: "Wärmepumpe"
          power_w: "{{ states('sensor.heatpump_power') | float }}"
          role: "consumer"
```
