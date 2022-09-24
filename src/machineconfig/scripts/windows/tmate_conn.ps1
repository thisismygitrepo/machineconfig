
$pyparser=Resolve-Path("$PSScriptRoot/../python/tmate_conn.py")
echo $pyparser
activate_ve
python $pyparser $args
