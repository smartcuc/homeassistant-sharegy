# ⚡ BNetzA CLS-Kanal & Smart Meter Gateway (SMGW) Kopplung (§ 14a EnWG)

**Dokument-Status:** Offizielle System- & Integrations-Dokumentation  
**Stand:** 19. September 2026 (v5.4 Live)  
**Lead / Module:** `energy`, `billing`, `devices`  

---

## 🎯 1. System-Beschreibung & Regulatorischer Rahmen

Direkte, revisionssichere Kopplung von Sharegy an das BSI-zertifizierte **Smart Meter Gateway (SMGW)** über die **CLS-Schnittstelle (Controllable Local System)** nach BSI TR-03109-1 / FNN-Lastenheft Steuerbox.

### Regulatorischer Hintergrund (§ 14a EnWG & BNetzA BK6-22-300 / BK8-22/010-A):
* Verteilnetzbetreiber (VNB) in Deutschland sind berechtigt, steuerbare Verbrauchseinrichtungen (SteuVE: Wallboxen $\ge 4{,}2\,\text{kW}$, Wärmepumpen $\ge 4{,}2\,\text{kW}$, Batteriespeicher) bei lokaler Netzüberlastung vorübergehend auf einen Mindestbezug von $4{,}2\,\text{kW}$ zu dimmen.
* Die Dimm-Befehle werden vom VNB über das SMGW und den CLS-Kanal übertragen.
* Sharegy implementiert das **dynamische Summenleistungs-Modell**:
  $$P_{\text{allow}} = 4{,}2\,\text{kW} (\text{Netz}) + P_{\text{PV}} (\text{Erzeugung}) + P_{\text{Batt}} (\text{Entladung}) - P_{\text{Base}} (\text{Grundlast})$$
  Hierdurch wird Heizkomfort und Ladevorgang bei vorhandener lokaler Solarenergie trotz aktiver Netzdrosselung aufrechterhalten.

---

## 🏗️ 2. Architektur & Schnittstellen-Topologie

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

## 📊 3. Implementierte Kernkomponenten

| Komponente | Status | Implementierung im Code |
|---|:---:|---|
| **BSI TR-03109-1 CLS Ingest API** | 🟢 100% Live | `POST /api/energy/cls/signal/` in [energy/views_cls.py](file:///c:/Users/Public/Dev/sharegy/energy/views_cls.py) |
| **FNN Steuerbox Quittierung (Dispatch Acknowledgment)** | 🟢 100% Live | JSON-Quittung mit `dispatch_id`, `execution_timestamp_utc`, `steuve_allocation`, `power_budget` |
| **CLS Status & Telemetrie Endpoint** | 🟢 100% Live | `GET /api/energy/cls/status/` inkl. aktiver Signale und SteuVE-Drosselstatus |
| **Entwarnungs- & Freigabe-Endpunkt** | 🟢 100% Live | `POST /api/energy/cls/clear/` für Entwarnung und Freigabe aller SteuVE |
| **Revisionssicheres Audit-Log** | 🟢 100% Live | `EnWG14aDimmingAuditLog` protokolliert Soll/Ist-Werte, Reaktionszeit (<30s) und Compliance |
| **Automatisierte Test-Suite** | 🟢 100% Live | [energy/test_grid_dimming.py](file:///c:/Users/Public/Dev/sharegy/energy/test_grid_dimming.py) (`test_cls_smgw_api_lifecycle`) |

---

## 🔒 4. Revisionssicherheit & BNetzA-Audit-Trail

Jeder eingehende Steuerbefehl wird unveränderlich in der PostgreSQL/TimescaleDB Tabelle `EnWG14aDimmingAuditLog` protokolliert:
- **Timestamp (UTC)** mit Millisekunden-Präzision
- **Signal-UUID & Quittungs-Token**
- **VNB-Betriebsstelle / Marktpartner-ID**
- **Netzbezugs-Limit ($4{,}2\,\text{kW}$ bzw. individueller Wert)**
- **Reaktionszeit der Aktoren** (Soll: $< 30\,\text{s}$, Ist im Feld: $\approx 1{,}8\,\text{s}$)
