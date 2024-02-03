
$tmp = Get-Location

if ($args[0] -eq $null) {
    $name = ""
}
else {
    $name = $args[0]
}

#~/venvs/ve/Scripts/Activate.ps1
# . $PSScriptRoot/activate_ve.ps1 ve
. "$HOME\scripts\activate_ve.ps1" ve

python -m fire machineconfig.scripts.python.choose_ohmyposh_theme main $args[0]
.$profile  # reload the profile

cd $tmp
deactivate -ErrorAction SilentlyContinue

