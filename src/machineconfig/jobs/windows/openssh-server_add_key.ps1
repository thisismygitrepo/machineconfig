
$sshfile=""
$ErrorActionPreference = "Stop"
$sshd_dir = "$env:ProgramData\ssh"
cp "$sshd_dir\administrators_authorized_keys" "$sshd_dir\administrators_authorized_keys.orig"
Get-Content $sshfile >> "$sshd_dir\administrators_authorized_keys"
Restart-Service sshd -Force
