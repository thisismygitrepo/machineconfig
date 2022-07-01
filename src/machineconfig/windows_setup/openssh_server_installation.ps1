
$ErrorActionPreference = "Stop"

# Install SSH-Server on a windows machine. see this other way as well: https://github.com/PowerShell/Win32-OpenSSH/wiki/Install-Win32-OpenSSH
# ALL of the following require admin priviliages:
# PowerShell.exe -ExecutionPolicy Bypass -File "C:\bypass\prompt\standard.ps1" 2>&1>$null

Add-WindowsCapability -Online -Name OpenSSH.Server
Add-WindowsCapability -Online -Name OpenSSH.Client
#New-NetFirewallRule -Name sshd -DisplayName 'OpenSSH SSH Server' -Enabled True -Direction Inbound -Protocol TCP -Action Allow -LocalPort 22 -Program "%WINDIR%\System32\OpenSSH\sshd.exe"

# Must Enable ssh-agent before starting. But even before that, one need to update path so that same shell has access to the NEWLY added ssh program
$env:Path = [System.Environment]::GetEnvironmentVariable("Path","Machine") + ";" + [System.Environment]::GetEnvironmentVariable("Path","User")
Set-Service -Name sshd -StartupType Automatic
#Set-Service -Name ssh-agent -StartupType Automatic
#Start-Service ssh-agent
# Starting the service for the first time will populate the directory with config files.
Start-Service sshd

# Next up, change default shell to powershell, becuse CMD is lame
# following: https://github.com/PowerShell/Win32-OpenSSH/wiki/DefaultShell
$shell = "C:\Windows\System32\wsl.exe"  # "C:\Windows\System32\WindowsPowerShell\v1.0\powershell.exe"
New-ItemProperty -Path "HKLM:\SOFTWARE\OpenSSH" -Name DefaultShell -Value $shell -PropertyType String -Force
New-ItemProperty -Path "HKLM:\SOFTWARE\OpenSSH" -Name DefaultShellCommandOption -Value "/c" -PropertyType String -Force
