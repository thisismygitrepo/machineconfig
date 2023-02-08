#!/usr/bin/bash

cd ~ || exit
mkdir code
cd ~/code || exit
git clone https://github.com/thisismygitrepo/crocodile.git --depth 4
git clone https://github.com/thisismygitrepo/machineconfig.git  --depth 4


# CAUTION: The below is preferred over: ~/scripts/activate_ve.ps1 because this script explictly places the repos
# in the locations as above, and are used as below subsequently
. ~/code/machineconfig/src/machineconfig/scripts/linux/activate_ve
# no assumptions on which ve is activate is used for installation, this is dictated by activate_ve.
# this only solves the matter of where to find activate_ve script


cd ~/code/crocodile || exit
pip install -e .
pip install -r requirements.txt
cd ~/code/machineconfig || exit
pip install -e .
cd ~ || exit
