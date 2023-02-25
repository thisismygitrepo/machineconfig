
# I created this with inspiration from https://github.com/gokcehan/lf/wiki/Integrations#zoxide
$result = . $(~\AppData\Local\Microsoft\WindowsApps\tere.exe) $args
lf -remote "send ${id} cd '${result}'"
