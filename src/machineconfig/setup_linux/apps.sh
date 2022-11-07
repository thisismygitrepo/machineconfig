#!/usr/bin/bash


# ----------------- package manager -----------------
sudo apt update -y
sudo apt upgrade -y
# do-release-upgrade # /etc/update-manager/release-upgrades
sudo apt install nala -y  # nala is a command line tool for managing your Linux system
sudo nala update && sudo nala upgrade -y  # this is suprior to apt

sudo nala remove mlocate  # solves wsl2 slow Initializing plocate database; this may take some time..

# -------------------- Utilities --------------------
curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash -  # The NodeSource repository, must add to get latest node
# consider asdf tool for managing versions of python, node, etc.
sudo nala update
sudo nala install nodejs -y  # for nvim plugins
sudo nala install npm -y  # for nvim plugins
npm i sharewifi -g
sudo nala install graphviz -y

#curl --compressed -o- -L https://yarnpkg.com/install.sh | bash
sudo nala install wget -y  # for downloading files
sudo nala install curl -y  # for handling http requests
sudo nala install make -y  # lvim and spacevim require it.
sudo nala install net-tools -y  # gives ifconfig
sudo nala install git -y  # for version control

# ------------------- File Managers ---------------------------

sudo nala install bat -y  # cat with colors.
sudo nala install ranger -y   # terminal-based file explorer, alternative: lf (Go-based), tere (Rust-based), nnn (C-based), vifm (C-based), mc (C-based), etc
# ranger is good, but for consistency with Windows, use lf:
curl https://raw.githubusercontent.com/thisismygitrepo/machineconfig/main/src/machineconfig/setup_linux/tools/lf.sh | sh

sudo nala install fzf -y  # fuzzy finder: searches contents of all files, including .git
sudo nala install fd-find -y  # find alternative
sudo nala install ripgrep -y  # rg command, rust-based, blazingly fast grep.
sudo nala install ugrep -y  # just as good as grep, but consistent with windows

sudo nala install ncdu -y   # disk usage analyzer.
sudo nala install exa -y  # replacement for ls. no ner fonts, unlike lsd

sudo nala install tmux -y # allows multiple terminals that are persistent.
# sudo nala install tmate -y  # remote tmux, see https://tmate.io


# ---------------------------- text style ------------------------------------
sudo nala install sl -y  # for fun
sudo nala install cmatrix -y  # for fun
sudo nala install hollywood -y  # for fun
sudo nala install neofetch -y  # for system info
neofetch
sudo nala install fortune -y  # generate random text in the form of piece of wisdom
sudo nala install boxes -y  # for ascii banners. boxes -l for list of boxes.
sudo nala install cowsay -y  # animals saying things. Different figures with -f. Full list: cowsay -l
sudo nala install lolcat -y  # for coloring text in terminal.
sudo nala install toilet -y  # large ascii text
sudo nala install figlet -y  # large ascii text. See: showfigfonts for full list of fonts. use -f to change font.
# see more here: https://linoxide.com/linux-fun-terminal-crazy-output/
# midnight commander, similarv# Asciiquarium# https://github.com/bartobri/no-more-secrets
# https://www.youtube.com/watch?v=haitmoSyTls


# ------------------------------ EDITORS -----------------------------
# curl https://sh.rustup.rs -sSf | sh
curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh
#sudo nala install neovim -y  # nvim, but not latest release
bash <(curl -s https://raw.githubusercontent.com/LunarVim/LunarVim/rolling/utils/installer/install-neovim-from-release)
# https://github.com/LunarVim/LunarVim
bash <(curl -s https://raw.githubusercontent.com/lunarvim/lunarvim/master/utils/installer/install.sh)
# https://spacevim.org/quick-start-guide/#linux-and-macos
curl -sLf https://spacevim.org/install.sh | bash

bash -c "$(curl -fsSL https://raw.githubusercontent.com/ohmybash/oh-my-bash/master/tools/install.sh)"

# zsh
#sudo nala install zsh
# sh -c "$(curl -fsSL https://raw.githubusercontent.com/ohmyzsh/ohmyzsh/master/tools/install.sh)"
# sudo nala install zsh-syntax-highlighting -y
# sudo nala install zsh-autosuggestions -y
# sudo nala install zsh-theme-powerlevel10k -y
# sudo nala install zsh-completions -y
# sudo nala install zsh-history-substring-search -y


