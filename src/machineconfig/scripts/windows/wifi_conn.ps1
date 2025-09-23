
$pyparser=Resolve-Path("$PSScriptRoot/../python/wifi_conn.py")
uv run --no-dev --project $HOME/code/machineconfig python $pyparser $args
