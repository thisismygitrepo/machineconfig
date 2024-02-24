

if [ -z "$package_manager" ]; then
  package_manager="apt"  # see if variable package_manager is defined, if not, define it as "nix"
fi


# ---------------------------- text style ------------------------------------
yes '' | sed 3q; echo "----------------------------- installing fortune ----------------------------"; yes '' | sed 3q
if [ "$package_manager" = "apt" ]; then
  sudo apt install fortune -y || true  # generate random text in the form of piece of wisdom
else
  ~/.nix-profile/bin/nix-env -iA nixpkgs.fortune || true
fi

yes '' | sed 3q; echo "----------------------------- installing boxes ----------------------------"; yes '' | sed 3q
if [ "$package_manager" = "apt" ]; then
  sudo apt install boxes -y || true  # for ascii banners. boxes -l for list of boxes.
else
  ~/.nix-profile/bin/nix-env -iA nixpkgs.boxes || true
fi

# yes '' | sed 3q; echo "----------------------------- installing cowsay ----------------------------"; yes '' | sed 3q
# if [ "$package_manager" = "apt" ]; then
#   sudo apt install cowsay -y || true  # animals saying things. Different figures with -f. Full list: cowsay -l
# else
#   # ~/.nix-profile/bin/nix-env -iA nixpkgs.neo-cowsay || true
#   # ~/.nix-profile/bin/nix-env -iA nixpkgs.cowsay || true
# fi
sudo apt install cowsay -y || true  # animals saying things. This installer gives different figures to nix installer. Sticking to this one to avoid errors.


yes '' | sed 3q; echo "----------------------------- installing lolcat ----------------------------"; yes '' | sed 3q
if [ "$package_manager" = "apt" ]; then
  sudo apt install lolcat -y || true  # for coloring text in terminal.
else
  ~/.nix-profile/bin/nix-env -iA nixpkgs.lolcat || true
fi

yes '' | sed 3q; echo "----------------------------- installing toilet ----------------------------"; yes '' | sed 3q
if [ "$package_manager" = "apt" ]; then
  sudo apt install toilet -y || true  # large ascii text
else
  ~/.nix-profile/bin/nix-env -iA nixpkgs.toilet || true
fi

yes '' | sed 3q; echo "----------------------------- installing figlet ----------------------------"; yes '' | sed 3q
if [ "$package_manager" = "apt" ]; then
  sudo apt install figlet -y || true  # large ascii text. See: showfigfonts for full list of fonts. use -f to change font.
  ~/.nix-profile/bin/nix-env -iA nixpkgs.nms || true
else
  ~/.nix-profile/bin/nix-env -iA nixpkgs.figlet || true
fi

# see more here: https://linoxide.com/linux-fun-terminal-crazy-output/
# midnight commander, similarv# Asciiquarium# https://github.com/bartobri/no-more-secrets
# https://www.youtube.com/watch?v=haitmoSyTls


# ---------------------------- Fun ------------------------------------
yes '' | sed 3q; echo "----------------------------- installing sl ----------------------------"; yes '' | sed 3q
if [ "$package_manager" = "apt" ]; then
  sudo apt install sl -y || true  # for fun
else
  ~/.nix-profile/bin/nix-env -iA nixpkgs.sl || true
fi


yes '' | sed 3q; echo "----------------------------- installing aafire ----------------------------"; yes '' | sed 3q
sudo apt-get install libaa-bin -y


# yes '' | sed 3q; echo "----------------------------- installing sharewifi ----------------------------"; yes '' | sed 3q
# npm install sharewifi -g || true


yes '' | sed 3q; echo "----------------------------- installing easy-sharing ----------------------------"; yes '' | sed 3q
# Making sure npm is available in the terminal
export NVM_DIR="$HOME/.nvm"
[ -s "$NVM_DIR/nvm.sh" ] && \. "$NVM_DIR/nvm.sh"  # This loads nvm
npm install -g easy-sharing  # based on https://github.com/parvardegr/sharing
# alternative: https://github.com/mifi/ezshare


yes '' | sed 3q; echo "----------------------------- installing sshfs ----------------------------"; yes '' | sed 3q
if [ "$package_manager" = "apt" ]; then
  sudo apt install sshfs  # mount remote filesystems over ssh
else
  ~/.nix-profile/bin/nix-env -iA nixpkgs.sshfs || true
fi

yes '' | sed 3q; echo "----------------------------- installing samba ----------------------------"; yes '' | sed 3q
#sudo apt install samba  # LAN-based file sharing


