devops() {
    "$HOME/.local/bin/uv" run --python 3.13 --no-dev --project $HOME/code/machineconfig devops "$@"
}
agents() {
    "$HOME/.local/bin/uv" run --python 3.13 --no-dev --project $HOME/code/machineconfig agents "$@"
}
cloud() {
    "$HOME/.local/bin/uv" run --python 3.13 --no-dev --project $HOME/code/machineconfig cloud "$@"
}
croshell() {
    "$HOME/.local/bin/uv" run --python 3.13 --no-dev --project $HOME/code/machineconfig croshell "$@"
}
fire() {
    "$HOME/.local/bin/uv" run --python 3.13 --no-dev --project $HOME/code/machineconfig fire "$@"
}
ftpx() {
    "$HOME/.local/bin/uv" run --python 3.13 --no-dev --project $HOME/code/machineconfig ftpx "$@"
}
kill_process() {
    "$HOME/.local/bin/uv" run --python 3.13 --no-dev --project $HOME/code/machineconfig kill_process "$@"
}
sessions() {
    "$HOME/.local/bin/uv" run --python 3.13 --no-dev --project $HOME/code/machineconfig sessions "$@"
}
