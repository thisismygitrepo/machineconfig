Write-Host "
🚀 ===========================================
📦 Machine Configuration Installation Script
============================================="

Write-Host "ℹ️  If you have execution policy issues, run:
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser"
Write-Host "💡 To accept all prompts automatically, run: `$yesAll = `$true`n"


Write-Host "🔄 Setting up Python environment..."
Invoke-WebRequest -Uri "https://raw.githubusercontent.com/thisismygitrepo/machineconfig/main/src/machineconfig/setup_windows/ve.ps1" -OutFile "ve.ps1"
.\ve.ps1
rm ve.ps1

Write-Host "`n🔄 Setting up repositories..."
Invoke-WebRequest -Uri "https://raw.githubusercontent.com/thisismygitrepo/machineconfig/main/src/machineconfig/setup_windows/repos.ps1" -OutFile "repos.ps1"
.\repos.ps1
rm repos.ps1

Write-Host "`n📂 ============================================
🔄 DOTFILES MIGRATION OPTIONS
============================================="

Write-Host "🖱️  Method 1: USING MOUSE WITHOUT KB OR BROWSER SHARE
    On original machine, run:
    cd ~/dotfiles/creds/msc
    easy-sharing . --password rew
    Then open browser on new machine to get MouseWithoutBorders password"

Write-Host "`n🔐 Method 2: USING SSH
    FROM REMOTE, RUN:
    ftpx ~/dotfiles `$(hostname):^ -z"

Write-Host "`n💻 For WSL:
    wsl_server.ps1
    ftpx ~/dotfiles `$env:USERNAME@localhost:2222 -z
    # OR:
    New-Item -ItemType SymbolicLink -Path `$env:USERPROFILE\dotfiles -Target \\wsl`$\Ubuntu\home\`$env:USERNAME\dotfiles"

Write-Host "`n☁️  Method 3: USING INTERNET SECURE SHARE
    cd ~
    cloud_copy SHARE_URL . --config ss
    (requires symlinks to be created first)"

Write-Host "`n----------------------------------------"
if (-not $yesAll) {
    $choice = Read-Host "🔒 Install SSH Server [y]/n"
} else {
    $choice = "y"
}
if ([string]::IsNullOrEmpty($choice)) { $choice = "y" }
if ($choice -eq "y" -or $choice -eq "Y") {
    Write-Host "`n🔧 Installing and configuring SSH server..."
    Add-WindowsCapability -Online -Name OpenSSH.Server~~~~0.0.1.0
    Start-Service sshd
    Set-Service -Name sshd -StartupType 'Automatic'
    Write-Host "✅ SSH Server installed and configured successfully!"
} else {
    Write-Host "⏭️  Skipping SSH server installation"
}

Write-Host "`n✨ ===========================================
🎉 Installation Complete!
============================================="

# Confirm copying finished
if (-not $yesAll) {
    $choice = Read-Host "Did you finish copying [y]/n ? "
} else {
    $choice = "y"
}
if ([string]::IsNullOrEmpty($choice)) { $choice = "y" }
if ($choice -eq "y" -or $choice -eq "Y") {
    Write-Host "Proceeding..."
} else {
    Write-Host "Installation aborted."
}

# Create Symlinks
if (-not $yesAll) {
    $createLinksChoice = Read-Host "Create (Sym/Hard)links (finish dotfiles transfer first) [y]/n ? "
} else {
    $createLinksChoice = "y"
}
if ([string]::IsNullOrEmpty($createLinksChoice)) { $createLinksChoice = "y" }

if ($createLinksChoice -eq "y" -or $createLinksChoice -eq "Y") {
    if (-not $yesAll) {
        $linkTypeChoice = Read-Host "Create Symlinks (s) or Hardlinks (h) [s]/h ? "
    } else {
        $linkTypeChoice = "h"
    }

    . ~\code\machineconfig\.venv\Scripts\Activate.ps1

    if ($linkTypeChoice -eq "s" -or $linkTypeChoice -eq "S") {
        python -m fire machineconfig.profile.create main --choice=all
    } elseif ($linkTypeChoice -eq "h" -or $linkTypeChoice -eq "H") {
        # python -m fire machineconfig.profile.create_hardlinks main --choice=all
        python -m fire machineconfig.profile.create main --choice=all
    } else {
        Write-Host "Invalid choice for link type. Installation aborted."
    }

    # icacls "~\.ssh\*" /inheritance:r /grant:r "$($env:USERNAME):(F)"
    # icacls "~\.ssh" /inheritance:r /grant:r "$($env:USERNAME):(F)"
} else {
    Write-Host "Installation aborted."
}

