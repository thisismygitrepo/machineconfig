
. "$HOME\code\machineconfig\.venv\Scripts\activate.ps1"

python $PSScriptRoot/../python/snapshot.py $args
deactivate -ErrorAction SilentlyContinue
