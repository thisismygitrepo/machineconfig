#!/usr/bin/bash


# --GROUP:Terminal eye-candy
# Using nala package manager
echo "📥 Installing fortune - random wisdom generator..."
echo "📥 Installing toilet - large ASCII text generator..."
echo "📥 Installing sl - steam locomotive animation..."
echo "📥 Installing aafire - ASCII art fire animation..."
echo "📥 Installing cmatrix - Matrix-style terminal animation..."
echo "📥 Installing hollywood - Hollywood hacker terminal effect..."
echo "📥 Installing chafa - terminal image viewer..."
sudo nala install fortune -y || true
sudo nala install toilet -y || true
sudo nala install sl -y || true
sudo nala install libaa-bin -y
echo 'keyboard-configuration keyboard-configuration/layout select US English' | sudo debconf-set-selections
echo 'keyboard-configuration keyboard-configuration/layoutcode string us' | sudo debconf-set-selections
sudo DEBIAN_FRONTEND=noninteractive nala install -y cmatrix
sudo nala install hollywood -y || true
sudo nala install chafa -y


# --GROUP:Network tools: sshfs,samba
echo "📥 Installing sshfs - mount remote filesystems over SSH..."
echo "📥 Installing Samba - LAN-based file sharing..."
sudo nala install sshfs
sudo nala install samba

# --GROUP:Dev tools: graphviz,make,rust,libssl-dev,sqlite3,postgresql-client,redis-tools
echo "📥 Installing Graphviz - graph visualization software..."
echo "📥 Installing make - build automation tool..."
sudo nala install graphviz -y || true
sudo nala install make -y || true  # Required by LunarVim and SpaceVim
echo "📥 Installing Rust programming language and toolchain..."
(curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh) || true
echo "📥 Installing SSL development libraries for Rust..."
sudo nala install libssl-dev -y


# --GROUP:Databases: sqlite3,postgresql-client,redis-tools
echo "📥 Installing SQLite - lightweight SQL database..."
echo "📥 Installing PostgreSQL client..."
echo "📥 Installing Redis command-line tools..."
sudo nala install sqlite3 -y || true
sudo nala install postgresql-client -y || true
sudo nala install redis-tools -y || true

