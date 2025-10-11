#!/bin/bash
. <( curl -sSL "https://raw.githubusercontent.com/thisismygitrepo/machineconfig/main/src/machineconfig/setup_linux/uv.sh")
devops() {
    "$HOME/.local/bin/uv" run --python 3.14 --with "machineconfig>=5.84" devops "$@"
}
agents() {
    "$HOME/.local/bin/uv" run --python 3.14 --with "machineconfig>=5.84" agents "$@"
}
cloud() {
    "$HOME/.local/bin/uv" run --python 3.14 --with "machineconfig>=5.84" cloud "$@"
}
croshell() {
    "$HOME/.local/bin/uv" run --python 3.14 --with "machineconfig>=5.84" croshell "$@"
}
fire() {
    "$HOME/.local/bin/uv" run --python 3.14 --with "machineconfig>=5.84" fire "$@"
}
ftpx() {
    "$HOME/.local/bin/uv" run --python 3.14 --with "machineconfig>=5.84" ftpx "$@"
}
sessions() {
    "$HOME/.local/bin/uv" run --python 3.14 --with "machineconfig>=5.84" sessions "$@"
}

echo "devops command is now defined in this shell session."
