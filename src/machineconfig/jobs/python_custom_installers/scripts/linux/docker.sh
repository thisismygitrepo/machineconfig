#!/bin/bash
#=======================================================================
# 🐳 DOCKER INSTALLATION SCRIPT 🐳
#=======================================================================
# This script installs Docker on Debian/Ubuntu-based Linux distributions

#-----------------------------------------------------------------------
# 🔍 SYSTEM DETECTION | Identify OS distribution and version
#-----------------------------------------------------------------------
echo """#=======================================================================
🔍 DETECTING SYSTEM | Identifying OS distribution and version
#=======================================================================
"""

get_os_type() {
    if [ -f "/etc/debian_version" ]; then
        if [ -f "/etc/ubuntu_version" ] || [ -f "/etc/lsb-release" ]; then
            echo "ubuntu"
        else
            echo "debian"
        fi
    fi
}

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

get_debian_version() {
    lsb_release -cs
}

OS_TYPE=$(get_os_type)
if [ "$OS_TYPE" = "ubuntu" ]; then
    DISTRO_VERSION=$(get_ubuntu_base_version)
else
    DISTRO_VERSION=$(get_debian_version)
fi

echo "🖥️ Detected OS: $OS_TYPE"
echo "📋 Distribution version: $DISTRO_VERSION"

#-----------------------------------------------------------------------
# 🔑 REPOSITORY SETUP | Adding Docker's official repository
#-----------------------------------------------------------------------
echo """#=======================================================================
🔑 REPOSITORY SETUP | Adding Docker's official repository
#=======================================================================
"""

# Install prerequisites
echo "📥 Installing prerequisites..."
sudo nala update
sudo nala install ca-certificates curl -y

# Add Docker's official GPG key
echo "🔐 Adding Docker's official GPG key..."
sudo install -m 0755 -d /etc/apt/keyrings
sudo curl -fsSL "https://download.docker.com/linux/$OS_TYPE/gpg" | sudo gpg --dearmor -o /etc/apt/keyrings/docker.gpg

# Add the repository to Apt sources
echo "📝 Adding Docker repository to sources list..."
echo \
  "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/$OS_TYPE \
  $DISTRO_VERSION stable" | \
  sudo tee /etc/apt/sources.list.d/docker.list > /dev/null

#-----------------------------------------------------------------------
# 📦 INSTALLATION | Installing Docker packages
#-----------------------------------------------------------------------
echo """#=======================================================================
📦 INSTALLATION | Installing Docker packages
#=======================================================================
"""

echo "🔄 Updating package lists..."
sudo nala update
echo "📥 Installing Docker packages..."
sudo nala install docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin -y

#-----------------------------------------------------------------------
# 🚀 CONFIGURATION | Setting up Docker service and permissions
#-----------------------------------------------------------------------
echo """#=======================================================================
🚀 CONFIGURATION | Setting up Docker service and permissions
#=======================================================================
"""

echo "⚙️ Enabling Docker system service..."
sudo systemctl enable docker || echo "⚠️ Could not enable Docker service (may be WSL or systemd not available)"

echo "🧪 Testing Docker installation with hello-world..."
docker run hello-world || echo "⚠️ Docker hello-world test failed (you may need to start the Docker daemon)"

echo "👥 Adding current user to docker group..."
sudo groupadd docker 2>/dev/null || echo "ℹ️ Docker group already exists"
sudo usermod -aG docker $USER || echo "⚠️ Failed to add user to docker group"

echo """#=======================================================================
✅ INSTALLATION COMPLETE | Docker has been installed successfully
#=======================================================================

ℹ️ NOTES:
- You may need to log out and log back in for group changes to take effect
- Or run 'newgrp docker' to apply changes immediately
- On WSL, you may need to run: sudo service docker start

📚 TROUBLESHOOTING:
- If 'docker run hello-world' fails with connection error:
  For systemd systems: systemctl start dockerd
  For WSL without systemd: sudo service docker start
- For more information, visit: https://docs.docker.com/engine/install/linux-postinstall/
"""

# Additional notes:
# - In older WSL, after installation, 'docker run hello-world' may fail with connection error
#   See: https://stackoverflow.com/questions/44678725/cannot-connect-to-the-docker-daemon-at-unix-var-run-docker-sock-is-the-docker
# 
# - No internet in WSL docker instance: add /etc/docker/daemon.json
#   See: https://github.com/MicrosoftDocs/WSL/issues/422
# 
# - For Databricks environments only:
#   sudo nala install fuse-overlayfs

