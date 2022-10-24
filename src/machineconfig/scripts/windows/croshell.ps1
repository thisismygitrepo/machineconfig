

$ErrorActionPreference = "Stop"
#~/venvs/ve/Scripts/Activate.ps1
. $PSScriptRoot/activate_ve.ps1
python -m crocodile.run $args
deactivate