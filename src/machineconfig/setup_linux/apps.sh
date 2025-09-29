#!/usr#


# --GROUP:PACKAGE_MANAGERS & ABC: git,nano,net-utils,wget--
echo """#=======================================================================
📥 PACKAGE MANAGERS | Installing and configuring system package managers
#=======================================================================
"""
# Update apt and install nala
echo "🔄 Updating apt package lists..."
sudo apt update -y || true
echo "📥 Installing nala package manager..."
sudo apt install nala -y || true  # 🚀 Fast parallel apt manager
echo "📥 Installing essential network tools..."
sudo nala install curl wget gpg lsb-release apt-transport-https -y || true
sudo nala install git net-tools htop nano -y || true


# --GROUP:SYSTEM UTILS: fuse3,nfs-common,redis-tools--
echo """#=======================================================================
🛠️ SYSTEM UTILITIES | Installing essential system tools
#=======================================================================
"""
echo "📂 Installing filesystem utilities..."
sudo nala install fuse3 -y || true
sudo nala install nfs-common -y || true

# --GROUP:NODE_JS_ENVIRONMENT via NVM
echo """
#=======================================================================
📝 NODE.JS ENVIRONMENT | Installing Node Version Manager
#======================================================================="""
echo "📥 Installing Node Version Manager (NVM)..."
curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.40.3/install.sh | bash
echo "🔧 Configuring NVM environment..."
export NVM_DIR="$HOME/.nvm"
[ -s "$NVM_DIR/nvm.sh" ] && \. "$NVM_DIR/nvm.sh"
[ -s "$NVM_DIR/bash_completion" ] && \. "$NVM_DIR/bash_completion"
echo "📥 Installing latest Node.js..."
nvm install node || true
