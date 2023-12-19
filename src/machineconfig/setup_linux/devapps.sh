#!/usr/bin/bash

. ~/scripts/activate_ve 've'
python -m fire machineconfig.scripts.python.devops_devapps_install main  --which=all  # this installs everything.
. ~/.bashrc
deactivate
