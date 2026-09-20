# 💾 Sharegy – Database & Server Configuration Backup & Disaster Recovery Guide

Dieses Dokument beschreibt die Einrichtung der automatisierten täglichen Datenbank-Backups und monatlichen System-/Konfigurations-Backups auf dem Produktionsserver sowie die Wiederherstellung (Disaster Recovery).

---

## 📋 1. Übersicht & Skripte

Im Verzeichnis `scripts/` stehen folgende produktionsreife Werkzeuge zur Verfügung:
1. [`scripts/backup_postgres_inflight.sh`](file:///c:/Users/Public/Dev/sharegy/scripts/backup_postgres_inflight.sh) – Kontinuierliches 5-Minuten In-Flight PostgreSQL Delta-Backup direkt an das Moniy Vault (ohne lokalen Festplatten-Bloat).
2. [`scripts/backup_db.sh`](file:///c:/Users/Public/Dev/sharegy/scripts/backup_db.sh) – Tägliches komprimiertes PostgreSQL/TimescaleDB Full-Backup (14 Tage Retention).
3. [`scripts/backup_config.sh`](file:///c:/Users/Public/Dev/sharegy/scripts/backup_config.sh) – Monatliches vollständiges Backup aller Server- & Applikations-Konfigurationen (`.env`, Nginx, Fail2ban, Systemd, UFW, Redis, Crontabs, Paketlisten; 12 Monate Retention).
4. [`scripts/restore_db.sh`](file:///c:/Users/Public/Dev/sharegy/scripts/restore_db.sh) – 1-Klick Restore-Hilfe für die Datenbank mit Sicherheitsabfrage und Service-Handling.
5. [`scripts/install_cron.sh`](file:///c:/Users/Public/Dev/sharegy/scripts/install_cron.sh) – Schlüsselfertiger Installer für die System-Crontab (`/etc/cron.d/sharegy`).

---

## ⚙️ 2. Schlüsselfertige Einrichtung auf dem Server

Führen Sie im App-Verzeichnis einfach den automatisierten Installer aus:

```bash
cd /var/www/sharegy/green
sudo bash scripts/install_cron.sh
```

Das Skript:
* Setzt alle Ausführungsrechte (`chmod +x`).
* Erstellt Verzeichnisse für Logs (`/var/log/sharegy`) und lokale Dumps (`/var/backups/sharegy`).
* Aktiviert die System-Crontab unter `/etc/cron.d/sharegy`.

### 🔍 Crontab prüfen & überwachen:
```bash
# Crontab-Einträge anzeigen:
cat /etc/cron.d/sharegy

# Cron-Ausführungen im Log mitverfolgen:
sudo journalctl -u cron -n 20 --no-pager
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
