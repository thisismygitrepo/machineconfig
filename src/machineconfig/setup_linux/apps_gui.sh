#!/bin/bash
# 🖥️ GUI APPLICATIONS AND DESKTOP ENVIRONMENT SETUP SCRIPT
# This script installs graphical user interfaces and desktop environments

echo """📦 INSTALLING GUI COMPONENTS | Setting up desktop environment
"""

# echo "📥 Installing Nautilus file manager..."
# sudo nala install nautilus -y  # 📂 graphical file manager
# sudo nala install x11-apps  # 🎨 few graphical test apps like xeyes

echo "📥 Installing XRDP - Remote Desktop Protocol server..."
sudo nala install xrdp -y  # 🔌 remote desktop protocol

# echo "📥 Installing X.Org server and components..."
# sudo nala install xorg -y  # 🎯 xorg server
# sudo nala install xinit -y  # 🚀 xorg init
# sudo nala install xserver-xorg -y  # 🖼️ xorg server

echo "📥 Installing XFCE4 desktop environment..."
sudo nala install xfce4 -y  # 🏠 xfce4 desktop environment

echo "📥 Installing XFCE4 additional components..."
sudo nala install xfce4-goodies -y  # ✨ xfce4 desktop environment extras

echo """🔧 CONFIGURING XRDP | Setting up Remote Desktop service
"""

# Back up original configuration
echo "📄 Creating backup of XRDP configuration..."
sudo cp /etc/xrdp/xrdp.ini /etc/xrdp/xrdp.ini.bak

# Change default port to avoid conflict with Windows RDP
echo "🔢 Changing XRDP port to 3391..."
sudo sed -i 's/3389/3391/g' /etc/xrdp/xrdp.ini

# Configure color depth and display settings
echo "🎨 Configuring display quality settings..."
sudo sed -i 's/max_bpp=32/#max_bpp=32\nmax_bpp=128/g' /etc/xrdp/xrdp.ini
sudo sed -i 's/xserverbpp=24/#xserverbpp=24\nxserverbpp=128/g' /etc/xrdp/xrdp.ini

# Set default session
echo "🖥️ Setting up default XFCE4 session..."
echo xfce4-session > ~/.xsession

# Configure startup window manager
echo "🚀 Configuring window manager startup..."
sudo sed -i 's/test/#test/g' /etc/xrdp/startwm.sh
sudo sed -i 's/exec/#exec/g' /etc/xrdp/startwm.sh
echo "startxfce4" | sudo tee -a /etc/xrdp/startwm.sh

echo """🚀 STARTING SERVICES | Initializing XRDP service
"""

echo "🔄 Starting XRDP service..."
sudo /etc/init.d/xrdp start

echo """✅ SETUP COMPLETE | GUI environment has been configured
"""
echo "ℹ️ Connect to this machine via Remote Desktop using port 3391"
# Alternative commands:
# sudo systemctl restart xrdp
# sudo service xrdp restart

