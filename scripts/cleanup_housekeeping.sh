#!/usr/bin/env bash
# ==============================================================================
# Sharegy – Automated System Housekeeping & Session Cleanup Script
# ==============================================================================
# Features:
#  - Bereinigt abgelaufene Django-Sessions (clearsessions)
#  - Bereinigt abgelaufene Magic-Login- & Auth-Tokens (cleanup_tokens)
#  - MQTT Status-Reconciliation & Event-Queue Replay (mqtt_reconcile)
#  - Bereinigt alte temporäre Cache- & Scratch-Dateien
# ==============================================================================

set -eo pipefail

APP_DIR="${APP_DIR:-/var/www/sharegy/live}"
if [ ! -d "$APP_DIR" ]; then
    APP_DIR="$(cd "$(dirname "$0")/.." && pwd)"
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

# 1. Django Sessions bereinigen
log "Bereinige abgelaufene Django Sessions (clearsessions)..."
"$PYTHON_BIN" manage.py clearsessions >> "$LOG_FILE" 2>&1 || log "[WARN] clearsessions fehlgeschlagen."

# 2. Expired Auth Tokens bereinigen
log "Bereinige abgelaufene Auth- & Magic-Tokens (cleanup_tokens)..."
"$PYTHON_BIN" manage.py cleanup_tokens >> "$LOG_FILE" 2>&1 || log "[WARN] cleanup_tokens fehlgeschlagen."

# 3. MQTT Reconcile & State Sync
log "Führe MQTT State Reconciliation aus (mqtt_reconcile)..."
"$PYTHON_BIN" manage.py mqtt_reconcile >> "$LOG_FILE" 2>&1 || log "[WARN] mqtt_reconcile fehlgeschlagen."

# 4. Temporäre Cache-Dateien im OS bereinigen
log "Bereinige temporäre Dateien..."
find /tmp -type f -name "sharegy_tmp_*" -mtime +2 -delete 2>/dev/null || true

log "Housekeeping erfolgreich abgeschlossen."
log "========================================================================"
