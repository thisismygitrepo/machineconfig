#!/usr/bin/bash
#=======================================================================
# 🐊 CROCODILE SHELL SETUP SCRIPT
#=======================================================================
# This script sets up the crocodile shell environment with all dependencies

echo """#=======================================================================
🚀 ENVIRONMENT SETUP | Quick installation via URL shorteners
#=======================================================================
"""

echo """#=======================================================================
🐍 PYTHON ENVIRONMENT | Setting up Python virtual environment
#=======================================================================

Setting up Python virtual environment via bit.ly shortlink...
"""
# Alternative URL: curl https://raw.githubusercontent.com/thisismygitrepo/machineconfig/main/src/machineconfig/setup_linux/ve.sh | bash
curl bit.ly/cfgvelinux -L | bash

echo """#=======================================================================
📦 CODE REPOSITORIES | Cloning project repositories
#=======================================================================

Cloning essential repositories via bit.ly shortlink...
"""
# Alternative URL: curl https://raw.githubusercontent.com/thisismygitrepo/machineconfig/main/src/machineconfig/setup_linux/repos.sh | bash
curl bit.ly/cfgreposlinux -L | bash

echo """#=======================================================================
🔗 CONFIGURATION SETUP | Creating symbolic links
#=======================================================================

Setting up configuration symlinks...
Note: This may require sudo permissions for .ssh permissions
"""
source $HOME/code/machineconfig/src/machineconfig/setup_linux/symlinks.sh

echo """#=======================================================================
🔄 SHELL RELOADING | Refreshing shell configuration
#=======================================================================

Reloading bash configuration...
"""
. ~/.bashrc

echo """#=======================================================================
⚙️  DEVELOPMENT TOOLS | Developer applications
#=======================================================================

# To install development applications, run:
# source <(sudo cat ~/code/machineconfig/src/machineconfig/setup_linux/devapps.sh)

#=======================================================================
✅ SETUP COMPLETE | CroShell environment setup finished
#=======================================================================

🚀 Your CroShell development environment is ready to use!
"""

