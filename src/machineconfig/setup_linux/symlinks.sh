#!/usr/bin/bash
# 🔗 Symlink Creation and Profile Setup Script

# ⚠️ CAUTION: deliberately avoided using ~/scripts/activate_ve since this is yet to be established in this script.
source $HOME/venvs/ve/bin/activate

# 🛠️ Create configuration symlinks
python -m fire machineconfig.profile.create main --choice=all

# 🔄 Reload shell configuration
. ~/.bashrc

# 🚫 Deactivate virtual environment
deactivate || true
