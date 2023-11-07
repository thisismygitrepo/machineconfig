
# . $HOME\scripts\activate_ve.ps1
. $HOME\venvs\ve\Scripts\activate.ps1
python -m fire machineconfig.jobs.python.python_windows_installers_all main  # this installs everything.
deactivate
