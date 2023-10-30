
. $PSScriptRoot/activate_ve.ps1 've'
#~/venvs/ve/Scripts/Activate.ps1
python $PSScriptRoot/../python/dotfile.py $args
deactivate -ErrorAction SilentlyContinue
