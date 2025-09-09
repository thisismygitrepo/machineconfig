
$pyparser=Resolve-Path("$PSScriptRoot/../python/wifi_conn.py")
. "$HOME\venvs\ve\Scripts\activate.ps1"
echo "Running $pyparser"
python $pyparser $args
deactivate -ErrorAction SilentlyContinue

