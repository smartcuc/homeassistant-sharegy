# 💾 Sharegy – Database & Server Configuration Backup & Disaster Recovery Guide

Dieses Dokument beschreibt die Einrichtung der automatisierten täglichen Datenbank-Backups und monatlichen System-/Konfigurations-Backups auf dem Produktionsserver sowie die Wiederherstellung (Disaster Recovery).

---

## 📋 1. Übersicht & Skripte

Im Verzeichnis `scripts/` stehen drei produktionsreife Werkzeuge zur Verfügung:
1. [`scripts/backup_db.sh`](file:///c:/Users/Public/Dev/eswes/scripts/backup_db.sh) – Tägliches komprimiertes PostgreSQL/TimescaleDB Backup (14 Tage Retention).
2. [`scripts/backup_config.sh`](file:///c:/Users/Public/Dev/eswes/scripts/backup_config.sh) – Monatliches vollständiges Backup aller Server- & Applikations-Konfigurationen (`.env`, Nginx, Fail2ban, Systemd, UFW, Redis, Crontabs, Paketlisten; 12 Monate Retention).
3. [`scripts/restore_db.sh`](file:///c:/Users/Public/Dev/eswes/scripts/restore_db.sh) – 1-Klick Restore-Hilfe für die Datenbank mit Sicherheitsabfrage und Service-Handling.

---

## ⚙️ 2. Einrichtung auf dem Server

### Schritt 1: Ausführungsrechte vergeben
```bash
chmod +x /var/www/sharegy/live/scripts/backup_db.sh
chmod +x /var/www/sharegy/live/scripts/backup_config.sh
chmod +x /var/www/sharegy/live/scripts/restore_db.sh
```

### Schritt 2: Verzeichnisse und Rechte anlegen
```bash
sudo mkdir -p /var/backups/sharegy/db
sudo mkdir -p /var/backups/sharegy/config
sudo mkdir -p /var/log/sharegy
sudo chown -R www-data:www-data /var/backups/sharegy /var/log/sharegy
```

### Schritt 3: Automatisierte Cronjobs einrichten (`sudo crontab -e`)
Öffnen Sie die Root-Crontab:
```bash
sudo crontab -e
```

Fügen Sie die beiden Jobs ein:
```cron
# ==============================================================================
# Sharegy Backup Cronjobs
# ==============================================================================
# 1. Tägliches Datenbank-Backup (PostgreSQL & TimescaleDB) um 03:00 Uhr
0 3 * * * /var/www/sharegy/live/scripts/backup_db.sh >> /var/log/sharegy/cron_backup.log 2>&1

# 2. Monatliches Server- & Konfigurations-Backup (.env, Nginx, Systemd, UFW, F2B) am 1. jeden Monats um 03:30 Uhr
30 3 1 * * /var/www/sharegy/live/scripts/backup_config.sh >> /var/log/sharegy/cron_config_backup.log 2>&1
```

---

## 🔍 3. Manuelles Testen

Führen Sie die Skripte einmal manuell aus, um die Erstellung und Integrität zu prüfen:
```bash
# Datenbank-Backup testen:
sudo /var/www/sharegy/live/scripts/backup_db.sh

# Konfigurations-Backup testen:
sudo /var/www/sharegy/live/scripts/backup_config.sh
```

**Ergebnis prüfen**:
```bash
ls -la /var/backups/sharegy/db/
ls -la /var/backups/sharegy/config/
cat /var/log/sharegy/db_backup.log
cat /var/log/sharegy/config_backup.log
```

---

## 🔄 4. Wiederherstellung (Disaster Recovery)

### A. Datenbank wiederherstellen
Im Notfall oder zur Wiederherstellung eines Datenbank-Dumps:
```bash
sudo /var/www/sharegy/live/scripts/restore_db.sh /var/backups/sharegy/db/sharegy_db_eswes_YYYYMMDD_HHMMSS.dump
```

### B. Konfigurationen wiederherstellen / einsehen
Die `.tar.gz` Datei ist mit `chmod 600` geschützt und kann bei Server-Neuaufbau entpackt werden:
```bash
tar -ztvf /var/backups/sharegy/config/sharegy_config_backup_YYYYMMDD_HHMMSS.tar.gz
```
Inhalt:
* `env/shared.env` & `env/live.env`
* `nginx/` (vollständige Nginx-Konfiguration)
* `fail2ban/` (Jails & Filter)
* `systemd/` (Service Units für Gunicorn, Daphne, Celery)
* `firewall/` (UFW-Regeln & Status)
* `databases/` (Redis & PostgreSQL Configs)
* `cron/` (Crontabs)
* `system_info.txt` & `installed_packages_dpkg.txt`
