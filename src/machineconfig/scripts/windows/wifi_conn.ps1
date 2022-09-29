
$pyparser=Resolve-Path("$PSScriptRoot/../python/wifi_conn.py")
echo $pyparser
activate_ve
python $pyparser $args
