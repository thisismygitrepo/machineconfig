#!/usr/bin/bash

. ~/scripts/activate_ve 've'
python -m fire machineconfig.scripts.python.devops_devapps_install main  --which=AllEssentials  # this installs everything.
. ~/.bashrc
deactivate
