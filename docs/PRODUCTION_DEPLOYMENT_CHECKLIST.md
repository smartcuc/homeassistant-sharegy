# 🚀 Sharegy – Production Deployment & Go-Live Checklist

Diese Checkliste dient als verbindlicher Leitfaden für das **Produktivreif-Deployment (Production Go-Live)** der Sharegy Energy Management & Energy Sharing Plattform.

---

## 📋 Übersicht der 9 Kernbereiche

```
┌───────────────────────────────────────────────────────────────────────────────────┐
│                     SHAREGY PRODUCTION DEPLOYMENT ARCHITEKTUR                     │
├───────────────────────────────────────────────────────────────────────────────────┤
│ 1. 🛡️ SERVER, LINUX & TLS-SICHERHEIT (Nginx Reverse Proxy, HSTS, UFW, Let's Encrypt)│
│ 2. 🗄️ TIMESCALEDB & POSTGRESQL (Hypertables, Continuous Aggregates, Retention)     │
│ 3. ⚡ REDIS & CELERY WORKER QUEUES (realtime, fiscal, analytics, background)      │
│ 4. 🔌 DAPHNE ASGI & WEBSOCKETS (Shelly Outbound-WSS, OCPP 1.6-J CSMS Gateway)     │
│ 5. 🌐 FRONTEND BUILD & STATIC ASSETS (Vite React Build, SPA Routing, collectstatic)│
│ 6. ☀️ HARDWARE CONNECTIVITY (Sungrow OpenAPI, Discovergy wMSB, Inverter YAML Maps) │
│ 7. 💳 STRIPE PAYMENTS & SEPA-ABRECHNUNG (Pain.008 XML, § 42b EnWG, MSCONS EDIFACT)│
│ 8. 📈 MONITORING, METRICS & SENTRY (Healthchecks, Prometheus /metrics, Sentry DSN)│
│ 9. 💾 BACKUP, DISASTER RECOVERY & CRONJOBS (backup_db.sh, Retention, restore_db.sh)│
└───────────────────────────────────────────────────────────────────────────────────┘
```

---

## 1. 🛡️ Server, Linux & TLS-Sicherheit

- [ ] **Betriebssystem**: Ubuntu 22.04 LTS oder 24.04 LTS mit aktuellem Patch-Stand (`apt update && apt upgrade -y`).
- [ ] **UFW Firewall**:
  ```bash
  sudo ufw default deny incoming
  sudo ufw default allow outgoing
  sudo ufw allow 22/tcp      # SSH (oder Custom Port)
  sudo ufw allow 80/tcp      # HTTP (Let's Encrypt Challenge & Redirect)
  sudo ufw allow 443/tcp     # HTTPS / WSS
  sudo ufw enable
  ```
- [ ] **TLS & Nginx Zertifikate**:
  - Let's Encrypt Zertifikate via `certbot --nginx -d sharegy.de -d api.sharegy.de -d app.sharegy.de`.
  - Certbot Auto-Renewal Timer aktiv: `sudo systemctl status certbot.timer` & `sudo certbot renew --dry-run`.
  - HTTP Strict Transport Security (`HSTS: max-age=31536000; includeSubDomains; preload`).
  - TLS 1.2 und TLS 1.3 only mit sicheren Ciphers.
- [ ] **Umgebungsvariablen (`/var/www/sharegy/shared/.env`)**:
  - `DEBUG=False`
  - `HTTPS=True`
  - `DJANGO_SETTINGS_MODULE=backend.settings.prod`
  - `SECRET_KEY` = 64-stelliger kryptografischer Zufallsschlüssel.
  - `ALLOWED_HOSTS=sharegy.de,api.sharegy.de,app.sharegy.de`
  - Dateiberechtigungen restriktiv setzen: `chmod 600 /var/www/sharegy/shared/.env`.

---

## 2. 🗄️ PostgreSQL 16 & TimescaleDB 2.x Hypertables

- [ ] **Extensions aktiviert**:
  ```sql
  CREATE EXTENSION IF NOT EXISTS timescaledb CASCADE;
  CREATE EXTENSION IF NOT EXISTS pgcrypto CASCADE;
  ```
- [ ] **Django-Migrationen ausführen**:
  ```bash
  python manage.py migrate
  ```
- [ ] **TimescaleDB Hypertables & Retention initialisieren**:
  ```bash
  python manage.py setup_timescaledb
  ```
  *Richtet automatisch Hypertables für `devices_devicemetric`, `devices_devicemetric1m..1h`, `core_intervalreading`, `core_balanceslot` und `market_spotprice` ein.*
- [ ] **Handbuch & Wissensportal initialisieren**:
  ```bash
  python manage.py seed_helpcenter
  ```
  *Erstellt/aktualisiert alle 37 Handbuch-Artikel in Deutsch & Englisch.*
- [ ] **Daten-Retention Policies verifiziert**:
  - Hochfrequente 1s/5s Roh-Telemetrie komprimiert nach 7 Tagen, bereinigt nach 30 Tagen.
  - Stündliche & tägliche Aggregate bleiben dauerhaft erhalten.
  - 15m Bilanzierungsdaten gem. § 42b EnWG revisionssicher für 10 Jahre archivieren.

---

## 3. ⚡ Redis & Celery Multi-Queue Setup

- [ ] **Redis 7.x Server**:
  - Gesichert mit starkem Passwort (`requirepass` in `/etc/redis/redis.conf`).
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
  - `/ocpp/v16/<station_id>/` & `/ocpp/v201/<station_id>/` – OCPP CSMS Gateway für Wallboxen.
