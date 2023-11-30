
. "$HOME\scripts\activate_ve.ps1" ve

python -m machineconfig.scripts.python.scheduler $Args

deactivate -ErrorAction SilentlyContinue
