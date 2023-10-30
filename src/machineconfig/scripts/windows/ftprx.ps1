
#~/venvs/ve/Scripts/Activate.ps1
. $PSScriptRoot/activate_ve.ps1 ve
python $PSScriptRoot/../python/ftprx.py $args
deactivate -ErrorAction SilentlyContinue
