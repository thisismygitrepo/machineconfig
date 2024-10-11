
# consider wayland instead of xorg

# install chrome:
# wget https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb
# sudo dpkg -i google-chrome-stable_current_amd64.deb

# desktop enviroments.
# sudo nala install gnome-session -y  # gnome 0.3GB
# sudo nala install ubuntu-gnome-desktop -y  # 1.2GB
/home/linuxbrew/.linuxbrew/bin/brew install neovim


flatpak install flathub org.mozilla.Thunderbird
# flatpak install flathub com.brave.Browser
flatpak install flathub org.wezfurlong.wezterm
flatpak run org.wezfurlong.wezterm
flatpak install net.christianbeier.Gromit-MPX

# flatpak install com.tomjwatson.Emote  --noninteractive
flatpak install flathub com.github.hluk.copyq --noninteractive

sudo nala install remmina remmina-plugin-rdp -y
# as per https://remmina.org/how-to-install-remmina/
# flatpak remote-add --user --if-not-exists flathub https://flathub.org/repo/flathub.flatpakrepo
# flatpak install org.freedesktop.Platform
# flatpak install org.freedesktop.Platform.openh264
# flatpak install --user flathub org.remmina.Remmina
# flatpak run --user org.remmina.Remmina

sudo nala install rofi -y


## =============== rofi emoji and its dependencies ==========================
# sudo nala install pipx -y
# pipx install rofimoji
# nix-env -iA nixpkgs.rofi-emoji
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
