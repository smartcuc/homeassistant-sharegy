#!/usr/bin/env bash
# ==============================================================================
# Sharegy – Automated Production Cron & Operations Setup Script
# ==============================================================================
# Usage:
#   sudo bash scripts/install_cron.sh
# ==============================================================================

set -eo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
APP_DIR="$(cd "${SCRIPT_DIR}/.." && pwd)"
CRON_SRC="${SCRIPT_DIR}/crontab.example"
CRON_DEST="/etc/cron.d/sharegy"

echo "========================================================================"
echo "🚀 Sharegy Operations & Cron Installer"
echo "========================================================================"
echo "App Directory: $APP_DIR"
echo "Script Directory: $SCRIPT_DIR"

# 1. Berechtigungen für alle Shell-Skripte setzen
echo "[1/4] Setze Ausführungsrechte (chmod +x) für alle Skripte..."
chmod +x "$SCRIPT_DIR"/*.sh

# 2. Log- und Backup-Verzeichnisse anlegen
echo "[2/4] Erstelle Verzeichnisse für Logs und Backups..."
mkdir -p /var/log/sharegy
mkdir -p /var/backups/sharegy/db
mkdir -p /var/backups/sharegy/db_diff

# 3. Berechtigungen anpassen
if id "pi" >/dev/null 2>&1; then
    chown -R pi:pi /var/log/sharegy /var/backups/sharegy 2>/dev/null || true
fi
if id "sharegy" >/dev/null 2>&1; then
    chown -R sharegy:sharegy /var/log/sharegy /var/backups/sharegy 2>/dev/null || true
fi

# 4. Cron-Datei mit dynamischem Pfad nach /etc/cron.d/sharegy kopieren
if [ -w "/etc/cron.d" ] || [ "$EUID" -eq 0 ]; then
    echo "[3/4] Generiere und installiere System-Crontab nach $CRON_DEST..."
    sed "s|{{APP_DIR}}|$APP_DIR|g" "$CRON_SRC" > "$CRON_DEST"
    chmod 644 "$CRON_DEST"
    chown root:root "$CRON_DEST"
    echo "✅ Crontab erfolgreich unter $CRON_DEST aktiviert!"
else
    echo "⚠️ Keine Schreibrechte auf /etc/cron.d. Bitte führe das Skript mit 'sudo' aus:"
    echo "   sudo bash scripts/install_cron.sh"
    exit 1
fi

echo "========================================================================"
echo "✅ Setup erfolgreich abgeschlossen!"
echo "Aktive System-Cronjobs (/etc/cron.d/sharegy):"
echo "------------------------------------------------------------------------"
cat "$CRON_DEST"
echo "========================================================================"
