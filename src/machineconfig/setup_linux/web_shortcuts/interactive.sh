#!/bin/bash

echo """#=======================================================================
📦 MACHINE CONFIGURATION | Interactive Installation Script
#=======================================================================
"""

read -p "📥 Install Apps [y]/n? " choice

if [[ "$choice" == "y" || "$choice" == "Y" ]]; then
    echo """    #=======================================================================
    📦 APPLICATIONS | Installing base system applications
    #=======================================================================
    """
    curl https://raw.githubusercontent.com/thisismygitrepo/machineconfig/main/src/machineconfig/setup_linux/apps.sh | bash
else
    echo """    ⏭️  Skipping applications installation
    """
fi

echo """#=======================================================================
🔄 SYSTEM UPDATE | Package management
#=======================================================================
"""
read -p "🔄 Upgrade system packages [y]/n? " choice

if [[ "$choice" == "y" || "$choice" == "Y" ]]; then
    echo """    📦 Upgrading system packages...
    """
    sudo nala upgrade -y
else
    echo """    ⏭️  Skipping system upgrade
    """
fi

echo """#=======================================================================
🐍 PYTHON ENVIRONMENT | Virtual environment setup
#=======================================================================
"""
read -p "🐍 Install UV and repos [y]/n? " choice
if [[ "$choice" == "y" || "$choice" == "Y" ]]; then
    echo """    🔧 Setting up Python environment...
    """
    curl https://raw.githubusercontent.com/thisismygitrepo/machineconfig/main/src/machineconfig/setup_linux/ve.sh | bash
    curl https://raw.githubusercontent.com/thisismygitrepo/machineconfig/main/src/machineconfig/setup_linux/repos.sh | bash
else
    echo """    ⏭️  Skipping virtual environment setup
    """
fi


echo """#=======================================================================
🔒 SSH SERVER | Remote access setup
#=======================================================================
"""
read -p "🔒 Install SSH Server [y]/n? " choice
choice=${choice:-y}
if [[ "$choice" == "y" || "$choice" == "Y" ]]; then
    echo """    🔧 Installing SSH server...
    """
    sudo nala install openssh-server -y
else
    echo """    ⏭️  Skipping SSH server installation
    """
fi

echo """#=======================================================================
📂 DOTFILES MIGRATION | Configuration transfer options
#=======================================================================

🖱️  Method 1: USING MOUSE WITHOUT KB OR BROWSER SHARE
    On original machine, run:
    cd ~/dotfiles/creds/msc
    easy-sharing . --password rew --username al
    Then open brave on new machine to get MouseWithoutBorders password

🔐 Method 2: USING SSH
    FROM REMOTE, RUN:
    fptx ~/dotfiles $USER@$(hostname):^ -z
    # OR, using IP address if router has not yet found the hostname:
    fptx ~/dotfiles $USER@$(hostname -I | awk '{print $1}'):^ -z

☁️  Method 3: USING INTERNET SECURE SHARE
    cd ~
    cloud_copy SHARE_URL . --config ss
    (requires symlinks to be created first)
"""

echo """#=======================================================================
📂 DOTFILES STATUS | Configuration files check
#=======================================================================
"""
read -p "📂 Have you finished copying dotfiles? [y]/n? " choice

echo """#=======================================================================
🔗 SYMLINK CREATION | Configuration setup
#=======================================================================
"""
read -p "🔗 Create Symlinks (finish dotfiles transfer first) [y]/n? " choice
choice=${choice:-y}
if [[ "$choice" == "y" || "$choice" == "Y" ]]; then
    echo """    🔧 Creating symlinks and setting permissions...
    """
    uv run --python 3.13 --with machineconfig python -m fire machineconfig.profile.create main --choice=all
    sudo chmod 600 $HOME/.ssh/*
    sudo chmod 700 $HOME/.ssh
else
    echo """    ⏭️  Skipping symlink creation
    """
fi

echo """#=======================================================================
⚡ CLI APPLICATIONS | Command-line tools installation
#=======================================================================
"""
read -p "⚡ Install CLI Apps [y]/n? " choice
choice=${choice:-y}
if [[ "$choice" == "y" || "$choice" == "Y" ]]; then
    echo """    🔧 Installing CLI applications...
    """
    uv run --python 3.13 --with machineconfig python -m fire machineconfig.scripts.python.devops_devapps_install main --which=AllEssentials
    . $HOME/.bashrc
else
    echo """    ⏭️  Skipping CLI apps installation
    """
fi

echo """#=======================================================================
🛠️  DEVELOPMENT TOOLS | Software development packages
#=======================================================================
"""
read -p "🛠️  Install Development Tools (rust, libssql-dev, ffmpeg, wezterm, brave, code) [y]/n? " choice
choice=${choice:-y}
if [[ "$choice" == "y" || "$choice" == "Y" ]]; then
    echo """    🔧 Installing development tools... """
    (curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh) || true
    sudo nala install libssl-dev -y
    sudo nala install ffmpeg -y
    uv run --python 3.13 --with machineconfig python -m fire machineconfig.scripts.python.devops_devapps_install main --which=wezterm,brave,code
else
    echo """    ⏭️  Skipping development tools installation
    """
fi

echo """#=======================================================================
📚 REPOSITORIES | Project code retrieval
#=======================================================================
"""
read -p "📚 Retrieve Repositories to ~/code [y]/n? " choice
choice=${choice:-y}
if [[ "$choice" == "y" || "$choice" == "Y" ]]; then
    echo """    🔄 Cloning repositories...
    """
    repos ~/code --clone --cloud odg1
else
    echo """    ⏭️  Skipping repository retrieval
    """
fi

echo """#=======================================================================
💾 DATA RETRIEVAL | Backup restoration
#=======================================================================
"""
read -p "💾 Retrieve Data [y]/n? " choice
choice=${choice:-y}
if [[ "$choice" == "y" || "$choice" == "Y" ]]; then
    echo """    🔄 Retrieving data...
    """
    uv run --python 3.13 --with machineconfig python -m fire machineconfig.scripts.python.devops_backup_retrieve main --direction=RETRIEVE
else
    echo """    ⏭️  Skipping data retrieval
    """
fi

echo """#=======================================================================
🎨 ASCII ART | Terminal visualization tools
#=======================================================================
"""
read -p "🎨 Install ASCII Art Libraries [y]/n? " choice
choice=${choice:-y}
if [[ "$choice" == "y" || "$choice" == "Y" ]]; then
    echo """    🎨 Installing ASCII art libraries...
    """
    curl bit.ly/cfgasciiartlinux -L | sudo bash
else
    echo """    ⏭️  Skipping ASCII art installation
    """
fi

# echo """# 📧 Thunderbird Setup Note:
# Run after installing Thunderbird and starting it once:
# cd ~/AppData/Roaming/ThunderBird/Profiles
# \$res = ls
# \$name = \$res[0].Name
# mv \$backup_folder \$name
# """

echo """#=======================================================================
✨ INSTALLATION COMPLETE | System setup finished successfully
#=======================================================================

🎉 Your system has been configured successfully!
🔄 You may need to reboot to apply all changes.
"""
