# 🛡️ Cloudflare Infrastruktur, Edge-Caching & DNS-Setup

**Status:** 🟢 100 % Abgeschlossen & Live  
**Live-Schaltung:** 13. September 2026  
**Zonen:** `sharegy.de` (Free Tier Anycast Edge), `smartevo.de` (Pro Plan)  
**Lead / Modul:** `infra`, `security`, `operations`  

---

## 🎯 1. Übersicht & Architektur

Die gesamte Web-, API- und Frontend-Infrastruktur von **Sharegy** (`sharegy.de`) wird über das globale Anycast-Netzwerk von Cloudflare betrieben. Dies entlastet das Backend um ~95 %, schützt vor DDoS- und Bot-Angriffen und liefert Frontend-Assets mit sub-10ms Latenz in der gesamten DACH-Region aus.

```
[Endnutzer / Mobile App / Partner]
                │
                ▼ (HTTPS / HTTP3 / TLS 1.3)
┌─────────────────────────────────────────────────────────────┐
│                   CLOUDFLARE ANYCAST EDGE                   │
├─────────────────────────────────────────────────────────────┤
│ 1. Universal SSL (Full Strict)                              │
│ 2. Always Use HTTPS & Automatic HTTPS Rewrites              │
│ 3. 3x Aktive Edge Cache Rules:                              │
│    • /assets/*  ➔ Cache Everything (1 Monat Edge & Browser) │
│    • /api/*     ➔ Bypass Cache                              │
│    • /ws/*      ➔ Bypass Cache & WebSocket Stream           │
└──────────────────────────────┬──────────────────────────────┘
                               │
            ┌──────────────────┴──────────────────┐
            ▼ (HTTPS Proxy)                       ▼ (Reine DNS-Auflösung)
┌──────────────────────────────────────┐  ┌───────────────────────────────────┐
│        Sharegy Web & API             │  │         Direkte Services          │
│ • IP: 172.160.240.172                │  │ • mail.sharegy.de (IMAP/SMTP)     │
│ • sharegy.de, api.sharegy.de         │  │ • mqtt.sharegy.de (MQTTS Port 8883)│
│ • Nginx Reverse Proxy + Gunicorn     │  │ • cpanel, ftp, webmail (Nur DNS)  │
└──────────────────────────────────────┘  └───────────────────────────────────┘
```

---

## 📋 2. DNS-Konfigurationstabelle (`sharegy.de`)

| Hostname | Typ | Ziel / Wert | Proxy-Status | Zweck |
|---|:---:|---|:---:|---|
| **`sharegy.de`** | `A` | `172.160.240.172` | 🟠 **Mit Proxy** | Haupt-Frontend & Webanwendung |
| **`api.sharegy.de`** | `A` | `172.160.240.172` | 🟠 **Mit Proxy** | Django REST API Endpunkte |
| **`www.sharegy.de`** | `CNAME` | `sharegy.de` | 🟠 **Mit Proxy** | Web-Weiterleitung auf Apex |
| **`demo.sharegy.de`** | `CNAME` | `sharegy.de` | 🟠 **Mit Proxy** | Demo-Portal (Weiterleitung auf `/demo`) |
| **`mqtt.sharegy.de`** | `A` | `172.160.240.172` | 🔘 **Nur DNS** | **MQTTS Broker** (Port 8883 / TLS für Gateways & Sensoren) |
| **`mail.sharegy.de`** | `A` | `192.250.229.161` | 🔘 **Nur DNS** | Mailserver (IMAP 993, SMTP 465/587) |
| **`ftp.sharegy.de`** | `CNAME` | `sharegy.de` | 🔘 **Nur DNS** | FTP-Zugang (Port 21) |
| **`cpanel`, `whm`, `webmail`** | `A` | `192.250.229.161` | 🔘 **Nur DNS** | Server-Verwaltungstools |
| **`sharegy.de`** | `MX` | `mail.sharegy.de` (Prio 0) | 🔘 **Nur DNS** | E-Mail-Routing |
| **`default._domainkey`** | `TXT` | *DKIM Public Key* | 🔘 **Nur DNS** | E-Mail DKIM Signatur |
| **`_dmarc`** | `TXT` | `v=DMARC1; p=none;` | 🔘 **Nur DNS** | DMARC Richtlinie |
| **`sharegy.de`** | `TXT` | `v=spf1 +a +mx ... ~all` | 🔘 **Nur DNS** | SPF E-Mail-Absenderschutz |

---

## 🔒 3. SSL/TLS & Sicherheitseinstellungen

* **Verschlüsselungsmodus**: **Vollständig (strikt) / Full (Strict)**
  * *Zertifikatsvalidierung*: Vollständige CA-Prüfung zwischen Cloudflare Edge und dem Ursprungsserver (`172.160.240.172`).
* **Edge-Zertifikate**:
  * Hostnames: `*.sharegy.de`, `sharegy.de`
  * Typ: Universal SSL (Automatisch verwaltet & verlängert)
  * **Immer HTTPS verwenden**: 🟢 Aktiv (HTTP $\rightarrow$ HTTPS 301 Redirect)
  * **TLS-Mindestversion**: `TLS 1.2`
  * **TLS 1.3**: 🟢 Aktiv (0-RTT Handshake für Mobilfunk/Apps)
  * **Automatische HTTPS-Rewrites**: 🟢 Aktiv

---

## ⚡ 4. Aktive Cache Rules (Edge Caching)

In Cloudflare unter *Caching $\rightarrow$ Cache Rules* sind 3 Regeln in exakter Priorität aktiv:

1. **`Cache Frontend Assets`**
   * *Bedingung*: `URI-Pfad beginnt mit /assets/`
   * *Aktion*: **Eligible for cache**, Edge TTL: `1 month`, Browser TTL: `1 month`
   * *Nutzen*: Statische Bundles (JS, CSS, Icons, Fonts) werden zu 100 % aus dem Edge-RAM ausgeliefert.
2. **`Bypass API`**
   * *Bedingung*: `URI-Pfad beginnt mit /api/`
   * *Aktion*: **Bypass cache**
   * *Nutzen*: Echtzeit-Telemetrie und Authentifizierung gehen immer direkt an Django.
3. **`Bypass WebSockets`**
   * *Bedingung*: `URI-Pfad beginnt mit /ws/`
   * *Aktion*: **Bypass cache**, WebSockets enabled
   * *Nutzen*: Ununterbrochener Live-Stream für Daphne/Channels.

---

## 🌐 5. Netzwerk & WebSockets

* **WebSockets**: 🟢 **Aktiv** (Zwingend erforderlich für Daphne Channels Live-Daten)
* **HTTP/3 (QUIC)**: 🟢 **Aktiv** (Schnellste Verbindung für Android/iOS Apps)
* **IP-Geolokation**: 🟢 **Aktiv** (Übergibt `CF-IPCountry` für automatische Sprache & Netztarife)
* **Max. Upload-Größe**: `100 MB`
