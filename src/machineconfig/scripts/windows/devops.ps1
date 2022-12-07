
$op_script = "~/tmp_results/shells/python_return_command.ps1"
if (Test-Path $op_script ) {
  Remove-Item $op_script
}

. $PSScriptRoot/activate_ve.ps1 $Args[0]
#~/venvs/ve/Scripts/Activate.ps1
echo "Using virtual enviroment: $env:VIRTUAL_ENV"
$script_root = (Get-Item $PSScriptRoot).Target
python $script_root/../python/devops.py $args
. $op_script
#deactivate
