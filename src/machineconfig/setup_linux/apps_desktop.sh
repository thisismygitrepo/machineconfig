
# consider wayland instead of xorg

# install chrome:
# wget https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb
# sudo dpkg -i google-chrome-stable_current_amd64.deb

# desktop enviroments.
# sudo nala install gnome-session -y  # gnome 0.3GB
# sudo nala install ubuntu-gnome-desktop -y  # 1.2GB


yes '' | sed 3q; echo "----------------------------- installing Thunderbird & Brave ----------------------------"; yes '' | sed 3q
flatpak install flathub org.mozilla.Thunderbird
flatpak install flathub com.brave.Browser
flatpak install flathub org.wezfurlong.wezterm
flatpak run org.wezfurlong.wezterm
ln -s /home/$USER/.nix-profile/share/applications/* /home/$USER/.local/share/applications/

yes '' | sed 3q; echo "----------------------------- installing remmina--------------------------------"; yes '' | sed 3q
sudo nala install remmina remmina-plugin-rdp -y

# as per https://brave.com/linux/
# sudo nala install curl
# sudo curl -fsSLo /usr/share/keyrings/brave-browser-archive-keyring.gpg https://brave-browser-apt-release.s3.brave.com/brave-browser-archive-keyring.gpg
# echo "deb [signed-by=/usr/share/keyrings/brave-browser-archive-keyring.gpg] https://brave-browser-apt-release.s3.brave.com/ stable main"|sudo tee /etc/apt/sources.list.d/brave-browser-release.list
# sudo nala update
# sudo nala install brave-browser


# as per https://code.visualstudio.com/docs/setup/linux
sudo nala install wget gpg
wget -qO- https://packages.microsoft.com/keys/microsoft.asc | gpg --dearmor > packages.microsoft.gpg
sudo install -D -o root -g root -m 644 packages.microsoft.gpg /etc/apt/keyrings/packages.microsoft.gpg
echo "deb [arch=amd64,arm64,armhf signed-by=/etc/apt/keyrings/packages.microsoft.gpg] https://packages.microsoft.com/repos/code stable main" |sudo tee /etc/apt/sources.list.d/vscode.list > /dev/null
rm -f packages.microsoft.gpg
sudo nala install apt-transport-https
sudo nala update
sudo nala install code # or code-insiders

