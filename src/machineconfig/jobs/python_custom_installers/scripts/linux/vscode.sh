#!/bin/bash
#=======================================================================
# 💻 VS CODE INSTALLATION SCRIPT 💻
#=======================================================================
# This script installs Visual Studio Code on Ubuntu/Debian-based Linux distributions
# Reference: https://code.visualstudio.com/docs/setup/linux

echo """
#=======================================================================
🔑 ADDING REPOSITORY KEYS | Setting up Microsoft repository
#=======================================================================
"""

# Check if GPG key is already installed
if [ ! -f /etc/apt/keyrings/packages.microsoft.gpg ]; then
    echo "🔐 Downloading and installing Microsoft GPG key..."
    wget -qO- https://packages.microsoft.com/keys/microsoft.asc | gpg --dearmor > packages.microsoft.gpg
    sudo install -D -o root -g root -m 644 packages.microsoft.gpg /etc/apt/keyrings/packages.microsoft.gpg
    rm -f packages.microsoft.gpg
else
    echo "✅ Microsoft GPG key already installed"
fi

# Check if VS Code repository is already added
if [ ! -f /etc/apt/sources.list.d/vscode.list ]; then
    echo "📝 Adding VS Code repository to sources list..."
    echo "deb [arch=amd64,arm64,armhf signed-by=/etc/apt/keyrings/packages.microsoft.gpg] https://packages.microsoft.com/repos/code stable main" | sudo tee /etc/apt/sources.list.d/vscode.list > /dev/null
else
    echo "✅ VS Code repository already configured"
fi

echo """
#=======================================================================
📦 INSTALLING VS CODE | Updating and installing packages
#=======================================================================
"""

# Update package lists for VS Code repository only
echo "🔄 Updating package lists for VS Code repository..."
sudo nala update -o Dir::Etc::sourcelist="sources.list.d/vscode.list" -o Dir::Etc::sourceparts="-" -o APT::Get::List-Cleanup="0"

# Install VS Code
echo "📥 Installing Visual Studio Code..."
sudo nala install code -y

echo """
#=======================================================================
🔄 CHECKING FOR VS CODE INSIDERS | Updating if installed
#=======================================================================
"""

# Check if VS Code Insiders is installed and update if found
if command -v code-insiders >/dev/null 2>&1; then
    echo "🔍 VS Code Insiders found, updating..."
    sudo nala install code-insiders -y
else
    echo "ℹ️ VS Code Insiders not installed, skipping"
fi

echo """
#=======================================================================
✅ INSTALLATION COMPLETE | VS Code has been installed successfully
#=======================================================================
"""
echo "🚀 You can now launch VS Code from your applications menu or by typing 'code' in terminal"

