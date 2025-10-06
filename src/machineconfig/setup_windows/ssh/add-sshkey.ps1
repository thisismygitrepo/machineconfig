
# This script adds a public key to the authorized_keys file for the sshd service
# as a result, a remote can connet to the machine if they got the corresponding private key (identity).

# https://docs.microsoft.com/en-us/windows-server/administration/openssh/openssh_keymanagement
# http://woshub.com/using-ssh-key-based-authentication-on-windows/

$ErrorActionPreference = "Stop"
$sshd_dir = "$env:ProgramData\ssh"
$sshfile = "$env:USERPROFILE\.ssh\pubkey.pub"  # this directory is for normal users, not admins.
# Once they are populated, we can create administrators_authorized_keys

Get-Content $sshfile >> "$sshd_dir\administrators_authorized_keys"
# set appropirate persmissions for this file
Set-Location $sshd_dir
icacls administrators_authorized_keys /inheritance:r /grant "Administrators:F" /grant "SYSTEM:F"
# Lastly, enabling public key authentication.
$sshd_config = "$sshd_dir\sshd_config"
(Get-Content $sshd_config) -replace '#PubkeyAuthentication', 'PubkeyAuthentication' | Out-File -encoding ASCII $sshd_config
#(Get-Content $sshd_dir\sshd_config) -replace 'AuthorizedKeysFile __PROGRAMDATA__', '#AuthorizedKeysFile __PROGRAMDATA__' | Out-File -encoding ASCII $sshd_config
#(Get-Content $sshd_dir\sshd_config) -replace 'Match Group administrators', '#Match Group administrators' | Out-File -encoding ASCII $sshd_config
#cat C:\ProgramData\ssh\sshd_config

# to load the fresh settings, we need to restart the service:
Restart-Service sshd -Force

#Write-Host "Use this to Login/test Now"
#write-host ssh $env:UserName@localhost
# debug tip: use nano editor to inspect files above, if unreadable max-text format is used, ssh won't work.
