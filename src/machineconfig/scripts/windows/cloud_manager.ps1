
. $PSScriptRoot/activate_ve.ps1 ve  # use the default ve.
python -i $PSScriptRoot/../python/cloud_manager.py $args
deactivate -ErrorAction SilentlyContinue
