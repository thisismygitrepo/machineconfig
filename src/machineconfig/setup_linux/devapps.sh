#!/usr/bin/bash

. $HOME/venvs/ve/bin/activate
python -m fire machineconfig.scripts.python.devops_devapps_install main --which=AllEssentials  # this installs everything.
. $HOME/.bashrc
deactivate
