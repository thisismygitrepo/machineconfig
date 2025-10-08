#!/bin/bash
. <( curl -sSL "https://raw.githubusercontent.com/thisismygitrepo/machineconfig/main/src/machineconfig/setup_linux/uv.sh")
devops() {
    "$HOME/.local/bin/uv" run --python 3.13 --with machineconfig devops "$@"
}
agents() {
    "$HOME/.local/bin/uv" run --python 3.13 --with machineconfig agents "$@"
}
cloud() {
    "$HOME/.local/bin/uv" run --python 3.13 --with machineconfig cloud "$@"
}
croshell() {
    "$HOME/.local/bin/uv" run --python 3.13 --with machineconfig croshell "$@"
}
fire() {
    "$HOME/.local/bin/uv" run --python 3.13 --with machineconfig fire "$@"
}
ftpx() {
    "$HOME/.local/bin/uv" run --python 3.13 --with machineconfig ftpx "$@"
}
kill_process() {
    "$HOME/.local/bin/uv" run --python 3.13 --with machineconfig kill_process "$@"
}
sessions() {
    "$HOME/.local/bin/uv" run --python 3.13 --with machineconfig sessions "$@"
}

echo "devops command is now defined in this shell session."
