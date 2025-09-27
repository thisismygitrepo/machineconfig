#!/usr/bin/b# --BLOCK:TEXT_STYLE_TOOLS--
echo """#=======================================================================
🎨 TEXT STYLE TOOLS | Installing terminal text formatters
#======================================================================="""
#================# --BLOCK:FUN_TERMINAL_TOOLS--
echo """#=======================================================================
🎮 FUN TERMINAL TOOLS | Installing amusing terminal animations
#======================================================================="""============# --BLOCK:FILE_SHARING_TOOLS--
echo """#=======================================================================
🔄 FILE SHARING TOOLS | Installing network sharing utilities
#======================================================================="""===================# --BLOCK:DEV_TOOLS--
echo """#=======================================================================
📊 DEVELOPMENT TOOLS | Installing programming utilities
#======================================================================="""===============
# 🛠️ DE# --BLOCK:TERMINAL_EYE_CANDY--
echo """#=======================================================================
🎬 TERMINAL EYE CANDY | Installing visual terminal effects
#======================================================================="""OPMENT TOOLS AND F# --BLOCK:DATABASE_TOOLS--
echo """#=======================================================================
💾 DATABASE TOOLS | Installing database clients
#======================================================================="""UTILITI# --BLOCK:IMAGE_TOOLS--
echo """#=======================================================================
🎨 IMAGE TOOLS | Installing terminal image viewers
#======================================================================="""INSTALLATION SCRIPT
#=======================================================================
# This script installs various development tools and fun terminal utilities

# Set default package manager if not defined
if [ -z "$package_manager" ]; then
  package_manager="nala"  # 📦 Default package manager
  echo "ℹ️ Using default package manager: $package_manager"
fi

echo """#=======================================================================
🎨 TEXT STYLE TOOLS | Installing terminal text formatters
#=======================================================================
"""

echo "📥 Installing fortune - random wisdom generator..."
if [ "$package_manager" = "nala" ]; then
  sudo nala install fortune -y || true
else
  ~/.nix-profile/bin/nix-env -iA nixpkgs.fortune || true
fi

echo "📥 Installing toilet - large ASCII text generator..."
if [ "$package_manager" = "nala" ]; then
  sudo nala install toilet -y || true
else
  ~/.nix-profile/bin/nix-env -iA nixpkgs.toilet || true
fi
# More fun terminal tools: https://linoxide.com/linux-fun-terminal-crazy-output/
# Examples: midnight commander, Asciiquarium, https://github.com/bartobri/no-more-secrets

echo """#=======================================================================
🎮 FUN TERMINAL TOOLS | Installing amusing terminal animations
#=======================================================================
"""

echo "📥 Installing sl - steam locomotive animation..."
if [ "$package_manager" = "nala" ]; then
  sudo nala install sl -y || true
else
  ~/.nix-profile/bin/nix-env -iA nixpkgs.sl || true
fi

echo "📥 Installing aafire - ASCII art fire animation..."
sudo nala install libaa-bin -y

echo """#=======================================================================
🔄 FILE SHARING TOOLS | Installing network sharing utilities
#=======================================================================
"""

echo "📥 Installing easy-sharing - simple file sharing tool..."
# Making sure npm is available in the terminal
export NVM_DIR="$HOME/.nvm"
[ -s "$NVM_DIR/nvm.sh" ] && \. "$NVM_DIR/nvm.sh"  # This loads nvm
npm install -g easy-sharing  # based on https://github.com/parvardegr/sharing
# Alternative: https://github.com/mifi/ezshare

# echo "📥 Installing sshfs - mount remote filesystems over SSH..."
# if [ "$package_manager" = "nala" ]; then
#   sudo nala install sshfs
# else
#   ~/.nix-profile/bin/nix-env -iA nixpkgs.sshfs || true
# fi

echo "📥 Installing Samba - LAN-based file sharing..."
#sudo nala install samba

echo """#=======================================================================
📊 DEVELOPMENT TOOLS | Installing programming utilities
#=======================================================================
"""

echo "📥 Installing Graphviz - graph visualization software..."
if [ "$package_manager" = "nala" ]; then
  sudo nala install graphviz -y || true
else
  ~/.nix-profile/bin/nix-env -iA nixpkgs.graphviz || true
fi

echo "📥 Installing make - build automation tool..."
sudo nala install make -y || true  # Required by LunarVim and SpaceVim

# echo "📥 Installing lynx - text-based web browser..."
# if [ "$package_manager" = "nala" ]; then
#   sudo nala install lynx -y || true
# else
#   ~/.nix-profile/bin/nix-env -iA nixpkgs.lynx || true
# fi

# echo "📥 Installing SpaceVim - Vim distribution with plugins..."
# # https://spacevim.org/quick-start-guide/#linux-and-macos
# (curl -sLf https://spacevim.org/install.sh | bash) || true


echo """#=======================================================================
🎬 TERMINAL EYE CANDY | Installing visual terminal effects
#=======================================================================
"""

echo "📥 Installing cmatrix - Matrix-style terminal animation..."
if [ "$package_manager" = "nala" ]; then
  echo 'keyboard-configuration keyboard-configuration/layout select US English' | sudo debconf-set-selections
  echo 'keyboard-configuration keyboard-configuration/layoutcode string us' | sudo debconf-set-selections
  sudo DEBIAN_FRONTEND=noninteractive nala install -y cmatrix
else
  ~/.nix-profile/bin/nix-env -iA nixpkgs.cmatrix || true
fi

echo "📥 Installing hollywood - Hollywood hacker terminal effect..."
if [ "$package_manager" = "nala" ]; then
  sudo nala install hollywood -y || true
else
  ~/.nix-profile/bin/nix-env -iA nixpkgs.hollywood || true
fi

echo """#=======================================================================
💾 DATABASE TOOLS | Installing database clients
#=======================================================================
"""

echo "📥 Installing SQLite - lightweight SQL database..."
sudo nala install sqlite3 -y || true
echo "📥 Installing PostgreSQL client..."
sudo nala install postgresql-client -y || true

echo """#=======================================================================
🎨 IMAGE TOOLS | Installing terminal image viewers
#=======================================================================
"""

echo "📥 Installing chafa - terminal image viewer..."
sudo nala install chafa -y

echo """#=======================================================================
✅ INSTALLATION COMPLETE | Development tools and utilities installed
#=======================================================================
"""


# echo """#=======================================================================
# 🧰 PROGRAMMING LANGUAGES | Installing language runtimes and tools
# #=======================================================================
# """

# echo "📥 Installing Codon - high-performance Python compiler..."
# /bin/bash -c "$(curl -fsSL https://exaloop.io/install.sh)"

# echo "📥 Installing Rust programming language and toolchain..."
# (curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh) || true
# echo "📥 Installing SSL development libraries for Rust..."
# sudo nala install libssl-dev -y
