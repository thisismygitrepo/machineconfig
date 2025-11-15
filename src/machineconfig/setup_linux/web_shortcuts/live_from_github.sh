#!/bin/bash
. <( curl -sSL "https://raw.githubusercontent.com/thisismygitrepo/machineconfig/main/src/machineconfig/setup_linux/uv.sh")
. <( curl -sSL "https://raw.githubusercontent.com/thisismygitrepo/machineconfig/main/src/machineconfig/scripts/linux/wrap_mcfg")

alias mcfg='$HOME/.local/bin/uvx --python 3.14 --from "git+https://github.com/thisismygitrepo/machineconfig" mcfg'

alias d='wrap_in_shell_script mcfg devops'
alias c='wrap_in_shell_script mcfg cloud'
alias a='wrap_in_shell_script mcfg agents'
alias ss='wrap_in_shell_script mcfg sessions'
alias fx='wrap_in_shell_script mcfg ftpx'
alias f='wrap_in_shell_script mcfg fire'
alias rr='wrap_in_shell_script mcfg croshell'
alias u='wrap_in_shell_script mcfg utils'
alias t='wrap_in_shell_script mcfg terminal'
alias ms='wrap_in_shell_script mcfg msearch'

alias devops='mcfg devops'
alias cloud='mcfg cloud'
alias agents='mcfg agents'
alias sessions='mcfg sessions'
alias ftpx='mcfg ftpx'
alias fire='mcfg fire'
alias croshell='mcfg croshell'
alias utils='mcfg utils'
alias terminal='mcfg terminal'
alias msearch='mcfg msearch'


echo "mcfg command aliases are now defined in this shell session."

devops self interactive
