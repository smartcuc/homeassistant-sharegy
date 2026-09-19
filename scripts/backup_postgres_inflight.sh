#!/usr/bin/env bash
# ==============================================================================
# In-Flight 5-Minute PostgreSQL Delta Backup Streamer for Sharegy / Factofy
# Streams compressed PostgreSQL dumps to moniy Vault without local disk bloat
# ==============================================================================

set -euo pipefail

# Configuration
MONIY_URL="${MONIY_URL:-https://mon.sharegy.de}"
MONIY_KEY="${MONIY_S2S_KEY:-moniy-s2s-sharegy-factofy-production-auth-key-change-me}"
TENANT_ID="${BACKUP_TENANT_ID:-sharegy}"
DB_NAME="${POSTGRES_DB:-sharegy_db}"
DB_USER="${POSTGRES_USER:-postgres}"
DB_HOST="${POSTGRES_HOST:-127.0.0.1}"
DB_PORT="${POSTGRES_PORT:-5432}"

TIMESTAMP=$(date -u +"%Y%m%d_%H%M%S")
PREFIX="pg_delta_${DB_NAME}"

echo "[$(date -u)] Starting in-flight database backup stream to moniy for tenant '$TENANT_ID'..."

# Stream directly through pipe: pg_dump -> gzip -> curl stream
PGPASSWORD="${POSTGRES_PASSWORD:-}" pg_dump \
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
