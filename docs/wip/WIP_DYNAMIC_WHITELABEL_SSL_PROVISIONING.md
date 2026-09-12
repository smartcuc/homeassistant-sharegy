# 🛠️ [WIP] Dynamische Whitelabel SSL-Provisionierung für Custom Domains (CNAME)

**Status:** In Umsetzung / Basis implementiert  
**Fortschritt:** 🟡 70 %  
**Priorität:** 🟡 Mittel (Ziel: Q4 2026)  
**Lead / Modul:** `core`, `infra`, `theming`  

---

## 🎯 1. Feature-Beschreibung & Zielsetzung

Vollautomatisierte Ausstellung und Verlängerung von **Let's Encrypt SSL-Zertifikaten (TLS)** für B2B-Kunden, die ihr eigenes Energieportal unter einer eigenen Firmen-Subdomain betreiben möchten (z. B. `portal.stadtwerke-sonnenstadt.de` per CNAME auf `cname.sharegy.de`).

### Anforderungen:
* **Zero-Touch Onboarding**: Der Stadtwerke-Administrator trägt seine Domain im Whitelabel-Modal ein und setzt den CNAME bei seinem Domain-Registrar.
* **On-Demand TLS**: Das SSL-Zertifikat wird beim ersten HTTPS-Aufruf vollautomatisch via ACME / Let's Encrypt ausgestellt.
* **Sicherheit & Domain-Validation**: Zertifikate werden nur für Domains ausgestellt, die aktiv einem verifizierten `Tenant` in der Datenbank zugeordnet sind.

---

## 🏗️ 2. Architektur & ACME Ingress Proxy

```
[Kunde im Browser: https://portal.stadtwerke-koeln.de]
                         │
                         │ (CNAME auf cname.sharegy.de)
                         ▼
┌─────────────────────────────────────────────────────────────┐
│          Traefik / Caddy Ingress Proxy                      │
├─────────────────────────────────────────────────────────────┤
│ 1. On-Demand TLS Handshake (SNI: portal.stadtwerke-koeln.de)│
│ 2. Webhook an Sharegy Core: "Ist diese Domain freigegeben?" │
│ 3. Automatische ACME Challenge & Zertifikat-Ausstellung     │
└──────────────────────────────┬──────────────────────────────┘
                               │
                               ▼
┌─────────────────────────────────────────────────────────────┐
│          Sharegy Web App & Theming Engine                   │
│ • Domain-Lookup via /api/core/tenant/by-domain/             │
│ • Live-Injektion der Stadtwerke-Farben & Logo               │
└─────────────────────────────────────────────────────────────┘
```

---

## 📊 3. Aktueller Umsetzungsstand & Delta

| Komponente | Status | Implementiert im Code | Noch zu erledigen |
|---|:---:|---|---|
| **Datenmodell & APIs** | 🟢 100% | `Tenant.custom_domain`, `Tenant.is_whitelabel_active` und `/api/core/tenant/by-domain/`. | Webhook-Endpunkt zur Domain-Autorisierung für den Ingress. |
| **Dynamic Theming UI** | 🟢 100% | [`WhitelabelSettingsModal.jsx`](file:///c:/Users/Public/Dev/eswes/frontend/src/features/tenant/components/WhitelabelSettingsModal.jsx) mit CNAME-Anleitung. | DNS-Status-Badge (🟢 CNAME aktiv / 🔴 DNS nicht aufgelöst). |
| **Automatischer ACME Proxy** | 🟡 30% | Nginx Ingress für Wildcard-Domains. | Caddy / Traefik On-Demand TLS Konfiguration mit `ask` URL. |

---

## 🚀 4. Nächste Umsetzungsschritte

1. **Sprint 1**: Bereitstellung des Autorisierungs-Endpunkts `GET /api/core/tenant/verify-cname/?domain=...` für Caddy/Traefik `on_demand_tls`.
2. **Sprint 2**: Bereitstellung der Caddy Reverse-Proxy Konfiguration auf dem Produktivserver.
3. **Sprint 3**: Live-DNS-Verifikationsprüfung im Whitelabel-Modal im Frontend.
