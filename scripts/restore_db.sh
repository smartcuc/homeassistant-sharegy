#!/usr/bin/env bash
# ==============================================================================
# Sharegy – PostgreSQL / TimescaleDB Database Restore Script
# ==============================================================================
# Benutzung:
#   ./scripts/restore_db.sh /var/backups/sharegy/db/sharegy_db_eswes_20260910_030000.dump
# ==============================================================================

set -eo pipefail

BACKUP_FILE="$1"
if [ -z "$BACKUP_FILE" ] || [ ! -f "$BACKUP_FILE" ]; then
    echo "FEHLER: Bitte eine gültige Backup-Datei (.dump oder .sql.gz) angeben!"
    echo "Beispiel: $0 /var/backups/sharegy/db/sharegy_db_eswes_20260910_030000.dump"
    exit 1
fi

ENV_FILE="${ENV_FILE:-/var/www/sharegy/shared/.env}"
if [ ! -f "$ENV_FILE" ]; then
    ENV_FILE="/var/www/sharegy/live/.env"
fi

if [ -f "$ENV_FILE" ]; then
    export $(grep -v '^#' "$ENV_FILE" | grep -E '^(DB_NAME|DB_USER|DB_PASSWORD|DB_HOST|DB_PORT)=' | xargs)
fi

DB_NAME="${DB_NAME:-eswes}"
DB_USER="${DB_USER:-postgres}"
DB_HOST="${DB_HOST:-127.0.0.1}"
DB_PORT="${DB_PORT:-5432}"

if [ -n "$DB_PASSWORD" ]; then
    export PGPASSWORD="$DB_PASSWORD"
fi

echo "========================================================================"
echo "ACHTUNG: Wiederherstellung der Datenbank '$DB_NAME' von:"
echo "  $BACKUP_FILE"
echo "Ziel-Host: $DB_HOST:$DB_PORT (User: $DB_USER)"
echo "========================================================================"
read -p "Möchten Sie fortfahren? Alle bestehenden Daten werden überschrieben! (j/N): " CONFIRM
if [[ "$CONFIRM" != "j" && "$CONFIRM" != "J" && "$CONFIRM" != "y" && "$CONFIRM" != "Y" ]]; then
    echo "Abgebrochen durch Benutzer."
    exit 0
fi

echo "Stoppe temporär Hintergrunddienste (Gunicorn, Daphne, Celery)..."
sudo systemctl stop gunicorn daphne celery celery-beat || true

echo "Starte Restore-Prozess..."
if [[ "$BACKUP_FILE" == *.dump ]]; then
    # Custom Format Restore (-Fc)
    pg_restore -h "$DB_HOST" -p "$DB_PORT" -U "$DB_USER" -d "$DB_NAME" --clean --if-exists -v "$BACKUP_FILE" || true
elif [[ "$BACKUP_FILE" == *.sql.gz ]]; then
    # Plain Gzip SQL Restore
    gunzip -c "$BACKUP_FILE" | psql -h "$DB_HOST" -p "$DB_PORT" -U "$DB_USER" -d "$DB_NAME"
else
    echo "Unbekanntes Dateiformat! Nur .dump und .sql.gz werden unterstützt."
    exit 1
fi

echo "Starte Hintergrunddienste wieder..."
sudo systemctl start gunicorn daphne celery celery-beat || true

unset PGPASSWORD
echo "========================================================================"
echo "Wiederherstellung erfolgreich abgeschlossen!"
echo "========================================================================"
