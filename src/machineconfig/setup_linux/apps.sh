#!/usr/bin/env bash


# --GROUP:PACKAGE_MANAGERS & ABC: git,nano,net-utils,wget--
echo "🔄 Updating apt package lists..."
echo "📥 Installing nala package manager..."
echo "📥 Installing essential network tools..."
sudo apt update -y || true
sudo apt install nala -y || true  # 🚀 Fast parallel apt manager
sudo nala install curl wget gpg lsb-release apt-transport-https -y || true
sudo nala install git net-tools htop nano -y || true


# --GROUP:NODE_JS_ENVIRONMENT via NVM
echo "📥 Installing Node Version Manager (NVM)..."
curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.40.3/install.sh | bash
echo "🔧 Configuring NVM environment..."
export NVM_DIR="$HOME/.nvm"
[ -s "$NVM_DIR/nvm.sh" ] && \. "$NVM_DIR/nvm.sh"
[ -s "$NVM_DIR/bash_completion" ] && \. "$NVM_DIR/bash_completion"
echo "📥 Installing latest Node.js..."
nvm install node || true

# --GROUP:Terminal eye-candy
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


# --GROUP:Network tools: sshfs,samba,fuse3,nfs-common
echo "📥 Installing sshfs - mount remote filesystems over SSH..."
echo "📥 Installing Samba - LAN-based file sharing..."
sudo nala install sshfs
sudo nala install samba
sudo nala install fuse3 -y || true
sudo nala install nfs-common -y || true

# --GROUP:Dev tools: graphviz,make,rust,libssl-dev,sqlite3,postgresql-client,redis-tools
echo "📥 Installing Graphviz - graph visualization software..."
echo "📥 Installing make - build automation tool..."
echo "📥 Installing SSL development libraries for Rust..."
echo "📥 Installing Rust programming language and toolchain..."
sudo nala install graphviz -y || true
sudo nala install make -y || true  # Required by LunarVim and SpaceVim
(curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh) || true
sudo nala install libssl-dev -y


# --GROUP:Databases: sqlite3,postgresql-client,redis-tools
echo "📥 Installing SQLite - lightweight SQL database..."
echo "📥 Installing PostgreSQL client..."
echo "📥 Installing Redis command-line tools..."
sudo nala install sqlite3 -y || true
sudo nala install postgresql-client -y || true
sudo nala install redis-tools -y || true
