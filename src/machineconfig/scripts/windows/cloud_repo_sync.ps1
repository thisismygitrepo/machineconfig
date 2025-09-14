
. "$HOME\code\machineconfig\.venv\Scripts\activate.ps1"

# python $PSScriptRoot/../python/cloud_repo_sync.py $args
python -m machineconfig.scripts.python.cloud_repo_sync $args

deactivate -ErrorAction SilentlyContinue
