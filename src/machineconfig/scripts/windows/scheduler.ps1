
. "$HOME\scripts\activate_ve.ps1" ve

python -m fire machineconfig.scripts.python.scheduler main_parse $Args

deactivate -ErrorAction SilentlyContinue
