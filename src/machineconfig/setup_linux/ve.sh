

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


mkdir $HOME/venvs/ || true
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

if [ ! -f "$HOME/.cargo/bin/uv" ]; then
    echo "uv binary not found, installing..."
    curl -LsSf https://astral.sh/uv/install.sh | sh
fi

if ! command -v uv &> /dev/null; then
    echo "uv command not found in PATH, adding to PATH..."
    export PATH="$HOME/.cargo/bin:$PATH"
fi

uv venv $HOME/venvs/$ve_name --python 3.11 --python-preference only-managed


# check if $VIRTUAL_ENV is set
if [ -z "$VIRTUAL_ENV" ]; then
  source $HOME/venvs/ve/bin/activate || exit
fi
uv pip install --upgrade pip

cd $HOME
mkdir -p code
cd $HOME/code

git clone https://github.com/thisismygitrepo/crocodile.git --depth 4
git clone https://github.com/thisismygitrepo/machineconfig --depth 4  # Choose browser-based authentication.

cd $HOME/code/crocodile
if [ -n "$CROCODILE_EXRA" ]; then
  uv pip install -e .[$CROCODILE_EXRA]
else
  uv pip install -e .
fi


cd $HOME/code/machineconfig
uv pip install -e .
echo "✅ Finished installing virtual environment"
echo "💡 Use this to activate: source ~/venvs/$ve_name/bin/activate"


cd $HOME
