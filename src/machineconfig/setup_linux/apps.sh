#!/usr/bin/bash


# ----------------- package manager -----------------
sudo apt update -y
sudo apt upgrade -y
# do-release-upgrade # /etc/update-manager/release-upgrades
sudo apt install nala -y  # nala is a command line tool for managing your Linux system
sudo apt update && sudo apt upgrade -y  # this is suprior to apt

sudo apt remove mlocate  # solves wsl2 slow Initializing plocate database; this may take some time..

# -------------------- Utilities --------------------
curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash -  # The NodeSource repository, must add to get latest node
# consider asdf tool for managing versions of python, node, etc.
sudo apt update
sudo apt install nodejs -y  # for nvim plugins
sudo apt install npm -y  # for nvim plugins
npm i sharewifi -g
sudo apt install graphviz -y

#curl --compressed -o- -L https://yarnpkg.com/install.sh | bash
sudo apt install wget -y  # for downloading files
sudo apt install curl -y  # for handling http requests
sudo apt install make -y  # lvim and spacevim require it.
sudo apt install net-tools -y  # gives ifconfig
sudo apt install git -y  # for version control

# ------------------- File Managers ---------------------------

sudo apt install bat -y  # cat with colors.
sudo apt install ranger -y   # terminal-based file explorer, alternative: lf (Go-based), tere (Rust-based), nnn (C-based), vifm (C-based), mc (C-based), etc
# ranger is good, but for consistency with Windows, use lf:
curl https://raw.githubusercontent.com/thisismygitrepo/machineconfig/main/src/machineconfig/setup_linux/tools/lf.sh | sh

sudo apt install fzf -y  # fuzzy finder: searches contents of all files, including .git
sudo apt install fd-find -y  # find alternative
sudo apt install ripgrep -y  # rg command, rust-based, blazingly fast grep.
sudo apt install ugrep -y  # just as good as grep, but consistent with windows

sudo apt install ncdu -y   # disk usage analyzer.
sudo apt install exa -y  # replacement for ls. no ner fonts, unlike lsd

sudo apt install tmux -y # allows multiple terminals that are persistent.
# sudo apt install tmate -y  # remote tmux, see https://tmate.io


# ---------------------------- text style ------------------------------------
sudo apt install sl -y  # for fun
sudo apt install cmatrix -y  # for fun
sudo apt install hollywood -y  # for fun
sudo apt install neofetch -y  # for system info
neofetch
sudo apt install fortune -y  # generate random text in the form of piece of wisdom
sudo apt install boxes -y  # for ascii banners. boxes -l for list of boxes.
sudo apt install cowsay -y  # animals saying things. Different figures with -f. Full list: cowsay -l
sudo apt install lolcat -y  # for coloring text in terminal.
sudo apt install toilet -y  # large ascii text
sudo apt install figlet -y  # large ascii text. See: showfigfonts for full list of fonts. use -f to change font.
# see more here: https://linoxide.com/linux-fun-terminal-crazy-output/
# midnight commander, similarv# Asciiquarium# https://github.com/bartobri/no-more-secrets
# https://www.youtube.com/watch?v=haitmoSyTls


# ------------------------------ EDITORS -----------------------------
# curl https://sh.rustup.rs -sSf | sh
curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh
#sudo apt install neovim -y  # nvim, but not latest release
bash <(curl -s https://raw.githubusercontent.com/lunarvim/lunarvim/master/utils/installer/install.sh)
# https://spacevim.org/quick-start-guide/#linux-and-macos
curl -sLf https://spacevim.org/install.sh | bash

bash -c "$(curl -fsSL https://raw.githubusercontent.com/ohmybash/oh-my-bash/master/tools/install.sh)"

# zsh
#sudo apt install zsh
# sh -c "$(curl -fsSL https://raw.githubusercontent.com/ohmyzsh/ohmyzsh/master/tools/install.sh)"
# sudo apt install zsh-syntax-highlighting -y
# sudo apt install zsh-autosuggestions -y
# sudo apt install zsh-theme-powerlevel10k -y
# sudo apt install zsh-completions -y
# sudo apt install zsh-history-substring-search -y


