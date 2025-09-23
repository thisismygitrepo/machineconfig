#!/usr/bin/bash
uv run --no-dev --project $HOME/code/machineconfig -m fire machineconfig.scripts.python.devops_devapps_install main --which=AllEssentials
. $HOME/.bashrc
