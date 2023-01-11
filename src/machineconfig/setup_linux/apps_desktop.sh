
# consider wayland instead of xorg

# install chrome:
wget https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb
sudo dpkg -i google-chrome-stable_current_amd64.deb

# install snap store
sudo mv /etc/apt/preferences.d/nosnap.pref ~/Documents/nosnap.backup
sudo apt update
sudo apt install snapd

# install development apps:
sudo snap install pycharm-community --classic
sudo snap install code --classic
sudo snap install powershell --classic
# wget https://download-cdn.jetbrains.com/python/pycharm-community-2022.3.tar.gz

# desktop enviroments.
sudo apt install gnome-session -y  # gnome 0.3GB
sudo apt install ubuntu-gnome-desktop -y  # 1.2GB

