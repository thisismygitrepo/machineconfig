
$pyparser=Resolve-Path("$PSScriptRoot/../python/wifi_conn.py")
. "$HOME\code\crocodile\.venv\Scripts\activate.ps1"
echo "Running $pyparser"
python $pyparser $args
deactivate -ErrorAction SilentlyContinue

