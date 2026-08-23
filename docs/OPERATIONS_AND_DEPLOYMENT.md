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
