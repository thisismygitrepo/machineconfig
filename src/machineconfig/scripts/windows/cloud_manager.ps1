
. $PSScriptRoot/activate_ve.ps1
python -i $PSScriptRoot/../python/cloud_manager.py $args
deactivate -ErrorAction SilentlyContinue
