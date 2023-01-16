
#~/venvs/ve/Scripts/Activate.ps1
. $PSScriptRoot/activate_ve.ps1
python $PSScriptRoot/../python/bu_gdrive_rx.py $args
deactivate -ErrorAction SilentlyContinue