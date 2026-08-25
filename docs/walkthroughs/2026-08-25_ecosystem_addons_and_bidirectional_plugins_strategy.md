# 🔌 Strategiekonzept: Device-Profile Addon-System & Bi-direktionale Ökosystem-Plugins (HA, evcc, ioBroker)

**Datum**: 25. August 2026  
**Bereich**: System-Architektur, Hardware-Abstraktion, Smart Home & EMS-Aktorik

---

## 🎯 Strategische Weichenstellung: "Leverage Existing Ecosystems"

Statt einen eigenen, kostenintensiven Hardware-EMS-Control-Hub (mit 18–24 Monaten Entwicklungszeit, CE-Zertifizierungen und Treiber-Hölle) zu bauen, verfolgt Sharegy eine **10x schnellere und kapitaleffizientere Hebel-Strategie**:

1. **Sharegy = Das Gehirn & die Plattform (Cloud / SaaS)**:
   * KI-Solarprognose (Physics + Machine Learning).
   * Dynamische Börsenstrompreis-Bewertung (EPEX Spot / Day-Ahead).
   * 1h/2h/4h Smart Energy Optimizer (Opportunitätskosten-Modell).
   * Multi-Tenant, Mieterstrom & Energy-Sharing-Clearing (P2P-Tarife).
2. **Bestehende Open-Source-Ökosysteme = Die Hände & Füße (Lokal vor Ort)**:
   * **`Home Assistant`**: Schaltet 3.000+ Geräte, SG-Ready Wärmepumpen, Zigbee/Shelly-Relais.
   * **`evcc`**: Unangefochtener Marktführer für PV-E-Auto-Ladung (60+ Wallboxen, 1p/3p Phasenumschaltung).
   * **`ioBroker`**: Industriestandard für Modbus Master, KNX und SPS-Installationen.

```mermaid
graph TD
    subgraph Sharegy Cloud (Gehirn & Sharing-Ebene)
        OPT[🧠 Smart Energy Optimizer<br/>PV-Forecast & EPEX Spot]
        SHARE[👥 Energy Sharing & P2P-Tarife<br/>Quartiers- & Mieterstrom-Clearing]
        HUB[⚡ Zentraler MQTT Hub & REST API<br/>Bi-direktionale Bridge]
    end

    subgraph Lokale Vor-Ort-Akteure (Aktorik & Hardware-Treiber)
        HA[🏠 Home Assistant Add-on<br/>Schaltet Wärmepumpe, Shelly, Relais]
        EVCC[🚗 evcc Provider-Integration<br/>Phasenumschaltung & 60+ Wallboxen]
        IOB[📦 ioBroker Adapter<br/>KNX, SPS, Smart Home Steuerung]
    end

    subgraph Deklaratives Addon-System
        YAMLA[📄 sungrow_modbus.yaml]
        YAMLB[📄 sma_tripower.yaml]
        YAMLC[📄 fronius_solarapi.json]
    end

    OPT -->|Fahrplan: Lade von 13:00 - 17:00| HUB
    SHARE -->|Netz-Dimmung & Freigaben| HUB
    
    HUB <==>|Telemetrie hoch / Schaltbefehle runter| HA
    HUB <==>|Spotpreise & Solar-Surplus Vorgaben| EVCC
    HUB <==>|Objektbaum-Sync| IOB

    YAMLA --> HUB
    YAMLB --> HUB
    YAMLC --> HUB
```

---

## 1. 📦 Das deklarative Device-Profile Addon-System (3rd-Party Wechselrichter)

Um Hersteller wie **Sungrow, SMA, Fronius, Deye, Huawei, Kostal und SolarEdge** ohne Backend-Codeänderungen anzubinden, wird die Ingestion in **Transport** und **Mapping** getrennt:

### Architektur
* **Transport-Layer (Universal)**:
  * MQTT-Topic: `sharegy/ingest/{profile_slug}/{device_id}`
  * REST-Webhook: `POST /api/v1/ingest/adapter/{profile_slug}/`
* **Deklarative Profile (YAML / JSON)**:
  Jedes Profil beschreibt die Feldzuordnung auf die Sharegy Standard-Metriken (`pv_power_w`, `grid_power_w`, `battery_power_w`, `battery_soc`, `load_power_w`):

