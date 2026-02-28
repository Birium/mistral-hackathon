#!/usr/bin/env bash
set -e

VAULT_PATH=${VAULT_PATH:-/vault}
QMD_COLLECTION="vault"

echo "[start] Vault: $VAULT_PATH"

# Init QMD collection (idempotent — safe to re-run)
if ! qmd collection list | grep -q "$QMD_COLLECTION"; then
  echo "[start] Creating QMD collection..."
  qmd collection add "$VAULT_PATH" --name "$QMD_COLLECTION"
  qmd context add qmd://vault "Personal knowledge vault for projects and tasks"
else
  echo "[start] QMD collection already exists, skipping."
fi

# Index files (fast, always run)
echo "[start] Running qmd update..."
qmd update

# Embed only if no vectors yet (slow on first boot, skipped on restart)
VECTOR_COUNT=$(qmd status --json 2>/dev/null | python3 -c "import sys,json; d=json.load(sys.stdin); print(d.get('vectors',0))" 2>/dev/null || echo "0")
if [ "$VECTOR_COUNT" = "0" ]; then
  echo "[start] No embeddings found. Running qmd embed (this may take a while)..."
  qmd embed
else
  echo "[start] Embeddings exist ($VECTOR_COUNT vectors), skipping."
fi

echo "[start] Starting FastAPI..."
exec uvicorn main:app --host 0.0.0.0 --port 8000 --reload