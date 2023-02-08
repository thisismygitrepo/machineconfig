#!/usr/bin/bash

# CAUTION: deliberately avoided using ~/scripts/activate_ve since this is yet to be established in this script.
. ~/code/machineconfig/src/machineconfig/scripts/linux/activate_ve
python -m fire machineconfig.profile.create main --choice=all
. ~/.bashrc
deactivate
