#!/usr/bin/bash

cd ~ || exit
mkdir code
cd ~/code || exit
git clone https://github.com/thisismygitrepo/crocodile.git --depth 4
git clone https://github.com/thisismygitrepo/machineconfig.git  --depth 4

# check if $VIRTUAL_ENV is set
if [ -z "$VIRTUAL_ENV" ]; then
  source ~/venvs/ve/bin/activate || exit
fi

cd ~/code/crocodile || exit

if [ -n "$CROCODILE_EXRA" ]; then
  uv pip install -e .[$CROCODILE_EXRA]
else
  uv pip install -e .
fi

cd ~/code/machineconfig || exit
uv pip install -e .
cd ~ || exit
