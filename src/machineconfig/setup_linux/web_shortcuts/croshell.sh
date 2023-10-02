
# python & virtual enviornment
# curl https://raw.githubusercontent.com/thisismygitrepo/machineconfig/main/src/machineconfig/setup_linux/ve.sh | bash
curl bit.ly/cfgvelinux -L | bash

# repos
# curl https://raw.githubusercontent.com/thisismygitrepo/machineconfig/main/src/machineconfig/setup_linux/repos.sh | bash
curl bit.ly/cfgreposlinux -L | bash

# symlinks
source $HOME/code/machineconfig/src/machineconfig/setup_linux/symlinks.sh  # requires sudo since it invloves chmod of dotfiles/.ssh, however sudo doesn't work with source. best to have sudo -s earlier.
. ~/.bashrc

# devaps
# source <(sudo cat ~/code/machineconfig/src/machineconfig/setup_linux/devapps.sh)

