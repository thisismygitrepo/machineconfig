
#~/venvs/ve/Scripts/Activate.ps1
. $PSScriptRoot/activate_ve.ps1
python $PSScriptRoot/../python/snapshot.py $args
deactivate -ErrorAction SilentlyContinue
