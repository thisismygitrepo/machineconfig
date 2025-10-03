#!/bin/bash
# 🔤 NERD FONT INSTALLATION SCRIPT 🔤
# This script installs CascadiaCode Nerd Font for enhanced terminal and coding experience

echo """📥 DOWNLOADING | Fetching CascadiaCode Nerd Font
"""

# Navigate to Downloads directory
echo "📂 Changing to Downloads directory..."
cd ~/Downloads

# Download the font archive
echo "🔽 Downloading CascadiaCode Nerd Font..."
curl -LO https://github.com/ryanoasis/nerd-fonts/releases/download/v3.2.1/CascadiaCode.tar.xz

echo """📦 EXTRACTING | Unpacking font archive
"""
# Extract the fonts
echo "📂 Extracting font files..."
tar -xvf CascadiaCode.tar.xz

echo """🔧 INSTALLING | Setting up font files
"""
# Create fonts directory if it doesn't exist
echo "📁 Creating local fonts directory..."
mkdir -p ~/.local/share/fonts

# Move font files to the fonts directory
echo "📋 Moving font files to fonts directory..."
mv ./*.ttf ~/.local/share/fonts

# Update the font cache
echo "🔄 Updating font cache..."
fc-cache -f -v

echo """🧹 CLEANING UP | Removing temporary files
"""
# Clean up downloaded and extracted files
echo "🧹 Removing temporary files..."
rm -rf CascadiaCode
rm CascadiaCode.tar.xz

echo """✅ INSTALLATION COMPLETE | CascadiaCode Nerd Font has been installed
"""
echo "ℹ️ To verify installation, run: fc-list | grep CaskaydiaCove"
echo "💡 USE 'CaskaydiaCove Nerd Font' in VS Code and other applications"
echo "🔄 You may need to restart applications to see the new font"
