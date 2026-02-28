#!/usr/bin/env bash
set -e

# ── Guards ─────────────────────────────────────────────────────────────────
[[ -n "$VAULT_PATH" ]]  || { echo "❌ VAULT_PATH not set."; exit 1; }
[[ -n "$KNOWER_ENV" ]]  || { echo "❌ KNOWER_ENV not set (dev|prod)."; exit 1; }
[[ -n "$KNOWER_HOME" ]] || { echo "❌ KNOWER_HOME not set."; exit 1; }

CORE_PORT="${CORE_PORT:-8000}"
QMD_COLLECTION="vault"
EMBED_FLAG="$HOME/.local/share/knower/embed_done"

echo ""
echo "╔══════════════════════════════╗"
echo "║     Knower — Core            ║"
echo "╚══════════════════════════════╝"
echo ""
echo "  ENV   : $KNOWER_ENV"
echo "  VAULT : $VAULT_PATH"
echo "  PORT  : $CORE_PORT"
echo ""

# ── Init vault dir ──────────────────────────────────────────────────────
mkdir -p "$VAULT_PATH"

QMD_VAULT_STATE="$HOME/.local/share/knower/qmd_vault"

# ── Detect vault path change ───────────────────────────────────────────────
if [[ -f "$QMD_VAULT_STATE" ]]; then
  PREVIOUS_VAULT=$(cat "$QMD_VAULT_STATE")
  if [[ "$PREVIOUS_VAULT" != "$VAULT_PATH" ]]; then
    echo "[start] Vault path changed ($PREVIOUS_VAULT → $VAULT_PATH). Resetting QMD..."
    qmd collection remove "$QMD_COLLECTION" 2>/dev/null || true
    rm -f "$EMBED_FLAG"
  fi
fi

# Write current vault path as state
echo "$VAULT_PATH" > "$QMD_VAULT_STATE"

# ── QMD collection (idempotent) ─────────────────────────────────────────
if ! qmd collection list 2>/dev/null | grep -q "$QMD_COLLECTION"; then
  echo "[start] Creating QMD collection..."
  qmd collection add "$VAULT_PATH" --name "$QMD_COLLECTION"
  qmd context add "qmd://vault" "Personal knowledge vault for projects and tasks"
else
  echo "[start] QMD collection exists — skipping."
fi

# ──  BM25 index (fast, always run) ───────────────────────────────────────
echo "[start] Running qmd update..."
qmd update

# ──  Embed (slow — skip if already done) ─────────────────────────────────
if [[ ! -f "$EMBED_FLAG" ]]; then
  echo "[start] No embeddings found. Running qmd embed (first boot — may take a few minutes)..."
  qmd embed
  touch "$EMBED_FLAG"
  echo "[start] Embeddings done."
else
  echo "[start] Embeddings exist — skipping."
fi

# ── Start FastAPI ───────────────────────────────────────────────────────
cd "$KNOWER_HOME/core"

if [[ "$KNOWER_ENV" == "dev" ]]; then
  echo "[start] Starting uvicorn (dev, hot reload)..."
  exec uvicorn main:app \
    --host 127.0.0.1 \
    --port "$CORE_PORT" \
    --reload \
    --log-level debug
else
  echo "[start] Starting uvicorn (prod)..."
  exec uvicorn main:app \
    --host 127.0.0.1 \
    --port "$CORE_PORT" \
    --log-level info
fi