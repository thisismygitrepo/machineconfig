#!/usr/bin/bash


# ----------------- package manager -----------------
sudo apt update && sudo apt install nala -y  # nala is a command line tool for managing your Linux system
sudo nala update && sudo nala upgrade -y  # this is suprior to apt

# -------------------- Utilities --------------------
curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash -  # The NodeSource repository, must add to get latest node
# consider asdf tool for managing versions of python, node, etc.
sudo apt update
sudo apt install nodejs -y  # for nvim plugins
sudo apt install npm -y  # for nvim plugins
#curl --compressed -o- -L https://yarnpkg.com/install.sh | bash
sudo apt install wget -y  # for downloading files
sudo apt install curl -y  # for handling http requests
sudo apt install make -y  # lvim and spacevim require it.
sudo apt install net-tools -y  # gives ifconfig
sudo apt install git -y  # for version control
sudp apt install ncdu   # disk usage analyzer.
sudo apt install tmux -y # allows multiple terminals that are persistent.
# sudo apt install tmate -y  # remote tmux, see https://tmate.io
# https://github.com/leonwind/cli2cloud
# https://github.com/sorenisanerd/gotty
# https://devsession.is/


# ------------------- File Managers ---------------------------
sudo apt install bat -y  # cat with colors.
sudo apt install ranger -y   # terminal-based file explorer, alternative: lf (Go-based), tere (Rust-based), nnn (C-based), vifm (C-based), mc (C-based), etc
# ranger is good, but for consistency with Windows, use lf:
curl https://raw.githubusercontent.com/thisismygitrepo/machineconfig/main/src/machineconfig/setup_linux/tools/lf.sh | sh

sudo apt install fzf -y  # fuzzy finder
sudo apt install fd-find -y  # find alternative
sudo apt install ripgrep -y  # rg command, rust-based, blazingly fast grep.
sudo apt install ugrep -y  # just as good as grep, but consistent with windows
sudo apt install exa  # replacement for ls. no ner fonts, unlike lsd

cd ~
wget https://dystroy.org/broot/download/x86_64-linux/broot  # broot is an fzf variant. It's excellent for viewing folder structure and layered search.
chmod +x broot
sudo mv ./broot /usr/local/bin/


cd ~
mkdir "tmp_asdf"
cd tmp_asdf
wget https://github.com/zellij-org/zellij/releases/latest/download/zellij-x86_64-unknown-linux-musl.tar.gz
tar -xvzf *
chmod +x ./zellij
sudo mv ./zellij /usr/local/bin/
cd ~
rm -rdf tmp_asdf


cd ~
mkdir "tmp_asdf"
cd tmp_asdf
wget https://github.com/tbillington/kondo/releases/latest/download/kondo-x86_64-unknown-linux-gnu.tar.gz
tar -xvzf *
chmod +x ./kondo
sudo mv ./kondo /usr/local/bin/
cd ~
rm -rdf tmp_asdf


cd ~
mkdir "tmp_asdf"
cd tmp_asdf
get_latest_release() {
  curl --silent "https://api.github.com/repos/$1/releases/latest" | # Get latest release from GitHub api
    grep '"tag_name":' |                                            # Get tag line
    sed -E 's/.*"([^"]+)".*/\1/'                                    # Pluck JSON value
}
latest=$(get_latest_release "nushell/nushell")
wget https://github.com/nushell/nushell/releases/download/$latest/nu-$latest-x86_64-unknown-linux-gnu.tar.gz
tar -xvzf *
chmod +x ./nu
sudo mv ./nu /usr/local/bin/
cd ~
rm -rdf tmp_asdf



#cd ~
#mkdir "tmp_asdf"
#cd tmp_asdf
#wget https://github.com/Peltoche/lsd/releases/latest/download/lsd-0.23.1-x86_64-unknown-linux-gnu.tar.gz
#tar -xvzf *
#chmod +x ./lsd
#sudo mv ./lsd /usr/local/bin/
#cd ~
#rm -rdf tmp_asdf


# ---------------------------- text style ------------------------------------
bash -c "$(curl -fsSL https://raw.githubusercontent.com/ohmybash/oh-my-bash/master/tools/install.sh)"
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
bash <(curl -s https://raw.githubusercontent.com/LunarVim/LunarVim/rolling/utils/installer/install-neovim-from-release)
# https://github.com/LunarVim/LunarVim
bash <(curl -s https://raw.githubusercontent.com/lunarvim/lunarvim/master/utils/installer/install.sh)
# https://spacevim.org/quick-start-guide/#linux-and-macos
curl -sLf https://spacevim.org/install.sh | bash


# install chrome:
# wget https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb
# sudo dpkg -i google-chrome-stable_current_amd64.deb
# install snap store
# sudo mv /etc/apt/preferences.d/nosnap.pref ~/Documents/nosnap.backup
# sudo apt update
# sudo apt install snapd
# install development apps:
# sudo snap install pycharm-community --classic
# sudo snap install code --classic
# sudo snap install powershell --classic

# conda
#apt-get install libgl1-mesa-glx libegl1-mesa libxrandr2 libxrandr2 libxss1 libxcursor1 libxcomposite1 libasound2 libxi6 libxtst6
# miniconda
#wget https://repo.anaconda.com/miniconda/Miniconda3-py39_4.10.3-Linux-x86_64.sh
#bash Miniconda3-py39_4.10.3-Linux-x86_64.sh -y
#source .bashrc  # reload to activate conda
## notice that on linux, the default is that miniconda will be added to PATH unlike windows where this is not recommended

