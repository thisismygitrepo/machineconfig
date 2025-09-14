
$tmp = Get-Location

if ($args[0] -eq $null) {
    $name = ""
}
else {
    $name = $args[0]
}

. "$HOME\code\machineconfig\.venv\Scripts\activate.ps1"

python -m fire machineconfig.scripts.python.choose_wezterm_theme main2 $args[0]
.$profile  # reload the profile

cd $tmp
deactivate -ErrorAction SilentlyContinue

