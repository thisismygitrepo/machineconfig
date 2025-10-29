#!/bin/bash
. <( curl -sSL "https://raw.githubusercontent.com/thisismygitrepo/machineconfig/main/src/machineconfig/setup_linux/uv.sh")
. <( curl -sSL "https://raw.githubusercontent.com/thisismygitrepo/machineconfig/main/src/machineconfig/scripts/linux/wrap_mcfg")

alias devops='$HOME/.local/bin/uvx --python 3.14 --from "machineconfig>=7.35" devops'
alias cloud='$HOME/.local/bin/uvx --python 3.14 --from "machineconfig>=7.35" cloud'
alias agents='$HOME/.local/bin/uvx --python 3.14 --from "machineconfig>=7.35" agents'
alias sessions='$HOME/.local/bin/uvx --python 3.14 --from "machineconfig>=7.35" sessions'
alias ftpx='$HOME/.local/bin/uvx --python 3.14 --from "machineconfig>=7.35" ftpx'
alias fire='$HOME/.local/bin/uvx --python 3.14 --from "machineconfig>=7.35" fire'
alias croshell='$HOME/.local/bin/uvx --python 3.14 --from "machineconfig>=7.35" croshell'
alias utils='$HOME/.local/bin/uvx --python 3.14 --from "machineconfig>=7.35" utils'
alias terminal='$HOME/.local/bin/uvx --python 3.14 --from "machineconfig>=7.35" terminal'

alias d='wrap_in_shell_script devops'
alias c='wrap_in_shell_script cloud'
alias a='wrap_in_shell_script agents'
alias ss='wrap_in_shell_script sessions'
alias ff='wrap_in_shell_script ftpx'
alias f='wrap_in_shell_script fire'
alias rr='wrap_in_shell_script croshell'
alias u='wrap_in_shell_script utils'
alias t='wrap_in_shell_script terminal'

echo "mcfg command aliases are now defined in this shell session."
