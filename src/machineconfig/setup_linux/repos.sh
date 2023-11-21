#!/usr/bin/bash

cd ~ || exit
mkdir code
cd ~/code || exit
git clone https://github.com/thisismygitrepo/crocodile.git --depth 4
git clone https://github.com/thisismygitrepo/machineconfig.git  --depth 4


source ~/venvs/ve/bin/activate || exit

cd ~/code/crocodile || exit

if [ -n "$CROCODILE_EXRA" ]; then
  pip install -e .[$CROCODILE_EXRA]
else
  pip install -e .
fi

cd ~/code/machineconfig || exit
pip install -e .
cd ~ || exit
