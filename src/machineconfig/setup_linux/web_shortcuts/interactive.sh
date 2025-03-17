#!/bin/bash

echo "
🚀 ===========================================
📦 Machine Configuration Installation Script
============================================="

read -p "📥 Install Apps [y]/n? " choice

if [[ "$choice" == "y" || "$choice" == "Y" ]]; then
    echo -e "\n🔄 Installing base applications..."
    curl https://raw.githubusercontent.com/thisismygitrepo/machineconfig/main/src/machineconfig/setup_linux/apps.sh | bash
else
    echo "⏭️  Skipping applications installation"
fi

echo -e "\n----------------------------------------"
read -p "🔄 Upgrade system packages [y]/n? " choice

if [[ "$choice" == "y" || "$choice" == "Y" ]]; then
    echo -e "\n📦 Upgrading system packages..."
    sudo nala upgrade -y
else
    echo "⏭️  Skipping system upgrade"
fi

echo -e "\n----------------------------------------"
read -p "🐍 Install Python virtual environment 've' [y]/n? " choice
export ve_name="ve"
if [[ "$choice" == "y" || "$choice" == "Y" ]]; then
    echo -e "\n🔧 Setting up Python environment..."
    curl https://raw.githubusercontent.com/thisismygitrepo/machineconfig/main/src/machineconfig/setup_linux/ve.sh | bash
    curl https://raw.githubusercontent.com/thisismygitrepo/machineconfig/main/src/machineconfig/setup_linux/repos.sh | bash
else
    echo "⏭️  Skipping virtual environment setup"
fi

echo -e "\n📂 ============================================
🔄 DOTFILES MIGRATION OPTIONS
============================================="
echo -e "🖱️  Method 1: USING MOUSE WITHOUT KB OR BROWSER SHARE
    On original machine, run:
    cd ~/dotfiles/creds/msc
    easy-sharing . --password rew --username al
    Then open brave on new machine to get MouseWithoutBorders password"

echo -e "\n🔐 Method 2: USING SSH
    FROM REMOTE, RUN:
    fptx ~/dotfiles \$USER@\$(hostname):^ -z"

echo -e "\n☁️  Method 3: USING INTERNET SECURE SHARE
    cd ~
    cloud_copy SHARE_URL . --config ss
    (requires symlinks to be created first)"

echo -e "\n----------------------------------------"
read -p "🔒 Install SSH Server [y]/n? " choice
choice=${choice:-y}
if [[ "$choice" == "y" || "$choice" == "Y" ]]; then
    echo -e "\n🔧 Installing SSH server..."
    sudo nala install openssh-server -y
else
    echo "⏭️  Skipping SSH server installation"
fi

echo -e "\n----------------------------------------"
read -p "📂 Have you finished copying dotfiles? [y]/n? " choice
choice=${choice:-y}
if [[ "$choice" == "y" || "$choice" == "Y" ]]; then
    echo -e "\n🔧 Setting up SSH server..."
    sudo nala install openssh-server -y
else
    echo "⏭️  Skipping final SSH setup"
fi

echo -e "\n----------------------------------------"
read -p "🔗 Create Symlinks (finish dotfiles transfer first) [y]/n? " choice
choice=${choice:-y}
if [[ "$choice" == "y" || "$choice" == "Y" ]]; then
    echo -e "\n🔧 Creating symlinks and setting permissions..."
    source $HOME/venvs/ve/bin/activate
    python -m fire machineconfig.profile.create main --choice=all
    sudo chmod 600 $HOME/.ssh/*
    sudo chmod 700 $HOME/.ssh
else
    echo "⏭️  Skipping symlink creation"
fi

echo -e "\n----------------------------------------"
read -p "⚡ Install CLI Apps [y]/n? " choice
choice=${choice:-y}
if [[ "$choice" == "y" || "$choice" == "Y" ]]; then
    echo -e "\n🔧 Installing CLI applications..."
    . $HOME/venvs/ve/bin/activate
    python -m fire machineconfig.scripts.python.devops_devapps_install main --which=AllEssentials
    . $HOME/.bashrc
else
    echo "⏭️  Skipping CLI apps installation"
fi

echo -e "\n----------------------------------------"
read -p "🛠️  Install Development Tools [y]/n? " choice
choice=${choice:-y}
if [[ "$choice" == "y" || "$choice" == "Y" ]]; then
    echo -e "\n🔧 Installing development tools..."
    . $HOME/venvs/ve/bin/activate
    (curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh) || true
    sudo nala install libssl-dev -y
    sudo nala install ffmpeg -y
    python -m fire machineconfig.scripts.python.devops_devapps_install main --which=wezterm,brave,code,docker,warp-cli
else
    echo "⏭️  Skipping development tools installation"
fi

echo -e "\n----------------------------------------"
read -p "📚 Retrieve Repositories to ~/code [y]/n? " choice
choice=${choice:-y}
if [[ "$choice" == "y" || "$choice" == "Y" ]]; then
    echo -e "\n🔄 Cloning repositories..."
    repos ~/code --clone --cloud odg1
else
    echo "⏭️  Skipping repository retrieval"
fi

echo -e "\n----------------------------------------"
read -p "💾 Retrieve Data [y]/n? " choice
choice=${choice:-y}
if [[ "$choice" == "y" || "$choice" == "Y" ]]; then
    echo -e "\n🔄 Retrieving data..."
    . $HOME/venvs/ve/bin/activate
    python -m fire machineconfig.scripts.python.devops_backup_retrieve main --direction=RETRIEVE
else
    echo "⏭️  Skipping data retrieval"
fi

echo -e "\n----------------------------------------"
read -p "🎨 Install ASCII Art Libraries [y]/n? " choice
choice=${choice:-y}
if [[ "$choice" == "y" || "$choice" == "Y" ]]; then
    echo -e "\n🎨 Installing ASCII art libraries..."
    curl bit.ly/cfgasciiartlinux -L | sudo bash
else
    echo "⏭️  Skipping ASCII art installation"
fi

# echo -e "\n📧 Thunderbird Setup Note:
# Run after installing Thunderbird and starting it once:
# cd ~/AppData/Roaming/ThunderBird/Profiles
# \$res = ls
# \$name = \$res[0].Name
# mv \$backup_folder \$name"

echo -e "\n✨ ===========================================
🎉 Installation Complete! You may need to reboot.
============================================="
