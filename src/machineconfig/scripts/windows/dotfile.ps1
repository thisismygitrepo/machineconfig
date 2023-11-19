
# . $PSScriptRoot/activate_ve.ps1 've'
#~/venvs/ve/Scripts/Activate.ps1
. "$HOME\scripts\activate_ve.ps1" ve

# python $PSScriptRoot/../python/dotfile.py $args
python -m machineconfig.scripts.python.dotfile $args

deactivate -ErrorAction SilentlyContinue
