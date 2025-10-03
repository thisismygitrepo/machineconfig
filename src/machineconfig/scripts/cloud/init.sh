#!/bin/bash
# ☁️ CLOUD CONFIGURATION INITIALIZATION SCRIPT ☁️
# This script initializes cloud configuration settings and sets up the environment

echo """🔑 COLLECTING CONFIGURATION PARAMETERS | Setting up cloud environment
"""

# Check for required environment variables and prompt if not set
if [ -z "$CLOUD_CONFIG_NAME" ]; then
    echo """    #-----------------------------------------------------------------------
    📋 CONFIG NAME | Specify cloud configuration to run
    #-----------------------------------------------------------------------
    """
    read -s -p "💭 Enter CLOUD_CONFIG_NAME (should be under cloud_config_name): " CLOUD_CONFIG_NAME
    export CLOUD_CONFIG_NAME=$CLOUD_CONFIG_NAME
    echo ""
fi

if [ -z "$SHARE_URL" ]; then
    echo """    #-----------------------------------------------------------------------
    🔗 SHARE URL | Provide cloud share URL for configuration files
    #-----------------------------------------------------------------------
    ℹ️ To get share_url, go to dotfiles and run: cloud_copy . :^ --config ss
    """
    read -s -p "🔗 Enter SHARE_URL: " SHARE_URL
    export SHARE_URL=$SHARE_URL
    echo ""
fi

if [ -z "$DECRYPTION_PASSWORD" ]; then
    echo """    #-----------------------------------------------------------------------
    🔒 SECURITY | Enter decryption password
    #-----------------------------------------------------------------------
    """
    read -s -p "🔑 Enter DECRYPTION_PASSWORD: " DECRYPTION_PASSWORD
    export DECRYPTION_PASSWORD=$DECRYPTION_PASSWORD
    echo ""
fi

echo """📦 INSTALLING ESSENTIALS | Setting up core dependencies
"""

# Set up package manager
export package_manager="apt"

# Install essential applications
echo "📥 Installing essential Linux applications..."
curl bit.ly/cfgappslinux -L | bash

# Set up virtual environment
echo "🔧 Setting up Python virtual environment..."
curl bit.ly/cfgvelinux -L | bash

# Activate virtual environment
echo "🚀 Activating Python virtual environment..."
. $HOME/code/machineconfig/.venv/bin/activate

# Clone repositories
echo "📋 Setting up code repositories..."
curl bit.ly/cfgreposlinux -L | bash

echo """⚙️ CONFIGURING ENVIRONMENT | Setting up dotfiles
"""

# Link configuration files
echo "🔄 Creating symlinks for configuration files..."
source ~/code/machineconfig/src/machineconfig/setup_linux/symlinks.sh
sleep 1

# Copy cloud configurations
echo "☁️ Copying configuration files from cloud storage..."
~/scripts/cloud_copy $SHARE_URL $HOME --config ss

# Refresh symlinks
echo "🔄 Refreshing symlinks after cloud copy..."
source ~/code/machineconfig/src/machineconfig/setup_linux/symlinks.sh

# Reload shell configuration
echo "🔄 Reloading shell configuration..."
. ~/.bashrc

echo """📦 INSTALLING DEVELOPMENT TOOLS | Setting up development environment
"""

# Activate virtual environment
echo "🚀 Activating Python virtual environment..."
. $HOME/scripts/activate_ve '.venv'

# Install all essential development applications
echo "📥 Installing essential development applications..."
python -m fire machineconfig.scripts.python.devops_devapps_install main --which=essentials

# Reload shell configuration
echo "🔄 Reloading shell configuration..."
. ~/.bashrc

echo """✅ FINALIZING CONFIGURATION | Running cloud-specific initialization
"""

# Run cloud-specific initialization script
echo "⚙️ Running cloud-specific configuration: $CLOUD_CONFIG_NAME"
. $HOME/dotfiles/config/cloud/$CLOUD_CONFIG_NAME/init.sh

echo """✅ INITIALIZATION COMPLETE | Cloud environment has been set up successfully
"""
