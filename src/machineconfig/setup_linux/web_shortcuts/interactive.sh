#!/bin/bash
. <( curl -sSL "https://raw.githubusercontent.com/thisismygitrepo/machineconfig/main/src/machineconfig/setup_linux/uv.sh")
. <( curl -sSL "https://raw.githubusercontent.com/thisismygitrepo/machineconfig/main/src/machineconfig/scripts/linux/mcfgs.sh")

alias devops='$HOME/.local/bin/uvx --python 3.14 --from "machineconfig>=6.98" devops'
alias cloud='$HOME/.local/bin/uvx --python 3.14 --from "machineconfig>=6.98" cloud'
alias agents='$HOME/.local/bin/uvx --python 3.14 --from "machineconfig>=6.98" agents'
alias sessions='$HOME/.local/bin/uvx --python 3.14 --from "machineconfig>=6.98" sessions'
alias ftpx='$HOME/.local/bin/uvx --python 3.14 --from "machineconfig>=6.98" ftpx'
alias fire='$HOME/.local/bin/uvx --python 3.14 --from "machineconfig>=6.98" fire'
alias croshell='$HOME/.local/bin/uvx --python 3.14 --from "machineconfig>=6.98" croshell'
alias utils='$HOME/.local/bin/uvx --python 3.14 --from "machineconfig>=6.98" utils'
alias terminal='$HOME/.local/bin/uvx --python 3.14 --from "machineconfig>=6.98" terminal'

alias d='wrap_in_op_code devops'
alias c='wrap_in_op_code cloud'
alias a='wrap_in_op_code agents'
alias ss='wrap_in_op_code sessions'
alias ff='wrap_in_op_code ftpx'
alias f='wrap_in_op_code fire'
alias rr='wrap_in_op_code croshell'
alias u='wrap_in_op_code utils'
alias t='wrap_in_op_code terminal'

echo "mcfg command aliases are now defined in this shell session."
