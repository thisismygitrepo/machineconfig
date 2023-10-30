
. $PSScriptRoot/activate_ve.ps1 ve
python $PSScriptRoot/../python/cloud_repo_sync.py $args
deactivate -ErrorAction SilentlyContinue
