#!/usr/bin/bash


echo """📧 EMAIL CLIENT | Installing Thunderbird"""
echo "📥 Installing Thunderbird via Flatpak..."
flatpak install flathub org.mozilla.Thunderbird


echo """✏️ SCREEN ANNOTATION | Installing Gromit-MPX"""
echo "📥 Installing Gromit-MPX via Flatpak..."
flatpak install net.christianbeier.Gromit-MPX

echo """📋 CLIPBOARD MANAGERS | Installing CopyQ"""
echo "📥 Installing CopyQ via Flatpak..."
flatpak install flathub com.github.hluk.copyq --noninteractive

echo """🔗 REMOTE DESKTOP | Installing Remmina"""
echo "📥 Installing Remmina and RDP plugin..."
sudo nala install remmina remmina-plugin-rdp -y

# Alternative Remmina installation via flatpak (reference)
# echo "📥 Setting up Flatpak repositories..."
# flatpak remote-add --user --if-not-exists flathub https://flathub.org/repo/flathub.flatpakrepo
# flatpak install org.freedesktop.Platform
# flatpak install org.freedesktop.Platform.openh264
# flatpak install --user flathub org.remmina.Remmina
# flatpak run --user org.remmina.Remmina

echo """🚀 APPLICATION LAUNCHER | Installing Rofi
"""
echo "📥 Installing Rofi application launcher..."
sudo nala install rofi -y

echo """📎 CLIPBOARD HISTORY | Installing Greenclip
"""
# Session type detection (reference)
# session_type=$(echo $XDG_SESSION_TYPE)
# if [ "$session_type" == "x11" ]; then
#     echo "Detected X11 session. Installing X11-related packages and tools..."
#     sudo nala install xdotool xsel xclip -y
# elif [ "$session_type" == "wayland" ]; then
#     echo "Detected Wayland session. Installing Wayland-related packages and tools..."
#     sudo nala install wl-copy wtype -y
# else
#     echo "Unknown session type: $session_type"
#     exit 1
# fi

echo "📥 Downloading and installing Greenclip clipboard manager..."
wget -P ~/Downloads https://github.com/erebe/greenclip/releases/download/v4.2/greenclip
chmod +x ~/Downloads/greenclip
sudo mv ~/Downloads/greenclip /usr/bin/

echo "ℹ️ Usage instructions:"
echo "- Start daemon: greenclip daemon &"
echo "- With Rofi: rofi -modi \"clipboard:greenclip print\" -show clipboard -run-command '{cmd}'"
echo "- For emoji picker: rofi -modi \"emoji:rofimoji\" -show emoji"
echo "- Application launcher: rofi -show drun"

echo """🔄 APPLICATION LINKING | Linking applications to user space
"""
echo "🔗 Creating application symlinks..."
ln -s /home/$USER/.nix-profile/share/applications/* /home/$USER/.local/share/applications/

echo """✅ INSTALLATION COMPLETE | Desktop applications have been installed
"""
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

