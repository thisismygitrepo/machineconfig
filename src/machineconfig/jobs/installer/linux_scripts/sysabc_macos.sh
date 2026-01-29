/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
echo "🔄 Updating Homebrew..."
brew update || true

curl -fsSL https://bun.com/install | bash
# brew install openssl ffmpeg make curl nano git
echo "✅ Essential tools installation complete."