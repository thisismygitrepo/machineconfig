# Generate a random name (based on current timestamp hashed with SHA256)
$timestamp = Get-Date -Format o | Get-FileHash -Algorithm SHA256
$randomName = ($timestamp.Hash.Substring(0, 16))

# Define the output path
$env:OP_PROGRAM_PATH = "$HOME/tmp_results/tmp_scripts/machineconfig/${randomName}.ps1"

# Run your equivalent command (replace with your actual command)
mcfg @args

# Check if the file exists
if (Test-Path $env:OP_PROGRAM_PATH) {
    Write-Host "Found op program at: $env:OP_PROGRAM_PATH"
    & $env:OP_PROGRAM_PATH
} else {
    Write-Host "no op program found"
}
