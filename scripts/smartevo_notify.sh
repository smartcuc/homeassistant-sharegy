#!/usr/bin/env bash
# ==============================================================================
# Sharegy / smartEvo Automated Failure Escalation Helper
# ==============================================================================
# Intercepts script failures and opens an incident ticket in moniy
# ==============================================================================

notify_smartevo_failure() {
    local EXIT_CODE=$?
    local SCRIPT_NAME="$(basename "$0")"

    # Only escalate if script exited with error (non-zero)
    if [ "$EXIT_CODE" -ne 0 ]; then
        local HOSTNAME_STR="$(hostname 2>/dev/null || echo "sharegy-host")"
        local LOG_TARGET="${LOG_FILE:-/var/log/sharegy/${SCRIPT_NAME}.log}"
        local LOG_SNIPPET=""

        if [ -f "$LOG_TARGET" ]; then
            LOG_SNIPPET="$(tail -n 25 "$LOG_TARGET" 2>/dev/null | tr '\n' ' ' | sed 's/"/\\"/g')"
        else
            LOG_SNIPPET="Kein Logfile gefunden unter $LOG_TARGET"
        fi

        local TITLE="🚨 Cronjob Fehlgeschlagen: ${SCRIPT_NAME}"
        local DESC="Der Cronjob '${SCRIPT_NAME}' auf Host '${HOSTNAME_STR}' wurde mit Fehlercode ${EXIT_CODE} beendet.\n\nLetzte Logzeilen:\n${LOG_SNIPPET}"

        # Resolve moniy endpoint & key
        local TARGET_URL="${MONIY_URL:-https://mon.smartevo.de}"
        local TARGET_KEY="${MONIY_S2S_KEY:-nexus-s2s-sharegy-factofy-production-auth-key-change-me}"

        if [ -n "$TARGET_URL" ] && [ -n "$TARGET_KEY" ] && command -v curl >/dev/null 2>&1; then
            curl -s -X POST "${TARGET_URL}/api/v1/helpdesk/escalations" \
                -H "X-Moniy-S2S-Key: ${TARGET_KEY}" \
                -H "Content-Type: application/json" \
                -d "{\"source_platform\": \"sharegy\", \"title\": \"${TITLE}\", \"description\": \"${DESC}\", \"severity\": \"high\"}" >/dev/null 2>&1 || true
        fi
    fi
}
