#!/bin/bash
. <( curl -sSL "https://raw.githubusercontent.com/thisismygitrepo/machineconfig/main/src/machineconfig/setup_linux/uv.sh")
mcfg() {
    "$HOME/.local/bin/uv" run --python 3.14 --with "machineconfig>=6.58" mcfg "$@"
}
alias d="mcfg devops"
alias c="mcfg cloud"
alias a="mcfg agents"
alias s="mcfg sessions"
alias ff="mcfg ftpx"
alias f="mcfg fire"
alias r="mcfg croshell"
alias u="mcfg utils"
echo "mcfg command is now defined in this shell session."
