$winget = Get-Command winget -ErrorAction SilentlyContinue
if (-not $winget) {
    Write-Host "winget not found. Installing..."
    $finalUrl = (Invoke-WebRequest 'https://github.com/microsoft/winget-cli/releases/latest' -UseBasicParsing).BaseResponse.ResponseUri.AbsoluteUri
    $releaseTag = $finalUrl.Split('/')[-1]
    $DownloadUrl = "https://github.com/microsoft/winget-cli/releases/download/$releaseTag/Microsoft.DesktopAppInstaller_8wekyb3d8bbwe.msixbundle"
    $DestDir     = Join-Path $HOME "Downloads"
    $DestFile    = Join-Path $DestDir "Microsoft.DesktopAppInstaller_8wekyb3d8bbwe.msixbundle"
    # Create folder if it doesn't exist
    if (-not (Test-Path $DestDir)) {
        New-Item -ItemType Directory -Path $DestDir | Out-Null
    }
    Write-Host "Downloading winget installer..."
    # Invoke-WebRequest -Uri $DownloadUrl -OutFile $DestFile
    # Start-BitsTransfer -Source $DownloadUrl -Destination $DestFile  # 
    #Invoke-WebRequest -Uri $DownloadUrl -OutFile $DestFile -UseBasicParsing
    curl.exe -L -o $DestFile $DownloadUrl
    Write-Host "Saved to: $DestFile"
    # We MUST run Add-AppxPackage in Windows PowerShell
    Write-Host "Installing package via Windows PowerShell..."
    powershell.exe -NoLogo -NoProfile -Command "Add-AppxPackage -Path `"$DestFile`" "
    Write-Host "Installation complete."
    }
else {
    Write-Host "winget already available. Skipping installation."
}

winget install --no-upgrade --name "Powershell"                   --Id "Microsoft.PowerShell"       --source winget --scope user --accept-package-agreements --accept-source-agreements  # powershell require admin
winget install --no-upgrade --name "Windows Terminal"             --Id "Microsoft.WindowsTerminal"  --source winget --scope user --accept-package-agreements --accept-source-agreements  # Terminal is is installed by default on W 11
winget install --no-upgrade --name "Git"                          --Id "Git.Git"                    --source winget --scope user --accept-package-agreements --accept-source-agreements
powershell -c "irm bun.sh/install.ps1|iex"

# Install-Module -Name Terminal-Icons -Repository PSGallery -Force -AcceptLicense -PassThru -Confirm  # -RequiredVersion 2.5.10
# [System.Environment]::SetEnvironmentVariable('PYTHONUTF8', '1', 'User')
# [System.Environment]::SetEnvironmentVariable('PYTHONIOENCODING', 'utf-8', 'User')

