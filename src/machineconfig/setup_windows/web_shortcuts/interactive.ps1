
echo "If you have execution policy issues, run: Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser."
echo "If you want to accept everything, run: \$yesAll = $true"

# Set environment variable and execute scripts

$ve_name = "ve"
Invoke-WebRequest -Uri "https://raw.githubusercontent.com/thisismygitrepo/machineconfig/main/src/machineconfig/setup_windows/ve.ps1" -OutFile "ve.ps1"
.\ve.ps1

Invoke-WebRequest -Uri "https://raw.githubusercontent.com/thisismygitrepo/machineconfig/main/src/machineconfig/setup_windows/repos.ps1" -OutFile "repos.ps1"
.\repos.ps1

# Display messages about moving dotfiles
Write-Host "MOVING DOTFILES TO NEW MACHINE"
Write-Host "USING MOUSE WITHOUT KB OR BROWSER SHARE: On original machine, run: 'cd ~/dotfiles/creds/msc; easy-sharing . --password rew'. On new machine, open browser and navigate to URL to get password of mousewithoutborders"
Write-Host "USING SSH: FROM REMOTE, RUN: fptx ~/dotfiles $(hostname):^ -z"
Write-Host "* for WSL: `wsl_server.ps1; ftpx ~/dotfiles $env:USERNAME@localhost:2222 -z # OR: New-Item -ItemType SymbolicLink -Path $env:USERPROFILE\dotfiles -Target \\wsl$\Ubuntu\home\$env:USERNAME\dotfiles"
Write-Host "USING INTERNET SECURE SHARE: cd ~; cloud_copy SHARE_URL . --config ss (requires symlinks to be created first)"

# Install SSH Server
if (-not $yesAll) {
    $choice = Read-Host "Install SSH Server [y]/n ? "
} else {
    $choice = "y"
}
if ([string]::IsNullOrEmpty($choice)) { $choice = "y" }
if ($choice -eq "y" -or $choice -eq "Y") {
    Add-WindowsCapability -Online -Name OpenSSH.Server~~~~0.0.1.0
    Start-Service sshd
    Set-Service -Name sshd -StartupType 'Automatic'
    Write-Host "SSH Server installed and started."
} else {
    Write-Host "Installation aborted."
}

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

    . ~\venvs\ve\Scripts\Activate.ps1

    if ($linkTypeChoice -eq "s" -or $linkTypeChoice -eq "S") {
        python -m fire machineconfig.profile.create main --choice=all
    } elseif ($linkTypeChoice -eq "h" -or $linkTypeChoice -eq "H") {
        python -m fire machineconfig.profile.create_hardlinks main --choice=all
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
} else {
    $choice = "y"
}
if ([string]::IsNullOrEmpty($choice)) { $choice = "y" }
if ($choice -eq "y" -or $choice -eq "Y") {
    . ~\code\machineconfig\src\machineconfig\setup_windows\devapps.ps1
} else {
    Write-Host "Installation aborted."
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
    . ~\venvs\ve\Scripts\Activate.ps1
    python -m fire machineconfig.scripts.python.devops_backup_retrieve main --direction=RETRIEVE
} else {
    Write-Host "Installation aborted."
}


# Install Brave, WezTerm, and VSCode
if (-not $yesAll) {
    $choice = Read-Host "Install Brave+WezTerm+VSCode [y]/n ? "
} else {
    $choice = "y"
}
if ([string]::IsNullOrEmpty($choice)) { $choice = "y" }
if ($choice -eq "y" -or $choice -eq "Y") {
    . ~\venvs\ve\Scripts\Activate.ps1
    # python -m fire machineconfig.scripts.python.devops_devapps_install main --which=wezterm
    # python -m fire machineconfig.scripts.python.devops_devapps_install main --which=brave
    # python -m fire machineconfig.scripts.python.devops_devapps_install main --which=code
    winget install --no-upgrade --name "Windows Terminal"             --Id "Microsoft.WindowsTerminal"  --source winget --scope user --accept-package-agreements --accept-source-agreements  # Terminal is is installed by default on W 11
    winget install --no-upgrade --name "Brave"                        --Id "Brave.Brave"                --source winget --scope user --accept-package-agreements --accept-source-agreements
    winget install --no-upgrade --name "Microsoft Visual Studio Code" --Id "Microsoft.VisualStudioCode" --source winget --scope user --accept-package-agreements --accept-source-agreements
    python -m fire machineconfig.setup_windows.wt_and_pwsh.set_pwsh_theme install_nerd_fonts
    python -m fire machineconfig.setup_windows.wt_and_pwsh.set_wt_settings main

} else {
    Write-Host "Installation aborted."
}


# Install Apps
if (-not $yesAll) {
    $choice = Read-Host "Install Apps [y]/n ? "
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
