
nvim --headless +PlugInstall +qall  # this is non-interactive way of running :PlugInstall in nvim, run this after adding the plugins to init.vim
cd ~/.local/share/nvim/plugged/coc.nvim
npm install .
