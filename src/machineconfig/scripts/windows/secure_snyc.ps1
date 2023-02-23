
. $PSScriptRoot/activate_ve.ps1
python $PSScriptRoot/../python/secure_push.py $args
deactivate -ErrorAction SilentlyContinue
