#!/usr/bin/bash
# 📦 System Package Managers and Utilities Setup

# ----------------- 📥 Package Managers -----------------
yes '' | sed 3q; echo "----------------------------- installing upgrading and updating apt ----------------------------"; yes '' | sed 3q
sudo apt update -y || true
sudo apt install nala -y || true  # 🚀 Fast parallel apt manager
sudo nala install curl wget gpg lsb-release apt-transport-https -y || true  # 🌐 Network tools

# 📲 Install Nix Package Manager
curl -L https://nixos.org/nix/install | sh  # 🔄 Cross-platform package manager
. ~/.nix-profile/etc/profile.d/nix.sh

# 🍺 Install Homebrew
export NONINTERACTIVE=1
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

# -------------------- 🛠️ Utilities --------------------
yes '' | sed 3q; echo "----------------------------- installing fusemount3 --------------------------------"; yes '' | sed 3q
sudo nala install fuse3 -y || true  # 📂 Filesystem support
sudo nala install nfs-common -y || true  # 🗄️ NFS mounting support

yes '' | sed 3q; echo "----------------------------- installing uv --------------------------------"; yes '' | sed 3q
curl -LsSf https://astral.sh/uv/install.sh | sh  # ⚡ Fast Python package installer

yes '' | sed 3q; echo "----------------------------- installing nvm of nodejs --------------------------"; yes '' | sed 3q
# 📝 Node Version Manager setup
curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.40.1/install.sh | bash
export NVM_DIR="$HOME/.nvm"
[ -s "$NVM_DIR/nvm.sh" ] && \. "$NVM_DIR/nvm.sh"
[ -s "$NVM_DIR/bash_completion" ] && \. "$NVM_DIR/bash_completion"
nvm install node || true

yes '' | sed 3q; echo "----------------------------- installing git ----------------------------"; yes '' | sed 3q
sudo nala install git net-tools htop nano -y || true  # 🔧 Dev tools & system monitors

