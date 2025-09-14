
# . $PSScriptRoot/activate_ve.ps1 ve  # use the default ve.
. "$HOME\code\machineconfig\.venv\Scripts\activate.ps1"

# python -i $PSScriptRoot/../python/cloud_manager.py $args
python -i -m machineconfig.scripts.python.cloud_manager $args

deactivate -ErrorAction SilentlyContinue
