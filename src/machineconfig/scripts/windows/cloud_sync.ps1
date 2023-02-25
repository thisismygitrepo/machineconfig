
# ensure that python-output-script is deleted.
$op_script = "$HOME/tmp_results/shells/python_return_command.ps1"
if (Test-Path $op_script ) {
  Remove-Item $op_script
}

. $PSScriptRoot/activate_ve.ps1
python $PSScriptRoot/../python/cloud_sync.py $args

. $op_script

deactivate -ErrorAction SilentlyContinue
