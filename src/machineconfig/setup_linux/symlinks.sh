#!/usr/bin/bash
#=======================================================================
# 🔗 SYMLINK CREATION AND PROFILE SETUP SCRIPT
#=======================================================================
# This script establishes symbolic links for configuration files

echo """#=======================================================================
🔌 ENVIRONMENT ACTIVATION | Setting up Python environment
#=======================================================================
"""
echo """🐍 Activating Python virtual environment...
"""
source $HOME/code/machineconfig/.venv/bin/activate

echo """#=======================================================================
🔄 CONFIGURATION SETUP | Creating configuration symlinks
#=======================================================================
"""
echo """🛠️ Creating configuration symlinks for all profiles...
"""
python -m fire machineconfig.profile.create main --choice=all

echo """#=======================================================================
🔄 SHELL CONFIGURATION | Reloading shell environment
#=======================================================================
"""
echo """🔄 Reloading bash configuration...
"""
. ~/.bashrc

echo """#=======================================================================
🏁 CLEANUP | Deactivating virtual environment
#=======================================================================
"""
echo """🚫 Deactivating Python virtual environment...
"""
deactivate || true

echo """#=======================================================================
✅ SETUP COMPLETE | All symlinks created successfully
#=======================================================================
"""
