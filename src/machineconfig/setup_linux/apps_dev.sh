#!/usr/bin/bash


# --BLOCK:TEXT_STYLE_TOOLS--
# Using nala package manager
echo "ℹ️ Using nala package manager"

echo """#=======================================================================
🎨 TEXT STYLE TOOLS | Installing terminal text formatters
#=======================================================================
"""

echo "📥 Installing fortune - random wisdom generator..."
sudo nala install fortune -y || true

echo "📥 Installing toilet - large ASCII text generator..."
sudo nala install toilet -y || true
# More fun terminal tools: https://linoxide.com/linux-fun-terminal-crazy-output/
# Examples: midnight commander, Asciiquarium, https://github.com/bartobri/no-more-secrets

echo """#=======================================================================
🎮 FUN TERMINAL TOOLS | Installing amusing terminal animations
#=======================================================================
"""

echo "📥 Installing sl - steam locomotive animation..."
sudo nala install sl -y || true

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
sudo nala install graphviz -y || true

echo "📥 Installing make - build automation tool..."
sudo nala install make -y || true  # Required by LunarVim and SpaceVim


echo """#=======================================================================
🎬 TERMINAL EYE CANDY | Installing visual terminal effects
#=======================================================================
"""

echo "📥 Installing cmatrix - Matrix-style terminal animation..."
echo 'keyboard-configuration keyboard-configuration/layout select US English' | sudo debconf-set-selections
echo 'keyboard-configuration keyboard-configuration/layoutcode string us' | sudo debconf-set-selections
sudo DEBIAN_FRONTEND=noninteractive nala install -y cmatrix

echo "📥 Installing hollywood - Hollywood hacker terminal effect..."
sudo nala install hollywood -y || true

echo """#=======================================================================
💾 DATABASE TOOLS | Installing database clients
#=======================================================================
"""

echo "📥 Installing SQLite - lightweight SQL database..."
echo "📥 Installing PostgreSQL client..."
echo "📥 Installing Redis command-line tools..."
sudo nala install sqlite3 -y || true
sudo nala install postgresql-client -y || true
sudo nala install redis-tools -y || true

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
