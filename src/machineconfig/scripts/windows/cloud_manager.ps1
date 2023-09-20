
. $PSScriptRoot/activate_ve.ps1
python -i -c "from crocodile.cluster.loader_runner import CloudManager; cm = CloudManager(); cm.run()"
