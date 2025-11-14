#!/bin/bash
. <( curl -sSL "https://raw.githubusercontent.com/thisismygitrepo/machineconfig/main/src/machineconfig/setup_linux/uv.sh")
. <( curl -sSL "https://raw.githubusercontent.com/thisismygitrepo/machineconfig/main/src/machineconfig/scripts/linux/wrap_mcfg")

alias devops='$HOME/.local/bin/uvx --python 3.14 --from "git+https://github.com/thisismygitrepo/machineconfig" devops'
alias cloud='$HOME/.local/bin/uvx --python 3.14 --from "git+https://github.com/thisismygitrepo/machineconfig" cloud'
alias agents='$HOME/.local/bin/uvx --python 3.14 --from "git+https://github.com/thisismygitrepo/machineconfig" agents'
alias sessions='$HOME/.local/bin/uvx --python 3.14 --from "git+https://github.com/thisismygitrepo/machineconfig" sessions'
alias ftpx='$HOME/.local/bin/uvx --python 3.14 --from "git+https://github.com/thisismygitrepo/machineconfig" ftpx'
alias fire='$HOME/.local/bin/uvx --python 3.14 --from "git+https://github.com/thisismygitrepo/machineconfig" fire'
alias croshell='$HOME/.local/bin/uvx --python 3.14 --from "git+https://github.com/thisismygitrepo/machineconfig" croshell'
alias utils='$HOME/.local/bin/uvx --python 3.14 --from "git+https://github.com/thisismygitrepo/machineconfig" utils'
alias terminal='$HOME/.local/bin/uvx --python 3.14 --from "git+https://github.com/thisismygitrepo/machineconfig" terminal'
alias msearch='$HOME/.local/bin/uvx --python 3.14 --from "git+https://github.com/thisismygitrepo/machineconfig" msearch'

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