```yaml
# Beispiel: sungrow_sh10rt.yaml
vendor: "Sungrow"
model: "SH10RT Hybrid"
protocol: "modbus_tcp"
fields:
  pv_power_w:
    register: 5017
    scale: 1.0
    unit: "W"
  battery_soc:
    register: 13022
    scale: 0.1
    unit: "%"
  grid_power_w:
    register: 13008
    scale: 1.0
    unit: "W"
```

> 💡 **Vorteil**: Neue Wechselrichter und Speicher können in Minuten über Community-YAML-Profile hinzugefügt werden.

---

## 2. 🔌 Die 3 Bi-direktionalen Kern-Plug-ins

### A. Home Assistant Integration (`custom_components/sharegy`)
* **Ingest (HA $\rightarrow$ Sharegy)**:
  * Erkennt automatisch alle PV-, Zähler- und Batteriewerte in Home Assistant und sendet sie im Sekundentakt via MQTT an Sharegy.
* **Aktorik (Sharegy $\rightarrow$ HA)**:
  * Erstellt in Home Assistant Entitäten:
    * `sensor.sharegy_optimizer_best_window` (*"13:00 - 17:00 Uhr"*)
    * `binary_sensor.sharegy_solar_surplus_active` (*on/off*)
    * `switch.sharegy_auto_control` (*Automations-Freigabe*)
  * HA-Automationen schalten Waschmaschinen, SG-Ready Relais der Wärmepumpe oder Poolpumpen exakt nach dem Sharegy-Fahrplan.

### B. evcc Provider-Integration (`evcc custom tariff / loadpoint`)
* **evcc** ist die unangefochtene Nr. 1 für PV-geführtes Laden von Elektroautos (60+ Wallboxen, 1p/3p Umschaltung, Tesla/VW SoC-Abfrage).
* **Sharegy $\rightarrow$ evcc**:
  * evcc fragt die Sharegy API ab: `GET /api/energy/optimizer/`
  * evcc nutzt den von Sharegy berechneten Opportunitätskosten-Fahrplan als dynamischen Tarif (`tariff: custom`).
  * Ergebnis: Das Auto lädt vollautomatisch in den von Sharegy ermittelten 1h/2h/4h-Bestfenstern.

### C. Grafana Visualization & Cockpit Dashboards (`plugins/grafana`)
* **REST-Bridge**: Bereitstellung von `/api/grafana/search`, `/query` und `/annotations` (kompatibel mit Grafana JSON / Infinity Datasource).
* **Fertiges Cockpit**: `sharegy_energy_cockpit.json` mit Gauges, 24h-Verläufen, Börsenpreisen und Sub-Metering-Charts.

### D. Matter 1.3 Energy Management Hub (`providers.matter`)
* **Nativer CSA Matter 1.3 Hub**: Direkte Einbindung von Smart Plugs (Eve Energy, Shelly), EVSE-Wallboxen und Wärmepumpen via Thread / Wi-Fi / IP.
* **Unterstützte Cluster**:
  * `0x0090` Electrical Power Measurement (Live W, V, A, Power Factor).
  * `0x0091` Electrical Energy Measurement (kWh Zählerstände).
  * `0x0006` On/Off Cluster (Schalten & Toggeln).
  * `0x0098` / `0x0099` Device Energy Management & EVSE Wallbox-Ladedrosselung.

### E. ioBroker Adapter (`iobroker.sharegy`)
* Zwei-Wege-Synchronisation von Datenpunkten über den Sharegy MQTT-Hub für klassische KNX- und SPS-Installationen.

---

## 🚀 Fazit & Nutzen
* **Keine eigene Hardware nötig**: Spart 18 Monate Entwicklungszeit und massive Supportkosten.
* **100 % Kompatibilität**: Mit HA, Matter 1.3, Grafana und evcc ist Sharegy ab Tag 1 kompatibel zu nahezu allen am Markt existierenden Wallboxen, Wärmepumpen und Wechselrichtern.
* **Fokus auf Kernkompetenz**: Sharegy konzentriert sich auf KI-Prognosen, EPEX-Spot-Optimierung, Community-Bilanzen und Abrechnung.


