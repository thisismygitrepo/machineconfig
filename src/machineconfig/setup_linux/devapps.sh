#!/usr/bin/bash

. ~/venvs/ve/bin/activate
python -m fire machineconfig.scripts.python.devops_devapps_install main  --which=AllEssentials  # this installs everything.
. ~/.bashrc
deactivate
