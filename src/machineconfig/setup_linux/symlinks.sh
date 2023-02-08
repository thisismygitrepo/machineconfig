#!/usr/bin/bash

source ~/scripts/activate_ve
python -m fire machineconfig.profile.create main --choice=all
. ~/.bashrc
deactivate
