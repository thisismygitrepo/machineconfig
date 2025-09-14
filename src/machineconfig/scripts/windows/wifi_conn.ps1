
$pyparser=Resolve-Path("$PSScriptRoot/../python/wifi_conn.py")
. "$HOME\code\machineconfig\.venv\Scripts\activate.ps1"
echo "Running $pyparser"
python $pyparser $args
deactivate -ErrorAction SilentlyContinue

