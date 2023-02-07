
# python & virtual enviornment
curl https://raw.githubusercontent.com/thisismygitrepo/machineconfig/main/src/machineconfig/setup_linux/ve.sh | bash

# repos
curl https://raw.githubusercontent.com/thisismygitrepo/machineconfig/main/src/machineconfig/setup_linux/repos.sh | bash

# symlinks
source ~/code/machineconfig/src/machineconfig/setup_linux/symlinks.sh  # requires sudo since it invloves chmod of dotfiles/.ssh, however sudo doesn't work with source. best to have sudo -s earlier.
. ~/.bashrc

# devaps
source <(sudo cat ~/code/machineconfig/src/machineconfig/setup_linux/devapps.sh)

