#!/bin/bash

echo """
=======================================================================
📦 MACHINE CONFIGURATION | Interactive Installation Script. Installing uv then getting started.
======================================================================="""

curl https://raw.githubusercontent.com/thisismygitrepo/machineconfig/main/src/machineconfig/setup_linux/ve.sh | bash
$HOME/.local/bin/uv run --python 3.13 --with machineconfig devops interactive
