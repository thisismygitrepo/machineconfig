
$op_script = "~/tmp_results/shells/python_return_command.ps1"
if (Test-Path $op_script ) {
  Remove-Item $op_script
}

$ErrorActionPreference = "Stop"
#~/code/machineconfig/.venv/Scripts/Activate.ps1  # fixed ve

# Locate the python script to run relative to the current directory (which might be a symlink)
# $script_root = (Get-Item $PSScriptRoot).Target  # resolves symlink if any
# if ( $script_root -eq $null) {  # this does happen if a virtual enviroment is activated before running this script (don't know why)
# $script_root = $PSScriptRoot
# }
# if ( $script_root -eq $null) {
# # echo $MyInvocation.MyCommand.Path
# $script_root = Split-Path -Path $MyInvocation.MyCommand.Path -Parent
# }

$script_root = $MyInvocation.MyCommand.Path
. "$HOME\code\machineconfig\.venv\Scripts\activate.ps1"

#. "$script_root\..\activate_ve.ps1"  # dynamic v

python -m machineconfig.scripts.python.croshell $args
# python -m machineconfig.scripts.python.fire_jobs $args


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
