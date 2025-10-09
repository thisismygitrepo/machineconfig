#!/bin/bash
. <( curl -sSL "https://raw.githubusercontent.com/thisismygitrepo/machineconfig/main/src/machineconfig/setup_linux/uv.sh")
devops() {
    "$HOME/.local/bin/uv" run --python 3.14 --with "machineconfig>=5.72" devops "$@"
}
agents() {
    "$HOME/.local/bin/uv" run --python 3.14 --with "machineconfig>=5.72" agents "$@"
}
cloud() {
    "$HOME/.local/bin/uv" run --python 3.14 --with "machineconfig>=5.72" cloud "$@"
}
croshell() {
    "$HOME/.local/bin/uv" run --python 3.14 --with "machineconfig>=5.72" croshell "$@"
}
fire() {
    "$HOME/.local/bin/uv" run --python 3.14 --with "machineconfig>=5.72" fire "$@"
}
ftpx() {
    "$HOME/.local/bin/uv" run --python 3.14 --with "machineconfig>=5.72" ftpx "$@"
}
sessions() {
    "$HOME/.local/bin/uv" run --python 3.14 --with "machineconfig>=5.72" sessions "$@"
}

echo "devops command is now defined in this shell session."
