# 🛠️ [WIP] EEBUS & Cloud Ecosystem Bridge (Wärmepumpen & Haushaltsgeräte)

**Status:** In Konzeption / Phase 1 & 2 in Vorbereitung  
**Fortschritt:** 🟡 45 %  
**Priorität:** 🔴 Hoch (Ziel: Q4 2026 / Q1 2027)  
**Lead / Modul:** `energy`, `devices`, `adapters`, `mon-nexus`  
**Referenz-Architektur:** [`DECOUPLED_MONITORING_AND_REMOTE_RPC_ARCHITECTURE.md`](file:///c:/Users/Public/Dev/eswes/docs/architecture/DECOUPLED_MONITORING_AND_REMOTE_RPC_ARCHITECTURE.md)  

---

## 🎯 1. Feature-Beschreibung & Zielsetzung

Anbindung von steuerbaren Großverbrauchern — insbesondere **Wärmepumpen** (Vaillant, Viessmann, Bosch, Daikin, Stiebel Eltron) und **Smart-Home-Großgeräten** (BSH Home Connect: Bosch, Siemens, Neff) — über das standardisierte offene Kommunikationsprotokoll **EEBUS** (SHIP / SPINE) und herstellerspezifische Cloud-APIs.

### Kernziele:
* **§ 14a EnWG Konformität**: Netzdienliches Dimmen der Wärmepumpe auf maximal $4{,}2\,\text{kW}$ bei Netzüberlastung über die CLS-Schnittstelle des Smart Meter Gateways (SMGW).
* **Dynamische thermische Speicherung**: Erhöhung der Warmwasser- und Vorlauftemperatur ($+3\,^\circ\text{C}$ bis $+5\,^\circ\text{C}$) bei PV-Überschuss oder negativen Börsenstrompreisen.
* **Automatisierter Spül- & Waschmaschinen-Start**: Startfreigabe erst, wenn günstige PV- oder Börsenstrom-Energie zur Verfügung steht.

---

## 🏗️ 2. Architektur: Hybrid Cloud & Lokaler EEBUS Bridge Daemon

```
                        ┌────────────────────────────────────────────────────────┐
                        │             Sharegy EMS Optimizer ("Brain")            │
                        │       (§ 14a EnWG Dimmung, PV-Überschuss, Börsenpreis) │
                        └───────────────────────────┬────────────────────────────┘
                                                    │
                                                    ▼
                        ┌────────────────────────────────────────────────────────┐
                        │            mon.sharegy.de Gateway ("Carrier")          │
                        │               (Zero-Trust WSS Reverse-RPC)             │
                        └───────────────────────────┬────────────────────────────┘
                                                    │
                 ┌──────────────────────────────────┴──────────────────────────────────┐
                 │                                                                     │
                 ▼ (Phase 1: Cloud-to-Cloud Bridge)                                    ▼ (Phase 2: Lokale EEBUS Bridge)
   ┌───────────────────────────┐                                         ┌───────────────────────────┐
   │  Hersteller Cloud APIs    │                                         │   Sharegy EEBUS Daemon    │
   │  • myVAILLANT API         │                                         │   (Apache 2.0 / eebus-go) │
   │  • ViCare Developer API   │                                         │   (SHIP/SPINE, mDNS, TLS) │
   │  • Home Connect REST API  │                                         └─────────────┬─────────────┘
   └─────────────┬─────────────┘                                                       │
                 │                                                                     │
                 ▼                                                                     ▼
   ┌───────────────────────────┐                                         ┌───────────────────────────┐
   │  Cloud-integrierte Geräte │                                         │  Lokale EEBUS Geräte      │
   │  (Wärmepumpen / Kitchen)  │                                         │  (Wärmepumpe / SMGW CLS)  │
   └───────────────────────────┘                                         └───────────────────────────┘
```

---

## ⚖️ 3. Lizenz- & Technologie-Strategie für EEBUS

* **Keine GPL-Abhängigkeit:** Umgehung von Home Assistant Core GPL-Restriktionen für kommerzielle / White-Label-Installationen.
* **Apache 2.0 Referenz-Stack:** Nutzung des etablierten und zertifizierten `eebus-go` Stacks (entwickelt von der EEBus-Initiative / EVCC) als eigenständiger, schlanker Microservice-Daemon.
* **ioBroker-Kompatibilität (MIT):** Der lokale EEBUS-Daemon kann direkt mit dem `iobroker.sharegy`-Adapter kommunizieren.

---

## 📊 4. Aktueller Umsetzungsstand & Delta

| Komponente | Status | Implementiert im Code | Noch zu erledigen |
|---|:---:|---|---|
| **Datenmodell** | 🟢 100% | `DeviceConfig.energy_signal_type`, `MetricDefinition` (Vorlauf, Rücklauf, Durchfluss). | Erweiterung um `Device` Rollen `heat_pump_eebus` & `appliance_homeconnect`. |
| **Aktorik-Logik (Brain)** | 🟢 100% | SG-Ready Relais-Steuerung mit Anti-Cycling Verdichterschutz in `energy/flow_engine.py`. | Unterstützung feingranularer Sollwertanhebung via API ($^\circ\text{C}$). |
| **Phase 1: Cloud APIs** | 🟡 30% | Auth-Token-Verwaltung in `integrations/`. | REST-Clients für *Home Connect API* und *myVAILLANT API*. |
| **Phase 2: Native EEBUS Daemon** | 🟡 30% | Apache 2.0 Architektur & Reverse-RPC Protokoll definiert. | Build des headless `eebus-bridge` Daemons mit SHIP/SPINE Binding. |

---

## 🚀 5. Nächste Umsetzungsschritte

1. **Sprint 1**: Implementierung des `HomeConnectOAuthAdapter` für Geschirrspüler und Waschmaschinen (Abruf von `BSH.Common.Status.OperationState` & Remote-Start).
2. **Sprint 2**: Implementierung der `myVAILLANT` Cloud-Bridge zur Sollwertanpassung und Warmwasser-Schnellladung.
3. **Sprint 3**: Bereitstellung des schlanken `eebus-bridge` Docker-Images (Apache 2.0) für § 14a EnWG Dimmung.
4. **Sprint 4**: Integration in den Dispatch Hub (`/app/control`) mit Live-Statusanzeige und Schieberegler für thermische Pufferung.
