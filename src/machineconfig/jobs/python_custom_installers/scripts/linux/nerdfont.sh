#!/bin/sh

# download this: https://github.com/ryanoasis/nerd-fonts/releases/
cd ~/Downloads
curl -LO https://github.com/ryanoasis/nerd-fonts/releases/download/v3.2.1/CascadiaCode.tar.xz
tar -xvf CascadiaCode.tar.xz
mkdir -p ~/.local/share/fonts

# mv all *.ttf files to ~/.local/share/fonts
mv ./*.ttf ~/.local/share/fonts

# update font cache
fc-cache -f -v

# clean up
rm -rf CascadiaCode
rm CascadiaCode.tar.xz

# to check installed fonts
# fc-list | grep CascadiaCove
echo "USE 'CaskaydiaCove Nerd Font' in VSCODE"
