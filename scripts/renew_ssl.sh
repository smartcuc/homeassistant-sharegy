#!/usr/bin/env bash
# ==============================================================================
# Sharegy – Automated Let's Encrypt / SSL Certificate Renewal & Health Check
# ==============================================================================
# Features:
#  - Führt certbot renew non-interaktiv aus
#  - Automatischer Nginx Reload nach erfolgreichem Renewal (Post-Hook)
#  - Prüfung des Ablaufdatums des Zertifikats via OpenSSL
#  - Validierung des Live-HTTPS-Endpunkts (https://sharegy.de/api/operations/status/)
#  - Warnung bei Zertifikaten mit < 14 Tagen Restlaufzeit
# ==============================================================================

set -eo pipefail

LOG_FILE="${LOG_FILE:-/var/log/sharegy/ssl_renew.log}"
CERT_DOMAIN="${CERT_DOMAIN:-sharegy.de}"
CERT_PATH="/etc/letsencrypt/live/${CERT_DOMAIN}/fullchain.pem"
CHECK_URL="https://${CERT_DOMAIN}/api/operations/status/"

mkdir -p "$(dirname "$LOG_FILE")"

log() {
    local MSG="[$(date +"%Y-%m-%d %H:%M:%S")] $1"
    echo "$MSG"
    echo "$MSG" >> "$LOG_FILE" 2>&1 || true
}

log "========================================================================"
log "Starte SSL-Zertifikatsprüfung und Renewal für Domain: '$CERT_DOMAIN'..."

# 1. Certbot Renewal ausführen
if command -v certbot >/dev/null 2>&1; then
    log "Führe certbot renew aus..."
    certbot renew --non-interactive --quiet --post-hook "systemctl reload nginx" >> "$LOG_FILE" 2>&1 || {
        log "[WARN] certbot renew gab einen Fehler zurück. Siehe Logs."
    }
else
    log "[WARN] certbot ist nicht installiert oder nicht im PATH."
fi

# 2. Zertifikats-Ablaufdatum prüfen
if [ -f "$CERT_PATH" ]; then
    EXPIRY_DATE="$(openssl x509 -enddate -noout -in "$CERT_PATH" | cut -d= -f2)"
    EXPIRY_EPOCH="$(date -d "$EXPIRY_DATE" +%s 2>/dev/null || date -j -f "%b %d %T %Y %Z" "$EXPIRY_DATE" +%s 2>/dev/null || echo 0)"
    NOW_EPOCH="$(date +%s)"
    
    if [ "$EXPIRY_EPOCH" -gt 0 ]; then
        DAYS_LEFT=$(( (EXPIRY_EPOCH - NOW_EPOCH) / 86400 ))
        log "Zertifikat für '$CERT_DOMAIN' gültig bis: $EXPIRY_DATE (Restlaufzeit: $DAYS_LEFT Tage)"
        
        if [ "$DAYS_LEFT" -le 14 ]; then
            log "[CRITICAL] Zertifikat läuft in weniger als 14 Tagen ab ($DAYS_LEFT Tage)! Bitte manuell prüfen."
        fi
    fi
else
    log "[WARN] Kein lokales Zertifikat unter '$CERT_PATH' gefunden."
fi

# 3. HTTPS Endpunkt-Gesundheitsprüfung
if command -v curl >/dev/null 2>&1; then
    HTTP_CODE="$(curl -s -o /dev/null -w "%{http_code}" --connect-timeout 10 "$CHECK_URL" || echo "000")"
    if [ "$HTTP_CODE" -eq 200 ] || [ "$HTTP_CODE" -eq 301 ] || [ "$HTTP_CODE" -eq 302 ]; then
        log "HTTPS-Verbindung zu '$CHECK_URL' erfolgreich (HTTP $HTTP_CODE)."
    else
        log "[WARN] HTTPS-Verbindung zu '$CHECK_URL' lieferte HTTP Status $HTTP_CODE!"
    fi
fi

log "SSL-Prüfung abgeschlossen."
log "========================================================================"
