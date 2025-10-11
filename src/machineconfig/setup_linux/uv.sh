#!/usr/bin/bash

if [ ! -f "$HOME/.local/bin/uv" ]; then
    echo """📦 uv binary not found
   ⏳ Installing uv package manager..."""
    curl -LsSf https://astral.sh/uv/install.sh | sh
else
    echo """🔄 Updating uv package manager..."""
    $HOME/.local/bin/uv self update
fi
if ! command -v uv &> /dev/null; then
    echo """🔍 uv command not found in PATH ➕ Adding uv to system PATH..."""
    export PATH="$HOME/.local/bin:$PATH"
fi
$HOME/.local/bin/uv python install 3.14
