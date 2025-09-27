#!/bin/bash
#=======================================================================
# ⏱️ TIMESCALEDB INSTALLATION SCRIPT ⏱️
#=======================================================================
# This script installs TimescaleDB on Ubuntu/Debian-based Linux distributions
# Reference: https://docs.timescale.com/self-hosted/latest/install/installation-linux/

echo """#=======================================================================
🔍 DETECTING SYSTEM | Identifying OS distribution version
#=======================================================================
"""

get_ubuntu_base_version() {
    local os_codename=$(lsb_release -cs)
    case "$os_codename" in
        "wilma")
            echo "noble"  # Map Mint Wilma to the base image Ubuntu 24.04 LTS
            ;;
        "virginia")
            echo "jammy"  # Map Mint Virginia to the base image Ubuntu 22.04 LTS
            ;;
        *)
            echo "$os_codename"
            ;;
    esac
}

ubuntu_version=$(get_ubuntu_base_version)
echo "📋 Detected distribution: $ubuntu_version"

echo """#=======================================================================
🐘 INSTALLING POSTGRESQL | Setting up PostgreSQL dependencies
#=======================================================================
"""

# Add PostgreSQL repository setup
echo "🔧 Setting up PostgreSQL repository..."
sudo nala install postgresql-common -y
sudo /usr/share/postgresql-common/pgdg/apt.postgresql.org.sh -y

echo """#=======================================================================
🔑 ADDING REPOSITORY KEYS | Setting up TimescaleDB repository
#=======================================================================
"""

# Add TimescaleDB repository
echo "📝 Adding TimescaleDB repository to sources list..."
echo "deb https://packagecloud.io/timescale/timescaledb/ubuntu/ $ubuntu_version main" | sudo tee /etc/apt/sources.list.d/timescaledb.list

echo "🔐 Adding TimescaleDB GPG key..."
wget --quiet -O - https://packagecloud.io/timescale/timescaledb/gpgkey | sudo gpg --dearmor -o /etc/apt/trusted.gpg.d/timescaledb.gpg

echo """#=======================================================================
📦 INSTALLING TIMESCALEDB | Updating and installing packages
#=======================================================================
"""

# Update package lists
echo "🔄 Updating package lists..."
sudo nala update

# Install TimescaleDB with PostgreSQL 16
echo "📥 Installing PostgreSQL 16 and TimescaleDB..."
sudo nala install -y postgresql-16 postgresql-client-16 timescaledb-2-postgresql-16

echo """#=======================================================================
⚙️ CONFIGURING TIMESCALEDB | Optimizing database settings
#=======================================================================
"""

# Run TimescaleDB tuning tool
echo "🔧 Running TimescaleDB tuning utility..."
sudo timescaledb-tune

# Restart PostgreSQL service
echo "🔄 Restarting PostgreSQL service..."
sudo systemctl restart postgresql

echo """#=======================================================================
✅ INSTALLATION COMPLETE | TimescaleDB has been installed successfully
#=======================================================================
"""
echo "🚀 To connect to PostgreSQL, run: sudo -u postgres psql"
echo "💡 To enable TimescaleDB in a database, run: CREATE EXTENSION IF NOT EXISTS timescaledb CASCADE;"
echo "ℹ️ For more information, visit: https://docs.timescale.com/self-hosted/latest/install/"
