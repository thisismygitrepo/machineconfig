#!/usr/bin/bash

curl bit.ly/cfgvelinux -L | bash
curl bit.ly/cfgreposlinux -L | bash

cd $HOME/code/machineconfig
$HOME/.local/bin/uv sync --no-dev
$HOME/.local/bin/uv pip install -e ../crocodile

uv run --no-dev --project $HOME/code/machineconfig -m fire machineconfig.profile.create main --choice=all
. ~/.bashrc
