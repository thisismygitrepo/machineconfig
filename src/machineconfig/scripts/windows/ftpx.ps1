
#~/venvs/ve/Scripts/Activate.ps1
. "$HOME\venvs\ve\Scripts\activate.ps1"
python $PSScriptRoot/../python/ftpx.py $args
deactivate -ErrorAction SilentlyContinue
