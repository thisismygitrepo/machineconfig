
# . $PSScriptRoot/activate_ve.ps1 ve
. "$HOME\scripts\activate_ve.ps1" ve

# python $PSScriptRoot/../python/cloud_repo_sync.py $args
python -m machineconfig.scripts.python.cloud_repo_sync $args

deactivate -ErrorAction SilentlyContinue
