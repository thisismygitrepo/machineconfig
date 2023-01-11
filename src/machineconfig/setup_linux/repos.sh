#!/usr/bin/bash

cd ~ || exit
mkdir code
cd ~/code || exit
git clone https://github.com/thisismygitrepo/crocodile.git --depth 4
git clone https://github.com/thisismygitrepo/machineconfig.git  --depth 4


#ve_name='ve'
#source ~/venvs/$ve_name/bin/activate || exit
. ~/code/machineconfig/src/machineconfig/scripts/linux/activate_ve

cd ~/code/crocodile || exit
pip install -e .
pip install -r requirements.txt
cd ~/code/machineconfig || exit
pip install -e .
cd ~ || exit
