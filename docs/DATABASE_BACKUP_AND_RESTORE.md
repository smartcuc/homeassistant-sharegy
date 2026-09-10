# 💾 Sharegy – PostgreSQL & TimescaleDB Backup & Disaster Recovery Guide

Dieses Dokument beschreibt die Einrichtung des automatisierten täglichen Datenbank-Backups auf dem Produktionsserver sowie die Wiederherstellung (Disaster Recovery).

---

## 📋 1. Übersicht & Skripte

Im Verzeichnis `scripts/` stehen zwei produktionsreife Werkzeuge zur Verfügung:
1. [`scripts/backup_db.sh`](file:///c:/Users/Public/Dev/eswes/scripts/backup_db.sh) – Automatisiertes Backup mit Rotation, Kompression und Logging.
2. [`scripts/restore_db.sh`](file:///c:/Users/Public/Dev/eswes/scripts/restore_db.sh) – 1-Klick Restore-Hilfe mit Sicherheitsabfrage und Service-Handling.

---

## ⚙️ 2. Einrichtung auf dem Server

### Schritt 1: Ausführungsrechte vergeben
```bash
chmod +x /var/www/sharegy/live/scripts/backup_db.sh
chmod +x /var/www/sharegy/live/scripts/restore_db.sh
```

### Schritt 2: Verzeichnisse und Rechte anlegen
```bash
sudo mkdir -p /var/backups/sharegy/db
sudo mkdir -p /var/log/sharegy
sudo chown -R www-data:www-data /var/backups/sharegy
sudo chown -R www-data:www-data /var/log/sharegy
```

### Schritt 3: Täglichen Cronjob einrichten
Öffnen Sie die Crontab (z. B. für den Benutzer `root` oder `postgres` / `www-data`):
```bash
sudo crontab -e
```

Fügen Sie folgende Zeile ein (führt das Backup täglich um **03:00 Uhr nachts** aus):
```cron
# Tägliches Sharegy DB-Backup um 03:00 Uhr
0 3 * * * /var/www/sharegy/live/scripts/backup_db.sh >> /var/log/sharegy/cron_backup.log 2>&1
```

---

## 🔍 3. Manuelles Testen

Führen Sie das Skript einmal manuell aus, um die Verbindung und Dateierstellung zu testen:
```bash
sudo /var/www/sharegy/live/scripts/backup_db.sh
```

**Ergebnis prüfen**:
```bash
ls -la /var/backups/sharegy/db/
cat /var/log/sharegy/db_backup.log
```

---

## 🔄 4. Wiederherstellung (Restore)

Im Notfall oder zur Wiederherstellung eines Backups auf einem Staging-System:
```bash
sudo /var/www/sharegy/live/scripts/restore_db.sh /var/backups/sharegy/db/sharegy_db_eswes_YYYYMMDD_HHMMSS.dump
```
Das Skript stoppt temporär Web- & Worker-Dienste, führt den sauberen `pg_restore` durch und startet die Services anschließend wieder automatisch.
