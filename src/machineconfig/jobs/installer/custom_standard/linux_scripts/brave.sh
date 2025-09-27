#!/bin/bash
#=======================================================================
# 🦁 BRAVE BROWSER INSTALLATION SCRIPT 🦁
#=======================================================================
# This script installs the Brave browser on Linux systems
# Reference: https://brave.com/linux/

echo """#=======================================================================
🚀 STARTING BRAVE BROWSER INSTALLATION | Installing dependencies
#=======================================================================
"""

# Install curl if not already installed
echo "📥 Installing curl..."
sudo nala install curl -y

echo """#=======================================================================
🔑 ADDING REPOSITORY KEYS | Setting up Brave repository
#=======================================================================
"""

# Add the Brave browser PGP key
echo "🔐 Adding Brave browser archive keyring..."
sudo curl -fsSLo /usr/share/keyrings/brave-browser-archive-keyring.gpg https://brave-browser-apt-release.s3.brave.com/brave-browser-archive-keyring.gpg

# Add the Brave browser repository
echo "📝 Adding Brave repository to sources list..."
echo "deb [signed-by=/usr/share/keyrings/brave-browser-archive-keyring.gpg] https://brave-browser-apt-release.s3.brave.com/ stable main" | sudo tee /etc/apt/sources.list.d/brave-browser-release.list

echo """#=======================================================================
📦 INSTALLING BRAVE BROWSER | Updating and installing packages
#=======================================================================
"""

# Update package lists
echo "🔄 Updating package lists..."
sudo nala update

# Install Brave browser
echo "📥 Installing Brave browser..."
sudo nala install brave-browser -y

echo """#=======================================================================
✅ INSTALLATION COMPLETE | Brave browser has been installed successfully
#=======================================================================
"""
echo "🦁 You can now launch Brave browser from your applications menu or by typing 'brave-browser' in terminal"

