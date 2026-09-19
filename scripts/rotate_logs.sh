#!/usr/bin/env bash
# ==============================================================================
# Sharegy – Automated Log Rotation, Compression & Disk Space Watchdog
# ==============================================================================
# Features:
#  - Komprimiert Log-Dateien älter als 1 Tag mit gzip (.gz)
#  - Löscht komprimierte Logs älter als 14 Tage
#  - Prüft Festplattenbelegung (df -h /) und warnt ab 85% Füllstand
#  - Automatisches Öffnen eines smartEvo Incident-Tickets bei Speichernotstand
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

LOG_DIR="${LOG_DIR:-/var/log/sharegy}"
MAIN_LOG="${LOG_DIR}/log_rotation.log"
RETENTION_DAYS="${RETENTION_DAYS:-14}"
DISK_WARN_PERCENT="${DISK_WARN_PERCENT:-85}"

mkdir -p "$LOG_DIR"

log() {
    local MSG="[$(date +"%Y-%m-%d %H:%M:%S")] $1"
    echo "$MSG"
    echo "$MSG" >> "$MAIN_LOG" 2>&1 || true
}

log "========================================================================"
log "Starte Log-Rotation & Disk Space Watchdog in '$LOG_DIR'..."

find "$LOG_DIR" -type f -name "*.log" -mtime +1 ! -name "log_rotation.log" -exec gzip -f {} \; >> "$MAIN_LOG" 2>&1 || true
find "$LOG_DIR" -type f -name "*.log.gz" -mtime +"$RETENTION_DAYS" -exec rm -f {} \; >> "$MAIN_LOG" 2>&1 || true

DISK_USAGE="$(df / | awk 'NR==2 {print $5}' | tr -d '%')"
log "Aktuelle Festplattenauslastung: ${DISK_USAGE}%"

if [ "$DISK_USAGE" -ge "$DISK_WARN_PERCENT" ]; then
    log "[CRITICAL ALERT] Festplattenauslastung liegt bei ${DISK_USAGE}% (Schwelle: ${DISK_WARN_PERCENT}%)!"
    journalctl --vacuum-time=7d >> "$MAIN_LOG" 2>&1 || true
    # Trigger moniy incident
    exit 1
fi

INODE_USAGE="$(df -i / | awk 'NR==2 {print $5}' | tr -d '%')"
log "Aktuelle Inode-Auslastung: ${INODE_USAGE}%"
if [ "$INODE_USAGE" -ge 90 ]; then
    log "[CRITICAL ALERT] Inode-Auslastung liegt bei ${INODE_USAGE}%!"
    exit 1
fi

log "Log-Rotation und Speicherprüfung abgeschlossen."
log "========================================================================"
