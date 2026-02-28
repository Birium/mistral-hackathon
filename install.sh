#!/usr/bin/env bash
set -e

echo "Installing Knower CLI..."

# Get absolute path of the current directory
KNOWER_DIR="$(cd "$(dirname "$0")" && pwd)"
CLI_PATH="$KNOWER_DIR/knower"

# Ensure the CLI script is executable
chmod +x "$CLI_PATH"

# Create symlink
DEST_PATH="/usr/local/bin/knower"
echo "Creating symlink at $DEST_PATH (may require sudo password)..."
sudo ln -sf "$CLI_PATH" "$DEST_PATH"

echo ""
echo "✅ Knower installed successfully!"
echo "You can now use the 'knower' command from anywhere."
echo ""
echo "Try running:"
echo "  knower start"
echo "  knower visualize"
echo "  knower status"
