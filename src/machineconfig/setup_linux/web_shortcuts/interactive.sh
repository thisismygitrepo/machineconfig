#!/bin/bash
. <( curl -sSL "https://raw.githubusercontent.com/thisismygitrepo/machineconfig/main/src/machineconfig/setup_linux/uv.sh")
mcfg() {
    "$HOME/.local/bin/uv" run --python 3.14 --with "machineconfig>=5.84" mcfg "$@"
}
echo "mcfg command is now defined in this shell session."
