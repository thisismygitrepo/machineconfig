#!/usr/bin/bash


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
# $HOME/.local/bin/uv cache clean
