
Invoke-WebRequest https://raw.githubusercontent.com/thisismygitrepo/machineconfig/main/src/machineconfig/setup_windows/openssh-server.ps1 | Invoke-Expression

cd ~
echo $null >> .ssh/authorized_keys  # powershell way of touching a file if it doesn't exist
echo $pubkey_string >> .ssh/authorized_keys
echo $pubkey_string > .ssh/pubkey.pub

Invoke-WebRequest https://raw.githubusercontent.com/thisismygitrepo/machineconfig/main/src/machineconfig/setup_windows/openssh-server_add-sshkey.ps1 | Invoke-Expression
