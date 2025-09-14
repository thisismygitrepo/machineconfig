
# param(
#     [switch]$IgnoreKeyboardInterrupt
# )

# Generate a random string of 10 characters
$random_str = -join ((65..90) + (97..122) + (48..57) | Get-Random -Count 10 | ForEach-Object {[char]$_})
$op_script = "$HOME\tmp_results\shells\$random_str\python_return_command.ps1"
# Export the op_script variable to environment so python can access it
$env:op_script = $op_script

# Create directory if it doesn't exist
$script_dir = Split-Path -Path $op_script -Parent
if (-not (Test-Path $script_dir)) {
    New-Item -ItemType Directory -Path $script_dir -Force | Out-Null
}

# if (Test-Path $op_script ) {
#   Remove-Item $op_script
# }


# try {
#   # $null = & chafa --version
#   # & chafa "$HOME\code\machineconfig\assets\aafire.webp" --speed 2 --duration 1
#   # Chafa.exe "$HOME\code\machineconfig\assets\aafire.webp" --speed 2 --duration 1 --symbols ascii
#   Write-Host "🔥"
# } catch {
#   Write-Host "Chafa not found, skipping."
# }


. "$HOME\code\machineconfig\.venv\Scripts\activate.ps1"
python -m machineconfig.scripts.python.fire_jobs $args


if (Test-Path $op_script ) {
    . $op_script
}
else
{
    Write-Host "No output script to be executed at $op_script."
}

deactivate -ErrorAction SilentlyContinue