- [ ] **Nginx WebSocket Upgrade Header**:
  ```nginx
  proxy_http_version 1.1;
  proxy_set_header Upgrade $http_upgrade;
  proxy_set_header Connection "upgrade";
  proxy_read_timeout 86400s;
  ```

---

## 5. 🌐 Frontend Build & Static Assets

- [ ] **Frontend Production Build**:
  ```bash
  cd /var/www/sharegy/live/frontend
  npm install --frozen-lockfile
  npm run build
  ```
- [ ] **Django Static Assets sammeln**:
  ```bash
  cd /var/www/sharegy/live
  python manage.py collectstatic --noinput
  ```
- [ ] **Nginx SPA Routing & Static Handling**:
  ```nginx
  # Frontend Single-Page-App
  location / {
      root /var/www/sharegy/live/frontend/dist;
      try_files $uri $uri/ /index.html;
      expires 1h;
      add_header Cache-Control "public, no-transform";
  }

  # Django Static Files
  location /static/ {
      alias /var/www/sharegy/live/static/;
      expires 30d;
      access_log off;
  }

  # Django Backend API & Admin
  location ~ ^/(api|admin)/ {
      proxy_pass http://127.0.0.1:8000;
      proxy_set_header Host $host;
      proxy_set_header X-Real-IP $remote_addr;
      proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
      proxy_set_header X-Forwarded-Proto $scheme;
  }
  ```

---

## 6. ☀️ Hardware-Konnektivität & Profile

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

## 7. 💳 Stripe Payments, Abrechnung & Marktkommunikation

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

## 8. 📈 Monitoring, Metriken & Observability

- [ ] **Sentry Error & Performance Tracking**:
  - `SENTRY_DSN` in `.env` konfiguriert.
  - `SENTRY_ENVIRONMENT=production`
  - `SENTRY_TRACES_SAMPLE_RATE=0.05` (5% Sampling für minimale Performance-Last).
- [ ] **Healthcheck Endpoints**:
  - `GET /health/` – Prüft PostgreSQL/TimescaleDB, Redis, Celery & MQTT Ping.
  - Uptime Kuma / StatusCake Alerting auf Latenz $> 500\,\text{ms}$ oder HTTP $\neq 200$.
- [ ] **Log Rotation (`/etc/logrotate.d/sharegy`)**:
  ```logrotate
  /var/log/sharegy/*.log {
      daily
      missingok
      rotate 14
      compress
      delaycompress
      notifempty
      create 0640 www-data www-data
      sharedscripts
      postrotate
          systemctl reload gunicorn daphne > /dev/null 2>/dev/null || true
      endscript
  }
  ```

---

## 9. 💾 Backup, Disaster Recovery & Crontab-Konfiguration

- [ ] **Automatisierte Datenbank-Backups via [`scripts/backup_db.sh`](file:///c:/Users/Public/Dev/eswes/scripts/backup_db.sh)**:
  - Tägliches komprimiertes PostgreSQL & TimescaleDB Backup (`.dump` Custom-Format & `.sql.gz`).
  - Automatische Bereinigung alter Backups (Standard: 14 Tage Retention).
  - Protokollierung in `/var/log/sharegy/db_backup.log`.
- [ ] **Monatliches Server- & Konfigurations-Backup via [`scripts/backup_config.sh`](file:///c:/Users/Public/Dev/eswes/scripts/backup_config.sh)**:
  - Vollständige Sicherung von `.env`, Nginx, Fail2ban, Systemd Units, UFW, Redis, Crontabs & Paketlisten.
  - Sichere Dateirechte (`chmod 600`) und 12 Monate Retention.
- [ ] **Berechtigungen & Verzeichnisse anlegen**:
  ```bash
  sudo mkdir -p /var/backups/sharegy/db /var/backups/sharegy/config /var/log/sharegy
  sudo chown -R www-data:www-data /var/backups/sharegy /var/log/sharegy
  chmod +x /var/www/sharegy/live/scripts/backup_db.sh
  chmod +x /var/www/sharegy/live/scripts/backup_config.sh
  chmod +x /var/www/sharegy/live/scripts/restore_db.sh
  ```
- [ ] **Crontab-Einträge einrichten (`sudo crontab -e`)**:
  ```cron
  # ==============================================================================
  # Sharegy Automatisierte Backups
  # ==============================================================================
  # 1. Tägliches DB-Backup um 03:00 Uhr
  0 3 * * * /var/www/sharegy/live/scripts/backup_db.sh >> /var/log/sharegy/cron_backup.log 2>&1

  # 2. Monatliches System- & Konfigurations-Backup am 1. jedes Monats um 03:30 Uhr
  30 3 1 * * /var/www/sharegy/live/scripts/backup_config.sh >> /var/log/sharegy/cron_config_backup.log 2>&1
  ```
- [ ] **Disaster Recovery Test via [`scripts/restore_db.sh`](file:///c:/Users/Public/Dev/eswes/scripts/restore_db.sh)**:
  - Einmaliger Trockenlauf des Restore-Skripts zur Verifikation der Wiederherstellbarkeit.
- [ ] **DSGVO & Datenlöschung**:
  - 30-tägige Soft-Delete Bereinigung (`purge_pending_devices` und `purge_deleted_accounts`).
  - Revisionssicheres Logging von Nutzerdatenexporten gem. Art. 15 / 20 DSGVO.

---

### ✅ Freigabe & Sign-off

| Rolle | Name / Verantwortlicher | Status | Datum |
|---|---|:---:|---|
| **Lead Developer** | Sharegy Core Engineering | 🟢 BEREIT | 10.09.2026 |
| **DevOps / SysAdmin** | Platform Infrastructure | 🟢 BEREIT | 10.09.2026 |
| **Data Protection Officer** | Compliance & Legal | 🟢 BEREIT | 10.09.2026 |
