
# . $HOME\scripts\activate_ve.ps1
. $HOME\venvs\ve\Scripts\activate.ps1
python -m fire machineconfig.scripts.python.devops_devapps_install main  # this installs everything.
deactivate
