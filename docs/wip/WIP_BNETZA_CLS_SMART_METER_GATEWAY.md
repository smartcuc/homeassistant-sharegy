# ⚡ [LIVE] BNetzA CLS-Kanal & Smart Meter Gateway (SMGW) Kopplung (§ 14a EnWG)

**Status:** 🟢 100% Fertiggestellt & Live  
**Fortschritt:** 🟢 100 %  
**Priorität:** 🔴 Hoch / Abgeschlossen  
**Lead / Modul:** `energy`, `billing`, `devices`  

---

## 🎯 1. Feature-Beschreibung & Zielsetzung

Direkte, revisionssichere Kopplung von Sharegy an das BSI-zertifizierte **Smart Meter Gateway (SMGW)** über die **CLS-Schnittstelle (Controllable Local System)** nach BSI TR-03109-1 / FNN-Lastenheft Steuerbox.

### Regulatorischer Hintergrund (§ 14a EnWG & BNetzA BK6-22-300 / BK8-22/010-A):
* Netzbetreiber in Deutschland sind berechtigt, steuerbare Verbrauchseinrichtungen (SteuVE: Wallboxen $\ge 4{,}2\,\text{kW}$, Wärmepumpen $\ge 4{,}2\,\text{kW}$, PV-Speicher) bei lokaler Netzüberlastung vorübergehend auf einen Mindestbezug von $4{,}2\,\text{kW}$ zu dimmen.
* Die Dimm-Befehle werden vom Verteilnetzbetreiber (VNB) über das SMGW und den CLS-Kanal übertragen.
* Sharegy implementiert das **dynamische Summenleistungs-Modell**:
  $$P_{\text{allow}} = 4{,}2\,\text{kW} (\text{Netz}) + P_{\text{PV}} (\text{Erzeugung}) + P_{\text{Batt}} (\text{Entladung}) - P_{\text{Base}} (\text{Grundlast})$$
  Hierdurch wird Heizkomfort und Ladevorgang bei vorhandener lokaler Solarenergie trotz aktiver Netzdrosselung aufrechterhalten.

---

## 🏗️ 2. Architektur & Endpunkte

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
│   Sharegy CLS Gateway API Endpunkte  │
│ • POST /api/energy/cls/signal/       │ Ingest Drosselungsbefehl & Dispatch Acknowledgment
│ • GET  /api/energy/cls/status/       │ Live-Status, Limits, Audit-Log & SteuVE-Kaskade
│ • POST /api/energy/cls/clear/        │ Normalbetrieb / VNB-Entwarnung wiederherstellen
└──────────────────┬───────────────────┘
                   │ Merit-Order & Aktor-Kaskade
                   ▼
┌──────────────────────────────────────┐
│     Sharegy EMS Merit-Order Engine   │
│ • Wärmepumpe: Priorität 1 (Komfort)  │
│ • Heimspeicher: Netzladen gesperrt   │
│ • Wallbox: Dynamisch geregelt (6-16A)│
│ • Revisionssicheres Audit-Logging    │
└──────────────────────────────────────┘
```

---

## 📊 3. Umsetzungsstand & Validierung

| Komponente | Status | Implementierung |
|---|:---:|---|
| **BSI TR-03109-1 CLS Ingest API** | 🟢 100% | `POST /api/energy/cls/signal/` in [energy/views_cls.py](file:///C:/Users/Public/Dev/sharegy/energy/views_cls.py) |
| **FNN Steuerbox Quittierung (Dispatch Acknowledgment)** | 🟢 100% | JSON-Quittung mit `dispatch_id`, `execution_timestamp_utc`, `steuve_allocation`, `power_budget` |
| **CLS Status & Telemetrie Endpoint** | 🟢 100% | `GET /api/energy/cls/status/` inkl. aktiver Signale und SteuVE-Drosselstatus |
| **Entwarnungs- & Freigabe-Endpunkt** | 🟢 100% | `POST /api/energy/cls/clear/` für Entwarnung und Freigabe aller SteuVE |
| **Revisionssicheres Audit-Log** | 🟢 100% | `EnWG14aDimmingAuditLog` protokolliert Soll/Ist-Werte, Reaktionszeit (<30s) und Compliance |
| **Automatisierte Test-Suite** | 🟢 100% | [energy/test_grid_dimming.py](file:///C:/Users/Public/Dev/sharegy/energy/test_grid_dimming.py) (`test_cls_smgw_api_lifecycle`) |