yes '' | sed 3q; echo "----------------------------- installing cloudflared Warp --------------------------------"; yes '' | sed 3q
# as per Ubuntu of https://pkg.cloudflareclient.com/
curl -fsSL https://pkg.cloudflareclient.com/pubkey.gpg | sudo gpg --yes --dearmor --output /usr/share/keyrings/cloudflare-warp-archive-keyring.gpg
echo "deb [arch=amd64 signed-by=/usr/share/keyrings/cloudflare-warp-archive-keyring.gpg] https://pkg.cloudflareclient.com/ jammy main" | sudo tee /etc/apt/sources.list.d/cloudflare-client.list
sudo apt-get update && sudo apt-get install cloudflare-warp -y


yes '' | sed 3q; echo "----------------------------- installing graphviz ----------------------------"; yes '' | sed 3q
if [ "$package_manager" = "apt" ]; then
  sudo apt install graphviz -y || true
else
  ~/.nix-profile/bin/nix-env -iA nixpkgs.graphviz || true
fi

yes '' | sed 3q; echo "----------------------------- installing make ----------------------------"; yes '' | sed 3q
sudo apt install make -y || true  # lvim and spacevim require it.

# yes '' | sed 3q; echo "----------------------------- installing lynx ----------------------------"; yes '' | sed 3q
# if [ "$package_manager" = "apt" ]; then
#   sudo apt install lynx -y || true  # tex browser, just like w3m
# else
#   ~/.nix-profile/bin/nix-env -iA nixpkgs.lynx || true
#   ~/.nix-profile/bin/nix-env -iA nixpkgs.brave
# fi

# yes '' | sed 3q; echo "----------------------------- installing redis ----------------------------"; yes '' | sed 3q
# if [ "$package_manager" = "apt" ]; then
#   # installation for ubuntu as per https://redis.io/docs/getting-started/installation/install-redis-on-linux/
#   curl -fsSL https://packages.redis.io/gpg | sudo gpg --dearmor -o /usr/share/keyrings/redis-archive-keyring.gpg
#   echo "deb [signed-by=/usr/share/keyrings/redis-archive-keyring.gpg] https://packages.redis.io/deb $(lsb_release -cs) main" | sudo tee /etc/apt/sources.list.d/redis.list
#   sudo apt-get update
#   sudo apt-get install redis -y
# else
#   ~/.nix-profile/bin/nix-env -iA nixpkgs.redis || true
# fi


yes '' | sed 3q; echo "----------------------------- installing ncdu ----------------------------"; yes '' | sed 3q
if [ "$package_manager" = "apt" ]; then
  sudo apt install ncdu -y || true   # disk usage analyzer, like diskonaut
else
  ~/.nix-profile/bin/nix-env -iA nixpkgs.ncdu || true
fi



# yes '' | sed 3q; echo "----------------------------- installing spacevim ----------------------------"; yes '' | sed 3q
# # https://spacevim.org/quick-start-guide/#linux-and-macos
# (curl -sLf https://spacevim.org/install.sh | bash) || true


# ---------------------------- Programming Languages ------------------------------------
# yes '' | sed 3q; echo "----------------------------- installing codon ----------------------------"; yes '' | sed 3q
# /bin/bash -c "$(curl -fsSL https://exaloop.io/install.sh)"

# yes '' | sed 3q; echo "----------------------------- installing rust ----------------------------"; yes '' | sed 3q
# # curl https://sh.rustup.rs -sSf | sh
# (curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh) || true


yes '' | sed 3q; echo "----------------------------- installing cmatrix ----------------------------"; yes '' | sed 3q
if [ "$package_manager" = "apt" ]; then
  echo 'keyboard-configuration keyboard-configuration/layout select US English' | sudo debconf-set-selections
  echo 'keyboard-configuration keyboard-configuration/layoutcode string us' | sudo debconf-set-selections
  sudo DEBIAN_FRONTEND=noninteractive apt-get install -y cmatrix
else
  ~/.nix-profile/bin/nix-env -iA nixpkgs.cmatrix || true
fi

yes '' | sed 3q; echo "----------------------------- installing hollywood ----------------------------"; yes '' | sed 3q
if [ "$package_manager" = "apt" ]; then
  sudo apt install hollywood -y || true  # for fun
else
  ~/.nix-profile/bin/nix-env -iA nixpkgs.hollywood || true
fi
