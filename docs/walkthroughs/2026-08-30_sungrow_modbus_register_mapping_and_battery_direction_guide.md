# 📑 Sungrow Modbus Register Mapping & Batterie-Richtungs-Guide (Sharegy HEMS)

**Datum**: 30. August 2026  
**Status**: ✅ Freigegeben / Produktionsreif  
**Ziel**: Vollständige Referenz aller relevanten Modbus-Register für Sungrow Hybrid-Wechselrichter (SHxxRT, SHxxRS-Serie) zur präzisen physikalischen Bilanzierung im Sharegy Energy Management System.

---

## 1. ⚡ Echtzeit-Flüsse & Wirkleistungen (Live-Sankey & Dashboard)

Zur unterbrechungsfreien Visualisierung des Live-Energieflusses im Sharegy Dashboard und Sankey-Diagramm werden die folgenden Kern-Wirkleistungen (in Watt) bzw. der Batteriestrom im Intervall von **5–10 Sekunden** abgefragt:

| Parameter | Modbus-Adresse | Register-Nr. | Datentyp | Vorzeichen / Physikalische Bedeutung |
| :--- | :---: | :---: | :---: | :--- |
| **PV-Erzeugung Live** | `5016` | `5017–5018` | `uint32` (swap word) | `W` (reine Erzeugung aller MPPTs/Strings zusammen) |
| **Batteriestrom (Signed)** 🌟 | `5630` oder `13020` | `5631` / `13021` | `int16` (scale `0.1`) | **Zuverlässigste Richtungsquelle auf allen WR!**<br>• **`< 0`**: Batterie **lädt** ($I < 0\,\text{A}$)<br>• **`> 0`**: Batterie **entlädt** ($I > 0\,\text{A}$) |
| **Batterieleistung (Raw/Positiv)** | `13021` oder `5213` | `13022` / `5214` | `uint16` / `int32` | `W` (wird über `battery_current` automatisch vorzeichenkorrigiert) |
| **Batteriespannung** | `13019` | `13020` | `uint16` (scale `0.1`) | `V` (für $P = U \times I$ falls keine direkte Leistung vorliegt) |
| **Netzzähler (Smart Meter)** | `5600` | `5601–5602` | `int32` (swap word) | **Vorzeichenbehaftet!**<br>• **`> 0`**: Netz**bezug** (Import)<br>• **`< 0`**: Netz**einspeisung** (Export) |
| **Hausverbrauch Gesamt** | `13007` | `13008–13009` | `int32` (swap word) | `W` (echter gemessener Gesamthausverbrauch) |

> [!IMPORTANT]
> **Praxiserkenntnis zu Register 5213 und 12999 (Running State):**  
> • Register `5213` liefert bei vielen Inverter-Modellen / Firmwareständen stets `0`.  
> • Register `12999` ist oft bitmasken-kodiert und herstellerseitig zwischen Firmware-Versionen uneinheitlich.  
> • **Die robusteste & verlässlichste Methode**: **`battery_current` (Register `5630` bzw. `13020`)**! Da der Strom immer ein klares Vorzeichen besitzt (`-` beim Laden, `+` beim Entladen), nutzt Sharegy diesen Wert direkt, um das Vorzeichen der Batterieleistung zu bestimmen oder $P = U \times I$ hochpräzise zu errechnen.

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
