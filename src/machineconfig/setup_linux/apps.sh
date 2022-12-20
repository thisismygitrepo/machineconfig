#!/usr/bin/bash


# ----------------- package manager -----------------
sudo apt update -y
sudo apt upgrade -y
# do-release-upgrade # /etc/update-manager/release-upgrades
sudo apt install nala -y  # nala is a command line tool for managing your Linux system
sudo apt update && sudo apt upgrade -y  # this is suprior to apt

# sudo apt remove mlocate && plocate # solves wsl2 slow Initializing plocate database; this may take some time..
# ignoring indexing of windows files: https://askubuntu.com/questions/1251484/why-does-it-take-so-much-time-to-initialize-mlocate-database
sudo cp /etc/updatedb.conf /etc/updatedb.conf.bak
# add /mnt/c to PRUNEPATHS of /etc/updatedb.conf using sed

sudo sed -i 's/PRUNEPATHS="/PRUNEPATHS="\/mnt\/c /g' /etc/updatedb.conf


# PRUNEPATHS /mnt /etc/updatedb.conf
# sudo sed -i "s/^ *PRUNEFS *= *[\"']/&drvfs 9p /" /etc/updatedb.conf /etc/cron.daily/locate

# -------------------- Utilities --------------------
sudo apt install wget -y  # for downloading files
sudo apt install curl -y  # for handling http requests

# consider asdf tool for managing versions of python, node, etc.
# https://nodejs.org/en/download/package-manager/#debian-and-ubuntu-based-linux-distributions
# https://github.com/nodesource/distributions/blob/master/README.md
#curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash -  # The NodeSource repository, must add to get latest node
#curl -fsSL https://deb.nodesource.com/setup_19.x | sudo -E bash - &&\
#sudo apt update
#sudo apt install -y nodejs
#sudo apt install npm -y  # for nvim plugins

# according to: https://docs.npmjs.com/downloading-and-installing-node-js-and-npm its best to use nvm manager
curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.39.2/install.sh | bash
# shellcheck disable=SC2155
export NVM_DIR="$([ -z "${XDG_CONFIG_HOME-}" ] && printf %s "${HOME}/.nvm" || printf %s "${XDG_CONFIG_HOME}/nvm")"
[ -s "$NVM_DIR/nvm.sh" ] && \. "$NVM_DIR/nvm.sh" # This loads nvm
nvm install node
npm install -g npm

npm i sharewifi -g
sudo apt install graphviz -y
sudo apt install tmux -y # allows multiple terminals that are persistent.
sudo apt install make -y  # lvim and spacevim require it.
sudo apt install net-tools -y  # gives ifconfig
sudo apt install git -y  # for version control
#curl --compressed -o- -L https://yarnpkg.com/install.sh | bash
#curl https://rclone.org/install.sh | sudo bash  # onedrive equivalent.
sudo apt install lynx  # tex browser, just like w3m

# ------------------- File Managers ---------------------------

sudo apt install bat -y  # cat with colors.
# sudo apt install ranger -y   # terminal-based file explorer, alternative: lf (Go-based), tere (Rust-based), nnn (C-based), vifm (C-based), mc (C-based), etc
# ranger is good, but for consistency with Windows, use lf:
curl https://raw.githubusercontent.com/thisismygitrepo/machineconfig/main/src/machineconfig/setup_linux/tools/lf.sh | sh
sudo apt install zoxide
echo 'eval "$(zoxide init bash)"' >> ~/.bashrc

sudo apt install fzf -y  # fuzzy finder: searches contents of all files, including .git
sudo apt install fd-find -y  # find alternative
sudo apt install ripgrep -y  # rg command, rust-based, blazingly fast grep.
sudo apt install ugrep -y  # just as good as grep, but consistent with windows

sudo apt install ncdu -y   # disk usage analyzer, like diskonaut
# https://github.com/bootandy/dust
# https://github.com/dalance/procs#installation
sudo apt install exa -y  # replacement for ls. no ner fonts, unlike lsd

#wget https://github.com/sharkdp/hyperfine/releases/download/v1.15.0/hyperfine_1.15.0_amd64.deb
#sudo dpkg -i hyperfine_1.15.0_amd64.deb
#rm hyperfine_1.15.0_amd64.deb

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
# sudo apt install neovim -y  # nvim, but not latest release
# download neovim from release page
# sudo apt remove neovim
# sudo rm ~/.local/bin/nvim || true
cd ~
wget https://github.com/neovim/neovim/releases/download/stable/nvim-linux64.deb
sudo apt install ./nvim-linux64.deb
rm nvim-linux64.deb


# from https://www.lunarvim.org/docs/installation
LV_BRANCH='release-1.2/neovim-0.8' bash <(curl -s https://raw.githubusercontent.com/lunarvim/lunarvim/master/utils/installer/install.sh)
# https://spacevim.org/quick-start-guide/#linux-and-macos
curl -sLf https://spacevim.org/install.sh | bash

bash -c "$(curl -fsSL https://raw.githubusercontent.com/ohmybash/oh-my-bash/master/tools/install.sh)"
# replace OSH_THEME="font" with OSH_THEME="random" in ~/.bashrc
sed -i 's/OSH_THEME="font"/OSH_THEME="random"/' ~/.bashrc

# zsh
#sudo apt install zsh
# sh -c "$(curl -fsSL https://raw.githubusercontent.com/ohmyzsh/ohmyzsh/master/tools/install.sh)"
# sudo apt install zsh-syntax-highlighting -y
# sudo apt install zsh-autosuggestions -y
# sudo apt install zsh-theme-powerlevel10k -y
# sudo apt install zsh-completions -y
# sudo apt install zsh-history-substring-search -y

