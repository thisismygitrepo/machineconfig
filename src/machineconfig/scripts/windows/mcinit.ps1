
. "$HOME\code\machineconfig\\Scripts\activate.ps1"
python -m machineconfig.scripts.python.ai.mcinit $args
deactivate -ErrorAction SilentlyContinue
