
$tmp = pwd

if ($args[0] -eq $null) {
    $name = ""
}
else {
    $name = $args[0]
}

~/venvs/ve/Scripts/Activate.ps1
python -m fire machineconfig.setup_windows_terminal.ohmyposh choose $args[0]
.$profile  # reload the profile

cd $tmp

