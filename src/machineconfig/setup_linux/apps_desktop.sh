

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
