#!/bin/bash
#=======================================================================
# 🐘 POSTGRESQL INSTALLATION SCRIPT 🐘
#=======================================================================
# This script installs PostgreSQL database on Ubuntu/Debian systems
# Reference: https://www.postgresql.org/download/linux/ubuntu/

echo """#=======================================================================
🚀 STARTING POSTGRESQL INSTALLATION | Setting up PostgreSQL database
#=======================================================================
"""

# Install PostgreSQL common package
echo "📥 Installing PostgreSQL common package..."
sudo nala install postgresql-common -y

# Run the PostgreSQL repository setup script
echo "🔧 Setting up PostgreSQL repository..."
sudo /usr/share/postgresql-common/pgdg/apt.postgresql.org.sh -y

# Install PostgreSQL 17
echo """#=======================================================================
📦 INSTALLING POSTGRESQL | Installing PostgreSQL 17
#=======================================================================
"""
sudo nala install postgresql-17 -y
# Alternative: sudo nala install postgresql -y

echo """#=======================================================================
✅ INSTALLATION COMPLETE | PostgreSQL has been installed successfully
#=======================================================================
"""
echo "ℹ️ PostgreSQL service should be running automatically"
echo "💡 Connect to default 'postgres' database with: sudo -u postgres psql"
echo "🔄 To check service status: sudo systemctl status postgresql"

# REMOVAL INSTRUCTIONS:
echo """#-----------------------------------------------------------------------
📝 NOTES | For future reference
#-----------------------------------------------------------------------
To remove PostgreSQL completely:
sudo apt-get --purge remove postgresql postgresql-*
"""

# Alternative installation method (commented out):
# sudo sh -c 'echo "deb http://apt.postgresql.org/pub/repos/apt $ubuntu_version-pgdg main" > /etc/apt/sources.list.d/pgdg.list'
# curl -fsSL https://www.postgresql.org/media/keys/ACCC4CF8.asc | sudo gpg --dearmor -o /etc/apt/trusted.gpg.d/postgresql.gpg
# sudo nala update

