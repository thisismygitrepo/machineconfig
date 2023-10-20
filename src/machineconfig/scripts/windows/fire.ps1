
$op_script = "~/tmp_results/shells/python_return_command.ps1"
if (Test-Path $op_script ) {
  Remove-Item $op_script
}


. "$HOME\scripts\activate_ve.ps1" ve
python -m machineconfig.scripts.python.fire_jobs $args


if (Test-Path $op_script ) {
    . $op_script
#   content of $op_script
#  $content = Get-Content $op_script
#  Invoke-Expression $content | Add-History   # this way, $content will go to hisyory of powershell. You don't neet Add-history
}
else
{
    Write-Host "No output script to be executed @ $op_script"
}

deactivate -ErrorAction SilentlyContinue
