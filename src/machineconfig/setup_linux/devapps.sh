#!/usr/bin/bash

source ~/scripts/activate_ve
python -m fire machineconfig.scripts.python.devops_devapps_install main  # this installs everything.
. ~/.bashrc
deactivate
