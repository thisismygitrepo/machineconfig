#!/bin/bash
#=======================================================================
# 🖥️ WEZTERM TERMINAL INSTALLATION SCRIPT 🖥️
#=======================================================================
# This script installs WezTerm terminal emulator on Ubuntu/Debian-based Linux distributions
# Reference: https://wezfurlong.org/wezterm/install/linux.html

echo """#=======================================================================
🔑 ADDING REPOSITORY KEYS | Setting up WezTerm repository
#=======================================================================
"""

# Add WezTerm GPG key
echo "🔐 Adding WezTerm GPG key..."
curl -fsSL https://apt.fury.io/wez/gpg.key | sudo gpg --yes --dearmor -o /usr/share/keyrings/wezterm-fury.gpg

# Add WezTerm repository
echo "📝 Adding WezTerm repository to sources list..."
echo 'deb [signed-by=/usr/share/keyrings/wezterm-fury.gpg] https://apt.fury.io/wez/ * *' | sudo tee /etc/apt/sources.list.d/wezterm.list

echo """#=======================================================================
📦 INSTALLING WEZTERM | Updating and installing packages
#=======================================================================
"""

# Update package lists
echo "🔄 Updating package lists..."
sudo nala update

# Install WezTerm
echo "📥 Installing WezTerm terminal emulator..."
sudo nala install wezterm -y

echo """#=======================================================================
✅ INSTALLATION COMPLETE | WezTerm has been installed successfully
#=======================================================================
"""
echo "🚀 You can now launch WezTerm from your applications menu or by typing 'wezterm' in terminal"
echo "💡 Configure WezTerm by editing ~/.config/wezterm/wezterm.lua"
echo "🔗 For more information and configuration options, visit: https://wezfurlong.org/wezterm/"
