

$op_script = "~/tmp_results/shells/python_return_command.ps1"
if (Test-Path $op_script ) {
  Remove-Item $op_script
}


. "$HOME\code\machineconfig\.venv\Scripts\activate.ps1"
python -m machineconfig.scripts.python.start_terminals $args


if (Test-Path $op_script ) {
  . $op_script
}
else
{
    Write-Host "No output script to be executed @ $op_script"
}

deactivate -ErrorAction SilentlyContinue

