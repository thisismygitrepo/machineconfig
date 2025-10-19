#!/usr/bin/env bash

# Install or update uv (universal version manager) on macOS
# Mirrors Linux uv installer but adapts PATH and locations for mac

set -euo pipefail

UV_BIN="$HOME/.local/bin/uv"

if [ ! -f "$UV_BIN" ]; then
    echo "📦 uv binary not found — installing uv to $HOME/.local/bin..."
    mkdir -p "$HOME/.local/bin"
    curl -LsSf https://astral.sh/uv/install.sh | sh
    echo "✅ uv installed to $UV_BIN"
else
    echo "🔄 uv binary found — attempting self-update..."
    "$UV_BIN" self update || true
fi

# Ensure local bin is in PATH for this run
export PATH="$HOME/.local/bin:$PATH"

if ! command -v uv &> /dev/null; then
    echo "⚠️ uv not found in PATH even after install; add \"$HOME/.local/bin\" to your shell profile"
else
    echo "🔧 uv available: $(command -v uv)"
fi

# Example uv usage: ensure Python 3.14 is available (adjust as needed)
if command -v uv &> /dev/null; then
    echo "📥 Ensuring Python 3.14 via uv (if supported)"
    # uv may manage various runtimes; this is an example command and will be skipped gracefully if unsupported
    uv python install 3.14 || true
fi

echo "✅ uv setup complete"
