
if [ -z "$CLOUD_CONFIG_NAME" ]
then
    read -s -p "Enter CLOUD_CONFIG_NAME: " CLOUD_CONFIG_NAME
    export CLOUD_CONFIG_NAME=$CLOUD_CONFIG_NAME
fi

if [ -z "$DOTFILES_URL" ]
then
    read -s -p "Enter DOTFILES_URL: " DOTFILES_URL
    export DOTFILES_URL=$DOTFILES_URL
fi

if [ -z "$DOTFILES_URL" ]
then
    read -s -p "Enter DOTFILES_URL: " DOTFILES_URL
    export DOTFILES_URL=$DOTFILES_URL
fi

# essentials
export package_manager="apt"
curl bit.ly/cfgappslinux -L | bash
curl bit.ly/cfgvelinux -L | bash
. $HOME/venvs/ve/bin/activate
curl bit.ly/cfgreposlinux -L | bash
sudo apt install fuse3 -y  # required by rclone. Available by default on other distros

# dotfiles
source ~/code/machineconfig/src/machineconfig/setup_linux/symlinks.sh
sleep 1
~/scripts/fire $HOME/code/machineconfig/src/machineconfig/scripts/cloud/dotfiles.py get
source ~/code/machineconfig/src/machineconfig/setup_linux/symlinks.sh
. ~/.bashrc


. ~/scripts/activate_ve 've'
python -m fire machineconfig.scripts.python.devops_devapps_install main  --which=AllEssentials  # this installs everything.
. ~/.bashrc

. $HOME/dotfiles/config/cloud/$CLOUD_CONFIG_NAME/init.sh
