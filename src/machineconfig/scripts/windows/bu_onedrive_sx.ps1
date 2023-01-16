
#~/venvs/ve/Scripts/Activate.ps1
. $PSScriptRoot/activate_ve.ps1
python -m machineconfig.scripts.python.bu_onedrive_sx $args
deactivate -ErrorAction SilentlyContinue