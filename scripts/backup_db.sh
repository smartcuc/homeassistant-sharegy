#!/usr/bin/env bash
# ==============================================================================
# Sharegy – Automated PostgreSQL / TimescaleDB Full Backup Script
# ==============================================================================
# Features:
#  - Automatisches Laden der DB-Credentials aus .env
#  - Erstellung komprimierter, konsistenter pg_dump Backups (.dump / .sql.gz)
#  - S2S-Stream zu smartEvo moniy Vault
#  - Automatisches Öffnen eines smartEvo Incident-Tickets bei Fehlern
#  - Tägliches Backup-Logging mit Zeitstempeln
#  - Automatische Bereinigung alter Backups (Retention: 7 Tage)
# ==============================================================================

set -eo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
if [ -f "${SCRIPT_DIR}/smartevo_notify.sh" ]; then
    source "${SCRIPT_DIR}/smartevo_notify.sh"
    trap notify_smartevo_failure EXIT
fi

# ------------------------------------------------------------------------------
# 1. Konfiguration & Pfade
# ------------------------------------------------------------------------------
ENV_FILE="${ENV_FILE:-/var/www/sharegy/shared/.env}"
if [ ! -f "$ENV_FILE" ]; then
    ENV_FILE="/var/www/sharegy/live/.env"
fi
if [ ! -f "$ENV_FILE" ]; then
    ENV_FILE="${SCRIPT_DIR}/../.env.prod"
fi
if [ ! -f "$ENV_FILE" ]; then
    ENV_FILE="${SCRIPT_DIR}/../.env"
fi

BACKUP_DIR="${BACKUP_DIR:-/var/backups/sharegy/db}"
LOG_FILE="${LOG_FILE:-/var/log/sharegy/db_backup.log}"
RETENTION_DAYS="${RETENTION_DAYS:-7}"
DATE_STR="$(date +"%Y%m%d_%H%M%S")"

# ------------------------------------------------------------------------------
# 2. Umgebungsvariablen laden
# ------------------------------------------------------------------------------
if [ -f "$ENV_FILE" ]; then
    export $(grep -v '^#' "$ENV_FILE" | grep -E '^(DB_NAME|DB_USER|DB_PASSWORD|DB_HOST|DB_PORT|MONIY_URL|MONIY_S2S_KEY|S3_BACKUP_BUCKET|RCLONE_REMOTE)=' | xargs)
fi

DB_NAME="${DB_NAME:-eswes}"
DB_USER="${DB_USER:-postgres}"
DB_HOST="${DB_HOST:-127.0.0.1}"
DB_PORT="${DB_PORT:-5432}"
MONIY_URL="${MONIY_URL:-https://mon.smartevo.de}"
MONIY_KEY="${MONIY_S2S_KEY:-nexus-s2s-sharegy-factofy-production-auth-key-change-me}"

if [ -z "$DB_PASSWORD" ]; then
    echo "[$(date +"%Y-%m-%d %H:%M:%S")] [WARN] DB_PASSWORD ist nicht gesetzt. Versuche Verbindung ohne Passwort..."
else
    export PGPASSWORD="$DB_PASSWORD"
fi

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
log "Starte PostgreSQL/TimescaleDB Full Backup für Datenbank: '$DB_NAME'..."

BACKUP_FILE="${BACKUP_DIR}/sharegy_db_${DB_NAME}_${DATE_STR}.dump"
GZ_SQL_FILE="${BACKUP_DIR}/sharegy_db_${DB_NAME}_${DATE_STR}.sql.gz"

# Methode 1: Custom Archive Format (-Fc)
if pg_dump -h "$DB_HOST" -p "$DB_PORT" -U "$DB_USER" -Fc -b -v "$DB_NAME" > "$BACKUP_FILE" 2>> "$LOG_FILE"; then
    BACKUP_SIZE="$(du -h "$BACKUP_FILE" | cut -f1)"
    log "Custom-Dump erfolgreich erstellt: $BACKUP_FILE (Größe: $BACKUP_SIZE)"
else
    log "FEHLER beim Ausführen von pg_dump (-Fc)! Breche ab."
    exit 1
fi

# Methode 2: Gekapseltes SQL.gz
if command -v gzip >/dev/null 2>&1; then
    if pg_dump -h "$DB_HOST" -p "$DB_PORT" -U "$DB_USER" --clean --if-exists "$DB_NAME" | gzip -9 > "$GZ_SQL_FILE" 2>> "$LOG_FILE"; then
        GZ_SIZE="$(du -h "$GZ_SQL_FILE" | cut -f1)"
        log "SQL.gz Plain-Backup erfolgreich erstellt: $GZ_SQL_FILE (Größe: $GZ_SIZE)"
    fi
fi

# ------------------------------------------------------------------------------
# 4. Offsite Sync & moniy Streaming
# ------------------------------------------------------------------------------
if [ -n "$MONIY_URL" ] && [ -n "$MONIY_KEY" ] && command -v curl >/dev/null 2>&1; then
    log "Übertrage Full-Backup an smartEvo moniy Vault ($MONIY_URL)..."
    curl -sS -f -X POST "${MONIY_URL}/api/v1/backups/stream" \
        -H "X-Moniy-S2S-Key: ${MONIY_KEY}" \
        -H "X-Moniy-Tenant: sharegy" \
        -H "X-Moniy-Prefix: pg_full_${DB_NAME}" \
        -H "Content-Type: application/octet-stream" \
        --data-binary "@${GZ_SQL_FILE}" >> "$LOG_FILE" 2>&1 || log "[WARN] moniy Vault Sync fehlgeschlagen."
fi

if [ -n "$S3_BACKUP_BUCKET" ] && command -v aws >/dev/null 2>&1; then
    log "Synchronisiere Backup zu AWS S3 ($S3_BACKUP_BUCKET)..."
    aws s3 cp "$BACKUP_FILE" "s3://${S3_BACKUP_BUCKET}/db_backups/" >> "$LOG_FILE" 2>&1 || log "[WARN] S3 Upload fehlgeschlagen."
fi

if [ -n "$RCLONE_REMOTE" ] && command -v rclone >/dev/null 2>&1; then
    log "Synchronisiere Backup zu Rclone Remote ($RCLONE_REMOTE)..."
    rclone copy "$BACKUP_FILE" "${RCLONE_REMOTE}:sharegy_backups/" >> "$LOG_FILE" 2>&1 || log "[WARN] Rclone Sync fehlgeschlagen."
fi

# ------------------------------------------------------------------------------
# 5. Retention Management
# ------------------------------------------------------------------------------
log "Prüfe und bereinige Backups älter als $RETENTION_DAYS Tage..."
find "$BACKUP_DIR" -type f \( -name "sharegy_db_*.dump" -o -name "sharegy_db_*.sql.gz" \) -mtime +"$RETENTION_DAYS" -exec rm -v {} \; >> "$LOG_FILE" 2>&1 || true

log "Full Database Backup für '$DB_NAME' erfolgreich abgeschlossen."
log "========================================================================"
