# 🛡️ Cloudflare Multi-Domain Setup & Hardening Runbook

**Gültig für alle Domains:** `smartevo.de` (Pro), `sharegy.de`, `factofy.de`, `valofy.de`, `moniy.de`  
**Letzte Aktualisierung:** 17. September 2026  
**Status:** 🟢 Produktiv-Standard (BSI / RFC 9116 / M365 Enterprise)

---

## 🧭 Inhaltsverzeichnis & Schnell-Checkliste

1. [DNS & Domain-Sicherheit (DNSSEC, SPF, DKIM, DMARC, CAA)](#1-dns--domain-sicherheit)
2. [SSL/TLS & Verschlüsselung (Full Strict, HSTS, TLS 1.3)](#2-ssltls--verschl%C3%BCsselung)
3. [Performance & Speed (HTTP/3, 0-RTT, Brotli, Early Hints)](#3-performance--speed)
4. [WAF, Bot-Schutz & Rate Limiting](#4-waf-bot-schutz--rate-limiting)
5. [Transform Rules: Automatische Security-Header](#5-transform-rules-automatische-security-header)
6. [Caching & Edge Rules (Statische Assets vs. APIs)](#6-caching--edge-rules)
7. [Domain-spezifische Matrix](#7-domain-spezifische-matrix)

---

## 1. DNS & Domain-Sicherheit

### A. DNSSEC (Kryptografische Signatur der DNS-Zone)
* **Pfad im Dashboard:** `DNS` ➔ `Settings` ➔ **DNSSEC aktivieren**
* **Aktion:** Klicke auf *Enable DNSSEC*. Cloudflare generiert den **DS-Record** (Key Tag, Algorithm, Digest).
* **Registrar:** Trage diesen DS-Record bei deinem Domain-Registrar (z.B. INWX, Hetzner, Strato, Cloudflare Registrar) ein.
* **Nutzen:** Schützt vor DNS-Hijacking und gefälschten IP-Umleitungen.

---

### B. E-Mail-Authentifizierung (Microsoft 365 Standard)

Für jede Domain, die über Microsoft 365 sendet/empfängt:

```dns
# 1. SPF (TXT auf Apex @):
v=spf1 include:spf.protection.outlook.com -all

# 2. DMARC (TXT auf _dmarc):
v=DMARC1; p=reject; sp=reject; adkim=s; aspf=s; rua=mailto:c475189356a54d618a3c8ca0d9d108bc@dmarc-reports.cloudflare.net

# 3. DKIM (2x CNAME auf selector1._domainkey und selector2._domainkey):
selector1._domainkey  CNAME  selector1-<domain-prefix>._domainkey.<tenant>.onmicrosoft.com
selector2._domainkey  CNAME  selector2-<domain-prefix>._domainkey.<tenant>.onmicrosoft.com

# 4. MX Record:
@  MX  <domain-prefix>.mail.protection.outlook.com (Priorität 0 oder 10)
```

---

### C. CAA Records (Certification Authority Authorization)
Verhindert, dass unbefugte Dritte SSL-Zertifikate für eure Domains ausstellen lassen.

* **Pfad im Dashboard:** `DNS` ➔ `Records` ➔ `Add record`
* **Einträge:**
  ```dns
  Typ: CAA | Name: @ | Tag: Only allow specific CAs to issue certs (issue) | Value: "cloudflare.com"
  Typ: CAA | Name: @ | Tag: Only allow specific CAs to issue certs (issue) | Value: "letsencrypt.org"
  Typ: CAA | Name: @ | Tag: Only allow specific CAs to issue certs (issue) | Value: "digicert.com"
  Typ: CAA | Name: @ | Tag: Send violation reports to URL (iodef)           | Value: "mailto:security@smartevo.de"
  ```

---

## 2. SSL/TLS & Verschlüsselung

### A. Verschlüsselungsmodus: „Full (Strict)“
* **Pfad:** `SSL/TLS` ➔ `Overview`
* **Einstellung:** **Full (Strict)** *(Vollständig strikt)*
* **Warum:** Nur hier wird das SSL-Zertifikat des Ursprungsservers echt validiert.

### B. HSTS (HTTP Strict Transport Security)
* **Pfad:** `SSL/TLS` ➔ `Edge Certificates` ➔ `HTTP Strict Transport Security (HSTS)`
* **Einstellungen:**
  * **Enable HSTS:** 🟢 On
  * **Max-Age:** `1 year (31536000)`
  * **Apply to subdomains:** 🟢 On
  * **Preload:** 🟢 On
  * **No-Sniff:** 🟢 On

### C. Mindest-TLS-Version & Moderne Protokolle
* **Pfad:** `SSL/TLS` ➔ `Edge Certificates`
* **Always Use HTTPS:** 🟢 On
* **Minimum TLS Version:** `TLS 1.2` (oder `TLS 1.3`)
* **Opportunistic Encryption:** 🟢 On
* **TLS 1.3:** 🟢 On
* **Automatic HTTPS Rewrites:** 🟢 On

---

## 3. Performance & Speed

* **Pfad:** `Speed` ➔ `Optimization`

| Feature | Einstellung | Nutzen |
| :--- | :---: | :--- |
| **HTTP/3 (with QUIC)** | 🟢 **On** | Drastisch schnellere Latenz bei mobilen Netzen (PWA/App). |
| **0-RTT Connection Resumption** | 🟢 **On** | Wiederkehrende Verbindungen starten ohne Handshake-Verzögerung. |
| **Brotli** | 🟢 **On** | Bis zu 20% bessere JS/CSS-Kompression gegenüber Standard-Gzip. |
| **Early Hints (103)** | 🟢 **On** | Sendet CSS/Font-Links im HTTP 103 Status vor dem HTML-Rendering. |
| **Auto Minify** | 🟢 **HTML, CSS, JS** | Entfernt überflüssige Leerzeichen & Kommentare an der Edge. |

---

## 4. WAF, Bot-Schutz & Rate Limiting

### A. Bot Fight Mode (Kostenlos)
* **Pfad:** `Security` ➔ `Bots` ➔ **Bot Fight Mode: On**
* Schützt automatisch vor Credential-Stuffing, Content-Scraping und bösartigen Crawlern.

---

### B. Empfohlene Rate-Limiting-Regeln (`Security` ➔ `WAF` ➔ `Rate limiting rules`)

#### 1. Schutz für Authentifizierung & Magic Links (Sharegy / Factofy / Moniy)
* **Rule Name:** `Protect Auth Endpoints`
* **When incoming requests match:**
  ```text
  (http.request.uri.path starts_with "/api/v1/auth/") or 
  (http.request.uri.path starts_with "/api/auth/")
  ```
* **Rate:** Maximal **5 Anfragen pro 10 Minuten pro IP**
* **Action:** `Block` oder `Managed Challenge`

#### 2. Schutz für Kontakt- und Lead-Formulare (smartEvo)
* **Rule Name:** `Protect Contact Forms`
* **When incoming requests match:**
  ```text
  http.request.uri.path eq "/api/contact"
  ```
* **Rate:** Maximal **3 Anfragen pro 5 Minuten pro IP**
* **Action:** `Managed Challenge` (Cloudflare Turnstile)

---

## 5. Transform Rules: Automatische Security-Header

* **Pfad:** `Rules` ➔ `Transform Rules` ➔ `Modify Response Header` ➔ **Create Rule**
* **Rule Name:** `Security Headers (RFC & BSI Standard)`
* **If incoming requests match:** `All incoming requests`
* **Headers to Modify:**

| Action | Header Name | Value |
| :--- | :--- | :--- |
| **Set static** | `X-Frame-Options` | `SAMEORIGIN` |
| **Set static** | `X-Content-Type-Options` | `nosniff` |
| **Set static** | `Referrer-Policy` | `strict-origin-when-cross-origin` |
| **Set static** | `Permissions-Policy` | `camera=(), microphone=(), geolocation=(self)` |
| **Set static** | `X-XSS-Protection` | `1; mode=block` |

---

## 6. Caching & Edge Rules

* **Pfad:** `Caching` ➔ `Cache Rules`

### Regel 1: Statische Frontend-Assets maximal cachen
* **If:** `http.request.uri.path starts_with "/assets/" or http.request.uri.path starts_with "/_astro/" or http.request.uri.path starts_with "/_next/"`
* **Then:** **Eligible for cache**, Edge TTL: `1 month`, Browser TTL: `1 month`

### Regel 2: API & Dynamic niemals cachen
* **If:** `http.request.uri.path starts_with "/api/" or http.request.uri.path starts_with "/admin/"`
* **Then:** **Bypass cache**

### Regel 3: WebSockets für Live-Telemetrie durchleiten (Sharegy)
* **If:** `http.request.uri.path starts_with "/ws/"`
* **Then:** **Bypass cache**

---

## 7. Domain-spezifische Matrix

| Domain | Zweck & Framework | Wichtigste Cloudflare-Besonderheit |
| :--- | :--- | :--- |
| **`smartevo.de`** | Dachmarke & PV-Landingpages (Astro / Pages) | Turnstile auf `/api/contact`, Early Hints für Fonts, HSTS Preload |
| **`sharegy.de`** | EMS-, VPP- & Prosumer-Portal (React / Django) | Rate-Limiting auf `/api/v1/auth/`, WebSocket-Proxy für `/ws/` |
| **`factofy.de`** | B2B Daten- & IoT-Aggregator (Next.js) | Caching auf `/_next/static/*`, API Bypass auf `/api/*` |
| **`valofy.de`** | Flexibilitäts- & Asset-Bewertung | DNSSEC, Strict SSL, Security Headers |
| **`moniy.de`** | Finanz-, Abrechnungs- & Tarif-Engine | Strict Rate Limiting, Bot Fight Mode, HSTS 1 Year |
