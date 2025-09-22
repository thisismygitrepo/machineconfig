#!/usr/bin/bash
uv run --with machineconfig -m fire machineconfig.scripts.python.devops_devapps_install main --which=AllEssentials
. $HOME/.bashrc
