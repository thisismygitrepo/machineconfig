
# ensure that python-output-script is deleted.
$op_script = "~/tmp_results/shells/python_return_command.ps1"
if (Test-Path $op_script ) {
  Remove-Item $op_script
}


. "$HOME\code\machineconfig\.venv\Scripts\activate.ps1"

# Locate the python script to run relative to the current directory (which might be a symlink)
$script_root = (Get-Item $PSScriptRoot).Target  # resolves symlink if any
if ( $script_root -eq $null) {  # this does happen if a virtual enviroment is activated before running this script (don't know why)
$script_root = $PSScriptRoot
}

python $script_root/../python/devops.py $args

if (Test-Path $op_script ) {
  . $op_script
}
else
{
    Write-Host "🤷‍♂️ No output script to be executed @ $op_script"
}


deactivate -ErrorAction SilentlyContinue

