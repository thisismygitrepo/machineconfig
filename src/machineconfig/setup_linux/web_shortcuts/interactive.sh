
read -p "Install Apps [y]/n ? " choice

if [[ "$choice" == "y" || "$choice" == "Y" ]]; then
    curl https://raw.githubusercontent.com/thisismygitrepo/machineconfig/main/src/machineconfig/setup_linux/apps.sh | bash
else
    echo "Installation aborted."
fi


read -p "Upgrade system packages [y]/n ? " choice

if [[ "$choice" == "y" || "$choice" == "Y" ]]; then
    sudo nala upgrade -y
else
    echo "Installation upgrade."
fi


export ve_name="ve"
curl https://raw.githubusercontent.com/thisismygitrepo/machineconfig/main/src/machineconfig/setup_linux/ve.sh | bash
curl https://raw.githubusercontent.com/thisismygitrepo/machineconfig/main/src/machineconfig/setup_linux/repos.sh | bash


echo "MOVING DOTFILES TO NEW MACHINE"
echo "USING MOUSE WITHOUT KB OR BROWSER SHARE: On original machine, run: 'cd ~/dotfiles/creds/msc; easy-sharing . --password rew'. one new machine open brave and head to url to get password of mousewithoutborders"
echo "USING SSH: FROM REMOTE, RUN: fptx ~/dotfiles $(hostname):^ -z"
# * for wsl: `wsl_server.ps1; ftpx ~/dotfiles $env:USERNAME@localhost:2222 -z # OR: ln -s /mnt/c/Users/$(whoami)/dotfiles ~/dotfiles`
echo "USING INTERNET SECURE SHARE: cd ~; cloud_copy SHARE_URL . --config ss (requires symlinks to be created first)"

read -p "Install SSH Server [y]/n ? " choice
choice=${choice:-y}
if [[ "$choice" == "y" || "$choice" == "Y" ]]; then
    sudo nala install openssh-server -y
else
    echo "Installation aborted."
fi


read -p "Did you finish copying [y]/n ? " choice
choice=${choice:-y}
if [[ "$choice" == "y" || "$choice" == "Y" ]]; then
    sudo nala install openssh-server -y
else
    echo "Installation aborted."
fi


read -p "Create Symlinks (finish dotfiles transfer first) [y]/n ? " choice
choice=${choice:-y}
if [[ "$choice" == "y" || "$choice" == "Y" ]]; then
    source $HOME/venvs/ve/bin/activate
    python -m fire machineconfig.profile.create main --choice=all
    sudo chmod 600 $HOME/.ssh/*
    sudo chmod 700 $HOME/.ssh
else
    echo "Installation aborted."
fi


read -p "Install CLI Apps [y]/n ? " choice
choice=${choice:-y}
if [[ "$choice" == "y" || "$choice" == "Y" ]]; then
    source <(sudo cat ~/code/machineconfig/src/machineconfig/setup_linux/devapps.sh)
else
    echo "Installation aborted."
fi

read -p "Install DevTools [y]/n ? " choice
choice=${choice:-y}
if [[ "$choice" == "y" || "$choice" == "Y" ]]; then
    . $HOME/venvs/ve/bin/activate
    (curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh) || true
    sudo nala install libssl-dev -y  # required for web development
    sudo nala install ffmpeg -y
    python -m fire machineconfig.scripts.python.devops_devapps_install main --which=wezterm,brave,code,docker,warp-cli
else
    echo "Installation aborted."
fi


read -p "Retrieve Repos at ~/code [y]/n ? " choice
choice=${choice:-y}
if [[ "$choice" == "y" || "$choice" == "Y" ]]; then
    repos ~/code --clone --cloud odg1
else
    echo "Installation aborted."
fi


read -p "Retrieve data [y]/n ? " choice
choice=${choice:-y}
if [[ "$choice" == "y" || "$choice" == "Y" ]]; then
    . $HOME/venvs/ve/bin/activate
    python -m fire machineconfig.scripts.python.devops_backup_retrieve main --direction=RETRIEVE  # --which=all
else
    echo "Installation aborted."
fi


read -p "Install ascii art libs [y]/n ? " choice
choice=${choice:-y}
if [[ "$choice" == "y" || "$choice" == "Y" ]]; then
    curl bit.ly/cfgasciiartlinux -L | sudo bash
else
    echo "Installation aborted."
fi

# echo "run this after installing Thunderbird and starting it and shutting it down but before downloading backup"
# cd ~/AppData/Roaming/ThunderBird/Profiles
# $res = ls
# $name = $res[0].Name
# mv $backup_folder $name

echo "ALL DONE. Youh might need to reboot"
