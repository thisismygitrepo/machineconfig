
. "$HOME\code\machineconfig\.venv\Scripts\activate.ps1"

# python $PSScriptRoot/../python/dotfile.py $args
python -m machineconfig.scripts.python.dotfile $args

deactivate -ErrorAction SilentlyContinue
