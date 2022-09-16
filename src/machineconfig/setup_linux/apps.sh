

# The following can run with no prerequisites:
# when there is a !! sign, means the command before it requires input, putting another command behind it will cause it to fail

# https://gitlab.com/volian/nala/-/wikis/Installation  # https://gitlab.com/volian/nala
#echo "deb https://deb.volian.org/volian/ scar main" | sudo tee /etc/apt/sources.list.d/volian-archive-scar-unstable.list
#wget -qO - https://deb.volian.org/volian/scar.key | sudo tee /etc/apt/trusted.gpg.d/volian-archive-scar-unstable.gpg > /dev/null

sudo apt update && sudo apt install nala -y  # nala is a command line tool for managing your Linux system
sudo nala update && sudo nala upgrade -y  # this is suprior to apt

curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash -  # The NodeSource repository
sudo nala update
sudo nala install nodejs -y  # for nvim plugins
#curl --compressed -o- -L https://yarnpkg.com/install.sh | bash
sudo nala install npm -y  # for nvim plugins

sudo nala install wget -y  # for downloading files
sudo nala install curl -y  # for handling http requests
sudo nala install net-tools -y  # gives ifconfig
sudo nala install git -y  # for version control
sudp nala install ncdu   # disk usage analyzer.

sudo nala install tmux -y # allows multiple terminals that are persistent.
sudo nala install bat -y  # cat with colors.
sudo nala install ranger -y   # terminal-based file explorer, alternative: lf (Go-based), tere (Rust-based), nnn (C-based), vifm (C-based), mc (C-based), etc
sudo nala install fzf -y  # fuzzy finder
sudo nala install fd-find -y  # find alternative
sudo nala install ugrep -y  # just as good as grep, but consistent with windows

bash -c "$(curl -fsSL https://raw.githubusercontent.com/ohmybash/oh-my-bash/master/tools/install.sh)" -y
sudo nala install sl -y  # for fun
sudo nala install cmatrix -y  # for fun
sudo nala install hollywood -y  # for fun
sudo nala install neofetch -y  # for system info
sudo nala install boxes -y  # for ascii banners
sudo nala install toilet -y  # large ascii text
sudo nala install figlet -y  # large ascii text
neofetch

# ------------------------------ EDITORS -----------------------------
# curl https://sh.rustup.rs -sSf | sh
curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh
#sudo nala install neovim -y  # nvim, but not latest release
bash <(curl -s https://raw.githubusercontent.com/LunarVim/LunarVim/rolling/utils/installer/install-neovim-from-release)
# https://github.com/LunarVim/LunarVim
bash <(curl -s https://raw.githubusercontent.com/lunarvim/lunarvim/master/utils/installer/install.sh)
# https://spacevim.org/quick-start-guide/#linux-and-macos
curl -sLf https://spacevim.org/install.sh | bash


# midnight commander, similar
# Asciiquarium
# https://github.com/bartobri/no-more-secrets
# lolcat


# install chrome:
# wget https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb
# sudo dpkg -i google-chrome-stable_current_amd64.deb
# install snap store
# sudo mv /etc/apt/preferences.d/nosnap.pref ~/Documents/nosnap.backup
# sudo nala update
# sudo nala install snapd
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

