#!/usr/bin/bash

#ve_name='ve'
#source ~/venvs/$ve_name/bin/activate || exit
source ~/code/machineconfig/src/machineconfig/scripts/linux/activate_ve
python -m fire machineconfig.profile.create main --choice=all
. ~/.bashrc
deactivate
