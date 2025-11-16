#!/bin/bash
. <( curl -sSL "https://raw.githubusercontent.com/thisismygitrepo/machineconfig/main/src/machineconfig/setup_linux/uv.sh")
. <( curl -sSL "https://raw.githubusercontent.com/thisismygitrepo/machineconfig/main/src/machineconfig/scripts/linux/wrap_mcfg")

alias devops='$HOME/.local/bin/uvx --python 3.14 --from "machineconfig>=7.93" devops'
alias cloud='$HOME/.local/bin/uvx --python 3.14 --from "machineconfig>=7.93" cloud'
alias agents='$HOME/.local/bin/uvx --python 3.14 --from "machineconfig>=7.93" agents'
alias sessions='$HOME/.local/bin/uvx --python 3.14 --from "machineconfig>=7.93" sessions'
alias ftpx='$HOME/.local/bin/uvx --python 3.14 --from "machineconfig>=7.93" ftpx'
alias fire='$HOME/.local/bin/uvx --python 3.14 --from "machineconfig>=7.93" fire'
alias croshell='$HOME/.local/bin/uvx --python 3.14 --from "machineconfig>=7.93" croshell'
alias utils='$HOME/.local/bin/uvx --python 3.14 --from "machineconfig>=7.93" utils'
alias terminal='$HOME/.local/bin/uvx --python 3.14 --from "machineconfig>=7.93" terminal'
alias msearch='$HOME/.local/bin/uvx --python 3.14 --from "machineconfig>=7.93" msearch'

alias d='wrap_in_shell_script devops'
alias c='wrap_in_shell_script cloud'
alias a='wrap_in_shell_script agents'
alias ss='wrap_in_shell_script sessions'
alias fx='wrap_in_shell_script ftpx'
alias f='wrap_in_shell_script fire'
alias rr='wrap_in_shell_script croshell'
alias u='wrap_in_shell_script utils'
alias t='wrap_in_shell_script terminal'
alias ms='wrap_in_shell_script msearch'

echo "mcfg command aliases are now defined in this shell session."

devops self interactive