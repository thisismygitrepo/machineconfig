#!/usr/bin/bash

# no assumptions on which ve is activate is used for installation, this is dictated by activate_ve.
# this only solves the matter of where to find activate_ve script

cd ~ || exit
mkdir code
cd ~/code || exit
git clone https://github.com/thisismygitrepo/crocodile.git --depth 4
git clone https://github.com/thisismygitrepo/machineconfig.git  --depth 4


cd ~/code/crocodile || exit

if [ -n "$CROCODILE_EXRA" ]; then
  pip install -e .[$CROCODILE_EXRA]
else
  pip install -e .
fi

cd ~/code/machineconfig || exit
pip install -e .
cd ~ || exit
