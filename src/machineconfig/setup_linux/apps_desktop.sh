
# consider wayland instead of xorg

# install chrome:
# wget https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb
# sudo dpkg -i google-chrome-stable_current_amd64.deb

# desktop enviroments.
# sudo nala install gnome-session -y  # gnome 0.3GB
# sudo nala install ubuntu-gnome-desktop -y  # 1.2GB


flatpak install flathub org.mozilla.Thunderbird
flatpak install flathub com.brave.Browser
flatpak install flathub org.wezfurlong.wezterm
flatpak run org.wezfurlong.wezterm
flatpak install com.tomjwatson.Emote  --noninteractive
flatpak install flathub com.github.hluk.copyq --noninteractive
sudo nala install remmina remmina-plugin-rdp -y

sudo nala install rofie
# rofie -show drun -modi drun -theme ~/.config/rofi/launcher.rasi
nix-env -iA nixpkgs.rofi-emoji
# https://github.com/hluk/CopyQ
# https://github.com/SUPERCILEX/gnome-clipboard-history?tab=readme-ov-file
# https://github.com/SUPERCILEX/clipboard-history


ln -s /home/$USER/.nix-profile/share/applications/* /home/$USER/.local/share/applications/
