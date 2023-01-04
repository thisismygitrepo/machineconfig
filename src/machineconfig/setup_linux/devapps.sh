#!/usr/bin/bash

ve_name='ve'
source ~/venvs/$ve_name/bin/activate || exit
python -m fire machineconfig.jobs.python.python_linux_installers_all
. ~/.bashrc
deactivate
