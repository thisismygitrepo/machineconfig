#!/usr/bin/bash

# this script is for setting up a virtual environment for python
# --- Define ve name and python version here ---
if [ -z "$ve_name" ]; then
    ve_name="ve"
fi

if [ -z "$py_version" ]; then
    py_version=3.11  # fastest version.
fi
# --- End of user defined variables ---

# echo "🐍 Setting up virtual environment for Python $py_version"
# sleep 15

mkdir -p $HOME/venvs/ || true
cd $HOME/venvs/ || exit
# delete ~/venvs/$ve_name and its contents if it exists
if [ -d "$ve_name" ]; then
    echo ''
    echo '>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>'
    echo "🗑️ $ve_name already exists, deleting ..."
    echo '>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>'
    echo ''
    rm -rfd $ve_name
fi

if [ ! -f "$HOME/.local/bin/uv" ]; then
    echo "🔧 uv binary not found, installing..."
    curl -LsSf https://astral.sh/uv/install.sh | sh
fi

if ! command -v uv &> /dev/null; then
    echo "🔄 uv command not found in PATH, adding to PATH..."
    export PATH="$HOME/.cargo/bin:$PATH"
fi

$HOME/.local/bin/uv venv $HOME/venvs/$ve_name --python 3.11 --python-preference only-managed

# Check if a virtual environment is active and if it's different from the target one
if [ ! -z "$VIRTUAL_ENV" ]; then
    if [ "$VIRTUAL_ENV" != "$HOME/venvs/$ve_name" ]; then
        echo "🔄 Deactivating existing virtual environment: $(basename $VIRTUAL_ENV)"
        deactivate
    fi
fi

# Activate the target virtual environment if not already active
if [ -z "$VIRTUAL_ENV" ] || [ "$VIRTUAL_ENV" != "$HOME/venvs/$ve_name" ]; then
    echo "🔌 Activating virtual environment: $ve_name"
    source "$HOME/venvs/$ve_name/bin/activate" || exit
fi

$HOME/.local/bin/uv pip install --upgrade pip

echo "✨ Finished installing virtual environment"
echo "💡 Use this to activate: source ~/venvs/$ve_name/bin/activate"
