

# as per https://code.visualstudio.com/docs/setup/linux

# Check if GPG key is already installed
if [ ! -f /etc/apt/keyrings/packages.microsoft.gpg ]; then
    wget -qO- https://packages.microsoft.com/keys/microsoft.asc | gpg --dearmor > packages.microsoft.gpg
    sudo install -D -o root -g root -m 644 packages.microsoft.gpg /etc/apt/keyrings/packages.microsoft.gpg
    rm -f packages.microsoft.gpg
fi

# Check if VS Code repository is already added
if [ ! -f /etc/apt/sources.list.d/vscode.list ]; then
    echo "deb [arch=amd64,arm64,armhf signed-by=/etc/apt/keyrings/packages.microsoft.gpg] https://packages.microsoft.com/repos/code stable main" | sudo tee /etc/apt/sources.list.d/vscode.list > /dev/null
fi

# Install apt-transport-https if not installed
if ! dpkg -s apt-transport-https >/dev/null 2>&1; then
    sudo nala install apt-transport-https -y
fi

sudo nala update
sudo nala install code -y
