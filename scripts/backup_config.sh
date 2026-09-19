#!/usr/bin/env bash
# ==============================================================================
# Sharegy – Automated System & Application Configuration Backup Script
# ==============================================================================
# Sichert monatlich alle kritischen System- und Applikations-Konfigurationen:
#  1. .env Dateien (/var/www/sharegy/shared/.env, live/.env)
#  2. Nginx (/etc/nginx/)
#  3. Fail2ban (/etc/fail2ban/)
#  4. Systemd Units (/etc/systemd/system/gunicorn*, daphne*, celery*, etc.)
#  5. Logrotate (/etc/logrotate.d/)
#  6. UFW Firewall Regeln & Sysctl (/etc/ufw/, /etc/sysctl.conf)
#  7. Redis (/etc/redis/) & PostgreSQL Konfigurationen (/etc/postgresql/)
#  8. Crontab-Dateien (/etc/crontab, /etc/cron.*, user crontabs)
#  9. Let's Encrypt Konfiguration (/etc/letsencrypt/renewal/)
# 10. Paket- & System-Metadaten (dpkg-Paketliste, systemctl-Dienste, OS-Info)
# ==============================================================================

set -eo pipefail

# ------------------------------------------------------------------------------
# 1. Konfiguration
# ------------------------------------------------------------------------------
BACKUP_DIR="${BACKUP_DIR:-/var/backups/sharegy/config}"
LOG_FILE="${LOG_FILE:-/var/log/sharegy/config_backup.log}"
RETENTION_MONTHS="${RETENTION_MONTHS:-12}" # 12 Monate Historie behalten
DATE_STR="$(date +"%Y%m%d_%H%M%S")"
TEMP_STAGE_DIR="/tmp/sharegy_config_backup_${DATE_STR}"

mkdir -p "$BACKUP_DIR"
mkdir -p "$(dirname "$LOG_FILE")"

log() {
    local MSG="[$(date +"%Y-%m-%d %H:%M:%S")] $1"
    echo "$MSG"
    echo "$MSG" >> "$LOG_FILE" 2>&1 || true
}

log "========================================================================"
log "Starte monatliches Server- & Konfigurations-Backup..."

# ------------------------------------------------------------------------------
# 2. Temporäres Staging-Verzeichnis vorbereiten
# ------------------------------------------------------------------------------
rm -rf "$TEMP_STAGE_DIR"
mkdir -p "$TEMP_STAGE_DIR"
# Restriktive Rechte setzen (da .env Passwörter enthält)
chmod 700 "$TEMP_STAGE_DIR"

# A. Sharegy .env Dateien
mkdir -p "$TEMP_STAGE_DIR/env"
if [ -f "/var/www/sharegy/shared/.env" ]; then
    cp -p "/var/www/sharegy/shared/.env" "$TEMP_STAGE_DIR/env/shared.env"
    log "✓ /var/www/sharegy/shared/.env gesichert"
fi
if [ -f "/var/www/sharegy/live/.env" ]; then
    cp -p "/var/www/sharegy/live/.env" "$TEMP_STAGE_DIR/env/live.env"
    log "✓ /var/www/sharegy/live/.env gesichert"
fi

