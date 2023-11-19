
# . $PSScriptRoot/activate_ve.ps1 ve  # use the default ve.
. "$HOME\scripts\activate_ve.ps1" ve

# python -i $PSScriptRoot/../python/cloud_manager.py $args
python -i -m machineconfig.scripts.python.cloud_manager $args

deactivate -ErrorAction SilentlyContinue
