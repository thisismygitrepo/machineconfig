

# uninstall then install latest stable release:
# from https://www.lunarvim.org/docs/installation
bash <(curl -s https://raw.githubusercontent.com/lunarvim/lunarvim/master/utils/installer/uninstall.sh)
sudo rm -rdf ~/.config/lvim || true  # kill bad symlinks there
LV_BRANCH='release-1.2/neovim-0.8' bash <(curl -s https://raw.githubusercontent.com/lunarvim/lunarvim/master/utils/installer/install.sh)
export lvim="$HOME/.local/bin/lvim"

# config from Chris
sudo rm -rdf ~/.config/lvim || true # kill bad symlinks there
cd ~/.config
git clone https://github.com/ChristianChiarulli/lvim
sudo apt install xsel

pip install pynvim
pip install flake8

#lvim --headless + 'autocmd User PackerComplete quitall' +PackerSync
# :PackerSync
# :Copilot setup
