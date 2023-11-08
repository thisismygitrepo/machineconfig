

$ErrorActionPreference = "Stop"
#~/venvs/ve/Scripts/Activate.ps1  # fixed ve

# Locate the python script to run relative to the current directory (which might be a symlink)
$script_root = (Get-Item $PSScriptRoot).Target  # resolves symlink if any
if ( $script_root -eq $null) {  # this does happen if a virtual enviroment is activated before running this script (don't know why)
$script_root = $PSScriptRoot
}

. $script_root/activate_ve.ps1  # dynamic ve

python -m crocodile.run $args
deactivate -ErrorAction SilentlyContinue
