#!/usr/bin/bash

ve_name='ve'
source ~/venvs/$ve_name/bin/activate || exit
python -m fire machineconfig.profile.create main
. ~/.bashrc
