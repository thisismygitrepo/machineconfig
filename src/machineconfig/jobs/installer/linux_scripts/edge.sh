#!/bin/bash
# 🌐 MICROSOFT EDGE INSTALLATION SCRIPT 🌐
# This script installs Microsoft Edge browser on Linux systems

echo """🔑 ADDING REPOSITORY KEYS | Setting up Microsoft repository
"""

# Download and install Microsoft's GPG key
echo "🔐 Downloading Microsoft's GPG key..."
curl https://packages.microsoft.com/keys/microsoft.asc | gpg --dearmor > microsoft.gpg
echo "📝 Installing Microsoft's GPG key to trusted sources..."
sudo install -o root -g root -m 644 microsoft.gpg /etc/apt/trusted.gpg.d/

# Add the Microsoft Edge repository
echo "📝 Adding Microsoft Edge repository to sources list..."
sudo sh -c 'echo "deb [arch=amd64] https://packages.microsoft.com/repos/edge stable main" > /etc/apt/sources.list.d/microsoft-edge-dev.list'

# Clean up temporary files
echo "🧹 Cleaning up temporary files..."
sudo rm microsoft.gpg

echo """📦 INSTALLING MICROSOFT EDGE | Updating and installing packages
"""

# Update package lists
echo "🔄 Updating package lists..."
sudo nala update

# Install Microsoft Edge
echo "📥 Installing Microsoft Edge..."
sudo nala install microsoft-edge-stable

echo """✅ INSTALLATION COMPLETE | Microsoft Edge has been installed successfully
"""
echo "🌐 You can now launch Microsoft Edge from your applications menu or by typing 'microsoft-edge' in terminal"

