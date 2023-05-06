

activate_ve
$op_script = "~/tmp_results/shells/python_return_command.ps1"
if (Test-Path $op_script ) {
  Remove-Item $op_script
}


python -m machineconfig.scripts.python.chatgpt $args
cat $op_script
. $op_script


deactivate
