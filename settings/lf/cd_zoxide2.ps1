
# from https://github.com/gokcehan/lf/wiki/Integrations#zoxide
$result="$(zoxide query -i -- $Args)"
lf -remote "send ${id} cd '${result}'"
