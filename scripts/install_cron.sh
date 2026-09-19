#!/usr/bin/env bash
# ==============================================================================
# Sharegy – Automated Production Cron & Operations Setup Script
# ==============================================================================
# Usage:
#   sudo ./scripts/install_cron.sh
# ==============================================================================

set -eo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
APP_DIR="$(cd "${SCRIPT_DIR}/.." && pwd)"
CRON_SRC="${SCRIPT_DIR}/crontab.example"
CRON_DEST="/etc/cron.d/sharegy"

echo "========================================================================"
echo "Sharegy Operations & Cron Setup"
echo "========================================================================"

# 1. Berechtigungen für alle Shell-Skripte setzen
echo "1. Setze Ausführungsrechte (chmod +x) für alle Skripte in $SCRIPT_DIR..."
chmod +x "$SCRIPT_DIR"/*.sh

# 2. Log- und Backup-Verzeichnisse anlegen
echo "2. Erstelle Verzeichnisse für Logs und Backups..."
mkdir -p /var/log/sharegy
mkdir -p /var/backups/sharegy/db
mkdir -p /var/backups/sharegy/db_diff

# 3. Berechtigungen anpassen (falls User sharegy / postgres existieren)
if id "sharegy" >/dev/null 2>&1; then
    chown -R sharegy:sharegy /var/log/sharegy /var/backups/sharegy
fi

# 4. Cron-Datei nach /etc/cron.d kopieren
if [ -w "/etc/cron.d" ]; then
    echo "3. Installiere Crontab nach $CRON_DEST..."
    cp "$CRON_SRC" "$CRON_DEST"
    chmod 644 "$CRON_DEST"
    chown root:root "$CRON_DEST"
    echo "✅ Crontab erfolgreich unter $CRON_DEST aktiviert!"
else
    echo "⚠️ Keine Schreibrechte auf /etc/cron.d. Bitte führe das Skript mit 'sudo' aus."
fi

echo "========================================================================"
echo "Setup erfolgreich abgeschlossen!"
echo "Aktive Cronjobs:"
cat "$CRON_SRC"
echo "========================================================================"
