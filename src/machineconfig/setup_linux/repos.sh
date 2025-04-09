#!/usr/bin/bash
#=======================================================================
# 📦 CODE REPOSITORIES SETUP SCRIPT
#=======================================================================
# This script clones essential repositories and installs them in development mode

echo """
#=======================================================================
📂 DIRECTORY SETUP | Creating code directory structure
#=======================================================================
"""
# Create and enter code directory
cd $HOME
echo "📁 Creating code directory..."
mkdir -p code
cd $HOME/code

echo """
#=======================================================================
🐊 CLONING REPOSITORIES | Fetching project code bases
#=======================================================================
"""
echo "📥 Cloning crocodile repository..."
git clone https://github.com/thisismygitrepo/crocodile.git --depth 4

echo "📥 Cloning machineconfig repository..."
git clone https://github.com/thisismygitrepo/machineconfig --depth 4  # Choose browser-based authentication.

echo """
#=======================================================================
🐍 ACTIVATING ENVIRONMENT | Setting up Python virtual environment
#=======================================================================
"""
# Activate virtual environment if not already active
if [ -z "$VIRTUAL_ENV" ]; then
  echo "🚀 Activating Python virtual environment..."
  source $HOME/venvs/$ve_name/bin/activate || exit
fi

echo """
#=======================================================================
⚙️ INSTALLING PACKAGES | Installing projects in development mode
#=======================================================================
"""
# Install crocodile package
echo "📦 Installing crocodile package in development mode..."
cd $HOME/code/crocodile
if [ -n "$CROCODILE_EXRA" ]; then
  echo "🔍 Installing crocodile with extra dependencies: $CROCODILE_EXRA"
  $HOME/.local/bin/uv pip install -e .[$CROCODILE_EXRA]
else
  echo "🔍 Installing crocodile with standard dependencies"
  $HOME/.local/bin/uv pip install -e .
fi

# Install machineconfig package
echo "📦 Installing machineconfig package in development mode..."
cd $HOME/code/machineconfig
$HOME/.local/bin/uv pip install -e .

# Return to home directory
cd $HOME

echo """
#=======================================================================
✅ SETUP COMPLETE | Repositories cloned and installed successfully
#=======================================================================
"""
