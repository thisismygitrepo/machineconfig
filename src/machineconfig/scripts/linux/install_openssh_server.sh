
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

$sshd_dir = "$env:ProgramData\ssh"
$sshfile = "$env:USERPROFILE\.ssh\id_rsa.pub"  # this directory is for normal users, not admins.
# Once they are populated, we can create administrators_authorized_keys

type $sshfile >> "$sshd_dir\administrators_authorized_keys"
# set appropirate persmissions for this file
icacls administrators_authorized_keys /inheritance:r /grant "Administrators:F" /grant "SYSTEM:F"

# Lastly, enabling public key authentication.
(Get-Content "$sshd_dir\sshd_config") -replace '#PubkeyAuthentication', 'PubkeyAuthentication' | Out-File -encoding ASCII $sshd_config
#(Get-Content $sshd_dir\sshd_config) -replace 'AuthorizedKeysFile __PROGRAMDATA__', '#AuthorizedKeysFile __PROGRAMDATA__' | Out-File -encoding ASCII $sshd_config
#(Get-Content $sshd_dir\sshd_config) -replace 'Match Group administrators', '#Match Group administrators' | Out-File -encoding ASCII $sshd_config
#cat C:\ProgramData\ssh\sshd_config

# to load the fresh settings, we need to restart the service:
#Restart-Service ssh-agent -Force
Restart-Service sshd -Force

#Write-Host "Use this to Login/test Now"
#write-host ssh $env:UserName@localhost
