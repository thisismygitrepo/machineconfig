#!/usr/bin/bash

cd $HOME
mkdir -p code
cd $HOME/code

git clone https://github.com/thisismygitrepo/crocodile.git --depth 4
git clone https://github.com/thisismygitrepo/machineconfig --depth 4  # Choose browser-based authentication.

if [ -z "$VIRTUAL_ENV" ]; then
  source $HOME/venvs/$ve_name/bin/activate || exit
fi

cd $HOME/code/crocodile
if [ -n "$CROCODILE_EXRA" ]; then
  $HOME/.local/bin/uv pip install -e .[$CROCODILE_EXRA]
else
  $HOME/.local/bin/uv pip install -e .
fi


cd $HOME/code/machineconfig
$HOME/.local/bin/uv pip install -e .


cd $HOME
