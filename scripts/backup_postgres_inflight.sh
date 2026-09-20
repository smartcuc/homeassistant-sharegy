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

echo "[$(date -u)] Starting in-flight 5-minute database delta stream to moniy (${MONIY_URL}) for tenant '${TENANT_ID}' (DB: ${DB_NAME})..."

# Export lightweight delta SQL: recent records from the last 10 minutes across time-series & transaction tables
generate_delta_sql() {
    cat << 'EOF_HEADER'
-- ==============================================================================
-- Sharegy / smartEvo In-Flight 5-Minute Delta Snapshot
-- ==============================================================================
SET statement_timeout = '30s';
EOF_HEADER

    # Query all public tables that have time-based columns and dump rows from the last 10 minutes
    PGPASSWORD="${PGPASSWORD}" psql \
        -h "$DB_HOST" \
        -p "$DB_PORT" \
        -U "$DB_USER" \
        -d "$DB_NAME" \
        -X -A -t -c "
        SELECT format(
            '-- Table: %I.%I (%I)\n\copy %I.%I FROM STDIN WITH CSV HEADER;\n' ||
            '\copy (SELECT * FROM %I.%I WHERE %I >= NOW() - INTERVAL ''10 minutes'') TO STDOUT WITH CSV HEADER;\n\\.\n',
            t.table_schema, t.table_name, c.column_name,
            t.table_schema, t.table_name,
            t.table_schema, t.table_name, c.column_name
        )
        FROM information_schema.tables t
        JOIN (
            SELECT table_schema, table_name, column_name,
                   ROW_NUMBER() OVER(PARTITION BY table_schema, table_name ORDER BY 
                     CASE column_name 
                       WHEN 'timestamp' THEN 1 
                       WHEN 'created_at' THEN 2 
                       WHEN 'created' THEN 3 
                       WHEN 'time' THEN 4 
                       WHEN 'recorded_at' THEN 5 
                       WHEN 'updated_at' THEN 6 
                       ELSE 10 
                     END) as rn
            FROM information_schema.columns
            WHERE table_schema = 'public'
              AND column_name IN ('timestamp', 'created_at', 'created', 'time', 'recorded_at', 'updated_at')
        ) c ON t.table_schema = c.table_schema AND t.table_name = c.table_name AND c.rn = 1
        WHERE t.table_schema = 'public'
          AND t.table_type = 'BASE TABLE'
        ORDER BY t.table_name;
        " 2>/dev/null | PGPASSWORD="${PGPASSWORD}" psql -h "$DB_HOST" -p "$DB_PORT" -U "$DB_USER" -d "$DB_NAME" -X 2>/dev/null || true
}

# Stream directly through pipe: delta generator -> gzip -> curl stream
generate_delta_sql \
| gzip -c -4 \
| curl -sS -f -X POST "${MONIY_URL}/api/v1/backups/stream" \
    -H "X-Moniy-S2S-Key: ${MONIY_KEY}" \
    -H "X-Moniy-Tenant: ${TENANT_ID}" \
    -H "X-Moniy-Prefix: ${PREFIX}" \
    -H "Content-Type: application/octet-stream" \
    --data-binary @-

echo ""
echo "[$(date -u)] 5-minute delta backup streamed successfully to moniy (${MONIY_URL})."
