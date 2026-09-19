#!/usr/bin/env bash
# ==============================================================================
# Sharegy – Automated Log Rotation, Compression & Disk Space Watchdog
# ==============================================================================
# Features:
#  - Komprimiert Log-Dateien älter als 1 Tag mit gzip (.gz)
#  - Löscht komprimierte Logs älter als 14 Tage
#  - Prüft Festplattenbelegung (df -h /) und warnt ab 85% Füllstand
#  - Prüft Inode-Verbrauch und warnt ab 90%
# ==============================================================================

set -eo pipefail

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

# 1. Unkomprimierte alte Logs komprimieren
find "$LOG_DIR" -type f -name "*.log" -mtime +1 ! -name "log_rotation.log" -exec gzip -f {} \; >> "$MAIN_LOG" 2>&1 || true

# 2. Logs älter als Retention-Tage löschen
find "$LOG_DIR" -type f -name "*.log.gz" -mtime +"$RETENTION_DAYS" -exec rm -f {} \; >> "$MAIN_LOG" 2>&1 || true

# 3. Festplattenbelegung prüfen
DISK_USAGE="$(df / | awk 'NR==2 {print $5}' | tr -d '%')"
log "Aktuelle Festplattenauslastung: ${DISK_USAGE}%"

if [ "$DISK_USAGE" -ge "$DISK_WARN_PERCENT" ]; then
    log "[CRITICAL ALERT] Festplattenauslastung liegt bei ${DISK_USAGE}% (Schwelle: ${DISK_WARN_PERCENT}%)!"
    # Versuche Notfallbereinigung alter apt-Caches & temp files
    journalctl --vacuum-time=7d >> "$MAIN_LOG" 2>&1 || true
fi

# 4. Inodes prüfen
INODE_USAGE="$(df -i / | awk 'NR==2 {print $5}' | tr -d '%')"
log "Aktuelle Inode-Auslastung: ${INODE_USAGE}%"
if [ "$INODE_USAGE" -ge 90 ]; then
    log "[CRITICAL ALERT] Inode-Auslastung liegt bei ${INODE_USAGE}%!"
fi

log "Log-Rotation und Speicherprüfung abgeschlossen."
log "========================================================================"
