#!/bin/bash
. <( curl -sSL "https://raw.githubusercontent.com/thisismygitrepo/machineconfig/main/src/machineconfig/setup_linux/uv.sh")
devops() {
    "$HOME/.local/bin/uv" run --python 3.14 --with "machineconfig>=5.74" devops "$@"
}
agents() {
    "$HOME/.local/bin/uv" run --python 3.14 --with "machineconfig>=5.74" agents "$@"
}
cloud() {
    "$HOME/.local/bin/uv" run --python 3.14 --with "machineconfig>=5.74" cloud "$@"
}
croshell() {
    "$HOME/.local/bin/uv" run --python 3.14 --with "machineconfig>=5.74" croshell "$@"
}
fire() {
    "$HOME/.local/bin/uv" run --python 3.14 --with "machineconfig>=5.74" fire "$@"
}
ftpx() {
    "$HOME/.local/bin/uv" run --python 3.14 --with "machineconfig>=5.74" ftpx "$@"
}
sessions() {
    "$HOME/.local/bin/uv" run --python 3.14 --with "machineconfig>=5.74" sessions "$@"
}

echo "devops command is now defined in this shell session."
