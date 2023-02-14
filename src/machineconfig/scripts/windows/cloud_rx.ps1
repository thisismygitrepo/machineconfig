
#~/venvs/ve/Scripts/Activate.ps1
. $PSScriptRoot/activate_ve.ps1
python -m machineconfig.scripts.python.cloud_rx $args
deactivate -ErrorAction SilentlyContinue
