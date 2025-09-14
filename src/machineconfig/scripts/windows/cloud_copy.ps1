
#~/code/machineconfig/.venv/Scripts/Activate.ps1
# . $PSScriptRoot/activate_ve.ps1
# python -m machineconfig.scripts.python.cloud_copy $args
# deactivate -ErrorAction SilentlyContinue
try {
    . "$HOME\code\machineconfig\.venv\Scripts\activate.ps1"
    python -m machineconfig.scripts.python.cloud_copy $args
} catch {
    Write-Error $_.Exception.Message
} finally {
    deactivate -ErrorAction SilentlyContinue
}
