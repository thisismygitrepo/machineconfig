
# apps
# sudo -s
curl https://raw.githubusercontent.com/thisismygitrepo/machineconfig/main/src/machineconfig/setup_linux/apps.sh | bash
# virtual enviornment
curl https://raw.githubusercontent.com/thisismygitrepo/machineconfig/main/src/machineconfig/setup_linux/ve.sh | bash
# repos
curl https://raw.githubusercontent.com/thisismygitrepo/machineconfig/main/src/machineconfig/setup_linux/repos.sh | bash
# symlinks and bash profile.
# locally, run: `ftpsx username@hostname[:port] ~/dotfiles -z`
# for wsl: wsl_server.ps1; ftpsx $env:USERNAME@localhost:2222 ~/dotfiles -z # OR: ln -s /mnt/c/Users/$(whoami)/dotfiles ~/dotfiles
source ~/code/machineconfig/src/machineconfig/setup_linux/symlinks.sh  # requires sudo since it invloves chmod of dotfiles/.ssh, however sudo doesn't work with source. best to have sudo -s earlier.
# devapps
source <(sudo cat ~/code/machineconfig/src/machineconfig/setup_linux/devapps.sh)
