#!/bin/bash
. <( curl -sSL "https://raw.githubusercontent.com/thisismygitrepo/machineconfig/main/src/machineconfig/setup_linux/uv.sh")
devops() {
    "$HOME/.local/bin/uv" run --python 3.14 --with machineconfig>=5.67 devops "$@"
}
agents() {
    "$HOME/.local/bin/uv" run --python 3.14 --with machineconfig>=5.67 agents "$@"
}
cloud() {
    "$HOME/.local/bin/uv" run --python 3.14 --with machineconfig>=5.67 cloud "$@"
}
croshell() {
    "$HOME/.local/bin/uv" run --python 3.14 --with machineconfig>=5.67 croshell "$@"
}
fire() {
    "$HOME/.local/bin/uv" run --python 3.14 --with machineconfig>=5.67fire "$@"
}
ftpx() {
    "$HOME/.local/bin/uv" run --python 3.14 --with machineconfig>=5.67ftpx "$@"
}
sessions() {
    "$HOME/.local/bin/uv" run --python 3.14 --with machineconfig>=5.67sessions "$@"
}

echo "devops command is now defined in this shell session."
