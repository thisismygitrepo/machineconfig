#!/usr/bin/bash

# use this: source <(sudo cat ~/code/machineconfig/src/machineconfig/setup_linux/devapps.sh)
~/scripts/croshell -pN --file=~/code/machineconfig/src/machineconfig/jobs/python/python_linux_installers_all.py

## from: https://astronvim.github.io/
#mv ~/.config/nvim ~/.config/nvim.bak
#mv ~/.local/share/nvim/site ~/.local/share/nvim/site.bak
#git clone https://github.com/AstroNvim/AstroNvim ~/.config/nvim
#nvim +PackerSync


#cd ~/code
#git clone https://github.com/neovide/neovide
#cd neovide
#cargo build --release
#croshell.sh -c "P(r'~/code/neovide/target/release/neovide.exe').move(folder=get_env().WindowsApps)"
