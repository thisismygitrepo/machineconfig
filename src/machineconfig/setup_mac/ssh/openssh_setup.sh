#!/usr/bin/env bash

# 🔐 OpenSSH Setup for macOS
# This script sets up SSH configuration and permissions on macOS

echo "🔐 Starting OpenSSH setup for macOS..."

# ✅ SSH is built-in on macOS (OpenSSH comes pre-installed)
echo "✅ OpenSSH is pre-installed on macOS"

# 📁 Create SSH directory with correct permissions
echo "📁 Setting up SSH directory..."
mkdir -p ~/.ssh
chmod 700 ~/.ssh
echo "✅ SSH directory created with correct permissions (700)"

# 📝 Create authorized_keys file if it doesn't exist
if [ ! -f ~/.ssh/authorized_keys ]; then
    touch ~/.ssh/authorized_keys
    chmod 600 ~/.ssh/authorized_keys
    echo "✅ Created authorized_keys file"
else
    echo "✅ authorized_keys file already exists"
    chmod 600 ~/.ssh/authorized_keys
fi

# 🔑 Create SSH keys if they don't exist
if [ ! -f ~/.ssh/id_rsa ]; then
    echo "🔑 Generating SSH keys (RSA)..."
    ssh-keygen -t rsa -b 4096 -f ~/.ssh/id_rsa -N "" -C "$(whoami)@$(hostname)"
    echo "✅ SSH RSA keys generated: ~/.ssh/id_rsa"
else
    echo "✅ SSH keys already exist"
fi

# 🔐 Create Ed25519 keys (modern alternative)
if [ ! -f ~/.ssh/id_ed25519 ]; then
    echo "🔑 Generating SSH keys (Ed25519)..."
    ssh-keygen -t ed25519 -f ~/.ssh/id_ed25519 -N "" -C "$(whoami)@$(hostname)"
    echo "✅ SSH Ed25519 keys generated: ~/.ssh/id_ed25519"
else
    echo "✅ SSH Ed25519 keys already exist"
fi

# 🔧 Configure SSH config file for convenience
SSH_CONFIG="$HOME/.ssh/config"
if [ ! -f "$SSH_CONFIG" ]; then
    echo "📝 Creating SSH config file..."
    cat > "$SSH_CONFIG" << 'EOF'
# SSH Config File for macOS
# Add your remote hosts below

# Example host configuration:
# Host myserver
#     HostName example.com
#     User username
#     Port 22
#     IdentityFile ~/.ssh/id_ed25519
#     IdentityFile ~/.ssh/id_rsa

# Global settings
Host *
    AddKeysToAgent yes
    UseKeychain yes
    IdentityFile ~/.ssh/id_ed25519
    IdentityFile ~/.ssh/id_rsa
    ServerAliveInterval 60
EOF
    chmod 600 "$SSH_CONFIG"
    echo "✅ SSH config file created: $SSH_CONFIG"
else
    echo "✅ SSH config file already exists"
fi

# 🔒 Ensure correct file permissions
echo "🔒 Setting correct SSH file permissions..."
chmod 700 ~/.ssh
chmod 600 ~/.ssh/authorized_keys 2>/dev/null || true
chmod 600 ~/.ssh/id_rsa 2>/dev/null || true
chmod 644 ~/.ssh/id_rsa.pub 2>/dev/null || true
chmod 600 ~/.ssh/id_ed25519 2>/dev/null || true
chmod 644 ~/.ssh/id_ed25519.pub 2>/dev/null || true
chmod 600 ~/.ssh/config 2>/dev/null || true
echo "✅ SSH file permissions configured correctly"

# ℹ️ Display SSH key information
echo ""
echo "📋 SSH Setup Summary:"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "SSH Directory: ~/.ssh"
echo "SSH Config: ~/.ssh/config"
echo ""
echo "Available SSH Keys:"
if [ -f ~/.ssh/id_rsa.pub ]; then
    echo "  • RSA Key: ~/.ssh/id_rsa"
fi
if [ -f ~/.ssh/id_ed25519.pub ]; then
    echo "  • Ed25519 Key: ~/.ssh/id_ed25519"
fi
echo ""
echo "💡 Next Steps:"
echo "  1. View your public key:"
echo "     cat ~/.ssh/id_ed25519.pub  (or id_rsa.pub)"
echo "  2. Add it to your GitHub/GitLab/server authorized_keys"
echo "  3. Test connection:"
echo "     ssh -v your_server"
echo "  4. Configure hosts in ~/.ssh/config for easy access"
echo ""
echo "📚 Learn more about SSH:"
echo "  • man ssh"
echo "  • man ssh-keygen"
echo "  • man ssh_config"
echo ""
echo "✅ OpenSSH setup complete!"
