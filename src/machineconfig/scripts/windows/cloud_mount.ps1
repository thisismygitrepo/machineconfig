

# ensure that python-output-script is deleted.
$op_script = "~/tmp_results/shells/python_return_command.ps1"
if (Test-Path $op_script ) {
  Remove-Item $op_script
}

. $PSScriptRoot/activate_ve.ps1 ve
$script_root = (Get-Item $PSScriptRoot).Target  # resolves symlink if any
if ( $script_root -eq $null) {  # this does happen if a virtual enviroment is activated before running this script (don't know why)
$script_root = $PSScriptRoot
}

# python -m fire $script_root/../python/cloud_mount.py $args
python -m machineconfig.scripts.python.cloud_mount $args
if (Test-Path $op_script ) {
  . $op_script
}
else
{
    Write-Host "No output script to be executed @ $op_script"
}

deactivate -ErrorAction SilentlyContinue
