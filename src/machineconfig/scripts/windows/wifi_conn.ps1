
$pyparser=Resolve-Path("$PSScriptRoot/../python/wifi_conn.py")
uv run --python 3.13 --with machineconfig python $pyparser $args
