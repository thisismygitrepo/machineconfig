
. $PSScriptRoot/activate_ve.ps1
python $PSScriptRoot/../python/secure_sync.py $args
deactivate -ErrorAction SilentlyContinue
