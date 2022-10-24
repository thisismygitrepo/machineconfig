
#~/venvs/ve/Scripts/Activate.ps1
. $PSScriptRoot/activate_ve.ps1
python $PSScriptRoot/../python/transfer_wsl_win.py $args
deactivate

