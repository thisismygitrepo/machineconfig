
#~/venvs/ve/Scripts/Activate.ps1
. $PSScriptRoot/activate_ve.ps1
python -m fire $PSScriptRoot/../python/pomodoro.py pomodoro $args
deactivate -ErrorAction SilentlyContinue
