
sudo apt remove neovim
sudo rm /home/aalsaf01/.local/bin/nvim || true
cd ~
wget https://github.com/neovim/neovim/releases/download/stable/nvim-linux64.deb
sudo apt install ./nvim-linux64.deb
rm nvim-linux64.deb


# from https://www.lunarvim.org/docs/installation
bash <(curl -s https://raw.githubusercontent.com/lunarvim/lunarvim/master/utils/installer/uninstall.sh)
sudo rm -rdf ~/.config/lvim || true  # kill bad symlinks there
LV_BRANCH='release-1.2/neovim-0.8' bash <(curl -s https://raw.githubusercontent.com/lunarvim/lunarvim/master/utils/installer/install.sh)
export lvim="$HOME/.local/bin/lvim"

sudo rm -rdf ~/.config/lvim || true
cd ~/.config
git clone https://github.com/ChristianChiarulli/lvim
sudo apt install xsel
pip install pynvim

# :PackerSync
# :Copilot setup