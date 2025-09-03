
. "$HOME\scripts\activate_ve.ps1" ve
python -m machineconfig.scripts.python.ai.mcinit $args
deactivate -ErrorAction SilentlyContinue
