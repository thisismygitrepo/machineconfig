
# Install SSH-Server on a windows machine.
# ALL of the following require admin priviliages:
# PowerShell.exe -ExecutionPolicy Bypass -File "C:\bypass\prompt\standard.ps1" 2>&1>$null

Add-WindowsCapability -Online -Name OpenSSH.Server
#New-NetFirewallRule -Name sshd -DisplayName 'OpenSSH SSH Server' -Enabled True -Direction Inbound -Protocol TCP -Action Allow -LocalPort 22 -Program "%WINDIR%\System32\OpenSSH\sshd.exe"

#Must Enable ssh-agent before starting
#Set-Service -Name ssh-agent -StartupType Automatic
#Start-Service ssh-agent
Set-Service -Name sshd -StartupType Automatic
Start-Service sshd
# Starting the service for the first time will populate the directory with config files.

# Next up, change default shell to powershell, becuse CMD is lame
# following: https://github.com/PowerShell/Win32-OpenSSH/wiki/DefaultShell
New-ItemProperty -Path "HKLM:\SOFTWARE\OpenSSH" -Name DefaultShell -Value "C:\Windows\System32\WindowsPowerShell\v1.0\powershell.exe" -PropertyType String -Force
New-ItemProperty -Path "HKLM:\SOFTWARE\OpenSSH" -Name DefaultShellCommandOption -Value "/c" -PropertyType String -Force
