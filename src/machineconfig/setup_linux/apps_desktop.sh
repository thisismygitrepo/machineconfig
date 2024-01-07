
# consider wayland instead of xorg

# install chrome:
# wget https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb
# sudo dpkg -i google-chrome-stable_current_amd64.deb

# install snap store
# sudo mv /etc/apt/preferences.d/nosnap.pref ~/Documents/nosnap.backup
# sudo apt update
# sudo apt install snapd

# install development apps:
# sudo snap install pycharm-community --classic
# sudo snap install code --classic
# sudo snap install powershell --classic
# wget https://download-cdn.jetbrains.com/python/pycharm-community-2022.3.tar.gz

# desktop enviroments.
# sudo apt install gnome-session -y  # gnome 0.3GB
# sudo apt install ubuntu-gnome-desktop -y  # 1.2GB


yes '' | sed 3q; echo "----------------------------- installing Thunderbird & Brave ----------------------------"; yes '' | sed 3q
flatpak install flathub org.mozilla.Thunderbird
flatpak install flathub com.brave.Browser
ln -s /home/$USER/.nix-profile/share/applications/* /home/$USER/.local/share/applications/


# as per https://brave.com/linux/
# sudo apt install curl
# sudo curl -fsSLo /usr/share/keyrings/brave-browser-archive-keyring.gpg https://brave-browser-apt-release.s3.brave.com/brave-browser-archive-keyring.gpg
# echo "deb [signed-by=/usr/share/keyrings/brave-browser-archive-keyring.gpg] https://brave-browser-apt-release.s3.brave.com/ stable main"|sudo tee /etc/apt/sources.list.d/brave-browser-release.list
# sudo apt update
# sudo apt install brave-browser


yes '' | sed 3q; echo "----------------------------- installing remmina--------------------------------"; yes '' | sed 3q
sudo apt install remmina remmina-plugin-rdp -y

