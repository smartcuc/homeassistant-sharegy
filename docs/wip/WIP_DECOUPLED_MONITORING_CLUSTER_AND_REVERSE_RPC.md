# 🛠️ [WIP] Entkoppelter Monitoring-Cluster, Dual-Socket WSS & In-Flight DB-Backup

**Status:** In Umsetzung / Architektur spezifiziert (v2.0 Dual-Plane & Backup Vault)  
**Fortschritt:** 🟡 55 %  
**Priorität:** 🔴 Hoch (Ziel: Q4 2026)  
**Plattformen:** Sharegy (Energy HEMS SaaS) & Factofy (Industrial IoT SaaS)  
**Spezifikations-Dokument:** [`DECOUPLED_MONITORING_AND_REMOTE_RPC_ARCHITECTURE.md`](file:///c:/Users/Public/Dev/eswes/docs/architecture/DECOUPLED_MONITORING_AND_REMOTE_RPC_ARCHITECTURE.md)  

---

## 🎯 1. Feature-Beschreibung & Zielsetzung

Strikte Trennung von **Business Data Plane** (Fachapplikationen mit eigenen DBs) und **Control Plane / Flotten-Monitoring** (zentraler Admin- & Backup-Knoten):
* **Dual-Socket Edge-Architektur:** Edge-Geräte (ioBroker / Factofy IPC) besitzen einen getrennten Daten-Socket (für Messwerte) und einen Admin-Socket (für Health-Heartbeats und Zero-Trust Reverse-RPC).
* **Zero-Trust Reverse-RPC:** Wartung, Log-Extraktion und Neustart von Edge-Adaptern hinter Firewalls/NAT ohne offene Ports oder VPN.
* **In-Flight Continuous Database Backup:** Alle 5 Minuten automatisches, verschlüsseltes Delta-Backup der PostgreSQL-Produktionsdatenbanken (Sharegy & Factofy) in den isolierten Monitoring-Tresor.
* **Maximale Ausfallsicherheit:** Deployments und Wartungsarbeiten an den Fachportalen (`app.sharegy.de`, `app.factofy.io`) trennen niemals die Flotten-Verbindungen.

---

## 🏗️ 2. Architektur & Subdomain-Routing

```
                        ┌────────────────────────────────────────────────────────┐
                        │         EDGE-GERÄT (z. B. ioBroker / Factofy IPC)      │
                        └───────────┬────────────────────────────────┬───────────┘
                                    │                                │
               [ 1. BUSINESS DATA PLANE ]               [ 2. CONTROL & ADMIN PLANE ]
               Reine Nutz- & Messdaten                  Flotten-Management & Fernwartung
                                    │                                │
                   WSS / HTTPS      │               WSS (Admin)      │
             (Messwerte, Zähler,    │             (Heartbeat, Logs,  │
              Leistung, Energie)    │              Reverse-RPC, OTA) │
                                    │                                │
                                    ▼                                ▼
     ┌──────────────────────────────────────────┐    ┌──────────────────────────────────────────┐
     │             SHAREGY APPLIKATION          │    │         ZENTRALES MONITORING & ADMIN     │
     │             (app.sharegy.de)             │    │         (mon.sharegy.de / mon.factofy)   │
     ├──────────────────────────────────────────┤    ├──────────────────────────────────────────┤
     │ • Eigene Datenbank: sharegy_prod_db      │    │ • Eigene Datenbank: mon_core_db          │
     │ • Abrechnung, § 42b EnWG, Mieterportal   │    │ • Flottenstatus (CPU, RAM, Uptime, FW)   │
     │ • Dynamische Stromtarife, EMS            │    │ • Zero-Trust Remote-RPC Tunnel           │
     │ • Port 8000 (Gunicorn WSGI)              │    │ • Port 8001 (Daphne ASGI Cluster)        │
     └────────────────────┬─────────────────────┘    └────────────────────▲─────────────────────┘
                          │                                               │
                          │   5-Minuten In-Flight Delta-Backup            │
                          └───────────────────────────────────────────────┤
                                                                          │
                             [ FACTOFY DATA PLANE ]                       │
                           ┌─────────────────────────┐                    │
                           │   FACTOFY APPLIKATION   │                    │
                           │   (app.factofy.io)      │────────────────────┘
                           ├─────────────────────────┤  5-Minuten In-Flight
                           │ • Eigene DB: factofy_db │  Delta-Backup
                           │ • Maschinen-OEE, Takt   │
                           └─────────────────────────┘
```

---

## 📊 3. Aktueller Umsetzungsstand & Delta

| Komponente | Status | Implementiert im Code | Noch zu erledigen |
|---|:---:|---|---|
| **WSS-Ingest Channels (Data Plane)** | 🟢 100% | `devices/consumers.py` & `consumers_ocpp.py` mit Deadband-Filter und Redis-Push. | Isolierter ASGI-Worker-Pool in Docker/Systemd. |
| **Partner-Diagnose API** | 🟢 100% | `/api/partner/diagnostics/<asset_id>/` und `PartnerDashboard.jsx`. | Asynchroner Server-to-Server RPC-Dispatch an `mon.sharegy.de`. |
| **Reverse-RPC Protokoll (JSON-RPC 2.0)** | 🟡 60% | Vollständige Spezifikation in [`DECOUPLED_MONITORING_AND_REMOTE_RPC_ARCHITECTURE.md`](file:///c:/Users/Public/Dev/eswes/docs/architecture/DECOUPLED_MONITORING_AND_REMOTE_RPC_ARCHITECTURE.md). | Client-seitige Unterstützung im offiziellen ioBroker-Adapter. |
| **In-Flight 5-Minuten DB-Backup Vault** | 🟡 40% | Konzept & RPO < 5 Min. Replikations-Architektur dokumentiert. | PostgreSQL WAL-Archivierungs-Skript & Dashboard-Status-Widget. |
| **DNS & SSL Setup** | 🟡 50% | Zertifikats-Konfiguration für `sharegy.de` & `factofy.io` Wildcards. | Nginx VHost für `mon.sharegy.de` mit Proxy-Buffering off. |

---

## 🚀 4. Nächste Umsetzungsschritte

1. **Sprint 1 (Ingress & DNS):** Nginx VHost-Konfiguration für `mon.sharegy.de` mit isoliertem ASGI Upstream-Port (8001).
2. **Sprint 2 (WSS Reverse-RPC):** Implementierung des bidirektionalen JSON-RPC Handlers in `devices/consumers.py` (`edge.rpc.request` -> Socket -> `edge.rpc.response`).
3. **Sprint 3 (Edge Client SDK & ioBroker):** Release des ioBroker-Adapter Updates (`iobroker.sharegy v1.5`) mit Dual-Socket-Unterstützung (Data + Admin).
4. **Sprint 4 (In-Flight Backup Engine):** Automatisierter 5-Minuten WAL-Delta Backup Sync von PostgreSQL in das Monitoring-SaaS.
