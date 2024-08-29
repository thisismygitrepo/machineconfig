#!/usr/bin/bash

# This scripts is meant to keep going even if some commands fail.

# ----------------- package managers -----------------
# apt, nala (fast parallel apt), brew & nix.

yes '' | sed 3q; echo "----------------------------- installing upgrading and updating apt ----------------------------"; yes '' | sed 3q
sudo apt update -y || true
# sudo apt upgrade -y || true
sudo install install curl wget -y || true  # for handling http requests


if [ -z "$package_manager" ]; then
  package_manager="apt"  # see if variable package_manager is defined, if not, define it as "nix"
fi

curl -L https://nixos.org/nix/install | sh  # cross *nix platforms.
. ~/.nix-profile/etc/profile.d/nix.sh

sudo apt install nala -y || true  # nala is a command line tool for managing your Linux system

# as per: https://brew.sh/
export NONINTERACTIVE=1  # to avoid confirmation prompts
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"


# sudo apt remove mlocate && plocate # solves wsl2 slow Initializing plocate database; this may take some time..
# ignoring indexing of windows files: https://askubuntu.com/questions/1251484/why-does-it-take-so-much-time-to-initialize-mlocate-database
#sudo cp /etc/updatedb.conf /etc/updatedb.conf.bak || true
# add /mnt/c to PRUNEPATHS of /etc/updatedb.conf using sed
#sudo sed -i 's/PRUNEPATHS="/PRUNEPATHS="\/mnt /g' /etc/updatedb.conf || true
# PRUNEPATHS /mnt /etc/updatedb.conf
# sudo sed -i "s/^ *PRUNEFS *= *[\"']/&drvfs 9p /" /etc/updatedb.conf /etc/cron.daily/locate
#exclude_dirs="/mnt /tmp /var/tmp"
#updatedb --prunepaths="$exclude_dirs"  # update the mlocate database
#updatedb --prunefs="NFS,smbfs,cifs"

# -------------------- Utilities --------------------

yes '' | sed 3q; echo "----------------------------- installing fusemount3 --------------------------------"; yes '' | sed 3q
sudo nala install fuse3 -y || true  # for rclone.
sudo nala install nfs-common -y || true  # for mounting nfs shares. Missing fom Ubuntu server by default.


yes '' | sed 3q; echo "----------------------------- installing uv --------------------------------"; yes '' | sed 3q
curl -LsSf https://astral.sh/uv/install.sh | sh


yes '' | sed 3q; echo "----------------------------- installing sqlite --------------------------"; yes '' | sed 3q
sudo nala install sqlite -y || true  # sqlite vscode extension requires this to be installed. It gives sqlite and sqlite3 commands.


yes '' | sed 3q; echo "----------------------------- installing nvm of nodejs --------------------------"; yes '' | sed 3q
# according to: https://docs.npmjs.com/downloading-and-installing-node-js-and-npm its best to use nvm manager
# https://github.com/nvm-sh/nvm?tab=readme-ov-file#install--update-script
curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.40.0/install.sh | bash
# shellcheck disable=SC2155
# this code below allows to use nvm straight away without having to restart the terminal
export NVM_DIR="$HOME/.nvm"
[ -s "$NVM_DIR/nvm.sh" ] && \. "$NVM_DIR/nvm.sh"  # This loads nvm
[ -s "$NVM_DIR/bash_completion" ] && \. "$NVM_DIR/bash_completion"  # This loads nvm bash_completion
nvm install node || true


yes '' | sed 3q; echo "----------------------------- installing net-tools ----------------------------"; yes '' | sed 3q
if [ "$package_manager" = "apt" ]; then
  sudo nala install net-tools -y || true  # gives ifconfig
else
  ~/.nix-profile/bin/nix-env -iA nixpkgs.nettools || true
fi


yes '' | sed 3q; echo "----------------------------- installing git ----------------------------"; yes '' | sed 3q
sudo nala install git -y || true  # for version control
sudo nala install htop -y || true  # for monitoring system resources


# ========================================= EDITORS =========================================
yes '' | sed 3q; echo "----------------------------- installing nano ----------------------------"; yes '' | sed 3q
if [ "$package_manager" = "apt" ]; then
  sudo nala install nano -y || true  # for editing files
else
  ~/.nix-profile/bin/nix-env -iA nixpkgs.nano || true
  # ~/.nix-profile/bin/nix-env -iA nixpkgs.vscode || true
fi


/home/linuxbrew/.linuxbrew/bin/brew install neovim


yes '' | sed 3q; echo "----------------------------- installing chafa ----------------------------"; yes '' | sed 3q
sudo nala install chafa -y  # like viu, one can ascii-ize images.
