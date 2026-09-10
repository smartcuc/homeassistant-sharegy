#!/usr/bin/env bash
# ==============================================================================
# Sharegy – Automated PostgreSQL / TimescaleDB Backup Script
# ==============================================================================
# Features:
#  - Automatisches Laden der DB-Credentials aus .env (/var/www/sharegy/shared/.env)
#  - Erstellung komprimierter, konsistenter pg_dump Backups (.dump / .sql.gz)
#  - Vollständig kompatibel mit TimescaleDB Hypertables & Continuous Aggregates
#  - Tägliches Backup-Logging mit Zeitstempeln
#  - Automatische Bereinigung alter Backups (Retention: 14 Tage standardmäßig)
#  - Optional: Offsite-Upload via rclone / AWS S3 / Hetzner Storage Box
# ==============================================================================

set -eo pipefail

# ------------------------------------------------------------------------------
# 1. Konfiguration & Pfade
# ------------------------------------------------------------------------------
ENV_FILE="${ENV_FILE:-/var/www/sharegy/shared/.env}"
if [ ! -f "$ENV_FILE" ]; then
    # Fallback für lokales Verzeichnis
    ENV_FILE="/var/www/sharegy/live/.env"
fi

BACKUP_DIR="${BACKUP_DIR:-/var/backups/sharegy/db}"
LOG_FILE="${LOG_FILE:-/var/log/sharegy/db_backup.log}"
RETENTION_DAYS="${RETENTION_DAYS:-14}"
DATE_STR="$(date +"%Y%m%d_%H%M%S")"

# ------------------------------------------------------------------------------
# 2. Umgebungsvariablen laden
# ------------------------------------------------------------------------------
if [ -f "$ENV_FILE" ]; then
    # Sicheres Parsen von Key-Value Paaren aus .env
    export $(grep -v '^#' "$ENV_FILE" | grep -E '^(DB_NAME|DB_USER|DB_PASSWORD|DB_HOST|DB_PORT)=' | xargs)
fi

DB_NAME="${DB_NAME:-eswes}"
DB_USER="${DB_USER:-postgres}"
DB_HOST="${DB_HOST:-127.0.0.1}"
DB_PORT="${DB_PORT:-5432}"

if [ -z "$DB_PASSWORD" ]; then
    echo "[$(date +"%Y-%m-%d %H:%M:%S")] [WARN] DB_PASSWORD ist nicht gesetzt. Versuche Verbindung ohne Passwort..."
else
    export PGPASSWORD="$DB_PASSWORD"
fi

# Verzeichnisse anlegen falls nicht vorhanden
mkdir -p "$BACKUP_DIR"
mkdir -p "$(dirname "$LOG_FILE")"

log() {
    local MSG="[$(date +"%Y-%m-%d %H:%M:%S")] $1"
    echo "$MSG"
    echo "$MSG" >> "$LOG_FILE" 2>&1 || true
}

# ------------------------------------------------------------------------------
# 3. Backup durchführen
# ------------------------------------------------------------------------------
log "========================================================================"
log "Starte PostgreSQL/TimescaleDB Backup für Datenbank: '$DB_NAME'..."

BACKUP_FILE="${BACKUP_DIR}/sharegy_db_${DB_NAME}_${DATE_STR}.dump"
GZ_SQL_FILE="${BACKUP_DIR}/sharegy_db_${DB_NAME}_${DATE_STR}.sql.gz"

# Methode 1: Custom Archive Format (-Fc) für maximale Performance & pg_restore Flexibilität
if pg_dump -h "$DB_HOST" -p "$DB_PORT" -U "$DB_USER" -Fc -b -v "$DB_NAME" > "$BACKUP_FILE" 2>> "$LOG_FILE"; then
    BACKUP_SIZE="$(du -h "$BACKUP_FILE" | cut -f1)"
    log "Custom-Dump erfolgreich erstellt: $BACKUP_FILE (Größe: $BACKUP_SIZE)"
else
    log "FEHLER beim Ausführen von pg_dump (-Fc)! Breche ab."
    exit 1
fi

# Methode 2 (Optional/Zusatz): Gekapseltes SQL.gz als universelles Text-Backup
if command -v gzip >/dev/null 2>&1; then
    if pg_dump -h "$DB_HOST" -p "$DB_PORT" -U "$DB_USER" --clean --if-exists "$DB_NAME" | gzip -9 > "$GZ_SQL_FILE" 2>> "$LOG_FILE"; then
        GZ_SIZE="$(du -h "$GZ_SQL_FILE" | cut -f1)"
        log "SQL.gz Plain-Backup erfolgreich erstellt: $GZ_SQL_FILE (Größe: $GZ_SIZE)"
    fi
fi

# ------------------------------------------------------------------------------
# 4. Optional: Offsite Sync (S3 / Rclone / Storage Box)
# ------------------------------------------------------------------------------
if [ -n "$S3_BACKUP_BUCKET" ] && command -v aws >/dev/null 2>&1; then
    log "Synchronisiere Backup zu AWS S3 ($S3_BACKUP_BUCKET)..."
    aws s3 cp "$BACKUP_FILE" "s3://${S3_BACKUP_BUCKET}/db_backups/" >> "$LOG_FILE" 2>&1 || log "[WARN] S3 Upload fehlgeschlagen."
fi

if [ -n "$RCLONE_REMOTE" ] && command -v rclone >/dev/null 2>&1; then
    log "Synchronisiere Backup zu Rclone Remote ($RCLONE_REMOTE)..."
    rclone copy "$BACKUP_FILE" "${RCLONE_REMOTE}:sharegy_backups/" >> "$LOG_FILE" 2>&1 || log "[WARN] Rclone Sync fehlgeschlagen."
fi

# ------------------------------------------------------------------------------
# 5. Retention Management: Alte Backups bereinigen
# ------------------------------------------------------------------------------
log "Bereinige lokale Backups älter als $RETENTION_DAYS Tage in $BACKUP_DIR..."
DELETED_FILES="$(find "$BACKUP_DIR" -type f \( -name "*.dump" -o -name "*.sql.gz" \) -mtime +"$RETENTION_DAYS" -print)"
if [ -n "$DELETED_FILES" ]; then
    find "$BACKUP_DIR" -type f \( -name "*.dump" -o -name "*.sql.gz" \) -mtime +"$RETENTION_DAYS" -delete
    log "Gelöschte alte Backups:"
    echo "$DELETED_FILES" | while read -r f; do log " - $f"; done
else
    log "Keine veralteten Backups zum Löschen gefunden."
fi

# Passwort aus Environment leeren
unset PGPASSWORD

log "Datenbank-Backup erfolgreich abgeschlossen."
log "========================================================================"
exit 0
