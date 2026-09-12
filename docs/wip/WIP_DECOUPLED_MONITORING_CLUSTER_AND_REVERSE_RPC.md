# 🛠️ [WIP] Entkoppelter Monitoring-Cluster & WSS Reverse-RPC Service (`mon.sharegy.de`)

**Status:** In Umsetzung / Architektur spezifiziert  
**Fortschritt:** 🟡 50 %  
**Priorität:** 🔴 Hoch (Ziel: Nächster Sprint / Q4 2026)  
**Lead / Modul:** `devices`, `consumers.py`, `routing.py`, `infra`  

---

## 🎯 1. Feature-Beschreibung & Zielsetzung

Physische und logische Ausgliederung der hochfrequenten IoT-Telemetrie und WSS-Verbindungen auf eine dedizierte Subdomain und Prozess-Schicht (`mon.sharegy.de`):
* **Keine Verbindungsabbrüche**: Portal-Deployments an `app.sharegy.de` trennen keine dauerhaft offenen Edge-Sockets.
* **Zero-Trust WSS Reverse-RPC**: Sichere, bidirektionale Wartung, Log-Extraktion und OTA-Konfiguration von Edge-Adaptern (ioBroker, Shelly, Home Assistant) hinter NAT/Firewalls.
* **Isolierter Blast-Radius**: Fehlverhalten von Edge-Geräten beeinflusst weder Kundenportal, Login noch Abrechnungssystem.

---

## 🏗️ 2. Architektur & Subdomain-Routing

```
                               ┌──────────────────────────────────────────────┐
                               │           DNS & INGRESS (NGINX/TRAEFIK)      │
                               └───────┬──────────────────────────────┬───────┘
                                       │                              │
                ┌──────────────────────▼───────┐      ┌───────────────▼────────────────────────┐
                │   app.sharegy.de (Portal)    │      │    mon.sharegy.de (Telemetrie/WSS)     │
                │   (Django WSGI / React)      │      │    (Django ASGI / Daphne Cluster)      │
                └──────────────┬───────────────┘      └────────────────┬───────────────────────┘
                               │                                       │
                               └───────────────► REDIS ◄───────────────┘
                                         (Channel Layer / Events)
```

---

## 📊 3. Aktueller Umsetzungsstand & Delta

| Komponente | Status | Implementiert im Code | Noch zu erledigen |
|---|:---:|---|---|
| **WSS-Ingest Channels** | 🟢 100% | `devices/consumers.py` & `consumers_ocpp.py` mit Deadband-Filter und Redis-Push. | Isolierter ASGI-Worker-Pool in Docker/Systemd. |
| **Partner-Diagnose API** | 🟢 100% | `/api/partner/diagnostics/<asset_id>/` und `PartnerDashboard.jsx`. | Asynchroner Redis-Event-Dispatch an aktive Sockets. |
| **Reverse-RPC Protokoll** | 🟡 40% | JSON-RPC 2.0 Payload-Spezifikation in [`DECOUPLED_MONITORING_AND_REMOTE_RPC_ARCHITECTURE.md`](file:///c:/Users/Public/Dev/eswes/docs/architecture/DECOUPLED_MONITORING_AND_REMOTE_RPC_ARCHITECTURE.md). | Client-seitige Unterstützung im offiziellen ioBroker-Adapter. |
| **DNS & SSL Setup** | 🟡 50% | Zertifikats-Konfiguration für `sharegy.de` Wildcard. | Nginx VHost für `mon.sharegy.de` mit Proxy-Buffering off. |

---

## 🚀 4. Nächste Umsetzungsschritte

1. **Sprint 1**: Nginx VHost-Konfiguration für `mon.sharegy.de` mit WebSocket-Upgrade Headern und separatem Upstream-Port.
2. **Sprint 2**: Implementierung des Reverse-RPC Event Handlers in `devices/consumers.py` (`edge.rpc.request` -> Socket -> `edge.rpc.response`).
3. **Sprint 3**: Release des ioBroker-Adapter Updates (`iobroker.sharegy v1.5`) mit Wartungs-Opt-In.
