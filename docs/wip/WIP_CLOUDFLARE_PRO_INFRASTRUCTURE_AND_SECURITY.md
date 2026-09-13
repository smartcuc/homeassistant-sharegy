# 🛡️ [WIP] Cloudflare Pro Integration, Edge Caching & API Security

**Status:** In Konzeption / Vorbereitung  
**Fortschritt:** 🟡 20 %  
**Priorität:** 🔴 Hoch (Ziel: Q4 2026 / Go-To-Market)  
**Lead / Modul:** `infra`, `security`, `frontend`, `api`  

---

## 🎯 1. Feature-Beschreibung & Zielsetzung

Integration der bestehenden **Cloudflare Pro Lizenz** in das Sharegy-Ökosystem (`sharegy.de`, `mon.sharegy.de`, Whitelabel-Domains). 
Ziel ist es, das Backend maximal zu entlasten, Ladezeiten für Web & native Apps (Android/iOS) durch Edge-Caching drastisch zu senken und die API sowie Auth-Endpunkte mit Enterprise-Sicherheitsregeln abzusichern.

### Kernziele:
* **Edge-Performance & Caching**: Auslieferung aller statischen Frontend-Assets (`/assets/*`), Grafiken und Fonts direkt aus dem Cloudflare-CDN (DACH/Europa Edge) mit 0 ms Backend-Last.
* **API & Magic-Link Schutz**: WAF & Super Bot Fight Mode zum Schutz der Authentifizierungsendpunkte (`/api/request-magic-link/`, `/api/magic-login/`) vor Brute-Force, Scrapern und E-Mail-Spam-Attacken.
* **WebSocket & Live-Telemetrie Stabilität**: Persistente, langlebige WebSocket-Verbindungen für Daphne/Channels (`/ws/telemetry/...`) mit automatischer TLS-Terminierung und HTTP/3 Priorisierung.
* **Whitelabel SSL via Cloudflare for SaaS**: Bereitstellung von Edge-SSL-Zertifikaten für Partner-Domains (`portal.stadtwerke-xyz.de`) per CNAME ohne manuelle Serverzertifikate.

---

## 🏗️ 2. Geplante Architektur & Traffic-Routing

```
[Nutzer (App / Browser / Partner)]
                 │
                 ▼ (HTTPS / HTTP3 / WSS)
┌─────────────────────────────────────────────────────────────┐
│                   CLOUDFLARE PRO EDGE                       │
├─────────────────────────────────────────────────────────────┤
│ 1. Managed WAF & OWASP Ruleset                              │
│ 2. Super Bot Fight Mode (Rate Limiting für /api/auth/*)     │
│ 3. Polish & Mirage (Verlustfreie WebP/AVIF-Kompression)    │
│ 4. Page Rules / Cache Rules:                                │
│    • /assets/*      ➔ Cache Everything (TTL: 1 Monat)       │
│    • /api/*         ➔ Bypass Cache                          │
│    • /ws/*          ➔ WebSocket Proxy (Bypass Cache)        │
└──────────────────────────────┬──────────────────────────────┘
                               │
            ┌──────────────────┴──────────────────┐
            ▼ (Proxy mit CF-Connecting-IP)        ▼ (WSS Stream)
┌──────────────────────────────────────┐  ┌───────────────────────────────────┐
│     Nginx / Gunicorn (Django API)    │  │    Daphne / Channels (WebSockets) │
│ • SECURE_PROXY_SSL_HEADER            │  │ • Live Flow & Telemetrie-Stream   │
│ • django-ratelimit mit realer IP     │  │ • Heartbeat & Reconnect Guards    │
└──────────────────────────────────────┘  └───────────────────────────────────┘
```

---

## 📋 3. Konfigurations-Blueprint

### A. Cloudflare Cache Rules (Zero-Backend-Load für Frontend)
1. **Regel 1: Static Assets**
   * *Match*: `(http.host eq "sharegy.de" and http.request.uri.path starts_with "/assets/")`
   * *Action*: **Cache Level: Cache Everything**, Edge Cache TTL: `1 month`, Browser TTL: `1 month`.
2. **Regel 2: Dynamic API & Auth**
   * *Match*: `(http.request.uri.path starts_with "/api/")`
   * *Action*: **Bypass Cache**, Polish: Off.
3. **Regel 3: WebSocket Stream**
   * *Match*: `(http.request.uri.path starts_with "/ws/")`
   * *Action*: **Bypass Cache**, WebSockets: Enabled.

### B. Cloudflare WAF & Security Rules
* **Super Bot Fight Mode**: Automatische Challenge für böswillige Bots und automatisierte Skripte.
* **Rate Limiting Rule**:
  * Pfad: `/api/request-magic-link/`
  * Schwelle: Max. 5 Requests pro 5 Minuten pro IP-Adresse $\rightarrow$ Managed Challenge / Block.
* **OWASP Managed Core Ruleset**: Paranoia Level 1 (Schutz vor SQL-Injection, XSS, RCE).

### C. Backend-Anpassung (`settings.py` & Nginx)
* **Real IP Forwarding**:
  ```python
  # Django settings.py
  SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
  USE_X_FORWARDED_HOST = True
  USE_X_FORWARDED_PORT = True
  ```
* **Nginx Real-IP Konfiguration**:
  ```nginx
  # Trust Cloudflare IPv4 & IPv6 Ranges
  set_real_ip_from 173.245.48.0/20;
  set_real_ip_from 103.21.244.0/22;
  set_real_ip_from 103.22.200.0/22;
  set_real_ip_from 103.31.4.0/22;
  set_real_ip_from 141.101.64.0/18;
  set_real_ip_from 108.162.192.0/18;
  set_real_ip_from 190.93.240.0/20;
  set_real_ip_from 188.114.96.0/20;
  set_real_ip_from 197.234.240.0/22;
  set_real_ip_from 198.41.128.0/17;
  set_real_ip_from 162.158.0.0/15;
  set_real_ip_from 104.16.0.0/13;
  set_real_ip_from 104.24.0.0/14;
  set_real_ip_from 172.64.0.0/13;
  set_real_ip_from 131.0.72.0/22;
  real_ip_header CF-Connecting-IP;
  ```

---

## 📊 4. Meilensteine & Roadmap

| Phase | Aufgabenbereich | Status | Ziel-Termin |
|---|---|:---:|---|
| **Phase 1** | DNS-Delegation & Domain-Setup in Cloudflare Pro | ⚪ Ausstehend | Sprint 1 (Q4 2026) |
| **Phase 2** | Konfiguration der 3 Cache Rules & WAF Rate Limiting | ⚪ Ausstehend | Sprint 1 (Q4 2026) |
| **Phase 3** | Nginx `real_ip_header CF-Connecting-IP` & Django Headers | ⚪ Ausstehend | Sprint 2 (Q4 2026) |
| **Phase 4** | WebSocket-Stresstest über Cloudflare Edge Proxy | ⚪ Ausstehend | Sprint 2 (Q4 2026) |
| **Phase 5** | Evaluierung von Cloudflare for SaaS für Whitelabel CNAMEs | ⚪ Ausstehend | Q1 2027 |
