#!/usr/bin/bash
#=======================================================================
# 🌐 WEB SHORTCUTS MASTER SCRIPT
#=======================================================================
# This script provides quick access to installation scripts via web

echo """#=======================================================================
📚 AVAILABLE INSTALLATION OPTIONS | Web-based installers
#=======================================================================

Choose from the following installation options:
"""

echo """#=======================================================================
📦 SYSTEM APPLICATIONS | Basic system applications
#=======================================================================

# To install system applications, run:
# curl https://raw.githubusercontent.com/thisismygitrepo/machineconfig/main/src/machineconfig/setup_linux/apps.sh | bash
"""

echo """#=======================================================================
🐍 PYTHON ENVIRONMENT | Virtual environment setup
#=======================================================================

Setting up Python virtual environment...
"""
curl https://raw.githubusercontent.com/thisismygitrepo/machineconfig/main/src/machineconfig/setup_linux/ve.sh | bash

echo """#=======================================================================
🔄 CODE REPOSITORIES | Cloning project repositories
#=======================================================================

Setting up code repositories...
"""
curl https://raw.githubusercontent.com/thisismygitrepo/machineconfig/main/src/machineconfig/setup_linux/repos.sh | bash

echo """#=======================================================================
⚙️  DEVELOPMENT TOOLS | Developer applications
#=======================================================================

# To install development applications, run:
# source <(sudo cat ~/code/machineconfig/src/machineconfig/setup_linux/devapps.sh)

#=======================================================================
✅ INSTALLATION COMPLETE | Basic environment setup finished
#=======================================================================
"""
