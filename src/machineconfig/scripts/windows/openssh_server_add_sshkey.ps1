
# run this script only after having public ssh key in place.script
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
Restart-Service sshd -Force

#Write-Host "Use this to Login/test Now"
#write-host ssh $env:UserName@localhost

