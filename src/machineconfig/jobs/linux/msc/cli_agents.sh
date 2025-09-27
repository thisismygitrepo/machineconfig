#!/bin/bash


# Terminal-based CLI agents and tools for productivity and coding.
npm install -g @github/copilot
npm install -g @google/gemini-cli
npm install -g @charmland/crush
npm install -g opencode-ai@latest  # or curl -fsSL https://opencode.ai/install | bash
uv tool install --force --python python3.12 --with pip aider-chat@latest
curl -fsSL https://app.factory.ai/cli | sh
# WARP TERMINAL CLI
# droid


# cursor-cli
curl https://cursor.com/install -fsS | bash
cd $HOME/Downloads
curl --proto '=https' --tlsv1.2 -sSf "https://desktop-release.q.us-east-1.amazonaws.com/latest/q-x86_64-linux.zip" -o "q.zip"
unzip q.zip
./q/install.sh  # goes to ~/.local/bin.
rm q.zip
rm -rfd q

# Vscode extensions for AI-assisted coding.
# Github copilot
# Roo
# Cline
# Kilocode
# Continue
# CodeGPT
# qodo (and cli)

# Editors based on AI
# Kiro
# Cursor
# Warp

