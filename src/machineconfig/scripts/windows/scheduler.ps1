
. "$HOME\code\machineconfig\.venv\Scripts\activate.ps1"

python -m machineconfig.scripts.python.scheduler $Args

deactivate -ErrorAction SilentlyContinue
