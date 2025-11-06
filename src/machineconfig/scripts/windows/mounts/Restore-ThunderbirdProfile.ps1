
<#
.SYNOPSIS
    Restores a Thunderbird profile from a backup.

.DESCRIPTION
    This script automates the restoration of a Thunderbird profile. It finds the
    default backup profile located in ~/.thunderbird and copies its contents to
    the active Thunderbird profile folder in AppData/Roaming.

    WARNING: This script will overwrite the current active Thunderbird profile.
    Ensure Thunderbird is closed before running.
#>

# --- Configuration ---
$ErrorActionPreference = "Stop"

# --- Script ---

# 1. Define the root paths for backup and active profiles
$thunderbirdBackupRoot = "$env:USERPROFILE\.thunderbird"
$thunderbirdAppdataRoot = "$env:APPDATA\Thunderbird"

Write-Host "Thunderbird Profile Restore Script"
Write-Host "-----------------------------------"

# 2. Find the default profile path from the backup's profiles.ini
try {
    $backupIniPath = Join-Path $thunderbirdBackupRoot "profiles.ini"
    $backupProfileRelativePath = (Get-Content $backupIniPath | Select-String -Pattern '^Path=' | Select-Object -First 1) -replace '^Path=', ''
    $backupProfileFullPath = Join-Path $thunderbirdBackupRoot $backupProfileRelativePath
    Write-Host "Found backup profile: $backupProfileFullPath" -ForegroundColor Green
}
catch {
    Write-Error "Could not find or read the backup profiles.ini at '$backupIniPath'."
    exit 1
}

# 3. Find the default profile path from the active installation's profiles.ini
try {
    $activeIniPath = Join-Path $thunderbirdAppdataRoot "profiles.ini"
    $activeProfileRelativePath = (Get-Content $activeIniPath | Select-String -Pattern '^Path=' | Select-Object -First 1) -replace '^Path=', ''
    $activeProfileFullPath = Join-Path $thunderbirdAppdataRoot $activeProfileRelativePath
    Write-Host "Found active profile: $activeProfileFullPath" -ForegroundColor Green
}
catch {
    Write-Error "Could not find or read the active profiles.ini at '$activeIniPath'."
    exit 1
}

# 4. Safety Check: Confirm both profile paths exist
if (-not (Test-Path -Path $backupProfileFullPath -PathType Container)) {
    Write-Error "Backup profile directory does not exist: $backupProfileFullPath"
    exit 1
}
if (-not (Test-Path -Path $activeProfileFullPath -PathType Container)) {
    Write-Error "Active profile directory does not exist: $activeProfileFullPath"
    exit 1
}

# 5. CRITICAL: Get user confirmation before proceeding
Write-Warning "This will completely overwrite the profile at '$activeProfileFullPath' with the contents of the backup."
$confirmation = Read-Host "Are you absolutely sure you want to continue? (y/n)"

if ($confirmation -ne 'y') {
    Write-Host "Operation cancelled by user." -ForegroundColor Yellow
    exit 0
}

# 6. Ensure Thunderbird is not running
Write-Host "Checking for running Thunderbird process..."
$thunderbirdProcess = Get-Process thunderbird -ErrorAction SilentlyContinue
if ($thunderbirdProcess) {
    Write-Host "Closing Thunderbird to prevent file conflicts..."
    Stop-Process -InputObject $thunderbirdProcess -Force
    Start-Sleep -Seconds 3 # Give it a moment to close gracefully
} else {
    Write-Host "Thunderbird is not running. Good."
}

# 7. Copy the backup profile to the active profile directory using robocopy
Write-Host "Starting profile restoration... (This may take a while)"
try {
    robocopy $backupProfileFullPath $activeProfileFullPath /MIR /E /IS /IT /NFL /NDL /NJH /NJS /nc /ns /np
    Write-Host "Profile restoration complete!" -ForegroundColor Green
    Write-Host "You can now start Thunderbird."
}
catch {
    Write-Error "An error occurred during the file copy operation."
    exit 1
}

