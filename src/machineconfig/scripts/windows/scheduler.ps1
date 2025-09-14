
. "$HOME\code\machineconfig\Scripts\activate.ps1"

python -m machineconfig.scripts.python.scheduler $Args

deactivate -ErrorAction SilentlyContinue
