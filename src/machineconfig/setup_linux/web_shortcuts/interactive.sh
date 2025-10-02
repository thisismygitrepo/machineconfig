#!/bin/bash

. <( curl -sSL "https://raw.githubusercontent.com/thisismygitrepo/machineconfig/main/src/machineconfig/setup_linux/ve.sh")
$HOME/.local/bin/uv run --python 3.13 --with machineconfig devops self interactive
