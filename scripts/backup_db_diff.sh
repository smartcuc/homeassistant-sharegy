#!/usr/bin/env bash
# ==============================================================================
# Sharegy – Automated PostgreSQL / TimescaleDB Differential Backup Script
# ==============================================================================
# Features:
#  - In-Flight Stream an smartEvo moniy Vault
#  - Automatisches Öffnen eines smartEvo Incident-Tickets bei Fehlern
#  - 48h lokale Retention
# ==============================================================================

set -eo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
if [ -f "${SCRIPT_DIR}/smartevo_notify.sh" ]; then
    source "${SCRIPT_DIR}/smartevo_notify.sh"
    trap notify_smartevo_failure EXIT
fi

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

DIFF_DIR="${DIFF_DIR:-/var/backups/sharegy/db_diff}"
LOG_FILE="${LOG_FILE:-/var/log/sharegy/db_diff_backup.log}"
RETENTION_HOURS="${RETENTION_HOURS:-48}"
DATE_STR="$(date +"%Y%m%d_%H%M%S")"

if [ -f "$ENV_FILE" ]; then
    export $(grep -v '^#' "$ENV_FILE" | grep -E '^(DB_NAME|DB_USER|DB_PASSWORD|DB_HOST|DB_PORT|MONIY_URL|MONIY_S2S_KEY)=' | xargs)
fi

DB_NAME="${DB_NAME:-eswes}"
DB_USER="${DB_USER:-postgres}"
DB_HOST="${DB_HOST:-127.0.0.1}"
DB_PORT="${DB_PORT:-5432}"
MONIY_URL="${MONIY_URL:-https://mon.smartevo.de}"
MONIY_KEY="${MONIY_S2S_KEY:-nexus-s2s-sharegy-factofy-production-auth-key-change-me}"

if [ -n "$DB_PASSWORD" ]; then
    export PGPASSWORD="$DB_PASSWORD"
fi

mkdir -p "$DIFF_DIR"
mkdir -p "$(dirname "$LOG_FILE")"

log() {
    local MSG="[$(date +"%Y-%m-%d %H:%M:%S")] $1"
    echo "$MSG"
    echo "$MSG" >> "$LOG_FILE" 2>&1 || true
}

log "Starte PostgreSQL In-Flight / Delta Backup für '$DB_NAME'..."

DIFF_FILE="${DIFF_DIR}/sharegy_delta_${DB_NAME}_${DATE_STR}.dump"

if pg_dump -h "$DB_HOST" -p "$DB_PORT" -U "$DB_USER" -Fc --no-owner --no-privileges "$DB_NAME" > "$DIFF_FILE" 2>> "$LOG_FILE"; then
    DIFF_SIZE="$(du -h "$DIFF_FILE" | cut -f1)"
    log "Lokaler Delta-Dump erstellt: $DIFF_FILE ($DIFF_SIZE)"
    
    if [ -n "$MONIY_URL" ] && [ -n "$MONIY_KEY" ] && command -v curl >/dev/null 2>&1; then
        curl -sS -f -X POST "${MONIY_URL}/api/v1/backups/stream" \
            -H "X-Moniy-S2S-Key: ${MONIY_KEY}" \
            -H "X-Moniy-Tenant: sharegy" \
            -H "X-Moniy-Prefix: pg_delta_${DB_NAME}" \
            -H "Content-Type: application/octet-stream" \
            --data-binary "@${DIFF_FILE}" >> "$LOG_FILE" 2>&1 && log "Delta-Dump erfolgreich an moniy Vault gestreamt." || log "[WARN] moniy Delta Stream fehlgeschlagen."
    fi
else
    log "FEHLER beim Delta-Dump von '$DB_NAME'!"
    exit 1
fi

find "$DIFF_DIR" -type f -name "sharegy_delta_*.dump" -mmin +$((RETENTION_HOURS * 60)) -exec rm -f {} \; >> "$LOG_FILE" 2>&1 || true

log "Delta Backup abgeschlossen."
