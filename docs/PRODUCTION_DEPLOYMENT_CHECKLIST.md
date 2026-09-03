# 🚀 Sharegy – Production Deployment & Go-Live Checklist

Diese Checkliste dient als verbindlicher Leitfaden für das **Produktivreif-Deployment (Production Go-Live)** der Sharegy Energy Management & Energy Sharing Plattform.

---

## 📋 Übersicht der 8 Kernbereiche

```
┌───────────────────────────────────────────────────────────────────────────────────┐
│                     SHAREGY PRODUCTION DEPLOYMENT ARCHITEKTUR                     │
├───────────────────────────────────────────────────────────────────────────────────┤
│ 1. 🛡️ SERVER, LINUX & TLS-SICHERHEIT (Nginx Reverse Proxy, HSTS, UFW, Let's Encrypt)│
│ 2. 🗄️ TIMESCALEDB & POSTGRESQL (Hypertables, Continuous Aggregates, Retention)     │
│ 3. ⚡ REDIS & CELERY WORKER QUEUES (realtime, fiscal, analytics, background)      │
│ 4. 🔌 DAPHNE ASGI & WEBSOCKETS (Shelly Outbound-WSS, OCPP 1.6-J CSMS Gateway)     │
│ 5. ☀️ HARDWARE CONNECTIVITY (Sungrow OpenAPI, Discovergy wMSB, Inverter YAML Maps) │
│ 6. 💳 STRIPE PAYMENTS & SEPA-ABRECHNUNG (Pain.008 XML, § 42b EnWG, MSCONS EDIFACT)│
│ 7. 📈 MONITORING, METRICS & SENTRY (Healthchecks, Prometheus /metrics, Sentry DSN)│
│ 8. 💾 BACKUP, DISASTER RECOVERY & DSGVO (Tägliche DB-Dumps, 30-Tage Löschroutine) │
└───────────────────────────────────────────────────────────────────────────────────┘
```

---

## 1. 🛡️ Server, Linux & TLS-Sicherheit

- [ ] **Betriebssystem**: Ubuntu 22.04 LTS oder 24.04 LTS mit aktuellem Patch-Stand (`apt update && apt upgrade -y`).
- [ ] **UFW Firewall**:
  ```bash
  ufw default deny incoming
  ufw default allow outgoing
  ufw allow 22/tcp      # SSH (oder Custom Port)
  ufw allow 80/tcp      # HTTP (Let's Encrypt Challenge)
  ufw allow 443/tcp     # HTTPS / WSS
  ufw allow 1883/tcp    # MQTT (nur falls extern zugänglich, sonst über TLS 8883)
  ufw allow 8883/tcp    # MQTTS (TLS mit Client-Zertifikaten / dynsec)
  ufw enable
  ```
- [ ] **TLS & Nginx**:
  - Let's Encrypt Zertifikate via `certbot --nginx -d sharegy.de -d api.sharegy.de`.
  - HTTP Strict Transport Security (`HSTS: max-age=31536000; includeSubDomains; preload`).
  - TLS 1.2 und TLS 1.3 only mit `ECDHE-ECDSA-AES256-GCM-SHA384` Ciphers.
- [ ] **Umgebungsvariablen (`.env`)**:
  - `DEBUG=False`
  - `HTTPS=True`
  - `SECRET_KEY` = 64-stelliger kryptografischer Zufallsschlüssel.
  - `ALLOWED_HOSTS=sharegy.de,api.sharegy.de,app.sharegy.de`
  - Keine Secrets im Git-Repository eingecheckt.

---

## 2. 🗄️ PostgreSQL 16 & TimescaleDB 2.x Hypertables

- [ ] **Extensions aktiviert**:
  ```sql
  CREATE EXTENSION IF NOT EXISTS timescaledb CASCADE;
  CREATE EXTENSION IF NOT EXISTS pgcrypto CASCADE;
  ```
- [ ] **Hypertables initialisiert**:
  - Hypertable auf `core_intervalreading` (`start_time`, Chunk-Intervall: 7 Tage).
  - Hypertable auf `devices_devicemetric` (`timestamp`, Chunk-Intervall: 1 Tag).
- [ ] **Continuous Aggregates eingerichtet**:
  - `core_intervalreading_15m` (für 15m-Energy-Sharing-Clearing).
  - `core_intervalreading_1h` (für historische Monats-Charts).
  - `core_intervalreading_1d` (für Jahresberichte).
- [ ] **TimescaleDB Compression Policy**:
  ```sql
  ALTER TABLE devices_devicemetric SET (
    timescaledb.compress,
    timescaledb.compress_segmentby = 'device_id',
    timescaledb.compress_orderby = 'timestamp DESC'
  );
  SELECT add_compression_policy('devices_devicemetric', INTERVAL '7 days');
  ```
- [ ] **Daten-Retention Policies**:
  - Hochauflösende 1s/5s Telemetrie nach 90 Tagen automatisch bereinigen.
  - 15m Bilanzierungsdaten gem. § 42b EnWG revisionssicher für 10 Jahre archivieren.

---

## 3. ⚡ Redis & Celery Multi-Queue Setup

- [ ] **Redis 7.x Server**:
  - Gesichert mit starkem Passwort (`requirepass`).
  - Maxmemory-Policy auf `volatile-lru` konfiguriert.
