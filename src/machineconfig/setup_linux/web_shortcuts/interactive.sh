#!/bin/bash
. <( curl -sSL "https://raw.githubusercontent.com/thisismygitrepo/machineconfig/main/src/machineconfig/setup_linux/uv.sh")
devops() {
    "$HOME/.local/bin/uv" run --python 3.14 --with machineconfig>=5.65 devops "$@"
}
agents() {
    "$HOME/.local/bin/uv" run --python 3.14 --with machineconfig>=5.65 agents "$@"
}
cloud() {
    "$HOME/.local/bin/uv" run --python 3.14 --with machineconfig>=5.65 cloud "$@"
}
croshell() {
    "$HOME/.local/bin/uv" run --python 3.14 --with machineconfig>=5.65 croshell "$@"
}
fire() {
    "$HOME/.local/bin/uv" run --python 3.14 --with machineconfig>=5.65fire "$@"
}
ftpx() {
    "$HOME/.local/bin/uv" run --python 3.14 --with machineconfig>=5.65ftpx "$@"
}
sessions() {
    "$HOME/.local/bin/uv" run --python 3.14 --with machineconfig>=5.65sessions "$@"
}

echo "devops command is now defined in this shell session."
