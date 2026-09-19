#!/usr/bin/env bash
# ==============================================================================
# Sharegy – Automated Market Prices (EPEX Spot / SMARD) & Weather Forecast Sync
# ==============================================================================
# Features:
#  - Ruft viertelstündliche Day-Ahead und Intraday Strompreise von SMARD & Energy-Charts ab
#  - Berechnet tagesaktuelle Preisanalysen & Heatmaps
#  - Führt Wetter- und PV-Erzeugungsprognosen für alle Liegenschaften aus
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

LOG_FILE="${LOG_FILE:-/var/log/sharegy/market_forecast_sync.log}"
mkdir -p "$(dirname "$LOG_FILE")"

log() {
    local MSG="[$(date +"%Y-%m-%d %H:%M:%S")] $1"
    echo "$MSG"
    echo "$MSG" >> "$LOG_FILE" 2>&1 || true
}

log "========================================================================"
log "Starte Synchronisation von Börsenstrompreisen & Erzeugungsprognosen..."

cd "$APP_DIR"

# 1. Börsenpreise abrufen
log "Synchronisiere EPEX Spot & SMARD Strommarkt-Preise..."
"$PYTHON_BIN" manage.py sync_market_prices >> "$LOG_FILE" 2>&1 || {
    log "[WARN] sync_market_prices lieferte einen Fehler."
}

# 2. Prognoseberechnung anstoßen
log "Berechne Wetter- und PV-Erzeugungsprognosen..."
"$PYTHON_BIN" manage.py run_forecasts >> "$LOG_FILE" 2>&1 || {
    log "[WARN] run_forecasts lieferte einen Fehler."
}

log "Marktpreis- und Prognose-Synchronisation erfolgreich beendet."
log "========================================================================"
