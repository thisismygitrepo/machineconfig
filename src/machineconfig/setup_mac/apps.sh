#!/usr/bin/env bash

/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
echo "🔄 Updating Homebrew..."
brew update || true

# --GROUP:ESSENTIAL_SYSTEM:git,nano,curl,nvm,nodejs,brave-browser,visual-studio-code
echo "📥 Installing essential tools..."
echo "📥 Installing Git version control..."
echo "📥 Installing Nano text editor..."
echo "📥 Installing Node Version Manager (NVM)..."
# Note: git and nano are pre-installed on macOS, but we install via Homebrew to ensure latest versions
brew install git || true
brew install nano || true
brew install curl || true
# Install NVM
if [ ! -s "$HOME/.nvm/nvm.sh" ]; then
    echo "📥 Installing NVM (Node Version Manager)..."
    curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.40.3/install.sh | bash
fi
echo "🔧 Configuring NVM environment..."
export NVM_DIR="$HOME/.nvm"
[ -s "$NVM_DIR/nvm.sh" ] && \. "$NVM_DIR/nvm.sh"
echo "📥 Installing latest Node.js..."
nvm install node || true
brew install --cask brave-browser || true
brew install --cask visual-studio-code || true

# Database tools
# echo "📥 Installing SQLite - lightweight SQL database..."
# echo "📥 Installing PostgreSQL client..."
# echo "📥 Installing Redis command-line tools..."
# brew install sqlite3 || true
# brew install postgresql || true
# brew install redis || true

# --GROUP:TerminalEyeCandy:fortune,toilet,sl,cmatrix,chafa
echo "📥 Installing fortune - random wisdom generator..."
echo "📥 Installing figlet - ASCII art text generator..."
echo "📥 Installing cowsay - ASCII cow speech generator..."
echo "📥 Installing lolcat - colorized text output..."
echo "📥 Installing chafa - terminal image viewer..."
brew install fortune || true
brew install figlet || true
brew install cowsay || true
brew install lolcat || true
brew install chafa || true

# --GROUP:NetworkTools: sshfs,nfs-utils
echo "📥 Installing SSHFS - mount remote filesystems over SSH..."
echo "📥 Installing NFS utilities..."
brew install sshfs || true
brew install nfs-utils || true

# --GROUP:DEV_SYSTEM: graphviz,make,rust,sqlite3,postgresql-client,redis-tools,ffmpeg
echo "📥 Installing Graphviz - graph visualization software..."
echo "📥 Installing make - build automation tool..."
echo "📥 Installing FFmpeg - multimedia framework..."
echo "📥 Installing SSL/TLS development libraries..."
echo "📥 Installing Rust programming language and toolchain..."
brew install graphviz || true
brew install make || true
brew install ffmpeg || true
brew install openssl || true

# Install Rust if not already installed
if ! command -v rustc &> /dev/null; then
    echo "📥 Installing Rust..."
    curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh -s -- -y || true
fi



