# 🚀 Deployment, Betrieb & Systemd Services

Sharegy läuft in Produktion auf Ubuntu 24.04 LTS (z. B. Raspberry Pi 5 oder Cloud VPS).

---

## 🔧 1. Systemd Services Übersicht

| Service | Befehl | Funktion |
|---|---|---|
| `gunicorn.service` | `systemctl status gunicorn` | Django REST API & WSGI/ASGI Webserver |
| `mqtt-consumer.service` | `systemctl status mqtt-consumer` | Asynchroner MQTT Ingestion Daemon |
| `celery.service` | `systemctl status celery` | Asynchrone Task Worker |
| `celerybeat.service` | `systemctl status celerybeat` | Scheduler für Wetter, Forecast, Spotpreise |
| `redis.service` | `systemctl status redis` | In-Memory Cache, Pub/Sub & Celery Broker |
| `postgresql.service` | `systemctl status postgresql` | PostgreSQL & TimescaleDB Zeitreihendatenbank |

---

## 🔄 2. Standard Deployment-Befehl

```bash
cd /var/www/sharegy/green
git pull origin main

# 1. Backend Migrationen & Statics
./venv/bin/python manage.py migrate
./venv/bin/python manage.py collectstatic --noinput

# 2. Frontend Build
cd frontend
npm install
npm run build
cd ..

# 3. Services neu starten
sudo systemctl restart gunicorn mqtt-consumer celery celerybeat
```

---

## 🩺 3. Health Checks & Admin Operations Dashboard

Unter `/admin/operations/` steht ein integriertes Operations-Dashboard bereit:
- **Redis Health**: Ping-Latenz & Verbindungsstatus.
- **MQTT Consumer**: Letztes empfangenes Datenpaket & Status.
- **Spotpreise**: Gültigkeit der Day-Ahead Preise für Heute & Morgen.
- **Wetter & Forecast**: Letzter erfolgreicher Open-Meteo Sync.
- **Celery Queues**: Live-Überwachung der 4 Prioritäts-Queues (`fiscal`, `realtime`, `analytics`, `background`).

---

## ⚡ 4. Celery 4-Stufen Prioritäts-Architektur

Um zu verhindern, dass schwere Batch-Jobs (z. B. 8.7 MB Wetter-Downloads oder ML-Training) zeitkritische Zähler-Abrechnungen oder 5-Sekunden-MQTT-Puffer blockieren, ist Celery in **4 strikte Prioritäts-Queues** unterteilt:

| Priorität | Queue | Aufgaben & Tasks | Verhalten |
| :--- | :--- | :--- | :--- |
| **1 (Höchste)** | `fiscal` | • `core.tasks.rollup_15min` (OBIS 15m Rollups)<br>• `core.tasks.process_dirty_balance`<br>• `billing.tasks.allocate_user_balance_last_24h`<br>• `billing.tasks.compute_balance_last_24h`<br>• `accounts.tasks.cleanup_tokens` | **Eichrecht & Abrechnung**: Wird immer absolut prioritär vor allen anderen Tasks abgearbeitet. |
| **2 (Hoch)** | `realtime` | • `integrations.tasks.flush_mqtt_buffer` (alle 5s)<br>• `energy.tasks.publish_pending_device_commands`<br>• `operations.tasks.run_health_checks` | **Live-EMS & Steuerung**: Garantiert verzögerungsfreie MQTT-Ingestion und sofortige Ausführung von Gerätesteuerbefehlen. |
| **3 (Normal)** | `analytics` | • `devices.tasks.run_*m_aggregation` (1m/5m/15m/1h)<br>• `market.tasks.fetch_spot_prices_retry`<br>• `market.tasks_analysis.compute_daily_spot_summary`<br>• `forecast.tasks.update_all_forecasts`<br>• `forecast.tasks_weather.fetch_weather_data`<br>• `integrations.tasks.sync_tibber`<br>• `demo.tasks.sync_demo_metrics` | **EMS-Analytics & Markt**: Standardbetrieb für Charts, Metrik-Explorer, Spotmarkt und Solarprognosen (Default Queue). |
| **4 (Niedrig)** | `background` | • `forecast.tasks.train_all_generator_ml_models` (KI/ML)<br>• `forecast.tasks_weather_observations.fetch_weather_observations`<br>• `devices.tasks.purge_pending_devices`<br>• `demo.tasks.cleanup_demo` | **Hintergrund & Batch**: CPU-lastiges ML-Training und 8.7 MB Sensor.Community Bulk-Downloads blockieren niemals Stufe 1–3. |

### 🛠️ Systemd Celery Worker Konfiguration (`/etc/systemd/system/celery.service`)

```ini
[Unit]
Description=Sharegy Celery Worker
After=network.target redis.service

[Service]
Type=forking
User=pi
Group=pi
WorkingDirectory=/var/www/sharegy/green
Environment="DJANGO_SETTINGS_MODULE=backend.settings.prod"
ExecStart=/var/www/sharegy/green/venv/bin/celery -A backend worker -Q fiscal,realtime,analytics,background -l INFO --concurrency=2 --pidfile=/var/run/celery/worker.pid
Restart=always

[Install]
WantedBy=multi-user.target
```
> **Hinweis zur Queue-Reihenfolge**: Durch `-Q fiscal,realtime,analytics,background` arbeitet Celery die Queues strikt von links nach rechts ab. Sobald ein Abrechnungs- oder MQTT-Task eingeht, wird dieser sofort vor wartenden Analyse- oder Hintergrundjobs vorgezogen.
