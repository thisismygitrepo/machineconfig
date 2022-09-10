

# The following can run with no prerequisites:
# when there is a !! sign, means the command before it requires input, putting another command behind it will cause it to fail

# https://gitlab.com/volian/nala/-/wikis/Installation  # https://gitlab.com/volian/nala
echo "deb https://deb.volian.org/volian/ scar main" | sudo tee /etc/apt/sources.list.d/volian-archive-scar-unstable.list
wget -qO - https://deb.volian.org/volian/scar.key | sudo tee /etc/apt/trusted.gpg.d/volian-archive-scar-unstable.gpg > /dev/null

sudo apt update && sudo apt install nala -y  # nala is a command line tool for managing your Linux system
sudo nala update && sudo nala -y upgrade  # this is suprior to apt
sudo nala install nodejs -y  # for nvim plugins

sudo nala install wget -y  # for downloading files
sudo nala install curl -y  # for handling http requests
sudo nala install net-tools  # gives ifconfig
sudo nala install git -y  # for version control

bash -c "$(curl -fsSL https://raw.githubusercontent.com/ohmybash/oh-my-bash/master/tools/install.sh)"
sudo nala install sl -y  # for fun
sudo nala install cmatrix -y  # for fun
sudo nala install hollywood -y  # for fun
sudo nala install neofetch -y  # for system info
neofetch

sudo nala install tmux -y # allows multiple terminals that are persistent.
sudo nala install ranger   # terminal-based file explorer, alternative: lf (Go-based), tere (Rust-based), nnn (C-based), vifm (C-based), mc (C-based), etc
sudo nala install bat  # cat with colors.
sudo nala install neovim -y  # nvim
sh -c 'curl -fLo "${XDG_DATA_HOME:-$HOME/.local/share}"/nvim/site/autoload/plug.vim --create-dirs https://raw.githubusercontent.com/junegunn/vim-plug/master/plug.vim'  # plugin manager for nvim
sudo nala install exuberant-ctags -y  # for tagbar


# midnight commander, similar
# ncdu disk usage analyzer.
# Asciiquarium
# https://github.com/bartobri/no-more-secrets
# boxes
# lolcat
# bottom  # rust-based alternative to htop
# micro # terminal-based text editor, alternative to nano
# https://www.youtube.com/watch?v=2OHrTQVlRMg


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

