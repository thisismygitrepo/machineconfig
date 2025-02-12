#!/usr/bin/bash
# 🖥️ Desktop Applications Installation Script

# 🌐 Web Browsers
# Chrome installation:
# wget https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb
# sudo dpkg -i google-chrome-stable_current_amd64.deb

# 📝 Text Editor
/home/linuxbrew/.linuxbrew/bin/brew install neovim

# 📧 Email Client
flatpak install flathub org.mozilla.Thunderbird

# 🖲️ Terminal Emulator
flatpak install flathub org.wezfurlong.wezterm
flatpak run org.wezfurlong.wezterm

# ✏️ Screen Annotation
flatpak install net.christianbeier.Gromit-MPX

# 📋 Clipboard Managers
flatpak install flathub com.github.hluk.copyq --noninteractive

# 🔗 Remote Desktop
sudo nala install remmina remmina-plugin-rdp -y
# Alternative Remmina installation via flatpak:
# flatpak remote-add --user --if-not-exists flathub https://flathub.org/repo/flathub.flatpakrepo
# flatpak install org.freedesktop.Platform
# flatpak install org.freedesktop.Platform.openh264
# flatpak install --user flathub org.remmina.Remmina
# flatpak run --user org.remmina.Remmina

# 🚀 Application Launcher
sudo nala install rofi -y

# 📎 Clipboard History (greenclip)
# https://github.com/fdw/rofimoji?tab=readme-ov-file#dependencies
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


wget -P ~/Downloads https://github.com/erebe/greenclip/releases/download/v4.2/greenclip
chmod +x ~/Downloads/greenclip
sudo mv ~/Downloads/greenclip /usr/bin/
# greenclip daemon &
# rofi -modi "emoji:rofimoji" -show emoji
# rofi -modi "clipboard:greenclip print" -show clipboard -run-command '{cmd}'
# rofi -show drunvv

# rofie -show drun -modi drun -theme ~/.config/rofi/launcher.rasi
# https://github.com/hluk/CopyQ
# https://github.com/SUPERCILEX/gnome-clipboard-history?tab=readme-ov-file
# https://github.com/SUPERCILEX/clipboard-history

ln -s /home/$USER/.nix-profile/share/applications/* /home/$USER/.local/share/applications/