# Install CLI Apps
if (-not $yesAll) {
    $choice = Read-Host "Install CLI Apps [y]/n ? "
    if ([string]::IsNullOrEmpty($choice)) { $choice = "y" }
    if ($choice -eq "y" -or $choice -eq "Y") {
        . ~\code\machineconfig\src\machineconfig\setup_windows\devapps.ps1
    } else {
        Write-Host "Installation aborted."
    }
    
} else {
    uv run --python 3.13 --with machineconfig python -m fire machineconfig.scripts.python.devops_devapps_install main  --which=AllEssentials
}


# Retrieve Repos
if (-not $yesAll) {
    $choice = Read-Host "Retrieve Repos at ~/code [y]/n ? "
} else {
    $choice = "y"
}
if ([string]::IsNullOrEmpty($choice)) { $choice = "y" }
if ($choice -eq "y" -or $choice -eq "Y") {
    repos ~\code --clone --cloud odg1
} else {
    Write-Host "Installation aborted."
}

# Retrieve Data
if (-not $yesAll) {
    $choice = Read-Host "Retrieve data [y]/n ? "
} else {
    $choice = "y"
}
if ([string]::IsNullOrEmpty($choice)) { $choice = "y" }
if ($choice -eq "y" -or $choice -eq "Y") {
    uv run --python 3.13 --with machineconfig python -m fire machineconfig.scripts.python.devops_backup_retrieve main --direction=RETRIEVE
} else {
    Write-Host "Installation aborted."
}


# Install Brave, WezTerm, and VSCode
if (-not $yesAll) {
    $choice = Read-Host "Install Brave+WindowsTerminal+WezTerm+VSCode [y]/n ? "
} else {
    $choice = "y"
}
if ([string]::IsNullOrEmpty($choice)) { $choice = "y" }
if ($choice -eq "y" -or $choice -eq "Y") {
    winget install --no-upgrade --name "Windows Terminal"             --Id "Microsoft.WindowsTerminal"  --source winget --scope user --accept-package-agreements --accept-source-agreements  # Terminal is is installed by default on W 11
    winget install --no-upgrade --name "Powershell"                   --Id "Microsoft.PowerShell"       --source winget --scope user --accept-package-agreements --accept-source-agreements  # powershell require admin
    winget install --no-upgrade --name "Brave"                        --Id "Brave.Brave"                --source winget --scope user --accept-package-agreements --accept-source-agreements
    winget install --no-upgrade --name "Microsoft Visual Studio Code" --Id "Microsoft.VisualStudioCode" --source winget --scope user --accept-package-agreements --accept-source-agreements
    uv run --python 3.13 --with machineconfig python -m fire machineconfig.setup_windows.wt_and_pwsh.install_nerd_fonts main
    uv run --python 3.13 --with machineconfig python -m fire machineconfig.setup_windows.wt_and_pwsh.set_wt_settings main
} else {
    Write-Host "Installation aborted."
}


# Install Apps
if (-not $yesAll) {
    $choice = Read-Host "Install Windows Apps [y]/n ? "
} else {
    $choice = "y"
}
if ($choice -eq "y" -or $choice -eq "Y") {
    Invoke-WebRequest -Uri "https://raw.githubusercontent.com/thisismygitrepo/machineconfig/main/src/machineconfig/setup_windows/apps.ps1" -OutFile "apps.ps1"
    .\apps.ps1
} else {
    Write-Host "Installation aborted."
}

# Instructions for Thunderbird profile restoration
# Run this after installing Thunderbird and starting it and shutting it down but before downloading backup
# cd ~/AppData/Roaming/ThunderBird/Profiles
# $res = Get-ChildItem
# $name = $res[0].Name
# Move-Item $backup_folder $name
