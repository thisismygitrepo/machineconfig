#!/usr/bin/bash

#ve_name='ve'
#source ~/venvs/$ve_name/bin/activate || exit
source ~/code/machineconfig/src/machineconfig/scripts/linux/activate_ve
# TODO: find a way to get path of activate_ve in more dynamic way that doesn't hardcode path to machineconfig.
python -m fire machineconfig.profile.create main
. ~/.bashrc
deactivate
