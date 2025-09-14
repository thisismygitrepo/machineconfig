
#~/code/machineconfig/.venv/Scripts/Activate.ps1
. "$HOME\code\machineconfig\.venv\Scripts\activate.ps1"
python $PSScriptRoot/../python/ftpx.py $args
deactivate -ErrorAction SilentlyContinue
