
. "$HOME\code\machineconfig\Scripts\activate.ps1"
python -m machineconfig.scripts.python.wsl_windows_transfer $args
deactivate -ErrorAction SilentlyContinue

