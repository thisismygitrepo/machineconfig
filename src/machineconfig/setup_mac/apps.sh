#!/usr/bin/env bash

# Detect Mac architecture
ARCH=$(uname -m)
if [[ "$ARCH" == "arm64" ]]; then
    echo "🍎 Detected Apple Silicon (M-series chip)"
    BREW_PATH="/opt/homebrew/bin/brew"
else
    echo "🍎 Detected Intel chip"
    BREW_PATH="/usr/local/bin/brew"
fi

# Check if Homebrew is installed, if not install it
if ! command -v brew &> /dev/null; then
    echo "🍺 Installing Homebrew for $ARCH architecture..."
    /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
    # Add Homebrew to PATH
    eval "$($BREW_PATH shellenv)"
    echo "✅ Homebrew installed successfully for $ARCH"
else
    echo "✅ Homebrew already installed"
    eval "$($BREW_PATH shellenv)"
fi

# Update Homebrew
echo "🔄 Updating Homebrew..."
brew update || true

# --GROUP:ESSENTIAL_SYSTEM:git,nano,curl,nvm,nodejs
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

# Database tools
echo "📥 Installing SQLite - lightweight SQL database..."
echo "📥 Installing PostgreSQL client..."
echo "📥 Installing Redis command-line tools..."
brew install sqlite3 || true
brew install postgresql || true
brew install redis || true

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

# --GROUP:OTHER_ESSENTIAL:htop,bottom,ripgrep,fd,fzf,zoxide
echo "📥 Installing htop - interactive process viewer..."
echo "📥 Installing bottom - alternative system monitor..."
echo "📥 Installing ripgrep - fast text search..."
echo "📥 Installing fd - fast file finder..."
echo "📥 Installing fzf - fuzzy finder..."
echo "📥 Installing zoxide - smart directory jumper..."
brew install htop || true
brew install bottom || true
brew install ripgrep || true
brew install fd || true
brew install fzf || true
brew install zoxide || true

# --GROUP:DEVELOPMENT:neovim,vim,tmux,screen,git-lfs
echo "📥 Installing Neovim - modern text editor..."
echo "📥 Installing Vim - text editor..."
echo "📥 Installing tmux - terminal multiplexer..."
echo "📥 Installing screen - terminal multiplexer..."
echo "📥 Installing Git LFS - large file support..."
brew install neovim || true
brew install vim || true
brew install tmux || true
brew install screen || true
brew install git-lfs || true

# --GROUP:BROWSERS_AND_DOWNLOADS:wget,curl,aria2
echo "📥 Installing aria2 - multi-protocol download utility..."
brew install aria2 || true

# --GROUP:COMPRESSION:zip,unzip,7z
# Note: zip and unzip are pre-installed on macOS, but we install p7zip for 7z support
echo "📥 Installing compression utilities..."
# zip and unzip are already pre-installed on macOS (no need to install)
brew install p7zip || true

# --GROUP:SHELLS_AND_TOOLS:bash,fish
# Note: Zsh is pre-installed on all modern macOS systems (since macOS Catalina in 2019)
echo "📥 Installing Fish - user-friendly shell..."
brew install fish || true

# --GROUP:CASKS:Essential GUI Applications (optional)
# GUI applications are handled separately by `apps_gui.sh` (and `apps_desktop.sh`).
# We avoid installing GUI casks by default to keep `apps.sh` safe for headless / CI usage.
# To install the GUI apps, either run `apps_gui.sh` directly or set INSTALL_CASKS=true.
echo "📥 GUI applications are optional and handled by setup_mac/apps_gui.sh"
if [ "${INSTALL_CASKS:-false}" = "true" ]; then
    echo "📥 Installing GUI apps via apps_gui.sh (INSTALL_CASKS=true)..."
    bash "$(dirname "$0")/apps_gui.sh"
else
    echo "ℹ️ To install GUI apps, either run:" 
    echo "   bash \"$(dirname \"$0\")/apps_gui.sh\"" 
    echo "  or set INSTALL_CASKS=true when running apps.sh:" 
    echo "   INSTALL_CASKS=true bash \"$(dirname \"$0\")/apps.sh\""
fi

echo "✅ Mac setup complete! 🎉"
echo "Architecture: $ARCH"
echo ""
echo "⚠️  Some applications may require additional configuration or restarts."
echo ""
echo "💡 Next Steps:"
if [[ "$ARCH" == "arm64" ]]; then
    echo "   1. Add to your shell profile (~/.zshrc or ~/.bash_profile):"
    echo "      export PATH=\"/opt/homebrew/bin:\$PATH\""
else
    echo "   1. Add to your shell profile (~/.zshrc or ~/.bash_profile):"
    echo "      export PATH=\"/usr/local/bin:\$PATH\""
fi
echo "   2. Reload shell: source ~/.zshrc  (or your shell config)"
echo "   3. Verify installation: brew --version"
echo ""
echo "🚀 Happy coding!"
