#!/usr/bin/bash

. ~/scripts/activate_ve 've'
python -m fire machineconfig.scripts.python.devops_devapps_install main  # this installs everything.
. ~/.bashrc
deactivate
