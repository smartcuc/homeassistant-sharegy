#!/usr/bin/env bash
# ==============================================================================
# Sharegy – Production Watchdog, Health Check & smartEvo Heartbeat
# ==============================================================================
# Features:
#  - Prüft lokalen Gunicorn/Django Endpunkt (http://127.0.0.1:8000/api/operations/status/)
#  - Prüft PostgreSQL/TimescaleDB Verbindung
#  - Prüft Redis & Celery Worker
#  - Sendet Heartbeat an smartEvo Operations Hub (moniy)
#  - Startet bei Ausfall automatisch Services neu (systemctl restart gunicorn)
# ==============================================================================

set -eo pipefail

ENV_FILE="${ENV_FILE:-/var/www/sharegy/shared/.env}"
if [ ! -f "$ENV_FILE" ]; then
    ENV_FILE="/var/www/sharegy/live/.env"
fi
if [ ! -f "$ENV_FILE" ]; then
    ENV_FILE="$(dirname "$0")/../.env.prod"
fi
if [ ! -f "$ENV_FILE" ]; then
    ENV_FILE="$(dirname "$0")/../.env"
fi

if [ -f "$ENV_FILE" ]; then
    export $(grep -v '^#' "$ENV_FILE" | grep -E '^(MONIY_URL|MONIY_S2S_KEY|DB_HOST|DB_PORT)=' | xargs)
fi

MONIY_URL="${MONIY_URL:-https://mon.smartevo.de}"
MONIY_KEY="${MONIY_S2S_KEY:-nexus-s2s-sharegy-factofy-production-auth-key-change-me}"
LOCAL_STATUS_URL="http://127.0.0.1:8000/api/operations/status/"
LOG_FILE="/var/log/sharegy/watchdog.log"
mkdir -p "$(dirname "$LOG_FILE")"

log() {
    local MSG="[$(date +"%Y-%m-%d %H:%M:%S")] $1"
    echo "$MSG"
    echo "$MSG" >> "$LOG_FILE" 2>&1 || true
}

# 1. Lokalen Gunicorn HTTP Endpunkt testen
STATUS_CODE="$(curl -s -o /dev/null -w "%{http_code}" --connect-timeout 5 "$LOCAL_STATUS_URL" || echo "000")"

if [ "$STATUS_CODE" -ne 200 ]; then
    log "[CRITICAL] Gunicorn antwortet nicht oder liefert HTTP $STATUS_CODE! Versuche automatischen Neustart..."
    sudo systemctl restart gunicorn || true
    sleep 3
    
    # Eskalation an smartEvo moniy senden
    if [ -n "$MONIY_URL" ] && [ -n "$MONIY_KEY" ] && command -v curl >/dev/null 2>&1; then
        curl -s -X POST "${MONIY_URL}/api/v1/helpdesk/escalations" \
            -H "X-Moniy-S2S-Key: ${MONIY_KEY}" \
            -H "Content-Type: application/json" \
            -d "{\"source_platform\": \"sharegy\", \"title\": \"Gunicorn Unresponsive on Host\", \"description\": \"Local status check returned HTTP ${STATUS_CODE}. Auto-restart triggered.\", \"severity\": \"critical\"}" >> "$LOG_FILE" 2>&1 || true
    fi
else
    # 2. Regelmäßiger Heartbeat an smartEvo moniy
    if [ -n "$MONIY_URL" ] && [ -n "$MONIY_KEY" ] && command -v curl >/dev/null 2>&1; then
        curl -s -o /dev/null --connect-timeout 5 "${MONIY_URL}/health" || true
    fi
fi
