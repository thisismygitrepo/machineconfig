

. "$HOME\code\machineconfig\.venv\Scripts\activate.ps1"

$op_script = "~/tmp_results/shells/python_return_command.ps1"
if (Test-Path $op_script ) {
  Remove-Item $op_script
}


python -m machineconfig.scripts.python.chatgpt $args

if (Test-Path $op_script ) {
    cat $op_script
  . $op_script
}
else
{
    Write-Host "No output script to be executed @ $op_script"
}


deactivate
