#!/usr/bin/bash

curl bit.ly/cfgvelinux -L | bash
curl bit.ly/cfgreposlinux -L | bash

cd $HOME/code/machineconfig
$HOME/.local/bin/uv sync --no-dev
$HOME/.local/bin/uv pip install -e ../crocodile

source $HOME/code/machineconfig/src/machineconfig/setup_linux/symlinks.sh
. ~/.bashrc
