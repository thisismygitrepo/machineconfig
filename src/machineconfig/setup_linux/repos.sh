#!/usr/bin/bash
#=======================================================================
# 📦 CODE REPOSITORIES SETUP SCRIPT
#=======================================================================
# This script clones essential repositories and installs them in development mode

echo """#=======================================================================
📂 DIRECTORY SETUP | Creating code directory structure
#=======================================================================
"""

# Create and enter code directory
cd $HOME

echo """🏗️  Creating directory structure...
    📁 $HOME/code
"""
mkdir -p code
cd $HOME/code

echo """
#=======================================================================
🔄 REPOSITORIES SETUP | Cloning project codebases
#=======================================================================
"""

echo """📥 Cloning repositories...
   🐊 crocodile     - Main utility package
   🔧 machineconfig - System configuration tools
"""

echo """⏳ Cloning crocodile repository...
"""
git clone https://github.com/thisismygitrepo/crocodile.git --depth 4

echo """⏳ Cloning machineconfig repository...
"""
git clone https://github.com/thisismygitrepo/machineconfig --depth 4  # Choose browser-based authentication.

echo """
#=======================================================================
🐍 PYTHON ENVIRONMENT | Setting up virtual environment
#=======================================================================
"""

# Activate virtual environment if not already active
if [ -z "$VIRTUAL_ENV" ]; then
  echo """  🔌 Activating Python virtual environment...
  """
  source $HOME/venvs/$ve_name/bin/activate || exit
fi

echo """
#=======================================================================
⚙️  PACKAGE INSTALLATION | Installing projects in development mode
#=======================================================================
"""

# Install crocodile package
echo """📦 Installing crocodile package in development mode...
"""
cd $HOME/code/crocodile
if [ -n "$CROCODILE_EXRA" ]; then
  echo """  ➕ Installing with extra dependencies: $CROCODILE_EXRA
  """
  $HOME/.local/bin/uv pip install -e .[$CROCODILE_EXRA]
else
  echo """  🔄 Installing with standard dependencies
  """
  $HOME/.local/bin/uv pip install -e .
fi

# Install machineconfig package
echo """📦 Installing machineconfig package in development mode...
"""
cd $HOME/code/machineconfig
$HOME/.local/bin/uv pip install -e .

# Return to home directory
cd $HOME

echo """
#=======================================================================
✅ INSTALLATION COMPLETE | Repository setup finished successfully
#=======================================================================

📚 Installed packages:
   ✓ crocodile     - Development mode
   ✓ machineconfig - Development mode

🏠 Returned to home directory: $HOME
"""
