
# from https://github.com/gokcehan/lf/wiki/Integrations#zoxide
$result="$(zoxide query --exclude "${PWD}" -- "$args")"
lf -remote "send ${id} cd '${result}'"
