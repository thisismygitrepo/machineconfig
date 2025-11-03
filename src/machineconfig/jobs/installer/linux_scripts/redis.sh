#!/usr/bin/bash
# 🔄 REDIS INSTALLATION SCRIPT 🔄
# This script installs Redis server on Debian/Ubuntu-based Linux distributions
# Reference: https://redis.io/docs/latest/operate/oss_and_stack/install/install-redis/install-redis-on-linux/

echo """🔍 DETECTING SYSTEM | Identifying OS distribution version
"""

get_ubuntu_base_version() {
    local mint_codename=$(lsb_release -cs)
    case "$mint_codename" in
        "wilma")
            echo "noble"
            ;;
        "virginia")
            echo "jammy"
            ;;
        *)
            echo "$mint_codename"
            ;;
    esac
}
ubuntu_version=$(get_ubuntu_base_version)
echo "📋 Detected distribution: $ubuntu_version"

echo """🔑 ADDING REPOSITORY KEYS | Setting up Redis repository
"""

# Add Redis GPG key
echo "🔐 Adding Redis GPG key..."
curl -fsSL https://packages.redis.io/gpg | sudo gpg --dearmor -o /usr/share/keyrings/redis-archive-keyring.gpg
sudo chmod 644 /usr/share/keyrings/redis-archive-keyring.gpg

# Add Redis repository
echo "📝 Adding Redis repository to sources list..."
echo "deb [signed-by=/usr/share/keyrings/redis-archive-keyring.gpg] https://packages.redis.io/deb $ubuntu_version main" | sudo tee /etc/apt/sources.list.d/redis.list

echo """📦 INSTALLING REDIS | Updating and installing packages
"""

# Update package lists
echo "🔄 Updating package lists..."
sudo nala update

# Install Redis
echo "📥 Installing Redis..."
sudo nala install redis -y
sudo nala install redis-tools -y

echo """✅ INSTALLATION COMPLETE | Redis has been installed successfully

📋 REDIS SERVER COMMANDS:
"""
echo "▶️  To start Redis server:           sudo systemctl start redis-server"
echo "⏹️  To stop Redis server:            sudo systemctl stop redis-server"
echo "🔄 To restart Redis server:         sudo systemctl restart redis-server"
echo "ℹ️  To check status of Redis server: sudo systemctl status redis-server"
echo "🚀 To enable Redis on boot:         sudo systemctl enable --now redis-server"
echo """💡 QUICK TEST | Try connecting to Redis with: redis-cli ping
"""
