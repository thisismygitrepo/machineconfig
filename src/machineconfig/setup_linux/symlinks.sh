#!/usr/bin/bash
uv run --no-dev --project $HOME/code/machineconfig -m fire machineconfig.profile.create main --choice=all
. ~/.bashrc
