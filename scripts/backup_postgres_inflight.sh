#!/usr/bin/env bash
# ==============================================================================
# In-Flight 5-Minute PostgreSQL Delta Backup Streamer for Sharegy / Factofy
# Streams compressed PostgreSQL dumps to moniy Vault without local disk bloat
# ==============================================================================

set -euo pipefail

# Safe helper to parse .env without evaluating arbitrary shell syntax
get_env_val() {
    local key="$1"
    local def="$2"
    local file=""
    for candidate in "./.env" "../.env" "/var/www/sharegy/green/.env" "/var/www/sharegy/.env"; do
        if [ -f "$candidate" ]; then
            file="$candidate"
            break
        fi
    done

    if [ -n "$file" ] && [ -f "$file" ]; then
        local val
        val=$(grep -E "^${key}=" "$file" 2>/dev/null | head -n 1 | cut -d '=' -f2- | sed -e 's/^[[:space:]]*//' -e 's/[[:space:]]*$//' -e 's/^["'\''"]//' -e 's/["'\''"]$//' || true)
        if [ -n "$val" ]; then
            echo "$val"
            return
        fi
    fi
    echo "$def"
}

# Configuration
MONIY_URL="${MONIY_URL:-$(get_env_val MONIY_URL https://mon.smartevo.de)}"
MONIY_KEY="${MONIY_S2S_KEY:-$(get_env_val MONIY_S2S_KEY $(get_env_val NEXUS_SERVER_TO_SERVER_API_KEY nexus-s2s-sharegy-factofy-production-auth-key-change-me))}"
TENANT_ID="${BACKUP_TENANT_ID:-$(get_env_val BACKUP_TENANT_ID sharegy)}"
DB_NAME="${POSTGRES_DB:-$(get_env_val POSTGRES_DB $(get_env_val DB_NAME sharegy))}"
DB_USER="${POSTGRES_USER:-$(get_env_val POSTGRES_USER $(get_env_val DB_USER postgres))}"
DB_HOST="${POSTGRES_HOST:-$(get_env_val POSTGRES_HOST $(get_env_val DB_HOST 127.0.0.1))}"
DB_PORT="${POSTGRES_PORT:-$(get_env_val POSTGRES_PORT $(get_env_val DB_PORT 5432))}"
PGPASSWORD="${POSTGRES_PASSWORD:-$(get_env_val POSTGRES_PASSWORD $(get_env_val DB_PASSWORD ""))}"

TIMESTAMP=$(date -u +"%Y%m%d_%H%M%S")
PREFIX="pg_delta_${DB_NAME}"

echo "[$(date -u)] Starting in-flight database backup stream to moniy (${MONIY_URL}) for tenant '${TENANT_ID}' (DB: ${DB_NAME})..."

# Stream directly through pipe: pg_dump -> gzip -> curl stream
PGPASSWORD="${PGPASSWORD}" pg_dump \
  -h "$DB_HOST" \
  -p "$DB_PORT" \
  -U "$DB_USER" \
  -d "$DB_NAME" \
  -F c \
  --no-owner \
  --no-privileges \
| gzip -c -4 \
| curl -sS -f -X POST "${MONIY_URL}/api/v1/backups/stream" \
    -H "X-Moniy-S2S-Key: ${MONIY_KEY}" \
    -H "X-Moniy-Tenant: ${TENANT_ID}" \
    -H "X-Moniy-Prefix: ${PREFIX}" \
    -H "Content-Type: application/octet-stream" \
    --data-binary @-

echo ""
echo "[$(date -u)] In-flight backup streamed successfully to moniy (${MONIY_URL})."
