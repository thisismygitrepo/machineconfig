#!/usr/bin/bash


echo """
#=======================================================================
🔄 REPOSITORIES SETUP | Cloning project codebases
#=======================================================================
"""

echo """📥 Setting up repositories...
   🐊 crocodile     - Main utility package
   🔧 machineconfig - System configuration tools
"""

mkdir -p $HOME/code
cd $HOME/code
# Setup crocodile repository
if [ -d "crocodile" ]; then
    echo """🔄 crocodile directory exists, updating...
    """
    cd crocodile
    git reset --hard
    git pull
    cd ..
else
    echo """⏳ Cloning crocodile repository...
    """
    git clone https://github.com/thisismygitrepo/crocodile.git --depth 4
fi

# Setup machineconfig repository
cd $HOME/code
if [ -d "machineconfig" ]; then
    echo """🔄 machineconfig directory exists, updating...
    """
    cd machineconfig
    git reset --hard
    git pull
    cd ..
else
    echo """⏳ Cloning machineconfig repository...
    """
    git clone https://github.com/thisismygitrepo/machineconfig --depth 4  # Choose browser-based authentication.
fi

cd $HOME/code/machineconfig
$HOME/.local/bin/uv sync --no-dev
$HOME/.local/bin/uv cache clean
