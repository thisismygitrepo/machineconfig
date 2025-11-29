
# OpenSSH Server Installation Script for Windows
# ALL of the following require admin privileges
# Two installation methods available: winget (default, recommended) or Windows Capability
# - winget: installs to "C:\Program Files\OpenSSH" (more up-to-date, from Win32-OpenSSH project)
# - capability: installs to "C:\Windows\System32\OpenSSH" (built-in Windows feature)
# SSH config files are always at "$env:ProgramData\ssh" irrespective of installation method.
# Note: if ssh key is created on Windows, it may not work on Linux due to DOS line endings.

$ErrorActionPreference = "Stop"
Set-ExecutionPolicy -Scope CurrentUser Bypass

# ===== INSTALLATION METHOD SELECTOR =====
$UseWinget = $true  # $true = winget (default, recommended), $false = Windows Capability


function Install-OpenSSH-Winget {
    Write-Host "Installing OpenSSH via winget..." -ForegroundColor Cyan
    winget install --no-upgrade --Id Microsoft.OpenSSH.Preview --source winget --accept-package-agreements --accept-source-agreements
    $wingetSshPath = "C:\Program Files\OpenSSH"
    $currentMachinePath = [System.Environment]::GetEnvironmentVariable("Path", "Machine")
    if ($currentMachinePath -notlike "*$wingetSshPath*") {
        Write-Host "Adding OpenSSH to system PATH..." -ForegroundColor Yellow
        [System.Environment]::SetEnvironmentVariable("Path", "$currentMachinePath;$wingetSshPath", "Machine")
    }
    $env:Path = [System.Environment]::GetEnvironmentVariable("Path", "Machine") + ";" + [System.Environment]::GetEnvironmentVariable("Path", "User")
}


function Install-OpenSSH-Capability {
    Write-Host "Installing OpenSSH via Windows Capability..." -ForegroundColor Cyan
    Add-WindowsCapability -Online -Name OpenSSH.Server
    Add-WindowsCapability -Online -Name OpenSSH.Client
    $env:Path = [System.Environment]::GetEnvironmentVariable("Path", "Machine") + ";" + [System.Environment]::GetEnvironmentVariable("Path", "User")
}


function Register-SshdService {
    param([string]$SshdExePath)
    Write-Host "Registering sshd service..." -ForegroundColor Yellow
    sc.exe create sshd binPath= "$SshdExePath" start= auto
    if ($LASTEXITCODE -ne 0) { throw "Failed to create sshd service" }
}


function Configure-SshdService {
    param([string]$SshdExePath)
    $serviceExists = Get-Service -Name sshd -ErrorAction SilentlyContinue
    if (-not $serviceExists) {
        Write-Host "sshd service not found, registering manually..." -ForegroundColor Yellow
        Register-SshdService -SshdExePath $SshdExePath
    }
    Set-Service -Name sshd -StartupType Automatic
    Start-Service sshd
    Write-Host "sshd service started successfully." -ForegroundColor Green
}


function Configure-Firewall {
    param([string]$SshdExePath)
    $existingRule = Get-NetFirewallRule -Name "OpenSSH-Server-In-TCP" -ErrorAction SilentlyContinue
    if (-not $existingRule) {
        Write-Host "Creating firewall rule for SSH..." -ForegroundColor Yellow
        New-NetFirewallRule -Name "OpenSSH-Server-In-TCP" -DisplayName "OpenSSH SSH Server" -Enabled True -Direction Inbound -Protocol TCP -Action Allow -LocalPort 22 -Program $SshdExePath
    } else {
        Write-Host "Firewall rule already exists." -ForegroundColor Green
    }
}


function Configure-DefaultShell {
    Write-Host "Configuring default shell for SSH..." -ForegroundColor Cyan
    $shell = "C:\Windows\System32\WindowsPowerShell\v1.0\powershell.exe"
    # Alternative: "C:\Program Files\PowerShell\7\pwsh.exe" (slower startup)
    # Alternative: "C:\Windows\System32\wsl.exe" (for WSL)
    if (-not (Test-Path "HKLM:\SOFTWARE\OpenSSH")) { New-Item -Path "HKLM:\SOFTWARE\OpenSSH" -Force | Out-Null }
    New-ItemProperty -Path "HKLM:\SOFTWARE\OpenSSH" -Name DefaultShell -Value $shell -PropertyType String -Force | Out-Null
    New-ItemProperty -Path "HKLM:\SOFTWARE\OpenSSH" -Name DefaultShellCommandOption -Value "/c" -PropertyType String -Force | Out-Null
    Write-Host "Default shell set to: $shell" -ForegroundColor Green
}


function Configure-SshAgent {
    Write-Host "Configuring ssh-agent service..." -ForegroundColor Cyan
    $agentService = Get-Service -Name ssh-agent -ErrorAction SilentlyContinue
    if ($agentService) {
        Set-Service -Name ssh-agent -StartupType Automatic
        Start-Service ssh-agent -ErrorAction SilentlyContinue
        Write-Host "ssh-agent service configured and started." -ForegroundColor Green
    } else {
        Write-Host "ssh-agent service not available." -ForegroundColor Yellow
    }
}


function Ensure-SshDirectory {
    $sshDir = Join-Path $env:USERPROFILE ".ssh"
    if (-not (Test-Path $sshDir)) {
        New-Item -ItemType Directory -Path $sshDir -Force | Out-Null
        Write-Host "Created .ssh directory at: $sshDir" -ForegroundColor Green
    }
}


# ===== MAIN EXECUTION =====
Write-Host "========================================" -ForegroundColor Magenta
Write-Host "OpenSSH Server Installation for Windows" -ForegroundColor Magenta
Write-Host "========================================" -ForegroundColor Magenta

if ($UseWinget) {
    Write-Host "Using winget installation method (recommended)" -ForegroundColor Cyan
    Install-OpenSSH-Winget
    $sshdExePath = "C:\Program Files\OpenSSH\sshd.exe"
} else {
    Write-Host "Using Windows Capability installation method" -ForegroundColor Cyan
    Install-OpenSSH-Capability
    $sshdExePath = "$env:WINDIR\System32\OpenSSH\sshd.exe"
}

Configure-SshdService -SshdExePath $sshdExePath
Configure-Firewall -SshdExePath $sshdExePath
Configure-DefaultShell
Configure-SshAgent
Ensure-SshDirectory

Write-Host "========================================" -ForegroundColor Magenta
Write-Host "OpenSSH Server installation complete!" -ForegroundColor Green
Write-Host "SSH config directory: $env:ProgramData\ssh" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Magenta
