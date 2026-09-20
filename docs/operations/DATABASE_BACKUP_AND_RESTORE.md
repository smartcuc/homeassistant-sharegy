# 💾 Sharegy – Database & Server Configuration Backup & Disaster Recovery Guide

Dieses Dokument beschreibt die Einrichtung der automatisierten täglichen Datenbank-Backups und monatlichen System-/Konfigurations-Backups auf dem Produktionsserver sowie die Wiederherstellung (Disaster Recovery).

---

## 📋 1. Übersicht & Backup-Strategie

Die Backup-Architektur folgt einem ressourcenschonenden, 2-stufigen Modell:

1. **5-Minuten In-Flight Delta-Backup ([`scripts/backup_postgres_inflight.sh`](file:///c:/Users/Public/Dev/sharegy/scripts/backup_postgres_inflight.sh))**:
   - Streamt alle 5 Minuten ausschließlich die neuen Datensätze (Messwerte, Telemetrie, Logs, Transaktionen der letzten 10 Minuten) komprimiert an das smartEvo moniy Vault.
   - Extrem leichtgewichtig (< 500 KB pro Stream), kein lokaler Festplatten-Bloat.
   - **Retention**: Im Moniy Vault für **24 Stunden** aufbewahrt und danach automatisch bereinigt.

2. **Tägliches PostgreSQL / TimescaleDB Full-Backup ([`scripts/backup_db.sh`](file:///c:/Users/Public/Dev/sharegy/scripts/backup_db.sh))**:
   - Erstellt täglich um 03:00 UTC einen vollständigen, konsistenten Datenbank-Dump (`pg_full_${DB_NAME}`, ca. 246 MB) und überträgt ihn an das Moniy Vault sowie lokal nach `/var/backups/sharegy/db`.
   - **Retention**: Für **14 Tage** im Vault und auf dem Server aufbewahrt.

3. **Monatliches Konfigurations-Backup ([`scripts/backup_config.sh`](file:///c:/Users/Public/Dev/sharegy/scripts/backup_config.sh))**:
   - Sichert am 1. jedes Monats alle Konfigurationsdateien (`.env`, Nginx, Systemd, Fail2ban, UFW, Crontabs; 12 Monate Retention).

4. **1-Klick Restore ([`scripts/restore_db.sh`](file:///c:/Users/Public/Dev/sharegy/scripts/restore_db.sh))**:
   - Schnelle Wiederherstellung von `.dump` und `.sql.gz` Snapshots mit Service-Handling und Sicherheitsabfrage.

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