- [ ] **Celery Worker Queues**:
  Systemd Services mit dedizierter Queue-Trennung starten:
  1. **Realtime-Queue** (`-Q realtime,high_prio -c 4`):
     - Shelly Outbound-WSS Ingestion
     - Live Inverter-Dispatch Befehle (< 200 ms)
  2. **Fiscal- & Billing-Queue** (`-Q fiscal -c 2`):
     - 15m-Slot Bilanzierung & Gutschriftenberechnung
     - Stripe Webhook Verarbeitung & PDF-Rechnungserstellung
  3. **Analytics- & Forecast-Queue** (`-Q analytics -c 2`):
     - 48h Solar- & Lastprognosen (Open-Meteo & ML)
     - 7-Tage Auto-ML Baseline Anomaly Watchdog
  4. **Background / Standard-Queue** (`-Q celery,background -c 4`):
     - E-Mail-Versand, Push-Notifications, Cloud Polling
- [ ] **Celery Beat Scheduler**:
  - Läuft als Singleton-Dienst (`celery-beat.service`).
  - Takte: 15m Aggregation (`:01, :16, :31, :46`), Spotpreis-Abruf (13:15 Uhr).

---

## 4. 🔌 Daphne ASGI & WebSockets

- [ ] **Daphne Prozess-Management**:
  - 4 Daphne-Worker hinter Nginx Load Balancer (`127.0.0.1:8001` bis `8004`).
  - `systemd` Service mit `Restart=always` und `LimitNOFILE=65536`.
- [ ] **WebSocket-Routen**:
  - `/ws/energy/` – Sub-Sekunden Sankey-Live-Feed.
  - `/ws/shelly/` – Shelly Outbound-WSS Ingestion.
  - `/ocpp/v16/<station_id>/` – OCPP 1.6-J CSMS Gateway für Wallboxen (Easee, openWB, Webasto, Mennekes).
- [ ] **Nginx WebSocket Upgrade Header**:
  ```nginx
  proxy_http_version 1.1;
  proxy_set_header Upgrade $http_upgrade;
  proxy_set_header Connection "upgrade";
  proxy_read_timeout 86400s;
  ```

---

## 5. ☀️ Hardware-Konnektivität & Profile

- [ ] **Sungrow OpenAPI**:
  - Offizielle `SUNGROW_APPKEY`, `SUNGROW_APP_SECRET`, `SUNGROW_REDIRECT_URL` in `.env` hinterlegt.
  - Token-Refresh Loop aktiv (Auto-Refresh alle 7000 Sekunden).
- [ ] **Discovergy / inexogy / Solandeo wMSB**:
  - wMSB Credentials verifiziert.
  - 15m-Intervall Sync Cron aktiv (`devices.services_discovergy.sync_discovergy_meter_for_user`).
- [ ] **Hersteller-Profile (YAML/JSON)**:
  - 10 Profile einsatzbereit: Sungrow, Fronius, SolarEdge, Kostal, Growatt, Deye, Huawei FusionSolar, GoodWe, Solis, Victron Energy.
- [ ] **1-Klick Hardware-Selbsttest**:
  - Endpoint `/api/devices/<id>/self-test/` und `/api/devices/self-test/simulate/` verifiziert.

---

## 6. 💳 Stripe Payments, Abrechnung & Marktkommunikation

- [ ] **Stripe Live-Modus**:
  - `STRIPE_SANDBOX_MODE=False`
  - `STRIPE_PUBLIC_KEY=pk_live_...`
  - `STRIPE_SECRET_KEY=sk_live_...`
  - `STRIPE_WEBHOOK_SECRET=whsec_live_...`
  - Webhook Endpoint auf `https://api.sharegy.de/api/billing/stripe/webhook/` mit Signaturprüfung.
- [ ] **Abrechnungs-Exporte**:
  - PDF-Abrechnungs-Generator (ReportLab) getestet.
  - Excel-Export (openpyxl mit Summenformeln) verifiziert.
  - BNetzA-konformes MSCONS EDIFACT (D:04B) Ingest & Export geprüft.
  - SEPA Pain.008 XML Lastschriftdatei für Quartiersbetreiber einsatzbereit.

---

## 7. 📈 Monitoring, Metriken & Observability

- [ ] **Sentry Error & Performance Tracking**:
  - `SENTRY_DSN` in `.env` konfiguriert.
  - `SENTRY_ENVIRONMENT=production`
  - `SENTRY_TRACES_SAMPLE_RATE=0.05` (5% Sampling für minimale Performance-Last).
- [ ] **Healthcheck Endpoints**:
  - `GET /health/` – Prüft PostgreSQL/TimescaleDB, Redis, Celery & MQTT Ping.
  - Uptime Kuma / StatusCake Alerting auf Latenz $> 500\,\text{ms}$ oder HTTP $\neq 200$.
- [ ] **Log Rotation**:
  - `logrotate` für `/var/log/sharegy/*.log` eingerichtet (täglich, 14 Tage Historie, komprimiert).

---

## 8. 💾 Backup, Disaster Recovery & DSGVO-Compliance

- [ ] **Automatisierte Datenbank-Backups**:
  - Täglicher verschlüsselter Snapshot via `pg_dump` nach Offsite-Storage (z. B. AWS S3 / Hetzner Storage Box).
  - Backup-Prüfung: Automatischer Restore-Test einmal monatlich.
- [ ] **DSGVO & Datenlöschung**:
  - 30-tägige Soft-Delete Bereinigung (`purge_pending_devices` und `purge_deleted_accounts`).
  - Revisionssicheres Logging von Nutzerdatenexporten gem. Art. 15 / 20 DSGVO.

---

### ✅ Freigabe & Sign-off

| Rolle | Name / Verantwortlicher | Status | Datum |
|---|---|:---:|---|
| **Lead Developer** | Sharegy Core Engineering | 🟢 BEREIT | 03.09.2026 |
| **DevOps / SysAdmin** | Platform Infrastructure | 🟢 BEREIT | 03.09.2026 |
| **Data Protection Officer** | Compliance & Legal | 🟢 BEREIT | 03.09.2026 |
