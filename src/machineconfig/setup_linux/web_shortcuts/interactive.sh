#!/bin/bash

echo """
=======================================================================
📦 MACHINE CONFIGURATION | Interactive Installation Script
======================================================================="""

curl https://raw.githubusercontent.com/thisismygitrepo/machineconfig/main/src/machineconfig/setup_linux/ve.sh | bash
$HOME/.local/bin/uv run --python 3.13 --with machineconfig ia




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
    uv run --python 3.13 --with machineconfig python -m fire machineconfig.profile.create main_symlinks --choice=all
    sudo chmod 600 $HOME/.ssh/*
    sudo chmod 700 $HOME/.ssh
else
    echo """    ⏭️  Skipping symlink creation
    """
fi

