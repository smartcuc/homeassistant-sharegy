#!/usr/bin/env bash
# ==============================================================================
# Sharegy – Automated System Housekeeping & Session Cleanup Script
# ==============================================================================
# Features:
#  - Bereinigt abgelaufene Django-Sessions (clearsessions)
#  - Bereinigt abgelaufene Magic-Login- & Auth-Tokens (cleanup_tokens)
#  - MQTT Status-Reconciliation & Event-Queue Replay (mqtt_reconcile)
#  - Automatisches Öffnen eines smartEvo Incident-Tickets bei Fehlern
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
if [ -f "$ENV_FILE" ]; then
    export $(grep -v '^#' "$ENV_FILE" | grep -E '^(MONIY_URL|MONIY_S2S_KEY)=' | xargs)
fi

APP_DIR="${APP_DIR:-/var/www/sharegy/live}"
if [ ! -d "$APP_DIR" ]; then
    APP_DIR="$(cd "${SCRIPT_DIR}/.." && pwd)"
fi

VENV_DIR="${VENV_DIR:-${APP_DIR}/venv}"
PYTHON_BIN="${VENV_DIR}/bin/python"
if [ ! -f "$PYTHON_BIN" ]; then
    PYTHON_BIN="python3"
fi

LOG_FILE="${LOG_FILE:-/var/log/sharegy/housekeeping.log}"
mkdir -p "$(dirname "$LOG_FILE")"

log() {
    local MSG="[$(date +"%Y-%m-%d %H:%M:%S")] $1"
    echo "$MSG"
    echo "$MSG" >> "$LOG_FILE" 2>&1 || true
}

log "========================================================================"
log "Starte System Housekeeping & Cleanup..."

cd "$APP_DIR"

log "Bereinige abgelaufene Django Sessions (clearsessions)..."
"$PYTHON_BIN" manage.py clearsessions >> "$LOG_FILE" 2>&1

log "Bereinige abgelaufene Auth- & Magic-Tokens (cleanup_tokens)..."
"$PYTHON_BIN" manage.py cleanup_tokens >> "$LOG_FILE" 2>&1

log "Führe MQTT State Reconciliation aus (mqtt_reconcile)..."
"$PYTHON_BIN" manage.py mqtt_reconcile >> "$LOG_FILE" 2>&1 || log "[WARN] mqtt_reconcile gab Warnung zurück."

log "Bereinige temporäre Dateien..."
find /tmp -type f -name "sharegy_tmp_*" -mtime +2 -delete 2>/dev/null || true

log "Housekeeping erfolgreich abgeschlossen."
log "========================================================================"
