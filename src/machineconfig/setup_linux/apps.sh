#!/usr# --BLOCK:PACKAGE_MANAGERS--
echo """#=======================================================================
📥 PACKAGE MANAGERS | Installing and configuring system package managers
#======================================================================="""n/bash
#=====# --BLOCK:NIX_PACKAGE_MANAGER--
echo """#=======================================================================
❄️ NIX PACKAGE MANAGER | Installing cross-platform package manager
#======================================================================="""==============# --BLOCK:SYSTEM_UTILITIES--
echo """#=======================================================================
🛠️ SYSTEM UTILITIES | Installing essential system tools
#======================================================================="""=========# --BLOCK:UV_PYTHON_INSTALLER--
echo """#=======================================================================
⚡ UV PYTHON INSTALLER | Installing fast Python package manager
#======================================================================="""=======================# --BLOCK:DEVELOPMENT_TOOLS--
echo """#=======================================================================
🔧 DEVELOPMENT TOOLS | Installing git and system utilities
#======================================================================="""========
# 📦 SYSTEM PACKAGE MANAGERS AND UTILITIES SETUP
#=======================================================================
# This script installs and configures essential package managers and utilities

echo """#=======================================================================
📥 PACKAGE MANAGERS | Installing and configuring system package managers
#=======================================================================
"""

# Update apt and install nala
echo "🔄 Updating apt package lists..."
sudo apt update -y || true

echo "📥 Installing nala package manager..."
sudo apt install nala -y || true  # 🚀 Fast parallel apt manager

echo "📥 Installing essential network tools..."
sudo nala install curl wget gpg lsb-release apt-transport-https -y || true

# Install Nix Package Manager
echo """#=======================================================================
❄️ NIX PACKAGE MANAGER | Installing cross-platform package manager
#=======================================================================
"""
# echo "📥 Installing Nix..."
# curl -L https://nixos.org/nix/install | sh
# . ~/.nix-profile/etc/profile.d/nix.sh

# # Install Homebrew
# echo """#=======================================================================
# 🍺 HOMEBREW PACKAGE MANAGER | Installing macOS-style package manager
# #=======================================================================
# """
# echo "📥 Installing Homebrew..."
# export NONINTERACTIVE=1
# /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

echo """#=======================================================================
🛠️ SYSTEM UTILITIES | Installing essential system tools
#=======================================================================
"""

# Filesystem utilities
echo "📂 Installing filesystem utilities..."
sudo nala install fuse3 -y || true
sudo nala install nfs-common -y || true
sudo nala install redis-tools -y || true

# Python package installer
echo """#=======================================================================
⚡ UV PYTHON INSTALLER | Installing fast Python package manager
#=======================================================================
"""
echo "📥 Installing uv Python package installer..."
curl -LsSf https://astral.sh/uv/install.sh | sh

# Node.js via NVM
# --BLOCK:NODE_JS_ENVIRONMENT--
echo """
#=======================================================================
📝 NODE.JS ENVIRONMENT | Installing Node Version Manager
#======================================================================="""

echo "📥 Installing Node Version Manager (NVM)..."
curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.40.3/install.sh | bash

# Set up NVM environment
echo "🔧 Configuring NVM environment..."
export NVM_DIR="$HOME/.nvm"
[ -s "$NVM_DIR/nvm.sh" ] && \. "$NVM_DIR/nvm.sh"
[ -s "$NVM_DIR/bash_completion" ] && \. "$NVM_DIR/bash_completion"

echo "📥 Installing latest Node.js..."
nvm install node || true

# Development tools
echo """#=======================================================================
🔧 DEVELOPMENT TOOLS | Installing git and system utilities
#=======================================================================
"""
echo "📥 Installing git and system tools..."
sudo nala install git net-tools htop nano -y || true

echo """#=======================================================================
✅ INSTALLATION COMPLETE | System package managers and utilities set up
#=======================================================================
"""

