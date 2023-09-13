
. $PSScriptRoot/activate_ve.ps1
python $PSScriptRoot/../python/password_manager.py $args
deactivate -ErrorAction SilentlyContinue
