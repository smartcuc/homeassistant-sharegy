#!/usr/bin/env bash
# ==============================================================================
# Sharegy – Automated TimescaleDB & Telemetry Maintenance Script
# ==============================================================================
# Features:
#  - Führt Metric-Rollups und Aggregationen aus (15m, 1h, 1d)
#  - Aktualisiert Continuous Aggregates und Hypertables
#  - Bereinigt abgelaufene Roh-Telemetrie-Ticks nach Retention-Richtlinie
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

LOG_FILE="${LOG_FILE:-/var/log/sharegy/timescaledb_maintenance.log}"
mkdir -p "$(dirname "$LOG_FILE")"

log() {
    local MSG="[$(date +"%Y-%m-%d %H:%M:%S")] $1"
    echo "$MSG"
    echo "$MSG" >> "$LOG_FILE" 2>&1 || true
}

log "========================================================================"
log "Starte TimescaleDB Telemetrie-Wartung & Rollups..."

cd "$APP_DIR"

# 1. TimescaleDB Setup / Hypertables Verify
log "Prüfe TimescaleDB Hypertables..."
"$PYTHON_BIN" manage.py setup_timescaledb >> "$LOG_FILE" 2>&1 || log "[WARN] setup_timescaledb gab Warnung zurück."

# 2. Metric Rollups
log "Führe Metric Rollups aus..."
"$PYTHON_BIN" manage.py rollup >> "$LOG_FILE" 2>&1 || log "[WARN] rollup gab Warnung zurück."

# 3. Aggregate Metrics
log "Aggregiere Geräte-Metriken..."
"$PYTHON_BIN" manage.py aggregate_metrics >> "$LOG_FILE" 2>&1 || log "[WARN] aggregate_metrics gab Warnung zurück."

# 4. Cleanup Daily Metrics (Raw Telemetry Retention)
log "Bereinige alte Roh-Telemetriedaten..."
"$PYTHON_BIN" manage.py cleanup_daily_metrics >> "$LOG_FILE" 2>&1 || log "[WARN] cleanup_daily_metrics gab Warnung zurück."

log "TimescaleDB Wartung erfolgreich beendet."
log "========================================================================"
