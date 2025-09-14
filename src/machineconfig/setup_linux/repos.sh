#!/usr/bin/bash

# Remove .venv folders if they exist
if [ -d "$HOME/code/machineconfig/.venv" ]; then
    echo """  🗑️  Removing existing .venv folder in machineconfig...
    """
    rm -rf "$HOME/code/machineconfig/.venv"
fi

if [ -d "$HOME/code/crocodile/.venv" ]; then
    echo """  🗑️  Removing existing .venv folder in crocodile...
    """
    rm -rf "$HOME/code/crocodile/.venv"
fi

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

echo """
#=======================================================================
🐍 PYTHON ENVIRONMENT | Setting up virtual environment
#=======================================================================
"""

# $HOME/.local/bin/uv venv
# $HOME/.local/bin/uv pip install -e .
uv sync
$HOME/.local/bin/uv pip install -e ../machineconfig
# $HOME/.local/bin/uv cache clean
