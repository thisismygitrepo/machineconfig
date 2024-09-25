
# consider wayland instead of xorg

# install chrome:
# wget https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb
# sudo dpkg -i google-chrome-stable_current_amd64.deb

# desktop enviroments.
# sudo nala install gnome-session -y  # gnome 0.3GB
# sudo nala install ubuntu-gnome-desktop -y  # 1.2GB
/home/linuxbrew/.linuxbrew/bin/brew install neovim


flatpak install flathub org.mozilla.Thunderbird
flatpak install flathub com.brave.Browser
flatpak install flathub org.wezfurlong.wezterm
flatpak run org.wezfurlong.wezterm
flatpak install com.tomjwatson.Emote  --noninteractive
flatpak install flathub com.github.hluk.copyq --noninteractive
sudo nala install remmina remmina-plugin-rdp -y

sudo nala install rofie
sudo nala install pipx
sudo pipx install rofimoji
# https://github.com/fdw/rofimoji?tab=readme-ov-file#dependencies


wget -P ~/Downloads https://github.com/erebe/greenclip/releases/download/v4.2/greenclip
chmod +x ~/Downloads/greenclip
sudo mv ~/Downloads/greenclip /usr/bin/
# greenclip daemon &

# rofi -modi "emoji:rofimoji" -show emoji
# rofi -modi "clipboard:greenclip print" -show clipboard -run-command '{cmd}'


# rofie -show drun -modi drun -theme ~/.config/rofi/launcher.rasi
nix-env -iA nixpkgs.rofi-emoji
# https://github.com/hluk/CopyQ
# https://github.com/SUPERCILEX/gnome-clipboard-history?tab=readme-ov-file
# https://github.com/SUPERCILEX/clipboard-history

ln -s /home/$USER/.nix-profile/share/applications/* /home/$USER/.local/share/applications/
