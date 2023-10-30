
#~/venvs/ve/Scripts/Activate.ps1
# . $PSScriptRoot/activate_ve.ps1
# python -m machineconfig.scripts.python.cloud_copy $args
# deactivate -ErrorAction SilentlyContinue
try {
    if (Test-Path "$PSScriptRoot/activate_ve.ps1") {
        . "$PSScriptRoot/activate_ve.ps1" ve
    } else {
        . "$HOME/activate_ve.ps1" ve
    }
    python -m machineconfig.scripts.python.cloud_copy $args
} catch {
    Write-Error $_.Exception.Message
} finally {
    deactivate -ErrorAction SilentlyContinue
}
