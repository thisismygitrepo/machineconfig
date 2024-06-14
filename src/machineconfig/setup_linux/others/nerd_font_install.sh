#!/bin/sh

# download this: https://github.com/ryanoasis/nerd-fonts/releases/download/v3.2.1/CascadiaCode.tar.xz
cd ~/Downloads
curl -LO https://github.com/ryanoasis/nerd-fonts/releases/download/v3.2.1/CascadiaCode.tar.xz

# extract it
tar -xvf CascadiaCode.tar.xz

# mkdir -p ~/.local/share/fonts
mkdir -p ~/.local/share/fonts

# mv all *.ttf files to ~/.local/share/fonts
mv CascadiaCode/*.ttf ~/.local/share/fonts

# update font cache
fc-cache -f -v

# clean up
rm -rf CascadiaCode
rm CascadiaCode.tar.xz

# to check installed fonts
# fc-list | grep CascadiaCode
