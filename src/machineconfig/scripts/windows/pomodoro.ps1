
# . $PSScriptRoot/activate_ve.ps1
. "$HOME\venvs\ve\Scripts\activate.ps1"

# python -m fire $PSScriptRoot/../python/pomodoro.py pomodoro $args
python -m fire machineconfig.scripts.python.pomodoro pomodoro $args

deactivate -ErrorAction SilentlyContinue
