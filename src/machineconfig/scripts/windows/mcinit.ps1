
. "$HOME\scripts\activate_ve.ps1" ve
python -m machineconfig.scripts.python.ai.init $args
deactivate -ErrorAction SilentlyContinue
