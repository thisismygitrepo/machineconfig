
#~/venvs/ve/Scripts/Activate.ps1
. $PSScriptRoot/activate_ve.ps1
python $PSScriptRoot/../python/bu_gdrive_sx.py $args
deactivate -ErrorAction SilentlyContinue
