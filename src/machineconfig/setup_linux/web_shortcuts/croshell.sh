#!/usr/bin/bash

curl bit.ly/cfgvelinux -L | bash
curl bit.ly/cfgreposlinux -L | bash
source $HOME/code/machineconfig/src/machineconfig/setup_linux/symlinks.sh
. ~/.bashrc
