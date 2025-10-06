
$ErrorActionPreference = "Stop"
# ALL of the following require admin priviliages:
Set-ExecutionPolicy Bypass
# PowerShell.exe -ExecutionPolicy Bypass -File "C:\bypass\prompt\standard.ps1" 2>&1>$null

# Install SSH-Server on a windows machine. see this one below if this one didn't work:
# to install: winget install --Id Microsoft.OpenSSH.Preview --source winget --scope user  # from: https://github.com/PowerShell/Win32-OpenSSH/wiki/Install-Win32-OpenSSH
# the result is installed in C:\Program Files\OpenSSH as opposed to C:\Windows\System32\OpenSSH which is the case if openssh is added as a feature/capability to windows
# However, notice the new path is not in PATH as is the cases with system variant, so it needs to be added manually.
# finally, ssh config files are always @ "$env:ProgramData\ssh" irrespective of installation method.
# if ssh key is created on windows, it doesn't work on linux and gives a cryptlib error. It must be read again and saved in non DOS format.

Add-WindowsCapability -Online -Name OpenSSH.Server
Add-WindowsCapability -Online -Name OpenSSH.Client

#New-NetFirewallRule -Name sshd -DisplayName 'OpenSSH SSH Server' -Enabled True -Direction Inbound -Protocol TCP -Action Allow -LocalPort 22 -Program "%WINDIR%\System32\OpenSSH\sshd.exe"

# Must Enable ssh-agent before starting. But even before that, one need to update path so that same shell has access to the NEWLY added ssh program
$env:Path = [System.Environment]::GetEnvironmentVariable("Path","Machine") + ";" + [System.Environment]::GetEnvironmentVariable("Path","User")

Set-Service -Name sshd -StartupType Automatic
#Get-Service -Name ssh-agent | Set-Service -StartupType Automatic
#Set-Service -Name ssh-agent -StartupType Automatic
#Start-Service ssh-agent
# Starting the service for the first time will populate the directory with config files.
Start-Service sshd

# Next up, change default shell to powershell, becuse CMD is lame
# following: https://github.com/PowerShell/Win32-OpenSSH/wiki/DefaultShell
$shell = "C:\Windows\System32\WindowsPowerShell\v1.0\powershell.exe"  # "C:\Windows\System32\wsl.exe"
# $shell = "C:\Program Files\PowerShell\7\pwsh.exe"  # it slows SSH down because of startup time, one can still use it by running it explicitly
New-ItemProperty -Path "HKLM:\SOFTWARE\OpenSSH" -Name DefaultShell -Value $shell -PropertyType String -Force
New-ItemProperty -Path "HKLM:\SOFTWARE\OpenSSH" -Name DefaultShellCommandOption -Value "/c" -PropertyType String -Force

cd ~
mkdir .ssh -ErrorAction SilentlyContinue
