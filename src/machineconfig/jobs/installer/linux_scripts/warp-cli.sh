#!/usr/bin/bash
# 🔒 CLOUDFLARE WARP INSTALLATION SCRIPT 🔒
# This script installs Cloudflare WARP client on Ubuntu/Debian-based Linux distributions
# Reference: https://pkg.cloudflareclient.com/

echo """🔍 DETECTING SYSTEM | Identifying OS distribution version
"""

get_ubuntu_base_version() {
    local mint_codename=$(lsb_release -cs)
    case "$mint_codename" in
        "wilma")
            echo "noble"  # Mint 22 (wilma) is based on Ubuntu 24.04 (noble)
            ;;
        "virginia")  # Mint 21 (virginia) is based on Ubuntu 22.04 (jammy)
            echo "jammy"
            ;;
        *)
            echo "$mint_codename"
            ;;
    esac
}
ubuntu_version=$(get_ubuntu_base_version)
echo "📋 Detected distribution: $ubuntu_version"

echo """🔑 ADDING REPOSITORY KEYS | Setting up Cloudflare repository
"""

# Add Cloudflare WARP GPG key
echo "🔐 Adding Cloudflare WARP GPG key..."
curl -fsSL https://pkg.cloudflareclient.com/pubkey.gpg | sudo gpg --yes --dearmor --output /usr/share/keyrings/cloudflare-warp-archive-keyring.gpg

# Add Cloudflare WARP repository
echo "📝 Adding Cloudflare WARP repository to sources list..."
echo "deb [signed-by=/usr/share/keyrings/cloudflare-warp-archive-keyring.gpg] https://pkg.cloudflareclient.com/ $ubuntu_version main" | sudo tee /etc/apt/sources.list.d/cloudflare-client.list

echo """📦 INSTALLING CLOUDFLARE WARP | Updating and installing packages
"""

# Update package lists
echo "🔄 Updating package lists..."
sudo nala update

# Install Cloudflare WARP
echo "📥 Installing Cloudflare WARP..."
sudo nala install cloudflare-warp -y

echo """🔧 REGISTERING WARP CLIENT | Setting up new registration
"""

# Register the WARP client
echo "📡 Registering WARP client..."
warp-cli registration new

echo """✅ INSTALLATION COMPLETE | Cloudflare WARP has been installed successfully
"""
echo "🚀 To connect to WARP, run: warp-cli connect"
echo "🔄 To disconnect from WARP, run: warp-cli disconnect"
echo "ℹ️ To check connection status, run: warp-cli status"
echo "🔐 For more information, visit: https://developers.cloudflare.com/warp-client/get-started/linux/"
