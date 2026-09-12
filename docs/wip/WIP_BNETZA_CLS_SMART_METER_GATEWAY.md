# 🛠️ [WIP] BNetzA CLS-Kanal & Smart Meter Gateway (SMGW) Kopplung (§ 14a EnWG)

**Status:** In Konzeption / Vorbereitung  
**Fortschritt:** 🟡 40 %  
**Priorität:** 🔴 Hoch (Ziel: Q1 / Q2 2027)  
**Lead / Modul:** `energy`, `billing`, `devices`  

---

## 🎯 1. Feature-Beschreibung & Zielsetzung

Direkte Kopplung von Sharegy an das BSI-zertifizierte **Smart Meter Gateway (SMGW)** über die **CLS-Schnittstelle (Controllable Local System)** nach BSI TR-03109-1 / FNN-Lastenheft Steuerbox.

### Regulatorischer Hintergrund (§ 14a EnWG):
* Seit 1. Januar 2024 sind Netzbetreiber in Deutschland berechtigt, steuerbare Verbrauchseinrichtungen (SteuVE: Wallboxen $\ge 4{,}2\,\text{kW}$, Wärmepumpen $\ge 4{,}2\,\text{kW}$, PV-Speicher) im Fall drohender Netzüberlastung vorübergehend auf einen Mindestbezug von $4{,}2\,\text{kW}$ zu dimmen.
* Die Dimm-Befehle werden vom Verteilnetzbetreiber (VNB) über das SMGW und die CLS-Schnittstelle in das Gebäude übertragen.
* Sharegy fungiert als **intelligentes EMS**, das den Dimm-Befehl empfängt und die verfügbaren $4{,}2\,\text{kW}$ dynamisch auf alle aktiven Geräte im Haushalt verteilt, anstatt sie hart abzuschalten.

---

## 🏗️ 2. Architektur & Signalfluss

```
[Verteilnetzbetreiber / VNB]
           │
           │ (BSI PKI / TLS-Tunnel)
           ▼
┌──────────────────────────────────────┐
│     Smart Meter Gateway (SMGW)       │ (Theben, PPC, EMH)
└──────────────────┬───────────────────┘
                   │ CLS / HAN Schnittstelle (BSI TR-03109-1)
                   ▼
┌──────────────────────────────────────┐
│     Lokaler Sharegy CLS Proxy        │ (Lokaler Dienst / ioBroker / Pi)
└──────────────────┬───────────────────┘
                   │ WSS / REST Event
                   ▼
┌──────────────────────────────────────┐
│     Sharegy EMS Merit-Order Engine   │
│ • Wallbox auf 2,1 kW drosseln        │
│ • Wärmepumpe auf 2,1 kW drosseln     │
│ • Haushaltsverbrauch unberührt       │
│ • Netzentgelt-Rückvergütung sichern  │
└──────────────────────────────────────┘
```

---

## 📊 3. Aktueller Umsetzungsstand & Delta

| Komponente | Status | Implementiert im Code | Noch zu erledigen |
|---|:---:|---|---|
| **Dimm-Logik & Priorität** | 🟢 100% | § 14a EnWG Drosselungs-Algorithmus in `energy/flow_engine.py` mit Priorisierung von Haushaltslasten vor SteuVE. | Dynamischer Dimm-Faktor aus externem Signal. |
| **VPP / Pooling API** | 🟢 100% | `/api/vpp/flexibility/` liefert aggregierte flexible Lasten und Steuerbarkeit. | Quittierungskanal für VNB-Netzleitstellen. |
| **Lokaler CLS-Proxy** | 🔴 10% | Netzwerk-Architektur & HAN-Protokoll-Spezifikation. | Lokaler Daemon zur Entschlüsselung von BSI-TR-03109-1 CLS-Nachrichten. |
| **FNN Steuerbox Testfälle** | 🔴 0% | Nicht gestartet. | Validierung gegen standardisierte FNN-Prüfprofile. |

---

## 🚀 4. Nächste Umsetzungsschritte

1. **Sprint 1**: Spezifikation des JSON-Payloads für netzdienliche Dimm-Signale im WSS-Ingest (`/ws/edge/v1/`).
2. **Sprint 2**: Implementierung der automatischen Dispatch-Quittierung (Empfangsbestätigung & Ausführungszeitpunkt an VNB-Gateway).
3. **Sprint 3**: UI-Warnbanner und Audit-Log im Dashboard, wenn eine netzseitige Drosselung aktiv ist.
