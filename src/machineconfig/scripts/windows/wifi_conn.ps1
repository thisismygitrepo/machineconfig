
$pyparser=Resolve-Path("$PSScriptRoot/../python/wifi_conn.py")
. $PSScriptRoot/activate_ve.ps1 ve
echo "Running $pyparser"
python $pyparser $args
deactivate -ErrorAction SilentlyContinue

