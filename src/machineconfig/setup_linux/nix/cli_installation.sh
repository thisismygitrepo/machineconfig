#!/bin/bash
#=======================================================================
# 📦 NIX CLI TOOLS INSTALLATION SCRIPT
#=======================================================================
# This script installs various command-line utilities using the Nix package manager

echo """#=======================================================================
🔄 SYSTEM UTILITIES | Installing system management tools
#=======================================================================
"""

# System upgrade tool
echo "📥 Installing topgrade - multi-package-manager upgrade tool..."
nix-env -iA nixpkgs.topgrade || true

# Process management
echo "📥 Installing procs - modern replacement for ps..."
nix-env -iA nixpkgs.procs || true

# File watching
echo "📥 Installing watchexec - executes commands when files change..."
nix-env -iA nixpkgs.watchexec || true

echo """#=======================================================================
📂 FILE MANAGEMENT | Installing file browsers and utilities
#=======================================================================
"""

# Terminal file managers
echo "📥 Installing xplr - hackable file explorer..."
nix-env -iA nixpkgs.xplr || true

echo "📥 Installing nnn - fast and flexible file manager..."
nix-env -iA nixpkgs.nnn || true

echo "📥 Installing joshuto - ranger-like file manager in Rust..."
nix-env -iA nixpkgs.joshuto || true

echo "📥 Installing lf - terminal file manager..."
nix-env -iA nixpkgs.lf || true

echo "📥 Installing broot - directory navigation tool..."
nix-env -iA nixpkgs.broot || true

echo "📥 Installing tere - faster alternative to cd..."
nix-env -iA nixpkgs.tere || true

# Disk usage analyzers
echo "📥 Installing dua - disk usage analyzer..."
nix-env -iA nixpkgs.dua || true

echo "📥 Installing diskonaut - terminal disk space navigator..."
nix-env -iA nixpkgs.diskonaut || true

# File cleanup
echo "📥 Installing kondo - cleanup tool for dev projects..."
nix-env -iA nixpkgs.kondo || true

echo """#=======================================================================
🖼️ VISUAL TOOLS | Installing terminal visualization tools
#=======================================================================
"""

# Terminal visualization
echo "📥 Installing viu - terminal image viewer..."
nix-env -iA nixpkgs.viu || true

echo "📥 Installing bottom - graphical process/system monitor..."
nix-env -iA nixpkgs.bottom || true

echo "📥 Installing delta - syntax-highlighting pager for git..."
nix-env -iA nixpkgs.delta || true

echo """#=======================================================================
🔧 DEVELOPMENT TOOLS | Installing programming utilities
#=======================================================================
"""

# Code editors
echo "📥 Installing helix - modal text editor..."
nix-env -iA nixpkgs.helix || true

# Terminal multiplexer
echo "📥 Installing zellij - terminal workspace with panes..."
nix-env -iA nixpkgs.zellij || true

# Development tools
echo "📥 Installing rust-analyzer - Rust language server..."
nix-env -iA nixpkgs.rust-analyzer || true

echo "📥 Installing tokei - code statistics tool..."
nix-env -iA nixpkgs.tokei || true

# Git interfaces
echo "📥 Installing gitui - terminal UI for git..."
nix-env -iA nixpkgs.gitui || true

echo """#=======================================================================
🔎 SEARCH TOOLS | Installing fuzzy finders and search utilities
#=======================================================================
"""

# Search history
echo "📥 Installing mcfly - search shell history with context..."
nix-env -iA nixpkgs.mcfly || true

# Fuzzy finder
echo "📥 Installing skim - fuzzy finder in Rust..."
nix-env -iA nixpkgs.skim || true

echo """#=======================================================================
🌐 NETWORK & CLOUD TOOLS | Installing file transfer and cloud utilities
#=======================================================================
"""

# File transfer
echo "📥 Installing termscp - terminal file transfer client..."
nix-env -iA nixpkgs.termscp || true

# Cloud storage
echo "📥 Installing rclone - rsync for cloud storage..."
nix-env -iA nixpkgs.rclone || true

echo """#=======================================================================
🛡️ SECURITY TOOLS | Installing password management utilities
#=======================================================================
"""

# Password management
echo "📥 Installing gopass - team password manager with git..."
nix-env -iA nixpkgs.gopass || true

echo """#=======================================================================
📚 DOCUMENTATION | Installing help and reference tools
#=======================================================================
"""

# Command reference
echo "📥 Installing tldr - simplified command documentation..."
nix-env -iA nixpkgs.tldr || true

# Shell alternatives
echo "📥 Installing nushell - modern shell alternative..."
nix-env -iA nixpkgs.nushell || true

echo """#=======================================================================
✅ INSTALLATION COMPLETE | All Nix CLI tools have been installed
#=======================================================================
"""

# Commented out tools
# echo "📥 Installing ots - one-time secret sharing..."
# nix-env -iA nixpkgs.ots || true

# echo "📥 Installing qrscan - QR code scanner..."
# nix-env -iA nixpkgs.qrscan || true

