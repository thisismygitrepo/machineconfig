
$pyparser=Resolve-Path("$PSScriptRoot/../python/wifi_conn.py")
echo $pyparser
#activate_ve
. $PSScriptRoot/activate_ve.ps1
python $pyparser $args
deactivate

