
$script_path = $PSScriptRoot + "/../python/devops.py"
. $PSScriptRoot/activate_ve.ps1 $Args[0]
#~/venvs/ve/Scripts/Activate.ps1
python $script_path $args
~/tmp_results/shells/python_return_command.ps1
#deactivate
