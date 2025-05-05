#!/usr/bin/bash
#=======================================================================
# 🔗 SYMLINK CREATION AND PROFILE SETUP SCRIPT
#=======================================================================
# This script establishes symbolic links for configuration files

echo """#=======================================================================
🔌 ENVIRONMENT ACTIVATION | Setting up Python environment
#=======================================================================
"""
# ⚠️ CAUTION: deliberately avoided using ~/scripts/activate_ve since this is yet to be established in this script.
echo """🐍 Activating Python virtual environment...
"""
source $HOME/venvs/ve/bin/activate

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
