#!/usr/bin/bash

# This scripts is meant to keep going even if some commands fail.

# ----------------- package manager -----------------
yes '' | sed 3q; echo "----------------------------- installing upgrading and updating apt ----------------------------"; yes '' | sed 3q
sudo apt update -y || true
# sudo apt upgrade -y || true
sudo apt install curl -y || true  # for handling http requests


if [ -z "$package_manager" ]; then
  package_manager="nix"  # see if variable package_manager is defined, if not, define it as "nix"
fi

if [ "$package_manager" = "nix" ]; then
  curl -L https://nixos.org/nix/install | sh  # cross *nix platforms.
  . ~/.nix-profile/etc/profile.d/nix.sh
else
  # sudo apt update || true 
  # sudo apt upgrade -y || true
  sudo apt install nala -y || true  # nala is a command line tool for managing your Linux system
fi

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


yes '' | sed 3q; echo "----------------------------- installing wget --------------------------------"; yes '' | sed 3q
if [ "$package_manager" = "apt" ]; then
  sudo apt install wget -y || true  # for downloading files
else
  ~/.nix-profile/bin/nix-env -iA nixpkgs.wget || true
fi


yes '' | sed 3q; echo "----------------------------- installing nvm of nodejs --------------------------"; yes '' | sed 3q
# according to: https://docs.npmjs.com/downloading-and-installing-node-js-and-npm its best to use nvm manager
curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.39.5/install.sh | bash
# shellcheck disable=SC2155
export NVM_DIR="$([ -z "${XDG_CONFIG_HOME-}" ] && printf %s "${HOME}/.nvm" || printf %s "${XDG_CONFIG_HOME}/nvm")"
[ -s "$NVM_DIR/nvm.sh" ] && \. "$NVM_DIR/nvm.sh" # This loads nvm

nvm install node || true


yes '' | sed 3q; echo "----------------------------- installing net-tools ----------------------------"; yes '' | sed 3q
if [ "$package_manager" = "apt" ]; then
  sudo apt install net-tools -y || true  # gives ifconfig
else
  ~/.nix-profile/bin/nix-env -iA nixpkgs.nettools || true
fi


yes '' | sed 3q; echo "----------------------------- installing git ----------------------------"; yes '' | sed 3q
# if [ "$package_manager" = "apt" ]; then
#   sudo apt install git -y || true  # for version control
# else
#   ~/.nix-profile/bin/nix-env -iA nixpkgs.git || true
# fi
sudo apt install git -y || true  # for version control
sudo apt install htop -y || true  # for monitoring system resources


#curl --compressed -o- -L https://yarnpkg.com/install.sh | bash
#curl https://rclone.org/install.sh | sudo bash  # onedrive equivalent.



# ------------------- File Managers ---------------------------
# yes '' | sed 3q; echo "----------------------------- installing bat ----------------------------"; yes '' | sed 3q
# if [ "$package_manager" = "apt" ]; then
#   sudo apt install bat -y || true  # cat with colors.
# else
#   ~/.nix-profile/bin/nix-env -iA nixpkgs.bat || true
# fi
#sudo apt install ranger -y   # terminal-based file explorer, alternative: lf (Go-based), tere (Rust-based), nnn (C-based), vifm (C-based), mc (C-based), etc

# yes '' | sed 3q; echo "----------------------------- installing zoxide ----------------------------"; yes '' | sed 3q
# if [ "$package_manager" = "apt" ]; then
#   sudo apt install zoxide -y || true
# else
#   ~/.nix-profile/bin/nix-env -iA nixpkgs.zoxide || true
# fi
# #sudo apt install zoxide || true
# (echo 'eval "$(zoxide init bash)"' >> ~/.bashrc) || true


yes '' | sed 3q; echo "----------------------------- installing skim ----------------------------"; yes '' | sed 3q
if [ "$package_manager" = "apt" ]; then
  sudo apt install curl
else
  ~/.nix-profile/bin/nix-env -iA nixpkgs.skim  # https://search.nixos.org/packages?channel=22.11&show=skim&from=0&size=50&sort=relevance&type=packages&query=skim || true
  ~/.nix-profile/bin/nix-env -iA nixpkgs.btop
fi

yes '' | sed 3q; echo "----------------------------- installing ugrep ----------------------------"; yes '' | sed 3q
if [ "$package_manager" = "apt" ]; then
  sudo apt install ugrep -y || true  # just as good as grep, but consistent with windows
else
  ~/.nix-profile/bin/nix-env -iA nixpkgs.ugrep || true
fi


yes '' | sed 3q; echo "----------------------------- installing neofetch ----------------------------"; yes '' | sed 3q
if [ "$package_manager" = "apt" ]; then
  sudo apt install neofetch -y || true  # for system info
else
  ~/.nix-profile/bin/nix-env -iA nixpkgs.neofetch || true
  ~/.nix-profile/bin/nix-env -iA nixpkgs.cpufetch || true
fi
neofetch || true



# ========================================= EDITORS =========================================
yes '' | sed 3q; echo "----------------------------- installing nano ----------------------------"; yes '' | sed 3q
if [ "$package_manager" = "apt" ]; then
  sudo apt install nano -y || true  # for editing files
else
  ~/.nix-profile/bin/nix-env -iA nixpkgs.nano || true
  # ~/.nix-profile/bin/nix-env -iA nixpkgs.vscode || true
fi



yes '' | sed 3q; echo "----------------------------- installing ohmybash ----------------------------"; yes '' | sed 3q
bash -c "$(curl -fsSL https://raw.githubusercontent.com/ohmybash/oh-my-bash/master/tools/install.sh)"
# replace OSH_THEME="font" with OSH_THEME="cupcake" in ~/.bashrc
(sed -i 's/OSH_THEME="font"/OSH_THEME="cupcake"/' ~/.bashrc) || true
# this starts a new shell process and stops execution at this point!



yes '' | sed 3q; echo "----------------------------- installing chafa ----------------------------"; yes '' | sed 3q
sudo apt install chafa -y  # like viu, one can ascii-ize images.


