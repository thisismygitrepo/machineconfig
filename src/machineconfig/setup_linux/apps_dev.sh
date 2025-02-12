#!/usr/bin/bash
# 🛠️ Development Tools and Fun Utilities Installation Script

if [ -z "$package_manager" ]; then
  package_manager="nala"  # 📦 Default package manager
fi

# 🎨 Text Style Tools
yes '' | sed 3q; echo "----------------------------- installing fortune ----------------------------"; yes '' | sed 3q
if [ "$package_manager" = "nala" ]; then
  sudo nala install fortune -y || true  # 🔮 Random wisdom generator
else
  ~/.nix-profile/bin/nix-env -iA nixpkgs.fortune || true
fi

yes '' | sed 3q; echo "----------------------------- installing toilet ----------------------------"; yes '' | sed 3q
if [ "$package_manager" = "nala" ]; then
  sudo nala install toilet -y || true  # 📝 Large ASCII text generator
else
  ~/.nix-profile/bin/nix-env -iA nixpkgs.toilet || true
fi
# see more here: https://linoxide.com/linux-fun-terminal-crazy-output/
# midnight commander, similarv# Asciiquarium# https://github.com/bartobri/no-more-secrets
# https://www.youtube.com/watch?v=haitmoSyTls

# 🎮 Fun Terminal Tools
yes '' | sed 3q; echo "----------------------------- installing sl ----------------------------"; yes '' | sed 3q
if [ "$package_manager" = "nala" ]; then
  sudo nala install sl -y || true  # 🚂 Steam locomotive animation
else
  ~/.nix-profile/bin/nix-env -iA nixpkgs.sl || true
fi

yes '' | sed 3q; echo "----------------------------- installing aafire ----------------------------"; yes '' | sed 3q
sudo nala install libaa-bin -y


# yes '' | sed 3q; echo "----------------------------- installing sharewifi ----------------------------"; yes '' | sed 3q
# npm install sharewifi -g || true


yes '' | sed 3q; echo "----------------------------- installing easy-sharing ----------------------------"; yes '' | sed 3q
# Making sure npm is available in the terminal
export NVM_DIR="$HOME/.nvm"
[ -s "$NVM_DIR/nvm.sh" ] && \. "$NVM_DIR/nvm.sh"  # This loads nvm
npm install -g easy-sharing  # based on https://github.com/parvardegr/sharing
# alternative: https://github.com/mifi/ezshare


# yes '' | sed 3q; echo "----------------------------- installing sshfs ----------------------------"; yes '' | sed 3q
# if [ "$package_manager" = "nala" ]; then
#   sudo nala install sshfs  # mount remote filesystems over ssh
# else
#   ~/.nix-profile/bin/nix-env -iA nixpkgs.sshfs || true
# fi


yes '' | sed 3q; echo "----------------------------- installing samba ----------------------------"; yes '' | sed 3q
#sudo nala install samba  # LAN-based file sharing


yes '' | sed 3q; echo "----------------------------- installing graphviz ----------------------------"; yes '' | sed 3q
if [ "$package_manager" = "nala" ]; then
  sudo nala install graphviz -y || true  # 📈 Graph visualization
else
  ~/.nix-profile/bin/nix-env -iA nixpkgs.graphviz || true
fi


yes '' | sed 3q; echo "----------------------------- installing make ----------------------------"; yes '' | sed 3q
sudo nala install make -y || true  # lvim and spacevim require it.


# yes '' | sed 3q; echo "----------------------------- installing lynx ----------------------------"; yes '' | sed 3q
# if [ "$package_manager" = "nala" ]; then
#   sudo nala install lynx -y || true  # tex browser, just like w3m
# else
#   ~/.nix-profile/bin/nix-env -iA nixpkgs.lynx || true
# fi


# yes '' | sed 3q; echo "----------------------------- installing spacevim ----------------------------"; yes '' | sed 3q
# # https://spacevim.org/quick-start-guide/#linux-and-macos
# (curl -sLf https://spacevim.org/install.sh | bash) || true


# ---------------------------- Programming Languages ------------------------------------
# yes '' | sed 3q; echo "----------------------------- installing codon ----------------------------"; yes '' | sed 3q
# /bin/bash -c "$(curl -fsSL https://exaloop.io/install.sh)"


yes '' | sed 3q; echo "----------------------------- installing rust ----------------------------"; yes '' | sed 3q
(curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh) || true
sudo nala install libssl-dev -y  # 🔐 SSL development libraries

# 🎬 Terminal Eye Candy
yes '' | sed 3q; echo "----------------------------- installing cmatrix ----------------------------"; yes '' | sed 3q
if [ "$package_manager" = "nala" ]; then
  echo 'keyboard-configuration keyboard-configuration/layout select US English' | sudo debconf-set-selections
  echo 'keyboard-configuration keyboard-configuration/layoutcode string us' | sudo debconf-set-selections
  sudo DEBIAN_FRONTEND=noninteractive nala install -y cmatrix  # 👾 Matrix-style animation
else
  ~/.nix-profile/bin/nix-env -iA nixpkgs.cmatrix || true
fi

yes '' | sed 3q; echo "----------------------------- installing hollywood ----------------------------"; yes '' | sed 3q
if [ "$package_manager" = "nala" ]; then
  sudo nala install hollywood -y || true  # 🎬 Hollywood hacker terminal effect
else
  ~/.nix-profile/bin/nix-env -iA nixpkgs.hollywood || true
fi

# 💾 Database Tools
yes '' | sed 3q; echo "----------------------------- installing sqlite --------------------------"; yes '' | sed 3q
sudo nala install sqlite3 -y || true  # 🗃️ SQLite database
sudo nala install postgresql-client -y || true  # 🐘 PostgreSQL client

# 🎨 Image Tools
yes '' | sed 3q; echo "----------------------------- installing chafa ----------------------------"; yes '' | sed 3q
sudo nala install chafa -y  # 🖼️ Terminal image viewer
