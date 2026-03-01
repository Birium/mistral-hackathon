#!/usr/bin/env bash
set -e

# ── Helpers ────────────────────────────────────────────────────────────────
ok()   { echo "  ✅ $*"; }
fail() { echo "  ❌ $*"; exit 1; }
info() { echo "  ➜  $*"; }

echo ""
echo "╔══════════════════════════════╗"
echo "║     Knower — Installer       ║"
echo "╚══════════════════════════════╝"
echo ""

KNOWER_HOME="$(cd "$(dirname "$0")" && pwd)"

# ── 1. Platform check ──────────────────────────────────────────────────────
[[ "$(uname)" == "Darwin" ]] || fail "Knower only supports macOS."
ok "macOS detected"

# ── 2. Dependency checks ───────────────────────────────────────────────────
check_version() {
  local cmd=$1 flag=$2 min=$3 label=$4
  raw=$($cmd $flag 2>&1 | head -1 | grep -oE '[0-9]+\.[0-9]+' | head -1)
  major=$(echo "$raw" | cut -d. -f1)
  if [[ -z "$major" || "$major" -lt "$min" ]]; then
    fail "$label >= $min required (found: ${raw:-none}). Install from https://$(echo $label | tr '[:upper:]' '[:lower:]').org"
  fi
  ok "$label $raw"
}

check_version python3 --version 3 "Python"
check_version node   --version  22 "Node.js"

command -v npm &>/dev/null || fail "npm not found. Install Node.js 22+."
ok "npm $(npm --version)"

command -v uv &>/dev/null || fail "uv not found. Install: curl -Ls https://astral.sh/uv/install.sh | sh"
ok "uv $(uv --version | awk '{print $2}')"

# ── 3. Install QMD globally ────────────────────────────────────────────────
info "Installing @tobilu/qmd globally..."
npm install -g @tobilu/qmd --silent
ok "qmd $(qmd --version 2>/dev/null || echo 'installed')"

# ── 4. Pre-download QMD models ─────────────────────────────────────────────
info "Pre-downloading QMD models (~2 GB, this may take several minutes)..."

QMD_WARMUP_DIR="$(mktemp -d)"

cat > "$QMD_WARMUP_DIR/warmup.md" << 'EOF'
# Knower warmup
This file is used during installation to pre-download QMD models.
EOF

qmd collection add "$QMD_WARMUP_DIR" --name _knower_warmup 2>/dev/null || true

# BM25 index — validates the collection before model downloads
qmd update 2>/dev/null || true

# Downloads embedding model (~300 MB)
info "  [1/2] Downloading embedding model (~300 MB)..."
qmd embed 2>/dev/null || true

# Downloads query-expansion (~1.1 GB) + reranker (~640 MB)
info "  [2/2] Downloading query-expansion and reranker models (~1.7 GB)..."
qmd query "warmup" -n 1 2>/dev/null || true

# Teardown
qmd collection remove _knower_warmup 2>/dev/null || true
rm -rf "$QMD_WARMUP_DIR"

ok "QMD models cached → ~/.cache/qmd/models/"

# ── 5. Python venv + deps ──────────────────────────────────────────────────
info "Creating Python venv in core/.venv..."
cd "$KNOWER_HOME/core"
uv venv .venv --python python3 --quiet
uv pip install --quiet -e . --python .venv/bin/python
cd "$KNOWER_HOME"
ok "Python venv ready"

# ── 6. Runtime dirs ────────────────────────────────────────────────────────
mkdir -p ~/.config/knower
mkdir -p ~/.local/share/knower/logs
ok "Runtime dirs ready"

# ── 7. Write KNOWER_HOME to config (preserve existing values) ──────────────
CONFIG="$HOME/.config/knower/config"

if grep -q "^KNOWER_HOME=" "$CONFIG" 2>/dev/null; then
  sed -i '' "s|^KNOWER_HOME=.*|KNOWER_HOME=$KNOWER_HOME|" "$CONFIG"
else
  echo "KNOWER_HOME=$KNOWER_HOME" >> "$CONFIG"
fi

if ! grep -q "^CORE_PORT=" "$CONFIG" 2>/dev/null; then
  echo "CORE_PORT=8000" >> "$CONFIG"
fi

ok "Config written → $CONFIG"

# ── 8. CLI symlink ─────────────────────────────────────────────────────────
chmod +x "$KNOWER_HOME/knower"
info "Creating symlink at /usr/local/bin/knower (may ask for password)..."
sudo ln -sf "$KNOWER_HOME/knower" /usr/local/bin/knower
ok "CLI linked"

# ── Done ───────────────────────────────────────────────────────────────────
echo ""
echo "✅ Knower installed. Next steps:"
echo ""
echo "   knower config vault ~/my-vault   # set your vault path"
echo "   knower start                     # start knower"
echo ""
