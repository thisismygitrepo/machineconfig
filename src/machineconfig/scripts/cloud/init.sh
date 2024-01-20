
if [ -z "$CLOUD_CONFIG_NAME" ]
then
    read -s -p "Enter CLOUD_CONFIG_NAME: " CLOUD_CONFIG_NAME
    export CLOUD_CONFIG_NAME=$CLOUD_CONFIG_NAME
fi

if [ -z "$SHARE_URL" ]
then
    read -s -p "Enter SHARE_URL: " SHARE_URL
    export SHARE_URL=$SHARE_URL
fi

if [ -z "$DECRYPTION_PASSWORD" ]
then
    read -s -p "Enter DECRYPTION_PASSWORD: " DECRYPTION_PASSWORD
    export DECRYPTION_PASSWORD=$DECRYPTION_PASSWORD
fi

# essentials
# TODO: https://askubuntu.com/questions/1367139/apt-get-upgrade-auto-restart-services
export package_manager="apt"
curl bit.ly/cfgappslinux -L | bash
curl bit.ly/cfgvelinux -L | bash
. $HOME/venvs/ve/bin/activate
curl bit.ly/cfgreposlinux -L | bash

# dotfiles
source ~/code/machineconfig/src/machineconfig/setup_linux/symlinks.sh
sleep 1
~/scripts/cloud_copy $SHARE_URL $HOME --config ss
source ~/code/machineconfig/src/machineconfig/setup_linux/symlinks.sh
. ~/.bashrc


. ~/scripts/activate_ve 've'
python -m fire machineconfig.scripts.python.devops_devapps_install main  --which=AllEssentials  # this installs everything.
. ~/.bashrc

. $HOME/dotfiles/config/cloud/$CLOUD_CONFIG_NAME/init.sh
