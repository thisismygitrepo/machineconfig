#!/usr/bin/bash
#=======================================================================
# 🐍 PYTHON VIRTUAL ENVIRONMENT SETUP SCRIPT
#=======================================================================
# This script sets up a virtual environment for Python development

# --- Define ve name and python version here ---
if [ -z "$ve_name" ]; then
    ve_name="ve"
fi

if [ -z "$py_version" ]; then
    py_version=3.13  # fastest version.
fi
# --- End of user defined variables ---

echo """#=======================================================================
🚀 VIRTUAL ENVIRONMENT SETUP | Creating Python $py_version environment
#=======================================================================
"""

mkdir -p $HOME/venvs/ || true
cd $HOME/venvs/ || exit

# Delete ~/venvs/$ve_name and its contents if it exists
if [ -d "$ve_name" ]; then
    echo """#=======================================================================
🗑️  CLEANING UP | Removing existing virtual environment
#=======================================================================

    ⚠️  Virtual environment '$ve_name' already exists
    🔄 Deleting existing environment...
"""
    rm -rfd $ve_name
fi

echo """#=======================================================================
🛠️  TOOLS INSTALLATION | Setting up package manager
#=======================================================================
"""

# Install uv package manager if not present, else, run an update using `uv self update`
if [ ! -f "$HOME/.local/bin/uv" ]; then
    echo """📦 uv binary not found
   ⏳ Installing uv package manager..."""
    curl -LsSf https://astral.sh/uv/install.sh | sh
else
    echo """🔄 Updating uv package manager..."""
    $HOME/.local/bin/uv self update
fi

# Add uv to PATH if not already there
if ! command -v uv &> /dev/null; then
    echo """🔍 uv command not found in PATH
   ➕ Adding uv to system PATH...
"""
    export PATH="$HOME/.local/bin:$PATH"
fi

echo """#=======================================================================
🐍 ENVIRONMENT CREATION | Building Python virtual environment
#=======================================================================

🏗️  Creating new virtual environment: $ve_name
    📍 Location: $HOME/venvs/$ve_name
    🐍 Python version: $py_version
"""

$HOME/.local/bin/uv python upgrade $py_version
$HOME/.local/bin/uv venv $HOME/venvs/$ve_name --python $py_version --python-preference only-managed

echo """#=======================================================================
🔌 ENVIRONMENT ACTIVATION | Setting up the environment
#=======================================================================
"""

# Check if a virtual environment is active and if it's different from the target one
if [ ! -z "$VIRTUAL_ENV" ]; then
    if [ "$VIRTUAL_ENV" != "$HOME/venvs/$ve_name" ]; then
        echo """🔄 Deactivating existing environment: $(basename $VIRTUAL_ENV)
"""
        deactivate
    fi
fi

# Activate the target virtual environment if not already active
if [ -z "$VIRTUAL_ENV" ] || [ "$VIRTUAL_ENV" != "$HOME/venvs/$ve_name" ]; then
    echo """🔌 Activating virtual environment: $ve_name
"""
    source "$HOME/venvs/$ve_name/bin/activate" || exit
fi

echo """#=======================================================================
📦 PACKAGE UPDATES | Updating core packages
#=======================================================================

🔄 Upgrading pip to latest version...
"""

# $HOME/.local/bin/uv pip install --upgrade pip

echo """#=======================================================================
✅ SETUP COMPLETE | Virtual environment created successfully
#=======================================================================

✨ Virtual environment '$ve_name' is ready to use!

📝 To activate this environment, run:
   $ source ~/venvs/$ve_name/bin/activate
"""
