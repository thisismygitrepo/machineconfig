
#~/venvs/ve/Scripts/Activate.ps1
. $PSScriptRoot/activate_ve.ps1 've'
# python $PSScriptRoot/../python/wsl_windows_transfer.py $args
python -m machineconfig.scripts.python.wsl_windows_transfer $args
deactivate -ErrorAction SilentlyContinue

