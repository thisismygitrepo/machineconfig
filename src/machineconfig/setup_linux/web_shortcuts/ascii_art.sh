
# check if path "/usr/games/cowsay" exists, if not install boxes:
if [ ! -f "/usr/games/cowsay" ]; then
  echo "----------------------------- installing boxes ----------------------------"
  sudo apt install cowsay -y || true  # for ascii banners. boxes -l for list of boxes.
  ~/.nix-profile/bin/nix-env -iA nixpkgs.cowsay || true
fi

# repeat for "/usr/games/lolcat"
if [ ! -f "/usr/games/lolcat" ]; then
  echo "----------------------------- installing lolcat ----------------------------"
#  sudo apt install lolcat -y || true  # for coloring text in terminal.
  ~/.nix-profile/bin/nix-env -iA nixpkgs.lolcat || true
fi


# repeat for "/usr/bin/boxes"
if [ ! -f "/usr/bin/boxes" ]; then
  echo "----------------------------- installing cowsay ----------------------------"
#  sudo apt install boxes -y || true  # animals saying things. Different figures with -f. Full list: cowsay -l
  ~/.nix-profile/bin/nix-env -iA nixpkgs.boxes || true
fi

# repeat for "/usr/bin/figlet
if [ ! -f "/usr/bin/figlet" ]; then
  echo "----------------------------- installing figlet ----------------------------"
  sudo apt install figlet -y || true  # large ascii text. See: showfigfonts for full list of fonts. use -f to change font.
  ~/.nix-profile/bin/nix-env -iA nixpkgs.figlet || true
fi

