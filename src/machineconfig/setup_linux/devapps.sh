#!/usr/bin/bash

#ve_name='ve'
#source ~/venvs/$ve_name/bin/activate || exit
source ~/scripts/activate_ve
python -m fire machineconfig.jobs.python.python_linux_installers_all main  # this installs everything.
. ~/.bashrc
deactivate