# B. Nginx Konfiguration
if [ -d "/etc/nginx" ]; then
    mkdir -p "$TEMP_STAGE_DIR/nginx"
    cp -rp /etc/nginx/* "$TEMP_STAGE_DIR/nginx/" 2>/dev/null || true
    log "✓ /etc/nginx gesichert"
fi

# C. Fail2ban
if [ -d "/etc/fail2ban" ]; then
    mkdir -p "$TEMP_STAGE_DIR/fail2ban"
    cp -rp /etc/fail2ban/* "$TEMP_STAGE_DIR/fail2ban/" 2>/dev/null || true
    log "✓ /etc/fail2ban gesichert"
fi

# D. Systemd Service Units (Sharegy-spezifisch & Custom)
mkdir -p "$TEMP_STAGE_DIR/systemd"
if [ -d "/etc/systemd/system" ]; then
    cp -p /etc/systemd/system/gunicorn* "$TEMP_STAGE_DIR/systemd/" 2>/dev/null || true
    cp -p /etc/systemd/system/daphne* "$TEMP_STAGE_DIR/systemd/" 2>/dev/null || true
    cp -p /etc/systemd/system/celery* "$TEMP_STAGE_DIR/systemd/" 2>/dev/null || true
    cp -p /etc/systemd/system/sharegy* "$TEMP_STAGE_DIR/systemd/" 2>/dev/null || true
    cp -p /etc/systemd/system/certbot* "$TEMP_STAGE_DIR/systemd/" 2>/dev/null || true
    log "✓ Systemd Service Units gesichert"
fi

# E. Logrotate
mkdir -p "$TEMP_STAGE_DIR/logrotate"
if [ -d "/etc/logrotate.d" ]; then
    cp -rp /etc/logrotate.d/* "$TEMP_STAGE_DIR/logrotate/" 2>/dev/null || true
    log "✓ /etc/logrotate.d gesichert"
fi

# F. UFW & Firewall
mkdir -p "$TEMP_STAGE_DIR/firewall"
if [ -d "/etc/ufw" ]; then
    cp -rp /etc/ufw/* "$TEMP_STAGE_DIR/firewall/" 2>/dev/null || true
    log "✓ /etc/ufw gesichert"
fi
if command -v ufw >/dev/null 2>&1; then
    ufw status verbose > "$TEMP_STAGE_DIR/firewall/ufw_status.txt" 2>/dev/null || true
fi
if command -v iptables-save >/dev/null 2>&1; then
    iptables-save > "$TEMP_STAGE_DIR/firewall/iptables.rules" 2>/dev/null || true
fi

# G. Redis & PostgreSQL Config
mkdir -p "$TEMP_STAGE_DIR/databases"
if [ -f "/etc/redis/redis.conf" ]; then
    cp -p "/etc/redis/redis.conf" "$TEMP_STAGE_DIR/databases/" 2>/dev/null || true
    log "✓ Redis-Konfiguration gesichert"
fi
if [ -d "/etc/postgresql" ]; then
    cp -rp /etc/postgresql/* "$TEMP_STAGE_DIR/databases/postgresql/" 2>/dev/null || true
    log "✓ PostgreSQL-Konfiguration gesichert"
fi

# H. Crontabs
mkdir -p "$TEMP_STAGE_DIR/cron"
cp -p /etc/crontab "$TEMP_STAGE_DIR/cron/" 2>/dev/null || true
cp -rp /etc/cron.* "$TEMP_STAGE_DIR/cron/" 2>/dev/null || true
if [ -d "/var/spool/cron/crontabs" ]; then
    cp -rp /var/spool/cron/crontabs "$TEMP_STAGE_DIR/cron/user_crontabs" 2>/dev/null || true
    log "✓ Crontabs gesichert"
fi

# I. Let's Encrypt Renewal Configs
if [ -d "/etc/letsencrypt/renewal" ]; then
    mkdir -p "$TEMP_STAGE_DIR/letsencrypt_renewal"
    cp -rp /etc/letsencrypt/renewal/* "$TEMP_STAGE_DIR/letsencrypt_renewal/" 2>/dev/null || true
    log "✓ Let's Encrypt Renewal-Metadaten gesichert"
fi

# J. System-Info & Paketlisten (für Bare-Metal Restore)
cat <<EOF > "$TEMP_STAGE_DIR/system_info.txt"
================================================================================
SHAREGY SERVER METADATEN (Generiert am: $(date))
================================================================================
Hostname:      $(hostname -f 2>/dev/null || hostname)
OS / Kernel:   $(uname -a)
Linux Distro:  $(lsb_release -d 2>/dev/null | cut -f2 || cat /etc/os-release | grep PRETTY_NAME | cut -d= -f2 || echo "Unknown")
Uptime:        $(uptime)
Python:        $(python3 --version 2>/dev/null || echo "N/A")
Node.js:       $(node --version 2>/dev/null || echo "N/A")
Nginx:         $(nginx -v 2>&1 || echo "N/A")
PostgreSQL:    $(psql --version 2>/dev/null || echo "N/A")
Redis:         $(redis-server -v 2>/dev/null || echo "N/A")
================================================================================
EOF

if command -v dpkg >/dev/null 2>&1; then
    dpkg --get-selections > "$TEMP_STAGE_DIR/installed_packages_dpkg.txt" 2>/dev/null || true
fi
if command -v systemctl >/dev/null 2>&1; then
    systemctl list-unit-files --state=enabled > "$TEMP_STAGE_DIR/enabled_services.txt" 2>/dev/null || true
fi

# ------------------------------------------------------------------------------
# 3. Komprimiertes Archiv erstellen
# ------------------------------------------------------------------------------
ARCHIVE_FILE="${BACKUP_DIR}/sharegy_config_backup_${DATE_STR}.tar.gz"

tar -czf "$ARCHIVE_FILE" -C "$TEMP_STAGE_DIR" .
chmod 600 "$ARCHIVE_FILE"
rm -rf "$TEMP_STAGE_DIR"

ARCHIVE_SIZE="$(du -h "$ARCHIVE_FILE" | cut -f1)"
log "✓ Konfigurations-Archiv erfolgreich erstellt: $ARCHIVE_FILE ($ARCHIVE_SIZE)"

# ------------------------------------------------------------------------------
# 4. Optional: Offsite Upload (AWS S3 / Rclone)
# ------------------------------------------------------------------------------
if [ -f "/var/www/sharegy/shared/.env" ]; then
    export $(grep -v '^#' /var/www/sharegy/shared/.env | grep -E '^(S3_BACKUP_BUCKET|RCLONE_REMOTE)=' | xargs 2>/dev/null) || true
fi

if [ -n "$S3_BACKUP_BUCKET" ] && command -v aws >/dev/null 2>&1; then
    log "Synchronisiere Konfigurations-Backup zu AWS S3 ($S3_BACKUP_BUCKET)..."
    aws s3 cp "$ARCHIVE_FILE" "s3://${S3_BACKUP_BUCKET}/config_backups/" >> "$LOG_FILE" 2>&1 || log "[WARN] S3 Upload fehlgeschlagen."
fi

if [ -n "$RCLONE_REMOTE" ] && command -v rclone >/dev/null 2>&1; then
    log "Synchronisiere Konfigurations-Backup zu Rclone Remote ($RCLONE_REMOTE)..."
    rclone copy "$ARCHIVE_FILE" "${RCLONE_REMOTE}:sharegy_config_backups/" >> "$LOG_FILE" 2>&1 || log "[WARN] Rclone Sync fehlgeschlagen."
fi

# ------------------------------------------------------------------------------
# 5. Retention: Backups älter als X Monate bereinigen (ca. RETENTION_MONTHS * 30 Tage)
# ------------------------------------------------------------------------------
RETENTION_DAYS=$(( RETENTION_MONTHS * 30 ))
log "Bereinige Konfigurations-Backups älter als $RETENTION_DAYS Tage ($RETENTION_MONTHS Monate) in $BACKUP_DIR..."
DELETED_CONFIGS="$(find "$BACKUP_DIR" -type f -name "sharegy_config_backup_*.tar.gz" -mtime +"$RETENTION_DAYS" -print)"
if [ -n "$DELETED_CONFIGS" ]; then
    find "$BACKUP_DIR" -type f -name "sharegy_config_backup_*.tar.gz" -mtime +"$RETENTION_DAYS" -delete
    log "Gelöschte alte Konfigurations-Archive:"
    echo "$DELETED_CONFIGS" | while read -r f; do log " - $f"; done
else
    log "Keine veralteten Konfigurations-Backups zum Löschen gefunden."
fi

log "Monatliches Konfigurations-Backup erfolgreich abgeschlossen."
log "========================================================================"
exit 0
