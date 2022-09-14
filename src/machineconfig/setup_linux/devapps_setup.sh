

## from: https://astronvim.github.io/
#mv ~/.config/nvim ~/.config/nvim.bak
#mv ~/.local/share/nvim/site ~/.local/share/nvim/site.bak
#git clone https://github.com/AstroNvim/AstroNvim ~/.config/nvim
#nvim +PackerSync

#nvim --headless +PlugInstall +qall  # this is non-interactive way of running :PlugInstall in nvim, run this after adding the plugins to init.vim
#cd ~/.local/share/nvim/plugged/coc.nvim
#npm install .
#nvim --headless -c 'CocInstall coc-pyright' -c 'qall'

cd ~/code
git clone https://github.com/neovide/neovide
cd neovide
cargo build --release
croshell.sh -c "P(r'~/code/neovide/target/release/neovide.exe').move(folder=get_env().WindowsApps)"
