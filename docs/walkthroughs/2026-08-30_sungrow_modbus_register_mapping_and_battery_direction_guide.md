# 📑 Sungrow Modbus Register Mapping & Batterie-Richtungs-Guide (Sharegy HEMS)

**Datum**: 30. August 2026  
**Status**: ✅ Freigegeben / Produktionsreif  
**Ziel**: Vollständige Referenz aller relevanten Modbus-Register für Sungrow Hybrid-Wechselrichter (SHxxRT, SHxxRS-Serie) zur präzisen physikalischen Bilanzierung im Sharegy Energy Management System.

---

## 1. ⚡ Echtzeit-Flüsse & Wirkleistungen (Live-Sankey & Dashboard)

Zur unterbrechungsfreien Visualisierung des Live-Energieflusses im Sharegy Dashboard und Sankey-Diagramm werden die folgenden 4 Kern-Wirkleistungen (in Watt) im Intervall von **5–10 Sekunden** abgefragt:

| Parameter | Modbus-Adresse | Register-Nr. | Datentyp | Vorzeichen / Physikalische Bedeutung |
| :--- | :---: | :---: | :---: | :--- |
| **PV-Erzeugung Live** | `5016` | `5017–5018` | `uint32` (swap word) | `W` (reine Erzeugung aller MPPTs/Strings zusammen) |
| **Batterieleistung Live** 🌟 | `5213` | `5214–5215` | `int32` (swap word) | **Vorzeichenbehaftet (TI Spec 1.1.11)!**<br>• **`< 0`**: Batterie **lädt** (Stromaufnahme/Last)<br>• **`> 0`**: Batterie **entlädt** (Einspeisung ins Haus) |
| **Netzzähler (Smart Meter)** | `5600` | `5601–5602` | `int32` (swap word) | **Vorzeichenbehaftet!**<br>• **`> 0`**: Netz**bezug** (Import)<br>• **`< 0`**: Netz**einspeisung** (Export) |
| **Hausverbrauch Gesamt** | `13007` | `13008–13009` | `int32` (swap word) | `W` (echter gemessener Gesamthausverbrauch) |

> [!TIP]
> **Warum Register `5213` statt alter Register `13021/13022`?**  
> In älteren Firmwares war `13021` immer positiv (unsigned) und benötigte ein separates Richtungsflag (`running_state`). Sungrow empfiehlt im aktuellen Standardprotokoll offiziell Register `5213`, welches die Batterieleistung nativ als vorzeichenbehaftetes `int32` liefert.

---

## 2. 🔋 Batterie-Status, SoC & Diagnose

Zur Überwachung des Ladezustands und für intelligente EMS-Ladestrategien:

| Parameter | Modbus-Adresse | Register-Nr. | Datentyp | Skalierung / Einheit | Bedeutung |
| :--- | :---: | :---: | :---: | :---: | :--- |
| **Batterie SoC** | `13022` | `13023` | `uint16` | `scale: 0.1` $\rightarrow$ `%` | Ladezustand (z. B. `655` = `65,5 %`) |
| **Batteriespannung** | `13019` | `13020` | `uint16` | `scale: 0.1` $\rightarrow$ `V` | Akkuspannung in Volt |
| **Running State (Status)** | `12999` | `13000` | `uint16` | `scale: 1` | `0` = Standby/Idle, `1` = Laden, `2` = Entladen |
| **Batterietemperatur** | `13024` | `13025` | `int16` | `scale: 0.1` $\rightarrow$ `°C` | Zelltemperatur |
| **State of Health (SoH)** | `13023` | `13024` | `uint16` | `scale: 0.1` $\rightarrow$ `%` | Batteriegesundheit |

---

## 3. 📊 Zählerstände für Energiebilanz & Sub-Metering (kWh)

Zur exakten Ermittlung von Tageserträgen, Autarkiequoten und solarem Deckungsgrad der Einzelverbraucher:

| Messgröße | Tageszähler (kWh) | Gesamtzähler (kWh) | Datentyp | Skalierung |
| :--- | :---: | :---: | :---: | :---: |
| **PV-Erzeugung** | `13001` (Reg 13002) | `13002` (Reg 13003) | `uint16` / `uint32` | `0.1` |
| **Netzbezug (Import)** | `13035` (Reg 13036) | `13036` (Reg 13037) | `uint16` / `uint32` | `0.1` |
| **Netzeinspeisung (Export)** | `13044` (Reg 13045) | `13045` (Reg 13046) | `uint16` / `uint32` | `0.1` |
| **Batterie-Ladung** | `13039` (Reg 13040) | `13040` (Reg 13041) | `uint16` / `uint32` | `0.1` |
| **Batterie-Entladung** | `13025` (Reg 13026) | `13026` (Reg 13027) | `uint16` / `uint32` | `0.1` |
| **Direkter Eigenverbrauch** | `13016` (Reg 13017) | `13017` (Reg 13018) | `uint16` / `uint32` | `0.1` |

---

## 4. 🧠 Automatische Richtungsauflösung im Sharegy-Backend

Für ältere Firmwares oder Adapter, die das unvorzeichenbehaftete Register `13021` mit `running_state` übergeben, verfügt das Sharegy-Backend über eine integrierte Normalisierungs-Pipeline (`normalize_battery_metrics` & `resolve_battery_direction`):

```python
# Auszug aus devices/services/metrics.py:
def resolve_battery_direction(direction_val):
    if direction_val in [1, "1", "charge", "charging", "laden", "in"]:
        return -1  # Laden -> physikalisch negative Wirkleistung
    elif direction_val in [2, "2", "-1", "discharge", "discharging", "entladen", "out"]:
        return 1   # Entladen -> physikalisch positive Wirkleistung
    elif direction_val in [0, "0", "idle", "standby", "off"]:
        return 0   # Standby -> 0.0 W
```

### Physikalische Bilanzierungs-Gleichung:
$$\text{Hausbedarf } P_{\text{Load}} = P_{\text{PV}} + P_{\text{Bat, Discharge}} + P_{\text{Grid, Import}} - P_{\text{Bat, Charge}} - P_{\text{Grid, Export}}$$

---

## 5. 🚀 Empfohlene Home Assistant / MQTT Payload-Konfiguration

Wird Sungrow über Home Assistant oder ein Modbus-to-MQTT Gateway an Sharegy angebunden, reicht folgender kompakter JSON-Payload:

```json
{
  "total_dc_power": 4200.0,
  "battery_power": -2500.0,
  "meter_active_power": -1200.0,
  "load_power": 500.0,
  "battery_level": 78.5
}
```

* **PV-Erzeugung**: $4.200\,\text{W}$
* **Batterieladung**: $2.500\,\text{W}$ (aus PV geladen)
* **Netzeinspeisung**: $1.200\,\text{W}$ (Überschuss ins Netz)
* **Hausverbrauch**: $500\,\text{W}$ ($4.200 - 2.500 - 1.200 = 500\,\text{W}$)
* **Solardeckung der Submeter**: **100 % Solarstrom**
